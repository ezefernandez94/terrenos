from django import template

register = template.Library()


@register.filter
def spanish_list(values):
    """[12, 24, 36] -> "12, 24 y 36". The inline Spanish copy; landing.js re-formats it per language."""
    items = [str(value) for value in values]
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + " y " + items[-1]
