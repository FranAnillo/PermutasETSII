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
  codigo = models.IntegerField( unique= True)

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
    
    def obtener_asignaturas(self):
      return Asignatura.objects.filter(grupo__estudiante=self).distinct()
    
    def obtener_grupos(self):
        return Grupo.objects.filter(estudiante=self).distinct()
    
    def __str__(self):
        return f'Perfil de {self.user.username}'

class Grupo (models.Model):
  numero_grupo = models.IntegerField()
  limite_estudiantes = models.IntegerField()
  tipo_grupo=models.CharField(max_length=10, choices=[('teoria', 'Teoria'), ('practica', 'Practica')])
  estudiante = models.ManyToManyField(Estudiante, blank=True)
  asignatura= models.ForeignKey(Asignatura, on_delete=models.CASCADE)


class Solicitud_Permuta(models.Model):
    estudiante1 = models.ForeignKey('Estudiante', related_name='estudiante_solicitud', on_delete=models.CASCADE)
    grupo1 = models.ForeignKey('Grupo', related_name='grupo_solicitud', on_delete=models.CASCADE)
    grupo_deseado = models.ManyToManyField('Grupo')
    asignatura = models.ForeignKey('Asignatura', related_name='asignatura_solicitada', on_delete=models.CASCADE)

    def clean(self):
        # Verificar que el estudiante pertenece al grupo
        if not self.grupo1.estudiante.filter(id=self.estudiante1.id).exists():
            raise ValidationError('El estudiante no pertenece al grupo seleccionado.')
        
    def save(self, *args, **kwargs):
        # Call the parent save method to ensure the instance is saved to the database
        super().save(*args, **kwargs)
        
        # Now we can safely perform the many-to-many check
        if self.grupo1 in self.grupo_deseado.all():

            raise ValidationError('No puedes solicitar una permuta al grupo al que perteneces.')
        
        # Save again to apply changes if no v

    def __str__(self):
        return f'Solicitud de {self.estudiante1.user.username} para cambiar de {self.grupo1.numero_grupo} a {[g.numero_grupo for g in self.grupo_deseado.all()]}'

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

    def __str__(self):
        return f'Permuta entre {self.estudiante1.user.username} y {self.estudiante2.user.username} en {self.asignatura.nombre}'
   