from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def render(passage):
    try:
        return mark_safe(passage.render())
    except Exception:
        return "Unable to load passage."


@register.simple_tag(takes_context=True)
def query(context, **kwargs):
    q = context["request"].GET.copy()
    for k, v in kwargs.items():
        if v:
            q[k] = v
        elif k in q:
            del q[k]
    return q.urlencode()
