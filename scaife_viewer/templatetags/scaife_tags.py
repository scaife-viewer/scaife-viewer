from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def render(passage):
    try:
        return mark_safe(passage.render())
    except Exception:
        return "Unable to load passage."
