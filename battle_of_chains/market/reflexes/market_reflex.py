from collections import defaultdict

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
        queryset = context['tanks']
        context['tanks'] = queryset.filter(**filters)

    def clear_filters(self):
        context = self.get_context_data()
        self.request.session['filters'] = defaultdict(set)
        queryset = context['tanks']
        context['tanks'] = queryset.all()

    def sort(self):
        context = self.get_context_data()
        queryset = context['tanks']
        filters = self.request.session.get('filters', None)
        if filters:
            queryset = queryset.filter(**filters)
        value = self.element.attributes['value']
        match value:
            case 'max_price':
                context['tanks'] = queryset.order_by('-price')
            case 'min_price':
                context['tanks'] = queryset.order_by('price')
            case _:
                context['tanks'] = queryset.order_by('-date_mod')
