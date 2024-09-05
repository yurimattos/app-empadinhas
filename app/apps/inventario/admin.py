from django.contrib import admin
from .models import Formulario, Inventario, InventarioItem, InventarioFormulario, TipoDeContagem

admin.site.register(Formulario)
admin.site.register(Inventario)
admin.site.register(InventarioItem)
admin.site.register(InventarioFormulario)
admin.site.register(TipoDeContagem)
