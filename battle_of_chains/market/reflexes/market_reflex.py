from collections import defaultdict

from django.core.paginator import Paginator
from sockpuppet.reflex import Reflex

from battle_of_chains.battle.models import BattleSettings


class MarketReflex(Reflex):
    def filter(self):
        context = self.get_context_data()
        filter_name = self.element.dataset['filter']
        filter_value = self.element.attributes['value']
        filters = self.request.session.get('filters', defaultdict(set))
        order_by = self.request.session.get('order_by', '-date_add')
        if self.element.attributes['type'] == 'checkbox':
            if self.element.attributes['checked']:
                filters[filter_name].add(filter_value)
            else:
                filters[filter_name].remove(filter_value)
                if len(filters[filter_name]) == 0:
                    del filters[filter_name]
        else:
            if int(filter_value) > 0:
                filters[filter_name] = filter_value
            else:
                del filters[filter_name]
        self.request.session['filters'] = filters
        queryset = context['paginator'].object_list
        queryset = queryset.filter(**filters).order_by(order_by)
        paginator = Paginator(queryset, BattleSettings.get_solo().tanks_per_page)
        context['order_by'] = order_by
        context['tanks'] = paginator.page(1)
        context['paginator'] = paginator

    def clear_filters(self):
        context = self.get_context_data()
        self.request.session['filters'] = defaultdict(set)
        queryset = context['paginator'].object_list
        queryset = queryset.all()
        paginator = Paginator(queryset, BattleSettings.get_solo().tanks_per_page)
        context['tanks'] = paginator.page(1)
        context['paginator'] = paginator

    def sort(self):
        context = self.get_context_data()
        queryset = context['paginator'].object_list
        filters = self.request.session.get('filters', None)
        if filters:
            queryset = queryset.filter(**filters)
        value = self.element.attributes['value']
        queryset = queryset.order_by(value)
        self.request.session['order_by'] = value
        context['order_by'] = value
        paginator = Paginator(queryset, BattleSettings.get_solo().tanks_per_page)
        context['tanks'] = paginator.page(1)
        context['paginator'] = paginator

    def page(self):
        context = self.get_context_data()
        filters = self.request.session.get('filters', None)
        order_by = self.request.session.get('order_by', '-date_add')
        page_number = self.element.dataset['page']
        context['order_by'] = order_by
        paginator = context['paginator']
        queryset = paginator.object_list
        if filters:
            queryset = queryset.filter(**filters)
        queryset = queryset.order_by(order_by)
        paginator = Paginator(queryset, BattleSettings.get_solo().tanks_per_page)
        context['paginator'] = paginator
        context['tanks'] = paginator.page(int(page_number))
