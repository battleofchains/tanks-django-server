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
        else:
            if int(filter_value) > 0:
                filters[filter_name] = filter_value
            else:
                del filters[filter_name]
        self.request.session['filters'] = filters

        queryset = context['tanks']
        context['tanks'] = queryset.filter(**filters)
