from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Asignatura,Estudiante,Grupo,Permuta

class StudentRegisterForm(Estudiante):
    nombre=forms.CharField(label='Nombre')
    apellidos=forms.CharField(label='Apellido(s)')
    email= forms.EmailField() 
    password1= forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2= forms.CharField(label='Repite la contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Estudiante
        fields = ['nombre','apellidos','username', 'email', 'password1','password2']
        help_texts = {k:"" for k in fields}