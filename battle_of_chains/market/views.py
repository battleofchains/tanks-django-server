from django.views.generic import TemplateView

from battle_of_chains.battle.models import Tank

from .models import Offer


class MarketPlaceView(TemplateView):
    template_name = 'pages/marketplace.html'

    def get_context_data(self, **kwargs):
        context = super(MarketPlaceView, self).get_context_data(**kwargs)
        offers = Offer.objects.filter(is_active=True)
        tanks = Tank.objects.filter(for_sale=True, basic_free_tank=False)
        context['offers'] = offers
        context['tanks'] = tanks
        return context
