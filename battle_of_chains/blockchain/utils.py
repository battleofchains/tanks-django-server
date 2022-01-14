import json
import logging
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Max
from django.urls import reverse
from web3 import Web3, auto
from web3.middleware import geth_poa_middleware

from battle_of_chains.battle.models import Tank
from battle_of_chains.blockchain.models import NFT, BlockchainEvent, Contract, Wallet

logger = logging.getLogger(__name__)
User = get_user_model()


def send_transaction(w3, txn, owner_address, owner_secret):
    try:
        gas = txn.estimateGas()
        txn = txn.buildTransaction(
            {'nonce': w3.eth.getTransactionCount(owner_address), 'gas': gas, "gasPrice": w3.eth.gas_price}
        )
        signed_txn = w3.eth.account.signTransaction(txn, owner_secret)
        transaction = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        tx_receipt = w3.eth.waitForTransactionReceipt(transaction)
        return tx_receipt
    except ValueError as e:
        logger.error(f'Error message: {e}')
        try:
            msg = json.loads(str(e))
        except Exception as e:
            raise e
        else:
            logger.exception(f'msg: {msg.get("message")}')


def get_w3_provider(contract: Contract) -> Web3:
    w3 = Web3(Web3.HTTPProvider(contract.network.rpc_url, request_kwargs={'timeout': 60}))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    owner = settings.CONTRACTS_OWNER
    w3.eth.defaultAccount = owner['address']
    return w3


def deploy_smart_contract(contract: Contract):
    w3 = get_w3_provider(contract)
    owner = settings.CONTRACTS_OWNER
    if not contract.address:
        logger.debug(f'Deploy...')
        smart_contract = w3.eth.contract(
            abi=contract.contract_definitions['abi'], bytecode=contract.contract_definitions['bytecode']
        )
        txn = smart_contract.constructor(contract.name, contract.symbol)
        tx_receipt = send_transaction(w3, txn, owner['address'], owner['secret'])
        contract_address = tx_receipt['contractAddress']
        contract.address = contract_address
        contract.is_active = True
        contract.save()
        logger.info(f'Contract is deployed at {contract_address}')
        logger.info(tx_receipt)
    else:
        logger.debug(f'Contract already deployed at {contract.address}')


def mint_nft(tank: Tank, mainnet=False):
    if NFT.objects.filter(tank=tank).exists():
        logger.error(f'NFT for tank {tank.id} already minted')
        return
    if not tank.owner or not tank.owner.wallet:
        logger.error(f'Tank {tank.id} owner has no associated wallet to mint to')
        return
    if mainnet:
        network_code = 'bsc-main'
    else:
        network_code = 'bsc-test'
    contract = Contract.objects.get(network__code=network_code, is_active=True, symbol='BOFCNFT')
    w3 = get_w3_provider(contract)
    owner = settings.CONTRACTS_OWNER
    smart_contract = w3.eth.contract(
        abi=contract.contract_definitions['abi'], address=w3.toChecksumAddress(contract.address)
    )
    address_to = tank.owner.wallet.address
    price = w3.toWei(tank.price, 'ether')
    meta_url = reverse('api:nft_meta-detail', args=[tank.id])
    meta_url = urljoin(settings.SITE_URL, meta_url)
    txn = smart_contract.functions.mint(tank.id, meta_url, address_to, price)
    tx_receipt = send_transaction(w3, txn, owner['address'], owner['secret'])
    logger.info(tx_receipt)
    if tx_receipt.get('transactionHash'):
        tx_hash = tx_receipt['transactionHash'].hex()
        NFT.objects.create(tank=tank, tx_hash=tx_hash, contract=contract, owner=tank.owner.wallet)


def process_event_data(event: str, data: dict):
    args = data['args']
    match event:
        case 'Purchase':
            new_owner_address = args['newOwner']
            nft_id = args['nftID']
            price = args['price']
            try:
                tank = Tank.objects.get(id=nft_id)
                new_owner = User.objects.get(wallet__address=new_owner_address)
            except Tank.DoesNotExist:
                logger.error(f'Tank with id {nft_id} does not exist')
            except User.DoesNotExist:
                logger.error(f'User with wallet address {new_owner_address} does not exist')
                tank.owner = None
                tank.price = Web3.fromWei(price, 'ether')
                tank.save()
                wallet, _ = Wallet.objects.get_or_create(address=new_owner_address)
                tank.nft.owner = wallet
                tank.nft.save()
            else:
                tank.owner = new_owner
                tank.price = Web3.fromWei(price, 'ether')
                tank.save()
                tank.nft.owner = new_owner.wallet
                tank.nft.save()
        case 'Minted':
            to_address = args['minter']
            nft_id = args['nftID']
            price = args['price']
            wallet, _ = Wallet.objects.get_or_create(address=to_address)
            try:
                tank = Tank.objects.get(id=nft_id)
                contract = Contract.objects.get(address=data['address'])
            except Tank.DoesNotExist:
                logger.error(f'Tank with id {nft_id} does not exist')
            except Contract.DoesNotExist:
                logger.error(f"Contract with address {data['address']} does not exist")
            else:
                tank.price = Web3.fromWei(price, 'ether')
                tank.save()
                NFT.objects.create(tank=tank, owner=wallet, contract=contract, tx_hash=data['transactionHash'].hex())
        case 'PriceUpdate':
            nft_id = args['nftID']
            price = args['newPrice']
            try:
                tank = Tank.objects.get(id=nft_id)
            except Tank.DoesNotExist:
                logger.error(f'Tank with id {nft_id} does not exist')
            else:
                tank.price = price
                tank.save()
        case 'NftListStatus':
            nft_id = args['nftID']
            is_listed = args['isListed']
            try:
                tank = Tank.objects.get(id=nft_id)
            except Tank.DoesNotExist:
                logger.error(f'Tank with id {nft_id} does not exist')
            else:
                tank.for_sale = bool(is_listed)
                tank.save()


def read_contract_events(contract: Contract):
    w3 = get_w3_provider(contract)
    smart_contract = w3.eth.contract(
        abi=contract.contract_definitions['abi'], address=w3.toChecksumAddress(contract.address)
    )
    for event in ('Purchase', 'Minted', 'PriceUpdate', 'NftListStatus'):
        last_block = BlockchainEvent.objects.filter(contract=contract, event=event)\
            .aggregate(last_block=Max('block_number'))['last_block'] or 0
        last_block = max(last_block, w3.eth.get_block_number() - 5000)
        event_filter = smart_contract.events.__getitem__(event).createFilter(fromBlock=last_block)
        for entry in event_filter.get_all_entries():
            logger.debug(entry)
            args = entry['args']
            be, created = BlockchainEvent.objects.get_or_create(
                tx_hash=entry['transactionHash'].hex(),
                defaults={'contract': contract,
                          'event': event,
                          'block_number': entry['blockNumber'],
                          'args': args}
            )
            if created:
                ts = w3.eth.getBlock(entry['blockNumber'])['timestamp']
                be.timestamp = ts
                be.save()
                process_event_data(event, entry)
