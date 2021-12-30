import json
import logging

from django.conf import settings
from django.urls import reverse
from web3 import Web3
from web3.middleware import geth_poa_middleware

from battle_of_chains.battle.models import Tank
from battle_of_chains.blockchain.models import NFT, Contract

logger = logging.getLogger(__name__)


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


def deploy_smart_contract(contract: Contract):
    w3 = Web3(Web3.HTTPProvider(contract.network.rpc_url, request_kwargs={'timeout': 600}))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    owner = settings.CONTRACTS_OWNER
    w3.eth.defaultAccount = owner['address']
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
    if not tank.owner.wallet:
        logger.error(f'Tank {tank.id} owner has no associated wallet to mint to')
        return
    if mainnet:
        network_code = 'bsc-main'
    else:
        network_code = 'bsc-test'
    contract = Contract.objects.get(network__code=network_code, is_active=True, symbol='BOFCNFT')
    w3 = Web3(Web3.HTTPProvider(contract.network.rpc_url, request_kwargs={'timeout': 600}))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    owner = settings.CONTRACTS_OWNER
    w3.eth.defaultAccount = owner['address']
    smart_contract = w3.eth.contract(
        abi=contract.contract_definitions['abi'], address=w3.toChecksumAddress(contract.address)
    )
    address_to = tank.owner.wallet.address
    price = w3.toWei(tank.price, 'ether')
    meta_url = reverse('api:nft_meta-detail', args=[tank.id])
    txn = smart_contract.functions.mint(meta_url, address_to, price)
    tx_receipt = send_transaction(w3, txn, owner['address'], owner['secret'])
    logger.info(tx_receipt)
    if tx_receipt.get('transactionHash'):
        tx_hash = tx_receipt['transactionHash'].hex()
        NFT.objects.create(
            tank=tank, tx_hash=tx_hash, contract=contract
        )
