from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from django_recaptcha.fields import ReCaptchaField
# EL TEMPLATE DEL FORMULARIO



class ProductoForm(ModelForm):
    #captcha = CaptchaField()
    captcha = ReCaptchaField()
    nombre = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Ingrese Nombre"}))
    precio = forms.IntegerField(min_value=0,widget=forms.NumberInput(attrs={"placeholder": "Ingrese Precio"}))
    stock  = forms.IntegerField(min_value=0,widget=forms.NumberInput(attrs={"placeholder": "Ingrese Stock"}))
    descripcion = forms.CharField(min_length=10,max_length=200,widget=forms.Textarea(attrs={"placeholder": "Ingrese descripción"}))
    historia = forms.CharField(min_length=10,max_length=200,widget=forms.Textarea(attrs={"placeholder": "Ingrese historia"}))
    
    class Meta:
        model = Producto
        #fields = ['nombre', 'precio','stock', 'descripcion', 'tipo']
        fields = '__all__'
        
class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ['username','email','password1','password2']