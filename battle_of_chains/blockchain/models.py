from urllib.parse import urljoin

from django.db import models

from battle_of_chains.battle.models import Tank


class Wallet(models.Model):
    address = models.CharField(max_length=50, verbose_name='Wallet address', primary_key=True)
    date_add = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Last update')

    def __str__(self):
        return self.address

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.address = self.address.lower()
        super(Wallet, self).save(force_insert, force_update, using, update_fields)


class Network(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')
    code = models.CharField(max_length=50, verbose_name='Code', default='')
    rpc_url = models.URLField(verbose_name='RPC URL')
    url_explorer = models.URLField(verbose_name='URL Explorer')

    def __str__(self):
        return self.name


class Contract(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50, default='')
    contract_definitions = models.JSONField()
    address = models.CharField(max_length=42, verbose_name='Contract address', blank=True, null=True)
    contract_url = models.URLField(verbose_name='Contract URL', blank=True, null=True)
    network = models.ForeignKey(Network, on_delete=models.PROTECT)
    date_add = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Last update')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class NFT(models.Model):
    tx_hash = models.CharField(max_length=100, primary_key=True)
    tank = models.OneToOneField(Tank, on_delete=models.SET_NULL, null=True)
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return 'NFT for ' + self.tank.name

    @property
    def link(self):
        if self.contract:
            path = f"/token/{self.contract.address}?a={self.tank_id}"
            return urljoin(self.contract.network.url_explorer, path)
        return ''


class BlockchainEvent(models.Model):
    tx_hash = models.CharField(max_length=100, verbose_name='Transaction Hash', primary_key=True)
    event = models.CharField(max_length=100, verbose_name='Event name', editable=False)
    args = models.JSONField(editable=False)
    block_number = models.PositiveIntegerField(default=1, editable=False)
    timestamp = models.PositiveIntegerField(editable=False, null=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, editable=False)
