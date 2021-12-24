import json
import logging
import os

from django.conf import settings
from web3 import Web3

from battle_of_chains.blockchain.models import Contract

logger = logging.getLogger(__name__)


def send_transaction(w3, txn, owner_address, owner_secret):
    try:
        gas = txn.estimateGas()
        txn = txn.buildTransaction({'nonce': w3.eth.getTransactionCount(owner_address), 'gas': gas})
        signed_txn = w3.eth.account.signTransaction(txn, owner_secret)
        transaction = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        tx_receipt = w3.eth.waitForTransactionReceipt(transaction)
        return tx_receipt
    except ValueError as e:
        logger.error(f'Error message: {e}')
        try:
            msg = json.loads(str(e))
        except:
            raise
        else:
            logger.exception(f'msg: {msg.get("message")}')


def deploy_smart_contract(contract: Contract):
    w3 = Web3(Web3.HTTPProvider(contract.network.rpc_url, request_kwargs={'timeout': 600}))
    owner = settings.CONTRACTS_OWNER
    w3.eth.defaultAccount = owner['address']
    with open(os.path.join(settings.ROOT_DIR, 'contracts', 'nft.json')) as f:  # TODO: change later
        contract_definitions = json.load(f)
    if not contract.address:
        logger.debug(f'Deploy...')
        contract = w3.eth.contract(abi=contract_definitions['abi'], bytecode=contract_definitions['bytecode'])
        txn = contract.constructor()
        tx_receipt = send_transaction(w3, txn, owner['address'], owner['secret'])
        contract_address = tx_receipt['contractAddress']
        contract.address = contract_address
        contract.save()
        logger.info(f'Contract is deployed at {contract_address}')
        logger.info(tx_receipt)
    else:
        logger.debug(f'Contract already deployed at {contract.address}')
