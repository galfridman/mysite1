from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]


upto.is_safe = True


@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class": css})
