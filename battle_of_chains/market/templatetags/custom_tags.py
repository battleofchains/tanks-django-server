from django.template.defaulttags import register

from battle_of_chains.utils.functions import truncate_trailing_zeroes


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='truncate_trailing_zeroes')
def truncate_trailing_zeroes_templatetag(value, round_to=6):
    return truncate_trailing_zeroes(value, round_to)
