from django import template

from ..models import recent


register = template.Library()


@register.simple_tag
def recently_read_by(user, limit=5):
    return recent(user, limit)
