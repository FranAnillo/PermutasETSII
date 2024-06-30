from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Estudiante,Grupo,Asignatura,Solicitud_Permuta
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

class StudentRegisterForm(UserCreationForm):
    nombre = forms.CharField(max_length=255)
    apellido = forms.CharField(max_length=255)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'nombre', 'apellido', 'email', 'password1', 'password2']
        help_texts = {k: "" for k in fields}


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class EstudianteUpdateForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'apellido', 'dni', 'domicilio', 'provincia','poblacion', 'telefono', 'image']

    def __init__(self, *args, **kwargs):
        super(EstudianteUpdateForm, self).__init__(*args, **kwargs)
        self.fields['dni'].widget.attrs['readonly'] = True
        
class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['numero_grupo', 'limite_estudiantes', 'tipo_grupo', 'estudiante', 'asignatura', 'proyecto_docente']

class ProyectoDocenteForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['proyecto_docente']

class AsignarAsignaturasForm(forms.ModelForm):
    asignaturas = forms.ModelMultipleChoiceField(
        queryset=Asignatura.objects.none(), 
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Estudiante
        fields = ['asignaturas']

    def __init__(self, *args, **kwargs):
        estudiante = kwargs.pop('estudiante', None)
        super(AsignarAsignaturasForm, self).__init__(*args, **kwargs)
        if estudiante:
            self.fields['asignaturas'].queryset = Asignatura.objects.filter(grado=estudiante.grado)



# forms.py
from django import forms
from .models import Solicitud_Permuta, Grupo, Asignatura

class SolicitudPermutaForm(forms.ModelForm):
    class Meta:
        model = Solicitud_Permuta
        fields = []

    def __init__(self, *args, **kwargs):
        estudiante = kwargs.pop('estudiante', None)
        super(SolicitudPermutaForm, self).__init__(*args, **kwargs)
        if estudiante:
            # Generate dropdown fields for each asignatura's grupos_no_matriculados
            for asignatura in estudiante.obtener_asignaturas():
                grupos = Grupo.grupos_no_matriculados(Grupo, estudiante, asignatura)
                if grupos.exists():
                    field_name = f'grupo_deseado_{asignatura.id}'
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=grupos,
                        required=False,
                        label=asignatura.nombre,
                        empty_label="Seleccione un grupo"
                    )
