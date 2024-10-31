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

class SolicitudPermutaForm(forms.ModelForm):
    class Meta:
        model = Solicitud_Permuta
        fields = []  # No incluir 'grupo_actual' para que no se muestre en el formulario

    def __init__(self, *args, **kwargs):
        self.estudiante = kwargs.pop('estudiante', None)
        super(SolicitudPermutaForm, self).__init__(*args, **kwargs)
        if self.estudiante:
            # Genera campos desplegables para los grupos no matriculados de cada asignatura
            for asignatura in self.estudiante.obtener_asignaturas():
                grupos = Grupo.grupos_no_matriculados(self.estudiante, asignatura)
                if grupos.exists():
                    field_name = f'grupos_deseados_{asignatura.id}'
                    self.fields[field_name] = forms.ModelMultipleChoiceField(
                        queryset=grupos,
                        required=False,
                        label=asignatura.nombre,
                        widget=forms.CheckboxSelectMultiple  # Usa checkboxes para la selección múltiple
                    )

    def save(self, commit=True):
        instance = super(SolicitudPermutaForm, self).save(commit=False)
        grupo_actual = self.estudiante.grupo_matriculado(instance.asignatura)
        print(grupo_actual)
        instance.grupo_actual = grupo_actual
        # Obtener el grupo matriculado del estudiante para la asignatura específica
        if grupo_actual is None:
            raise ValueError(f"El estudiante {self.estudiante} no está matriculado en ningún grupo para la asignatura {instance.asignatura}")
        print(f"Instancia de Solicitud_Permuta: {instance}, Grupo Actual: {instance.grupo_actual}")  # Agrega un print para depuración
        if commit:
            instance.save()
            self.save_m2m()  # Guardar la relación muchos-a-muchos si es necesario
        return instance


