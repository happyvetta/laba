from django import template

register = template.Library()


@register.inclusion_tag('templatetags/header.html', takes_context=True)
def header_tag(context):
    return {'user': context.get('user')}
