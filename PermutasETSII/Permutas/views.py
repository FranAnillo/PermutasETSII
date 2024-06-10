from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.template import loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User

from .decorators import logout_required
from .models import Estudiante
from .forms import CustomAuthenticationForm, StudentRegisterForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as auth_logout

# Create your views here.

def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())
@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')  # O redirigir a la página de inicio si prefieres
@login_required
def nuevaPermutas(request):
    template = loader.get_template('nueva-permuta.html')
    return HttpResponse(template.render())

def todasPermutas(request):
    template = loader.get_template('permutas.html')
    return HttpResponse(template.render())

@logout_required
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

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = StudentUpdateForm(request.POST, instance=request.user)
        e_form = EstudianteUpdateForm(request.POST, request.FILES, instance=request.user.estudiante)
        if u_form.is_valid() and e_form.is_valid():
            u_form.save()
            e_form.save()
            messages.success(request, f'¡Tu perfil ha sido actualizado!')
            return redirect('profile')
    else:
        u_form = StudentUpdateForm(instance=request.user)
        e_form = EstudianteUpdateForm(instance=request.user.estudiante)

    context = {
        'u_form': u_form,
        'e_form': e_form
    }

    return render(request, 'profile.html', context)

class StudentRegisterForm(UserCreationForm):
    nombre = forms.CharField(max_length=255)
    apellido = forms.CharField(max_length=255)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'nombre', 'apellido', 'email', 'password1', 'password2']
        help_texts = {k: "" for k in fields}

class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class EstudianteUpdateForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'apellido', 'email']

@logout_required
def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')  # Redirige a la página de inicio o donde desees
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})