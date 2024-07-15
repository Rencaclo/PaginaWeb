from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register('productos', ProductoViewset)
urlpatterns = [
     path('api/', include(router.urls)),
    path('api_proyecto/', api_proyecto, name="api_proyecto"),


    path('recuperarcontra', recuperar_contrasena , name="recuperarcontra"),
    path('', index, name="index"),
    path('shoping', shoping, name="shoping"),
    path('product', product, name="product"),
    path('about', about, name="about"),
    path('contact', contact, name="contact"),
    path('login', login, name="login"),
    path('registrar', registrar, name="registrar"),
    path('usuario', usuario, name="usuario"),
    path('register/', register, name="register"),
    path ('vistaadmin',  vistaadmin, name="vistaadmin"),
    path('productos', productos, name="productos"),
    path('logout/', logout, name='logout'),
    path('eliminar_historial/', eliminar_historial, name='eliminar_historial'),
    path('historial/', historial, name='historial'),
    path('generate_pdf/', generate_pdf,name="generate_pdf"),
    path('pagado/', pagado, name='pagado'),
    path('recuperar_contrasena/', recuperar_contrasena, name='recuperar_contrasena'),
    #CRUD
    path('agregar/', agregar, name="agregar"),
    path('actualizar/<codigo_producto>/', actualizar, name="actualizar"),
    path('eliminar/<codigo_producto>/', eliminar, name="eliminar"),
    path('buscar/', buscar, name='buscar'),
    path ('pago_exitoso', pago_exitoso, name="pago_exitoso"),
    

    #CARRITO
    path('vaciar_carrito/', vaciar_carrito, name='vaciar_carrito'),
    path('eliminar_carrito/<codigo_producto>/', eliminar_carrito, name='eliminar_carrito'),
    path('aumentar_cantidad/<codigo_producto>/', aumentar_cantidad, name='aumentar_cantidad'),
    path('disminuir_cantidad/<codigo_producto>/', disminuir_cantidad, name='disminuir_cantidad'),
]
