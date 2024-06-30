# Django imports
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.db.models import Q

# Project-specific imports
from .decorators import logout_required
from .models import Estudiante, Permuta, Solicitud_Permuta, Asignatura, Grupo
from .forms import AsignarAsignaturasForm, CustomAuthenticationForm, ProyectoDocenteForm, SolicitudPermutaForm, StudentRegisterForm, EstudianteUpdateForm, UserUpdateForm,GrupoForm

# Third-party imports
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Standard library imports
import os
import io
def is_delegacion_or_admin(user):
    return user.is_superuser or user.groups.filter(name='delegación').exists()
def is_delegacion(user):
    return user.groups.filter(name='delegación').exists()

def generate_pdf_from_existing(request,estudiante_id):
    # Ruta del archivo PDF original
    estudiante1= request.user.estudiante
    estudiante2 = get_object_or_404(Estudiante, id=estudiante_id)
    original_pdf_path = os.path.join(settings.BASE_DIR, 'documentacion', 'solicitud-permutas-2024-25.pdf')
    permutas = sacar_permutas_two_users(user1=estudiante1.user,user2=estudiante2.user)
    print(permutas)
    # Verificar si el archivo existe
    if not os.path.exists(original_pdf_path):
        return HttpResponse("El archivo PDF original no se encuentra en la ruta especificada.", status=404)

    try:
        # Crear un buffer de bytes para el nuevo contenido
        buffer = io.BytesIO()
        
        # Crear un PDF con ReportLab para el nuevo contenido
        c = canvas.Canvas(buffer, pagesize=letter)
        print(request.user.estudiante.grado)
        # Agregar contenido nuevo al PDF
        if estudiante1.grado.nombre == 'Grado en Ingeniería Informática - Ingeniería de Computadores':
            c.drawString(148, 572, "X") #Ingeniería de Computadores
        elif estudiante1.grado.nombre == 'Grado en Ingeniería Informática - Ingeniería del Software':
            c.drawString(218, 572, "X") #Ingeniería del Software
        elif estudiante1.grado.nombre == 'Grado en Ingeniería Informática - Tecnologías de la Información':
            c.drawString(288, 572, "X") #TI
        elif estudiante1.grado.nombre == 'Grado en Ingeniería de la Salud':
            c.drawString(358, 572, "X") #Ingeniería de la Salud

        #Solicitante 1
        c.drawString(87, 526, estudiante1.dni[:-1])#DNI-Número
        c.drawString(220, 526, estudiante1.dni[-1])#DNI-Letra
        c.setFont("Helvetica", 10)
        c.drawString(300, 526, estudiante1.nombre +' '+estudiante1.apellido )#Nombre
        c.setFont("Helvetica", 9)
        c.drawString(130, 512, estudiante1.domicilio) #Código Postal
        c.setFont("Helvetica", 7)
        c.drawString(464, 512, estudiante1.poblacion) #Población
        c.setFont("Helvetica", 12)
        c.drawString(130, 496, estudiante1.codigo_postal) #Código Postal
        c.setFont("Helvetica", 10)
        c.drawString(254, 497, estudiante1.provincia) #Provincia
        c.drawString(464, 497, estudiante1.telefono) #Teléfono
        
        #Solicitante 2
        c.drawString(87, 355, estudiante2.dni[:-1])#DNI-Número
        c.drawString(220, 355, estudiante2.dni[-1])#DNI-Letra
        c.setFont("Helvetica", 10)
        c.drawString(300, 355, estudiante2.nombre + ' '+ estudiante2.apellido)#Nombre
        c.setFont("Helvetica", 9)
        c.drawString(130, 340, estudiante2.domicilio) #Código Postal
        c.setFont("Helvetica", 7)
        c.drawString(464, 340, estudiante2.poblacion) #Población
        c.setFont("Helvetica", 12)
        c.drawString(130, 325, estudiante2.codigo_postal) #Código Postal
        c.setFont("Helvetica", 10)
        c.drawString(254, 326, estudiante2.provincia) #Provincia
        c.drawString(464, 326, estudiante2.telefono) #Teléfono
        
        x = 50
        y = 463
        y2=290
        i = 1

        for permuta in permutas:
            c.drawString(x, y, permuta.asignatura.codigo)#CÓDIGO
            c.drawString(x+65, y, permuta.asignatura.nombre) #ASIGNATURA
            c.drawString(x, y2, permuta.asignatura.codigo)#CÓDIGO
            c.drawString(x+65, y2, permuta.asignatura.nombre) #ASIGNATURA
            y2= y2-15
            y= y-15
            i=i+1
            if i == 5:
                x= 320
                y = 463
                y2=290
            elif i==10:
                break
                
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
            nombre_pdf = 'Permuta_'+estudiante1.nombre+'_'+estudiante1.apellido+'_'+estudiante1.nombre+'_'+estudiante1.apellido+'.pdf'
        return FileResponse(output_buffer, as_attachment=True, filename=nombre_pdf)
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

def sacar_permutas_two_users(user1,user2):
    permutas_solicitante = Permuta.objects.filter(
        Q(estudiante1__user=user1, estudiante2__user=user2) | 
        Q(estudiante1__user=user2, estudiante2__user=user1)
    )
    return permutas_solicitante


def subir_grupo(request):
    if request.method == 'POST':
        form = GrupoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_grupos')
    else:
        form = GrupoForm()
    return render(request, 'subir_grupo.html', {'form': form})

@login_required
@user_passes_test(is_delegacion_or_admin)
def actualizar_proyecto_docente(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.method == 'POST':
        form = ProyectoDocenteForm(request.POST, request.FILES, instance=grupo)
        if form.is_valid():
            form.save()
            return redirect('lista_grupos')  # O la vista a la que desees redirigir
    else:
        form = ProyectoDocenteForm(instance=grupo)
    return render(request, 'actualizar_proyecto_docente.html', {'form': form, 'grupo': grupo})

@login_required
def asignar_asignaturas(request):
    estudiante = get_object_or_404(Estudiante, user=request.user)
    if request.method == 'POST':
        form = AsignarAsignaturasForm(request.POST, instance=estudiante, estudiante=estudiante)
        if form.is_valid():
            form.save()
            return redirect('detalle_estudiante')  # Redirigir a una vista adecuada después de guardar
    else:
        form = AsignarAsignaturasForm(instance=estudiante, estudiante=estudiante)
    return render(request, 'asignar_asignaturas.html', {'form': form, 'estudiante': estudiante})

# views.py
@login_required
def detalle_estudiante(request):
    estudiante = get_object_or_404(Estudiante, user=request.user)
    return render(request, 'detalle_estudiante.html', {'estudiante': estudiante})

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SolicitudPermutaForm
from .models import Estudiante, Solicitud_Permuta

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SolicitudPermutaForm
from .models import Estudiante, Solicitud_Permuta

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SolicitudPermutaForm
from .models import Estudiante, Solicitud_Permuta, Grupo

@login_required
def crear_solicitud_permuta(request):
    estudiante = get_object_or_404(Estudiante, user=request.user)
    if request.method == 'POST':
        form = SolicitudPermutaForm(request.POST, estudiante=estudiante)
        if form.is_valid():
            for asignatura in estudiante.obtener_asignaturas():
                grupo_deseado = form.cleaned_data.get(f'grupo_deseado_{asignatura.id}')
                if grupo_deseado:
                    solicitud_permuta = Solicitud_Permuta(
                        estudiante1=estudiante,
                        grupo1=estudiante.grupo_set.filter(asignatura=asignatura).first(),
                        asignatura=asignatura
                    )
                    solicitud_permuta.save()
                    solicitud_permuta.grupo_deseado.add(grupo_deseado)
            return redirect('detalle_estudiante')  # Redirect to a suitable view after saving
    else:
        form = SolicitudPermutaForm(estudiante=estudiante)
    return render(request, 'crear_solicitud_permuta.html', {'form': form, 'estudiante': estudiante})
