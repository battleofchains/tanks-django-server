from django.core.paginator import Paginator
from django.db.models import Case, DecimalField, F, Max, Q, When
from django.views.generic import DetailView, TemplateView

from battle_of_chains.battle.models import BattleSettings, Tank, TankType


class MarketPlaceView(TemplateView):
    template_name = 'pages/marketplace.html'

    def get_context_data(self, **kwargs):
        context = super(MarketPlaceView, self).get_context_data(**kwargs)
        battle_settings = BattleSettings.get_solo()
        context['orders'] = {'-date_mod': 'Newest', '-price_actual': 'Max Price', 'price_actual': 'Min Price',
                             'primary': 'Primary', '-primary': 'Secondary'}
        context['order_by'] = '-date_mod'
        price_field = Case(
            When(basic_free_tank=True, then=F('offer__price')),
            default=F('price'),
            output_field=DecimalField()
        )
        tanks = Tank.objects.filter(
            Q(for_sale=True, basic_free_tank=False) | Q(basic_free_tank=True, offer__is_active=True)
        ).select_related('nft', 'type', 'offer').annotate(
            primary=F('offer__is_active'), price_actual=price_field
        ).order_by(context['order_by'])
        context['type_filter'] = TankType.objects.values_list('id', 'name')
        paginator = Paginator(tanks, battle_settings.tanks_per_page)
        context['paginator'] = paginator
        context['tanks'] = paginator.page(1)
        maxes = [Max(prop) for prop in ('level', 'moving_price', 'overlook', 'armor', 'hp')]
        range_filters = Tank.objects.aggregate(*maxes)
        context['range_filters'] = {k.split('__')[0]: v for k, v in range_filters.items()}
        context['bought_offers'] = []
        if self.request.user.is_authenticated:
            bought_offers = Tank.objects.filter(owner=self.request.user, origin_offer__isnull=False)\
                .values_list('origin_offer_id', 'id')
            context['bought_offers'] = dict(bought_offers)
        return context


class MarketPlaceDetailView(DetailView):
    queryset = Tank.objects.filter(
        Q(for_sale=True, basic_free_tank=False) | Q(basic_free_tank=True, offer__is_active=True)
    )
    template_name = 'pages/marketplace_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tank = self.object
        context['tank'] = tank
        context['similar_tanks'] = self.queryset.filter(type=tank.type, level=tank.level).exclude(pk=tank.pk)[:4]
        props = ('level', 'moving_price', 'overlook', 'hp', 'armor')
        context['props'] = {k: v for k, v in tank.__dict__.items() if k in props}
        return context
