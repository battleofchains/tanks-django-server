from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from battle_of_chains.battle.models import Projectile, Tank
from battle_of_chains.battle.serializers import ProjectileSerializer, TankNftMetaSerializer, TankSerializer
from battle_of_chains.blockchain.models import Contract, Wallet
from battle_of_chains.blockchain.serializers import ContractSerializer, WalletSerializer
from battle_of_chains.users.serializers import UserSerializer

User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    # def get_queryset(self, *args, **kwargs):
    #     assert isinstance(self.request.user.id, int)
    #     return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class TankViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = TankSerializer
    queryset = Tank.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user)


class ProjectileViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = ProjectileSerializer
    queryset = Projectile.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(tank_id__in=self.request.user.tanks.values_list('id', flat=True))


class ContractViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = ContractSerializer
    queryset = Contract.objects.filter(is_active=True)


class TankNftMetaViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = TankNftMetaSerializer
    queryset = Tank.objects.all()


class WalletViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()
        self.request.user.wallet = instance
        self.request.user.save()
