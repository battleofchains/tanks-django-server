from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, TemplateView, UpdateView

from battle_of_chains.battle.models import Tank
from battle_of_chains.market.models import Banner
from battle_of_chains.blockchain.utils import get_w3_provider

User = get_user_model()


class HangarView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/hangar.html'

    def get_context_data(self, **kwargs):
        context = super(HangarView, self).get_context_data(**kwargs)
        context['tanks'] = Tank.objects.filter(owner=self.request.user).select_related('nft', 'type')
        context['last_offer'] = Banner.objects.filter(is_active=True).order_by('-date_add').first()
        user = self.request.user
        user_assets = []
        if user.wallet:
            w3 = get_w3_provider()
            bnb = w3.eth.get_balance(user.wallet.address)
            user_assets.append(('bnb', bnb, 0))
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
    fields = ["username"]
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
