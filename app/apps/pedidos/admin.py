from django.contrib import admin
from .models import StatusPedido, Pedido, Comentario, ItensPedido

# Register your models here.
admin.site.register(StatusPedido)
admin.site.register(Pedido)
admin.site.register(ItensPedido)
admin.site.register(Comentario)