from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.template import loader
from django.contrib import messages

from .models import Estudiante
from .forms import StudentRegisterForm

# Create your views here.

def permutas(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def nuevaPermutas(request):
    template = loader.get_template('nueva-permuta.html')
    return HttpResponse(template.render())

def todasPermutas(request):
    template = loader.get_template('permutas.html')
    return HttpResponse(template.render())

def registro(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            nombre = form.cleaned_data.get('nombre')
            apellido = form.cleaned_data.get('apellido')
            email = form.cleaned_data.get('email')
            
            # Crear la instancia de Estudiante
            estudiante = Estudiante(user=user, nombre=nombre, apellido=apellido, email=email)
            estudiante.save()

            login(request, user)
            return redirect('/')  # Redirige a la página de inicio o a donde quieras
    else:
        form = StudentRegisterForm()
    return render(request, 'register.html', {'form': form})
