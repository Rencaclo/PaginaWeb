from django.contrib import admin
from .models import *
# Register your models here.

class ObrasAdmin(admin.ModelAdmin):
    list_display = ['nombre','precio','stock','descripcion','historia', 'imagen', 'tecnica']
    search_fields = ['nombre']
    list_per_page = 10

admin.site.register(TipoObras)
admin.site.register(Producto, ObrasAdmin)