from django import template
from bhp_dispatch.models import DispatchItem

register = template.Library()


@register.filter(name='is_dispatched')
def is_dispatched(item_identifier):
    """Returns dispatch status of the item based on the identifier."""
    locked = False
    if DispatchItem.objects.filter(
            item_identifier=item_identifier,
            is_dispatched=True).exists():
        locked = True
    return locked


@register.filter(name='dispatched_to')
def dispatched_to(item_identifier):
    """Returns the producer dispatch to based on the identifier."""
    if DispatchItem.objects.filter(
            item_identifier=item_identifier,
            is_dispatched=True):
        dispatch_item = DispatchItem.objects.get(
            item_identifier=item_identifier,
            is_dispatched=True)
    return dispatch_item.producer
