from django.conf import settings
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter, SimpleRouter

from battle_of_chains.api.views import (
    ContractViewSet, GlobalSettingsView, ProjectileViewSet, TankNewTokenIdViewSet, TankNftMetaViewSet, TankViewSet,
    UserViewSet, WalletViewSet,)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("tanks", TankViewSet)
router.register("projectiles", ProjectileViewSet)
router.register("contracts", ContractViewSet)
router.register("nft-meta", TankNftMetaViewSet, basename='nft_meta')
router.register("wallets", WalletViewSet)
router.register("new_token_id", TankNewTokenIdViewSet, basename='new_token_id')


app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    path("auth-token/", obtain_auth_token, name='auth-token'),
    path('settings/', GlobalSettingsView.as_view(), name='settings')
]
