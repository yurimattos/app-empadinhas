from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    valor = dictionary.get(key)
    if valor is None:
        return ""
    else:
        return valor