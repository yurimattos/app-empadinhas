import datetime
from django import template

register = template.Library()

@register.filter()
def validade(value, arg):
   newDate = value + datetime.timedelta(days=arg)
   newDateTratada = newDate.strftime("%d/%m/%Y")
   return newDateTratada