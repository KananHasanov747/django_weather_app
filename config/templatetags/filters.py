from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    """
    Take the value at the position 'i' in indexable
    """
    try:
        if not hasattr(indexable, "__getitem__"):
            return getattr(indexable, i)
        else:
            return indexable[i]
    except (ValueError, IndexError, KeyError) as e:
        return e


@register.filter
def is_in(value, args):
    if args is None:
        return False
    return value in [arg.strip() for arg in args.split(",")]


@register.filter
def replace(seq, _from, _to):
    return seq.replace(_from, _to)


@register.filter
def search(seq, value):
    return seq.find(value)
