import logging
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Max
from django.urls import reverse
from web3 import Web3
from web3.middleware import geth_poa_middleware

from battle_of_chains.battle.models import BattleSettings, Tank
from battle_of_chains.blockchain.models import NFT, BlockchainEvent, Contract, Wallet

logger = logging.getLogger(__name__)
User = get_user_model()

EVENTS = ('Minted', 'Purchase', 'PriceUpdate', 'NftListStatus')


class MintException(Exception):
    pass


def send_transaction(w3, txn, owner_address, owner_secret):
    gas = txn.estimateGas()
    txn = txn.buildTransaction(
        {'nonce': w3.eth.getTransactionCount(owner_address), 'gas': gas, "gasPrice": w3.eth.gas_price}
    )
    signed_txn = w3.eth.account.signTransaction(txn, owner_secret)
    transaction = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(transaction)
    return tx_receipt


def mint_nft(tank: Tank):
    if NFT.objects.filter(tank=tank).exists():
        raise MintException(f'NFT for tank {tank.id} already minted')
    if not tank.owner or not tank.owner.wallet:
        raise MintException(f'Tank {tank.id} owner has no associated wallet to mint to')
    network = BattleSettings.get_solo().active_network
    if not network:
        raise MintException('Network not set in Global Settings')
    contract = Contract.objects.get(
        network=network, is_active=True, symbol=BattleSettings.get_solo().nft_ticker
    )
    smart_contract = SmartContract(contract)
    smart_contract.mint_nft(tank)


def process_event_data(event: str, data: dict):
    args = data['args']
    logger.info(args)
    match event:
        case 'Purchase':
            new_owner_address = args['newOwner']
            nft_id = args['nftID']
            price = args['price']
            wallet, _ = Wallet.objects.get_or_create(address__iexact=new_owner_address)
            try:
                tank = Tank.objects.get(id=nft_id)
                contract = Contract.objects.get(address__iexact=data['address'])
                new_owner = User.objects.get(wallet=wallet)
                try:
                    NFT.objects.get(tank=tank)
                except NFT.DoesNotExist:
                    NFT.objects.create(tank=tank, owner=wallet, contract=contract,
                                       tx_hash=data['transactionHash'].hex())
            except Tank.DoesNotExist:
                logger.error(f'Tank with id {nft_id} does not exist')
            except Contract.DoesNotExist:
                logger.error(f"Contract with address {data['address']} does not exist")
            except User.DoesNotExist:
                logger.error(f'User with wallet address {new_owner_address} does not exist')
                tank.owner = None
                tank.price = Web3.fromWei(price, 'ether')
                tank.save()
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
            wallet, _ = Wallet.objects.get_or_create(address__iexact=to_address)
            try:
                tank = Tank.objects.get(id=nft_id)
                contract = Contract.objects.get(address__iexact=data['address'])
            except Tank.DoesNotExist:
                logger.error(f'Tank with id {nft_id} does not exist')
            except Contract.DoesNotExist:
                logger.error(f"Contract with address {data['address']} does not exist")
            else:
                tank.price = Web3.fromWei(price, 'ether')
                tank.for_sale = True
                tank.save()
                try:
                    NFT.objects.get(tank=tank)
                except NFT.DoesNotExist:
                    NFT.objects.create(tank=tank, owner=wallet, contract=contract,
                                       tx_hash=data['transactionHash'].hex())
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


class SmartContract:

    def __init__(self, contract):
        self.contract = contract
        self.w3 = self._get_w3_provider()
        self.smart_contract = self.w3.eth.contract(
            abi=contract.contract_definitions['abi'], address=self.w3.toChecksumAddress(contract.address)
        )
        self.owner = settings.CONTRACTS_OWNER

    def _get_w3_provider(self) -> Web3:
        w3 = Web3(Web3.HTTPProvider(self.contract.network.rpc_url, request_kwargs={'timeout': 60}))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        w3.eth.defaultAccount = self.owner['address']
        return w3

    def deploy(self):
        if not self.contract.address:
            logger.debug(f'Deploy...')
            smart_contract = self.w3.eth.contract(
                abi=self.contract.contract_definitions['abi'], bytecode=self.contract.contract_definitions['bytecode']
            )
            txn = smart_contract.constructor(self.contract.name, self.contract.symbol)
            try:
                tx_receipt = send_transaction(self.w3, txn, self.owner['address'], self.owner['secret'])
            except Exception as e:
                logger.exception(e)
            else:
                contract_address = tx_receipt['contractAddress']
                self.contract.address = contract_address
                self.contract.is_active = True
                self.contract.save()
                logger.info(f'Contract is deployed at {contract_address}')
                logger.info(tx_receipt)
        else:
            logger.debug(f'Contract already deployed at {self.contract.address}')

    def mint_nft(self, tank):
        address_to = self.w3.toChecksumAddress(tank.owner.wallet.address)
        price = self.w3.toWei(tank.price, 'ether')
        meta_url = reverse('api:nft_meta-detail', args=[tank.id])
        meta_url = urljoin(settings.SITE_URL, meta_url)
        txn = self.smart_contract.functions.mint(tank.id, meta_url, address_to, price)
        tx_receipt = send_transaction(
            self.w3, txn, self.w3.toChecksumAddress(self.owner['address']), self.owner['secret']
        )
        logger.info(tx_receipt)
        if tx_receipt.get('transactionHash'):
            tx_hash = tx_receipt['transactionHash'].hex()
            NFT.objects.create(tank=tank, tx_hash=tx_hash, contract=self.contract, owner=tank.owner.wallet)

    def read_events(self):
        for event in EVENTS:
            last_block = BlockchainEvent.objects.filter(contract=self.contract, event=event) \
                             .aggregate(last_block=Max('block_number'))['last_block'] or 0
            last_block = max(last_block, self.w3.eth.get_block_number() - 4900)
            event_filter = self.smart_contract.events.__getitem__(event).createFilter(fromBlock=last_block)
            for entry in event_filter.get_all_entries():
                self.process_log_entry(entry, event)

    def process_log_entry(self, entry, event):
        logger.debug(entry)
        args = entry['args']
        be, created = BlockchainEvent.objects.get_or_create(
            tx_hash=entry['transactionHash'].hex(),
            event=event,
            defaults={'contract': self.contract,
                      'block_number': entry['blockNumber'],
                      'args': self.w3.toJSON(args)}
        )
        if created:
            ts = self.w3.eth.getBlock(entry['blockNumber'])['timestamp']
            be.timestamp = ts
            be.save()
            process_event_data(event, entry)

    def read_events_by_tx(self, tx_hash):
        tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        smart_contract = self.w3.eth.contract(
            abi=self.contract.contract_definitions['abi'], address=self.w3.toChecksumAddress(self.contract.address)
        )
        for event in EVENTS:
            processed_logs = smart_contract.events.__getitem__(event)().processReceipt(tx_receipt)
            assert len(processed_logs) == 1
            entry = processed_logs[0]
            self.process_log_entry(entry, event)
