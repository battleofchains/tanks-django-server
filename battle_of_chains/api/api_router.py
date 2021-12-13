from django.conf import settings
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter, SimpleRouter

from battle_of_chains.api.views import (
    ProjectileViewSet,
    TankViewSet,
    UserViewSet,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("tanks", TankViewSet)
router.register("projectiles", ProjectileViewSet)


app_name = "api"
urlpatterns = router.urls
urlpatterns += [path("auth-token/", obtain_auth_token, name='auth-token')]
