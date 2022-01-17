from django.contrib import admin, messages

from battle_of_chains.utils.mixins import AdminNoChangeMixin

from .models import *
from .tasks import deploy_smart_contract_task


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'url_explorer')


@admin.register(Wallet)
class WalletAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_display = ('address', 'user', 'date_add', 'last_modified')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'address', 'network', 'is_active')
    actions = ('deploy_contracts',)

    def deploy_contracts(self, request, queryset):
        for obj in queryset:
            self.message_user(request, f"Contract {obj} is being deployed.", level=messages.INFO)
            deploy_smart_contract_task.delay(obj.pk)


@admin.register(NFT)
class NFTAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_display = ('tx_hash', 'tank', 'link')


@admin.register(BlockchainEvent)
class BlockchainLogAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_filter = ('event',)
