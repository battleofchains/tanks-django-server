from django.db.models import Max, Q
from django.views.generic import TemplateView

from battle_of_chains.battle.models import Tank, TankType


class MarketPlaceView(TemplateView):
    template_name = 'pages/marketplace.html'

    def get_context_data(self, **kwargs):
        context = super(MarketPlaceView, self).get_context_data(**kwargs)
        tanks = Tank.objects.filter(
            Q(for_sale=True, basic_free_tank=False) | Q(basic_free_tank=True, offer__is_active=True)
        )
        context['type_filter'] = TankType.objects.values_list('id', 'name')
        context['tanks'] = tanks.order_by('-date_mod')
        maxes = [Max(prop) for prop in ('level', 'moving_price', 'overlook', 'armor', 'hp')]
        range_filters = Tank.objects.aggregate(*maxes)
        context['range_filters'] = {k.split('__')[0]: v for k, v in range_filters.items()}
        return context
