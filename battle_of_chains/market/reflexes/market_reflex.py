from collections import defaultdict

from django.core.paginator import Paginator
from sockpuppet.reflex import Reflex


class MarketReflex(Reflex):
    def filter(self):
        context = self.get_context_data()
        filter_name = self.element.dataset['filter']
        filter_value = self.element.attributes['value']
        filters = self.request.session.get('filters', defaultdict(set))
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
        queryset = queryset.filter(**filters)
        paginator = Paginator(queryset, 4)
        context['tanks'] = paginator.page(1)
        context['paginator'] = paginator

    def clear_filters(self):
        context = self.get_context_data()
        self.request.session['filters'] = defaultdict(set)
        queryset = context['paginator'].object_list
        queryset = queryset.all()
        paginator = Paginator(queryset, 4)
        context['tanks'] = paginator.page(1)
        context['paginator'] = paginator

    def sort(self):
        context = self.get_context_data()
        queryset = context['paginator'].object_list
        filters = self.request.session.get('filters', None)
        if filters:
            queryset = queryset.filter(**filters)
        value = self.element.attributes['value']
        match value:
            case 'max_price':
                queryset = queryset.order_by('-price')
            case 'min_price':
                queryset = queryset.order_by('price')
            case _:
                queryset = queryset.order_by('-date_mod')
        paginator = Paginator(queryset, 4)
        context['tanks'] = paginator.page(1)
        context['paginator'] = paginator
