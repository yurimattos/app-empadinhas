from django.contrib import admin
from .models import CategoriaProduto, Lote, Produto, Lojas

# Register your models here.
admin.site.register(CategoriaProduto)
admin.site.register(Lote)
admin.site.register(Produto)
admin.site.register(Lojas)