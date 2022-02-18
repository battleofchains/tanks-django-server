from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, TemplateView, UpdateView

from battle_of_chains.battle.models import Battle, BattleSettings, Tank
from battle_of_chains.blockchain.models import Contract
from battle_of_chains.blockchain.utils import SmartContract
from battle_of_chains.market.models import Banner

User = get_user_model()


class HangarView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/hangar.html'

    def get_context_data(self, **kwargs):
        context = super(HangarView, self).get_context_data(**kwargs)
        global_settings = BattleSettings.get_solo()
        context['global_settings'] = global_settings
        context['tanks'] = Tank.objects.filter(owner=self.request.user).select_related('nft', 'type')
        context['last_offer'] = Banner.objects.filter(is_active=True).order_by('-date_add').first()
        user = self.request.user
        user_assets = []
        user_stats = {}
        if user.wallet:
            contract = Contract.objects.filter(is_active=True, symbol=global_settings.nft_ticker).first()
            smart_contract = SmartContract(contract)

            bnb = smart_contract.w3.eth.get_balance(smart_contract.w3.toChecksumAddress(user.wallet.address))
            bnb = smart_contract.w3.fromWei(bnb, 'ether')
            user_assets.append((global_settings.active_network.ticker, bnb, 0))

            value = smart_contract.get_user_balance(user.wallet.address)
            user_assets.append((contract.symbol, value, 0))

        context['user_assets'] = user_assets

        user_stats['xp'] = Tank.objects.filter(owner=user).aggregate(xp_sum=Sum('xp'))['xp_sum']
        battles = Battle.objects.filter(status=Battle.STATUS.FINISHED, players=user)
        user_stats['battles'] = battles.count()
        user_stats['wins'] = battles.filter(winner=user).count()
        user_stats['tanks_killed'] = 0
        context['user_stats'] = user_stats

        return context


class HangarDetailView(LoginRequiredMixin, DetailView):
    template_name = 'pages/hangar_detail.html'

    def get_queryset(self):
        return Tank.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tank = self.object
        context['tank'] = tank
        props = ('level', 'moving_price', 'overlook', 'hp', 'armor')
        context['props'] = {k: v for k, v in tank.__dict__.items() if k in props}
        return context


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = ["username", "notifications_disabled", "avatar"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return self.request.user.get_absolute_url()  # type: ignore [union-attr]

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:hangar", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
