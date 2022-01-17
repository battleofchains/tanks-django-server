from django.views.generic import ListView

from battle_of_chains.battle.models import Tank

from .models import Offer


class MarketPlaceView(ListView):
    queryset = Tank.objects.filter(for_sale=True, basic_free_tank=False)
    template_name = 'pages/marketplace.html'

    def get_context_data(self, **kwargs):
        context = super(MarketPlaceView, self).get_context_data(**kwargs)
        offers = Offer.objects.filter(is_active=True)
        context['offers'] = offers
        return context
