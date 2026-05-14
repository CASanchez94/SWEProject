from django import template

register = template.Library()

@register.filter
def file_extension(value):
    if not value:
        return ''
    name = str(value)
    if '.' in name:
        return name.split('.')[-1].upper()
    return 'FILE'