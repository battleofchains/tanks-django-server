from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.views.generic import TemplateView

from battle_of_chains.battle.models import BattleSettings, Tank, TankType


class MarketPlaceView(TemplateView):
    template_name = 'pages/marketplace.html'

    def get_context_data(self, **kwargs):
        context = super(MarketPlaceView, self).get_context_data(**kwargs)
        battle_settings = BattleSettings.get_solo()
        context['orders'] = {'-date_mod': 'Newest', '-price': 'Max Price', 'price': 'Min Price'}
        context['order_by'] = '-date_mod'
        tanks = Tank.objects.filter(
            Q(for_sale=True, basic_free_tank=False) | Q(basic_free_tank=True, offer__is_active=True)
        ).order_by(context['order_by'])
        context['type_filter'] = TankType.objects.values_list('id', 'name')
        paginator = Paginator(tanks, battle_settings.tanks_per_page)
        context['paginator'] = paginator
        context['tanks'] = paginator.page(1)
        maxes = [Max(prop) for prop in ('level', 'moving_price', 'overlook', 'armor', 'hp')]
        range_filters = Tank.objects.aggregate(*maxes)
        context['range_filters'] = {k.split('__')[0]: v for k, v in range_filters.items()}
        return context
