from django import template

# app_name = "web"

register = template.Library()


@register.filter(name="any_not_none")
def any_not_none(items):
    return any(item is not [0, "", None, False] for item in items)
