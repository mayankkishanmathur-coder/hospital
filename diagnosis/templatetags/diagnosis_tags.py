from django import template

register = template.Library()


@register.filter
def get_item(obj, key):
    """Get item from dictionary or attribute from object"""
    if isinstance(obj, dict):
        return obj.get(key)
    # For Django Form objects, access fields
    if hasattr(obj, 'fields') and key in obj.fields:
        return obj[key]
    return None
