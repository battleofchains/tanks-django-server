from django.contrib import admin

from battle_of_chains.utils.mixins import AdminNoChangeMixin

from .models import *


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'url_explorer')


@admin.register(Wallet)
class WalletAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_display = ('address', 'date_add', 'last_modified')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'address', 'network', 'deployed')


@admin.register(NFT)
class NFTAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_display = ('address', 'tank')
