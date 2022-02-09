import logging

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from battle_of_chains.battle.models import BattleSettings, Projectile, Tank
from battle_of_chains.battle.serializers import (
    GlobalSettingsSerializer,
    ProjectileSerializer,
    TankNewTokenIdSerializer,
    TankNftMetaSerializer,
    TankSerializer,
)
from battle_of_chains.blockchain.models import Contract, Wallet
from battle_of_chains.blockchain.serializers import ContractSerializer, WalletSerializer
from battle_of_chains.blockchain.utils import SmartContract
from battle_of_chains.users.serializers import UserSerializer

logger = logging.getLogger(__name__)
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


class TankNftMetaViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = TankNftMetaSerializer
    queryset = Tank.objects.all()
    permission_classes = [AllowAny]


class WalletViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get_object(self):
        return Wallet.objects.get(address__iexact=self.kwargs.get('pk'))

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = False
        try:
            wallet = Wallet.objects.get(
                address__iexact=serializer.validated_data.get('address')
            )
            wallet.save()
            if request.user.wallet != wallet:
                if hasattr(wallet, 'user'):
                    old_owner = wallet.user
                    old_owner.wallet = None
                    old_owner.save()
                request.user.wallet = wallet
                request.user.save()
        except Wallet.DoesNotExist:
            wallet = serializer.save()
            created = True
            request.user.wallet = wallet
            request.user.save()
        headers = self.get_success_headers(serializer.data)
        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class TankNewTokenIdViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = TankNewTokenIdSerializer
    queryset = Tank.objects.all()


class GlobalSettingsView(RetrieveAPIView):
    serializer_class = GlobalSettingsSerializer

    def get_object(self):
        return BattleSettings.get_solo()


class ReadBlockchainView(APIView):

    def post(self, request, format=None):
        tx_hash = request.POST.get('transactionHash')
        contract_address = request.POST.get('to')
        if not tx_hash or not contract_address:
            return Response({'error': 'invalid data received'}, status=HTTP_400_BAD_REQUEST)
        try:
            contract = Contract.objects.get(address=contract_address)
        except Contract.DoesNotExist:
            return Response({'error': f'Contract with address {contract_address} does not exist'},
                            status=HTTP_400_BAD_REQUEST)
        smart_contract = SmartContract(contract)
        try:
            smart_contract.read_events_by_tx(tx_hash)
        except Exception as e:
            logger.exception(f'Exception trying to read events from tx {tx_hash}: {e}')
            return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': True}, status=HTTP_200_OK)
