
import json
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .forms import ProductoForm, RegistroUsuarioForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework import viewsets
import requests
from .serializers import ProductoSerializer,TipoProductoSerializer
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa  
from django.template.loader import get_template
from django.forms.models import model_to_dict
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.conf import settings
#funcion generica que valida el grupo del usuario 
def grupo_requerido(nombre_grupo):
    def decorator(view_fuc):
        @user_passes_test(lambda user:user.groups.filter(name=nombre_grupo).exists())
        def wrapper(request, *arg, **kwargs):
            return view_fuc(request, *arg, **kwargs)
        return wrapper
    return decorator 
        
class ProductoViewset(viewsets.ModelViewSet):
    queryset = Producto.objects.all()  
    serializer_class = ProductoSerializer

def api_proyecto(request):

    #REALIZAMOS LA SOLICITUD AL API
    respuesta = requests.get('http://127.0.0.1:8000/api/productos/')
    respuesta2 = requests.get('https://mindicador.cl/api')
    #TRANSFROMAMOS EL JSON PARA LEERLO
    productos = respuesta.json()
    usdt = respuesta2.json()

    data = {
        'listaProductos' : productos,
        'usdt' : usdt, 
        
    }
    return render(request, 'core/api_proyecto.html', data)



def index(request):
    return render(request, 'core/index.html')



def login(request):
    return render(request, 'core/login.html')

def registrar(request):
    return render(request, 'core/registrar.html')

def index(request):
    return render(request, 'core/usuario.html')


#LISTAR
@login_required
def product(request):
    ProductoAll = Producto.objects.all() 
    data = {
        'listaProductos' : ProductoAll

    }

    return render(request, 'core/product.html', data)

@login_required
def agregar(request):

    data = {
        'form' : ProductoForm()
    }

    if request.method == 'POST':
        formulario = ProductoForm(request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            data['mensaje'] = "Guardado correctamente"
            
        else:
            data['form'] = formulario 
    return render (request, 'core/agregar.html', data)

@login_required
def actualizar(request,codigo_producto):
    producto = Producto.objects.get(codigo_producto=codigo_producto)
    data = {
        'form' :ProductoForm(instance=producto)
    }
    
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST,instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
         
            data['mensaje'] = "Actualizado correctamente" 
        else:
            data['form'] = formulario
        
    
    return render(request, 'core/actualizar.html', data)

#ELIMINAR
@login_required
def eliminar(request,codigo_producto):
    producto = Producto.objects.get(codigo_producto=codigo_producto)
    producto.delete()

    return redirect(to="product")

@login_required
def buscar(request):
    query = request.GET.get('q', '')
    productos = []
    if query:
        productos = Producto.objects.filter(nombre__icontains=query)
    
    context = {
        'productos': productos,
        'query': query,
    }
    return render(request, 'core/buscar.html', context)

def register(request):
    
    data ={
        'form' : RegistroUsuarioForm()
    }
    
    if request.method == 'POST':
        formulario = RegistroUsuarioForm(data = request.POST)
        if formulario.is_valid():
            formulario.save()
            #user = authenticate(username=formulario.cleaned_data["username"], password = formulario.cleaned_data["password1"])
            #login(request, user)
            messages.success(request, "Te has registrado correctamente")
            return redirect(to="index")
        data ["form"] = formulario

    return render(request, 'registration/register.html', data)









def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def index(request):
    return render(request, 'core/index.html')

def  vistaadmin(request):
    return render(request,'core/vistaadmin.html' )



@login_required
def productos(request):
    ProductoAll = Producto.objects.all() 
    data = {
        'listaProductos' : ProductoAll

    }
   
    if request.method == 'POST':
        codigo_producto = request.POST.get('codigo_producto')
        user = request.user.get_username()
        nombre_producto = request.POST.get('nombre')
        precio = request.POST.get('precio')
        producto = Producto.objects.get(codigo_producto=codigo_producto)
        producto.stock -= 1
        producto.save()

        if Carrito.objects.filter(codigo_producto=codigo_producto, usuario_producto=user, nombre_producto=nombre_producto).exists():
            carrito = Carrito.objects.get(codigo_producto=codigo_producto, usuario_producto=user, nombre_producto=nombre_producto)
            carrito.cantidad += 1
            carrito.total += int(precio)
            carrito.save()
        else:
            carrito = Carrito()
            carrito.codigo_producto = codigo_producto
            carrito.nombre_producto = nombre_producto
            carrito.precio_producto = precio  
            carrito.total = precio
            carrito.cantidad = 1
            carrito.usuario_producto = user
            carrito.imagen = request.POST.get('imagen')
            carrito.save()
    
    return render(request, 'core/productos.html', data)


#ESTE ES EL CARRO DE COMPRAS
@login_required
def shoping(request):
    respuesta = requests.get('https://mindicador.cl/api/dolar').json()
    valor_usd = respuesta['serie'][0]['valor']

    # Filtra los elementos del carrito que pertenecen al usuario actual
    carrito = Carrito.objects.filter(usuario_producto=request.user.username)
    total_precio = 0
    total_iva = 0
    total_final = 0
    for aux in carrito:
        total_precio += aux.total
        total_iva += round(aux.total * 0.19)  # Calcular el IVA del 19%
        # La línea siguiente se mueve fuera del bucle for
    total_final = round(float(total_iva + total_precio) / valor_usd, 2)  # suma el precio_total con el total_iva

    data = {'listaCarrito': carrito,
            'total_precio': total_precio,
            'total_iva': total_iva,
            'total_final': total_final,}
    return render(request, 'core/shoping.html', data)

#FUNCIONALIDAD DEL CARRITO
@login_required
def vaciar_carrito(request):
    # Obtener todos los elementos del carrito para el usuario actual
    carrito_usuario = Carrito.objects.filter(usuario_producto=request.user)

    # Restaurar el stock de cada producto en el carrito
    for item in carrito_usuario:
        producto = Producto.objects.get(codigo_producto=item.codigo_producto)
        producto.stock += item.cantidad
        producto.save()

    # Eliminar todos los elementos del carrito del usuario actual
    carrito_usuario.delete()

    return redirect('shoping')


@login_required
def pago_exitoso(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_data = data.get('paymentData')
            productos_comprados = []  # Lista para almacenar los productos comprados
            
            for item in payment_data:
                producto_info = {
                    'codigo_producto': item.get('codigo_producto'),
                    'nombre_producto': item.get('nombre_producto'),
                    'precio_producto': item.get('precio_producto'),
                    'cantidad': item.get('cantidad'),
                    'total': item.get('total'),
                }
                productos_comprados.append(producto_info)
            
            # Convertir la lista de productos comprados a JSON
            productos_comprados_json = json.dumps(productos_comprados)
            
            # Crear la orden con los productos comprados
            nueva_orden = Orden.objects.create(
                usuario_producto=request.user.username,
                productos_comprados=productos_comprados_json,
            )
            
            # Eliminar el contenido del carrito del usuario
            Carrito.objects.filter(usuario_producto=request.user.username).delete()
            
            return JsonResponse({'mensaje': 'Pago registrado correctamente'}, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required 
def historial(request):
    ordenes_query = Orden.objects.filter(usuario_producto=request.user.username)
    
    # Convertir el QuerySet a una lista de diccionarios
    ordenes = []
    for orden in ordenes_query:
        # Suponiendo que 'productos_comprados' es el campo que quieres convertir
        # y que 'orden' tiene un método o propiedad para acceder a él en formato JSON
        orden_dict = model_to_dict(orden)  # Convertir el modelo a diccionario
        orden_dict['productos_comprados'] = json.loads(orden.productos_comprados)
        orden_dict['fecha_compra'] = orden.fecha_compra  # Acceder al campo de fecha
        ordenes.append(orden_dict)
    
    data = {
        'ordenes': ordenes
    }
    return render(request, 'core/historial.html', data)

def recuperar_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        usuario = User.objects.filter(email=email).first()
        if usuario:
            # Aquí deberías generar un enlace seguro para la recuperación de contraseña
            enlace_recuperacion = "URL_PARA_RECUPERACION"
            send_mail(
                'Recuperación de Contraseña',
                f'Por favor, usa el siguiente enlace para recuperar tu contraseña: {enlace_recuperacion}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return render(request, 'emails/enviado.html')
        else:
            return render(request, 'registration/recuperarcontra.html', {'error': 'No se encontró el usuario'})
    return render(request, 'registration/recuperarcontra.html')

def generate_pdf(request):
    # Obtener las órdenes de compra del usuario actual
    ordenes = Orden.objects.filter(usuario_producto=request.user.username)
    
    # Decodificar el campo 'productos_comprados' para cada orden
    for orden in ordenes:
        orden.productos_comprados = json.loads(orden.productos_comprados)

    # Obtener la plantilla HTML para el PDF
    template_path = 'core/generate_pdf.html'
    template = get_template(template_path)
    
    # Renderizar la plantilla con los datos de las órdenes de compra, incluyendo 'productos_comprados' decodificados
    context = {'ordenes': ordenes}
    html = template.render(context)
    
    # Crear un objeto HttpResponse con el contenido HTML renderizado
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    
    # Convertir HTML a PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Si falla la creación del PDF, regresar un error
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF: %s' % html)
    
    return response

@login_required 
def eliminar_historial(request):
    if request.method == 'POST':
        # Obtener todas las órdenes de compra del usuario actual y eliminarlas
        Orden.objects.filter(usuario_producto=request.user.username).delete()
        
        messages.success(request, 'Historial eliminado correctamente.')
        return redirect('historial')
    
    return redirect('historial')  # Redirigir de vuelta al historial después de la eliminación


#Eliminar Carro
@login_required
def eliminar_carrito(request, codigo_producto):
    # Obtén el ítem del carrito
    aux = get_object_or_404(Carrito, codigo_producto=codigo_producto)
    
    # Encuentra el producto correspondiente usando el código de producto
    producto = get_object_or_404(Producto, codigo_producto=aux.codigo_producto)
    
    # Devuelve el stock del producto
    producto.stock += aux.cantidad
    producto.save()
    
    # Elimina el ítem del carrito
    aux.delete()
    
    # Redirige al carrito
    return redirect('shoping')

#Aumentar Carro
@login_required
def aumentar_cantidad(request, codigo_producto):
    aux = get_object_or_404(Carrito, codigo_producto=codigo_producto)

    producto = get_object_or_404(Producto, codigo_producto=aux.codigo_producto)
    
    if producto.stock > 0:
        # Aumenta la cantidad del ítem del carrito
        aux.cantidad += 1
        aux.total = aux.cantidad * aux.precio_producto  # Actualiza el total
        aux.save()
        
        # Reduce el stock del producto
        producto.stock -= 1
        producto.save()
    return redirect('shoping')

#Restar Carrito
@login_required
def disminuir_cantidad(request, codigo_producto):

    aux = get_object_or_404(Carrito, codigo_producto=codigo_producto)
    if aux.cantidad > 1:
        aux.cantidad -= 1
        aux.total = aux.cantidad * aux.precio_producto  
        aux.save()
        producto = get_object_or_404(Producto, codigo_producto=aux.codigo_producto)
        producto.stock += 1  #
    else:
        eliminar_carrito(request, codigo_producto)  
    return redirect('shoping')

def listar_productos(request):
    productos = Producto.objects.all()  # Suponiendo que tienes un modelo Producto
    paginator = Paginator(productos, 3)  # Número de productos a mostrar por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data = {
        'page_obj': page_obj,
    }

    return render(request, 'core/productos.html', data)

@login_required
def logout(request):
    logout(request)
    return redirect(request, 'core/base.html')

    
@login_required
def pagado(request):
    return render(request, 'core/pagado.html')