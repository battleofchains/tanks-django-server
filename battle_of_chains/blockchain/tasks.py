import logging
import time

from django.core.cache import cache

from battle_of_chains.battle.models import Tank
from battle_of_chains.blockchain.models import Contract
from battle_of_chains.blockchain.utils import deploy_smart_contract, mint_nft
from config.celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def deploy_smart_contract_task(self, contract_id):
    waited = 0
    while not cache.add(self.name, contract_id) and waited < 60 * 10:  # run only one task at a time
        time.sleep(5)
        waited += 5

    try:
        contract = Contract.objects.get(id=contract_id)
        deploy_smart_contract(contract)
    except Exception as e:
        logger.error(f'Cannot deploy contract {contract_id}. Error: {e}')
    finally:
        cache.delete(self.name)


@app.task(bind=True)
def mint_nft_task(self, tank_id):
    waited = 0
    while not cache.add(self.name, tank_id) and waited < 60 * 10:  # run only one task at a time
        time.sleep(5)
        waited += 5

    try:
        tank = Tank.objects.get(tank_id)
        mint_nft(tank)
    except Exception as e:
        logger.error(f'Cannot mint tank {tank_id}. Error: {e}')
    finally:
        cache.delete(self.name)
