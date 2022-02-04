from django import template

from battle_of_chains.utils.functions import truncate_trailing_zeroes

register = template.Library()


@register.filter(name='truncate_trailing_zeroes')
def truncate_trailing_zeroes_templatetag(value, round_to=None):
    return truncate_trailing_zeroes(value, round_to)
