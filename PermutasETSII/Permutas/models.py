from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Count

class Grado (models.Model):
  nombre= models.CharField(max_length=255, unique=True)
  
  def __str__(self):
    return  f'{self.nombre}'

class Asignatura (models.Model):
  nombre = models.CharField(max_length=255)
  grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
  curso = models.CharField(max_length=10, choices=[('primero', 'Primero'), ('segundo', 'Segundo'), ('tercero', 'Tercero'), ('cuarto', 'Cuarto')])
  codigo = models.CharField(unique= True ,max_length=7)

  def __str__(self):
    return  f'{self.nombre}'
  
class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    dni = models.CharField(max_length=9, unique=True)
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
    domicilio = models.CharField(max_length=255)
    provincia = models.CharField(max_length=50)
    poblacion = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=5)
    telefono = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="El número de teléfono debe ingresarse en el formato: '+999999999'. Hasta 15 dígitos permitidos.")])  # Nuevo campo de teléfono
    
    def obtener_asignaturas(self):
      return Asignatura.objects.filter(grupo__estudiante=self).distinct()
    
    def obtener_grupos(self):
        return Grupo.objects.filter(estudiante=self).distinct()
    
    def __str__(self):
        return f'Perfil de {self.user.username}'
    
    def grupo_matriculado(self, asignatura):
        grupo = Grupo.objects.filter(asignatura=asignatura, estudiante=self).first()
        print(f"Estudiante: {self}, Asignatura: {asignatura}, Grupo Matriculado: {grupo}")  # Agrega un print para depuración
        return grupo


class Grupo(models.Model):
    numero_grupo = models.IntegerField()
    limite_estudiantes = models.IntegerField()
    tipo_grupo = models.CharField(max_length=10, choices=[('teoria', 'Teoria'), ('practica', 'Practica')])
    estudiante = models.ManyToManyField(Estudiante, blank=True)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    proyecto_docente = models.FileField(upload_to='pdfs/', blank=True, null=True)
  
    @classmethod
    def grupo_matriculados(cls, estudiante, asignatura):
        return cls.objects.filter(asignatura=asignatura, estudiante=estudiante)
  
    @classmethod
    def grupos_no_matriculados(cls, estudiante, asignatura):
        return cls.objects.filter(asignatura=asignatura).exclude(estudiante=estudiante)
  
    def __str__(self):
        return f'Grupo {self.numero_grupo} de {self.asignatura.nombre}'


class Solicitud_Permuta(models.Model):
    estudiante = models.ForeignKey(Estudiante, related_name='solicitudes_permuta', on_delete=models.CASCADE)
    grupos_deseados = models.ManyToManyField(Grupo, related_name='deseos_permuta', blank=True)
    asignatura = models.ForeignKey(Asignatura, related_name='solicitudes_permuta', on_delete=models.CASCADE)
    grupo_actual = models.ForeignKey(Grupo, related_name='solicitudes_permuta', on_delete=models.CASCADE)

    def clean(self):
        # Verificar que el estudiante pertenece al grupo actual
        if not self.grupo_actual.estudiante.filter(id=self.estudiante.id).exists():
            raise ValidationError('El estudiante no pertenece al grupo seleccionado.')
        
        # Verificar que el grupo actual no esté en los grupos deseados
        if self.grupo_actual in self.grupos_deseados.all():
            raise ValidationError('No puedes solicitar una permuta al grupo al que perteneces.')
        
    def __str__(self):
        return f'Solicitud de {self.estudiante.user.username} para cambiar de {self.grupo_actual.numero_grupo} a {[g.numero_grupo for g in self.grupos_deseados.all()]}'

class Permuta(models.Model):
    estudiante1 = models.ForeignKey(Estudiante, related_name='permuta_estudiante1', on_delete=models.CASCADE)
    estudiante2 = models.ForeignKey(Estudiante, related_name='permuta_estudiante2', on_delete=models.CASCADE)
    grupo1 = models.ForeignKey(Grupo, related_name='permuta_grupo1', on_delete=models.CASCADE)
    grupo2 = models.ForeignKey(Grupo, related_name='permuta_grupo2', on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, related_name='asignatura', on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=[('solicitada', 'Solicitada'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')])
    aceptada_1 = models.BooleanField()
    aceptada_2 = models.BooleanField()

    def clean(self):
        if self.estudiante1 == self.estudiante2:
            raise ValidationError("Estudiante 1 y Estudiante 2 deben ser diferentes")

        # Verificar que estudiante1 no tiene otra permuta para la misma asignatura
        if Permuta.objects.filter(estudiante1=self.estudiante1, asignatura=self.asignatura).exclude(id=self.id).exists():
            raise ValidationError(f"{self.estudiante1.user.username} ya tiene una permuta para la asignatura {self.asignatura.nombre}")

        if Permuta.objects.filter(estudiante2=self.estudiante1, asignatura=self.asignatura).exclude(id=self.id).exists():
            raise ValidationError(f"{self.estudiante1.user.username} ya tiene una permuta para la asignatura {self.asignatura.nombre}")

        # Verificar que estudiante2 no tiene otra permuta para la misma asignatura
        if Permuta.objects.filter(estudiante1=self.estudiante2, asignatura=self.asignatura).exclude(id=self.id).exists():
            raise ValidationError(f"{self.estudiante2.user.username} ya tiene una permuta para la asignatura {self.asignatura.nombre}")

        if Permuta.objects.filter(estudiante2=self.estudiante2, asignatura=self.asignatura).exclude(id=self.id).exists():
            raise ValidationError(f"{self.estudiante2.user.username} ya tiene una permuta para la asignatura {self.asignatura.nombre}")

        # Verificar que estudiante1 esté en grupo1
        if not self.grupo1.estudiante.filter(id=self.estudiante1.id).exists():
            raise ValidationError(f"{self.estudiante1.user.username} no está inscrito en el grupo {self.grupo1.numero_grupo}")

        # Verificar que estudiante2 esté en grupo2
        if not self.grupo2.estudiante.filter(id=self.estudiante2.id).exists():
            raise ValidationError(f"{self.estudiante2.user.username} no está inscrito en el grupo {self.grupo2.numero_grupo}")

        # Verificar que grupo1 y grupo2 pertenecen a la asignatura
        if self.grupo1.asignatura != self.asignatura:
            raise ValidationError(f"El grupo {self.grupo1.numero_grupo} no pertenece a la asignatura {self.asignatura.nombre}")

        if self.grupo2.asignatura != self.asignatura:
            raise ValidationError(f"El grupo {self.grupo2.numero_grupo} no pertenece a la asignatura {self.asignatura.nombre}")

        # Verificar que grupo1 y grupo2 no están vacíos
        if not self.grupo1.estudiante.exists():
            raise ValidationError(f"El grupo {self.grupo1.numero_grupo} no tiene estudiantes")

        if not self.grupo2.estudiante.exists():
            raise ValidationError(f"El grupo {self.grupo2.numero_grupo} no tiene estudiantes")


    def __str__(self):
        return f'Permuta entre {self.estudiante1.user.username} y {self.estudiante2.user.username} en {self.asignatura.nombre}'
   