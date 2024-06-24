from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from django.template import loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.contrib.auth.models import User, Group
import os
from .decorators import logout_required
from .models import Estudiante,Permuta, Solicitud_Permuta
from .forms import CustomAuthenticationForm, StudentRegisterForm, EstudianteUpdateForm, UserUpdateForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as auth_logout
from django.conf import settings
# Create your views here.
import io
from django.http import FileResponse, HttpResponse
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Asignatura,Estudiante,Grupo

def generate_pdf_from_existing(request):
    print(request.user.username)
    # Ruta del archivo PDF original
    original_pdf_path = os.path.join(settings.BASE_DIR, 'documentacion', 'solicitud-permutas-2024-25.pdf')

    # Verificar si el archivo existe
    if not os.path.exists(original_pdf_path):
        return HttpResponse("El archivo PDF original no se encuentra en la ruta especificada.", status=404)

    try:
        # Crear un buffer de bytes para el nuevo contenido
        buffer = io.BytesIO()

        # Crear un PDF con ReportLab para el nuevo contenido
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Agregar contenido nuevo al PDF
        c.drawString(148, 572, "X") #Ingeniería de Computadores
        c.drawString(218, 572, "X") #Ingeniería del Software
        c.drawString(288, 572, "X") #TI
        c.drawString(358, 572, "X") #Ingeniería de la Salud

        #Solicitante 1
        c.drawString(87, 526, "75967897")#DNI-Número
        c.drawString(220, 526, "R")#DNI-Letra
        c.setFont("Helvetica", 10)
        c.drawString(300, 526, "Francisco José Anillo Carrasco")#Nombre
        c.setFont("Helvetica", 9)
        c.drawString(130, 512, "Calle Gabriel Miró 52 M") #Código Postal
        c.setFont("Helvetica", 7)
        c.drawString(464, 512, "La Línea de la Concepción") #Población
        c.setFont("Helvetica", 12)
        c.drawString(130, 496, "11300") #Código Postal
        c.setFont("Helvetica", 10)
        c.drawString(254, 497, "Cádiz") #Provincia
        c.drawString(464, 497, "667525025") #Teléfono
        
        #Solicitante 2
        c.drawString(87, 355, "75967897")#DNI-Número
        c.drawString(220, 355, "R")#DNI-Letra
        c.setFont("Helvetica", 10)
        c.drawString(300, 355, "Francisco José Anillo Carrasco")#Nombre
        c.setFont("Helvetica", 9)
        c.drawString(130, 340, "Calle Gabriel Miró 52 M") #Código Postal
        c.setFont("Helvetica", 7)
        c.drawString(464, 340, "La Línea de la Concepción") #Población
        c.setFont("Helvetica", 12)
        c.drawString(130, 325, "11300") #Código Postal
        c.setFont("Helvetica", 10)
        c.drawString(254, 326, "Cádiz") #Provincia
        c.drawString(464, 326, "667525025") #Teléfono

        # Terminar el PDF
        c.showPage()
        c.save()

        # Mover el buffer al inicio
        buffer.seek(0)

        # Leer el PDF original
        with open(original_pdf_path, 'rb') as f:
            original_pdf = PdfReader(f)

            # Leer el PDF con el nuevo contenido
            new_pdf = PdfReader(buffer)

            # Crear un nuevo PDF combinando ambos
            output_buffer = io.BytesIO()
            pdf_writer = PdfWriter()

            # Superponer el nuevo contenido sobre la primera página del PDF original
            original_page = original_pdf.pages[0]
            new_page = new_pdf.pages[0]
            original_page.merge_page(new_page)
            pdf_writer.add_page(original_page)

            # Añadir las páginas restantes del PDF original
            for page_num in range(1, len(original_pdf.pages)):
                page = original_pdf.pages[page_num]
                pdf_writer.add_page(page)

            # Escribir el contenido al nuevo archivo PDF
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)

        return FileResponse(output_buffer, as_attachment=True, filename='new_pdf.pdf')
    except Exception as e:
        return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)


def assign_user_to_group(request, user_id, group_name):
    user = User.objects.get(id=user_id)
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    user.save()
    return redirect('home')

def home(request):
    print("Usuario autenticado:", request.user.is_authenticated)
    return render(request, 'home.html')
@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')  # O redirigir a la página de inicio si prefieres
@login_required
def nuevaPermutas(request):
    print("Usuario autenticado:", request.user.is_authenticated)
    return render(request, 'nueva-permuta.html')

def todasPermutas(request):
    print("Usuario autenticado:", request.user.is_authenticated)
    return render(request, 'permutas.html')

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
    try:
        estudiante = request.user.estudiante
    except Estudiante.DoesNotExist:
        estudiante = None

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        e_form = EstudianteUpdateForm(request.POST, request.FILES, instance=estudiante)
        
        if u_form.is_valid() and e_form.is_valid():
            u_form.save()
            e_form.save()
            messages.success(request, f'Tu cuenta ha sido actualizada!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        e_form = EstudianteUpdateForm(instance=estudiante)

    context = {
        'u_form': u_form,
        'e_form': e_form,
    }

    return render(request, 'profile.html', context)


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
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})




@login_required
@permission_required('Permutas.view_permuta', raise_exception=True)
def view_permuta(request):
    # Tu lógica aquí
    return render(request, 'view_permuta.html')

@login_required
@permission_required('Permutas.add_permuta', raise_exception=True)
def add_permuta(request):
    # Tu lógica aquí
    return render(request, 'add_permuta.html')

@login_required
@permission_required('Permutas.change_permuta', raise_exception=True)
def change_permuta(request):
    # Tu lógica aquí
    return render(request, 'change_permuta.html')

@login_required
@permission_required('Permutas.delete_permuta', raise_exception=True)
def delete_permuta(request):
    # Tu lógica aquí
    return render(request, 'delete_permuta.html')

@login_required
def mis_permutas(request):
    usuario = request.user
    permutas_asociadas = sacar_permutas_user(usuario)
    context = {
        'permutas': permutas_asociadas
    }
    return render(request, 'mis_permutas.html', context)

def sacar_permutas_user(user):
    print(user)
    return Permuta.objects.filter(estudiante1__user=user) | Permuta.objects.filter(estudiante2__user=user)

@login_required
def aceptar_permuta(request, permuta_id):
    permuta = get_object_or_404(Permuta, id=permuta_id)
    if request.method == 'POST':
        usuario = request.user
        if permuta.estudiante1.user == usuario:
            permuta.aceptada_1=True
        elif permuta.estudiante2.user == usuario:
            permuta.aceptada_2=True

        if permuta.aceptada_1&permuta.aceptada_2:
            permuta.estado = 'aceptada'
            messages.success(request, 'Permuta aceptada exitosamente.')
        else:
            if permuta.aceptada_1:
                messages.success(request, f'Permuta aceptada exitosamente por tu parte debe aceptarla también {permuta.estudiante2.nombre} {permuta.estudiante2.apellido}.')
            elif permuta.aceptada_2:
                messages.success(request, f'Permuta aceptada exitosamente por tu parte debe aceptarla también {permuta.estudiante1.nombre} {permuta.estudiante1.apellido}.')
        permuta.save()
        return redirect('mis_permutas')
    return render(request, 'aceptar_permuta.html', {'permuta': permuta})
    
@login_required
def aceptar_solicitud_permuta(request, solicitud_permuta_id):
    solicitud = get_object_or_404(Solicitud_Permuta, id=solicitud_permuta_id)
    estudiante=request.user.estudiante
    grupo=Grupo.objects.get(asignatura=solicitud.asignatura, estudiante=estudiante)
    permuta = Permuta.objects.create(estudiante1 = solicitud.estudiante1, grupo1= solicitud.grupo1, asignatura= solicitud.asignatura,aceptada_1=True,aceptada_2=True,estado='solicitada', estudiante2=estudiante,grupo2= grupo)
    permuta.save()
    messages.success(request, 'Permuta aceptada exitosamente y permuta creada.')
    return render(request, 'home.html')
    

@login_required
def asignaturas_estudiante(request):
    estudiante = Estudiante.objects.get(user=request.user)
    asignaturas = Asignatura.objects.filter(grupo__estudiante=estudiante).distinct()

    context = {
        'asignaturas': asignaturas,
    }

    return render(request, 'asignaturas_estudiante.html', context)


@login_required
def asignaturas_estudiante(request):
    estudiante = Estudiante.objects.get(user=request.user)
    asignaturas = Grupo.objects.filter(grupo__estudiante=estudiante).distinct().objects

    context = {
        'asignaturas': asignaturas,
    }

    return render(request, 'mis_asignaturas.html', context)
    
@login_required
def grupos_estudiante(request):
    estudiante = Estudiante.objects.get(user=request.user)
    grupos = Grupo.objects.filter(estudiante=estudiante).distinct()

    context = {
        'grupos': grupos,
    }

    return render(request, 'grupos_estudiante.html', context)

@login_required
def permutas_all(request):
    usuario = request.user
    permutas_asociadas = sacar_permutas_not_user(usuario)
    context = {
        'permutas': permutas_asociadas
    }
    return render(request, 'permutas.html', context)

def sacar_permutas_not_user(user):
    return Solicitud_Permuta.objects.exclude(estudiante1__user=user)