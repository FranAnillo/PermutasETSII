from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class Grado (models.Model):
  nombre= models.CharField(max_length=255, unique=True)
  
  def __str__(self):
    return  f'{self.nombre}'

class Asignatura (models.Model):
  nombre = models.CharField(max_length=255)
  grado = models.ForeignKey(Grado, on_delete=models.CASCADE)

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
    telefono = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="El número de teléfono debe ingresarse en el formato: '+999999999'. Hasta 15 dígitos permitidos.")])  # Nuevo campo de teléfono
    
    def __str__(self):
        return f'Perfil de {self.user.username}'

class Grupo (models.Model):
  numero_grupo = models.IntegerField()
  limite_estudiantes = models.IntegerField()
  tipo_grupo=models.CharField(max_length=10, choices=[('teoria', 'Teoria'), ('practica', 'Practica')])
  estudiante = models.ManyToManyField(Estudiante)
  asignatura= models.ForeignKey(Asignatura, on_delete=models.CASCADE)

class Permuta(models.Model):
    estudiante1 = models.ForeignKey(Estudiante, related_name='permuta_estudiante1', on_delete=models.CASCADE)
    estudiante2 = models.ForeignKey(Estudiante, related_name='permuta_estudiante2', on_delete=models.SET_NULL, null=True, blank=True)
    grupo1 = models.ForeignKey(Grupo, related_name='permuta_grupo1', on_delete=models.CASCADE)
    grupo2 = models.ForeignKey(Grupo, related_name='permuta_grupo2', on_delete=models.SET_NULL, null=True, blank=True)
    asignatura = models.ForeignKey(Asignatura, related_name='asignatura', on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=[('solicitada', 'Solicitada'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')])

    def clean(self):
        if self.estudiante1 == self.estudiante2:
            raise ValidationError("Estudiante 1 y Estudiante 2 deben ser diferentes")

    def __str__(self):
        return f'Permuta entre {self.estudiante1.user.username} y {self.estudiante2.user.username} en {self.asignatura.nombre_asignatura}'
   