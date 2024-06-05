from django.db import models

# Create your models here.
class Asignatura (models.Model):
  nombre_asignatura = models.CharField(max_length=255)

class Estudiante(models.Model):
  nombre = models.CharField(max_length=255)
  apellido = models.CharField(max_length=255)
  email = models.EmailField(max_length=255)
  
  
class Grupo (models.Model):
  numero_grupo = models.IntegerField()
  limite_estudiantes = models.IntegerField()
  tipo_grupo=models.CharField(max_length=10, choices=[('teoria', 'Teoria'), ('practica', 'Practica')])
  estudiante = models.ManyToManyField(Estudiante)
  asignatura= models.ForeignKey(Asignatura, on_delete=models.CASCADE)

class Permuta(models.Model):
    estudiante1 = models.ForeignKey(Estudiante, related_name='permuta_estudiante1', on_delete=models.CASCADE)
    estudiante2 = models.ForeignKey(Estudiante, related_name='permuta_estudiante2', on_delete=models.CASCADE)
    grupo1 = models.ForeignKey(Grupo, related_name='permuta_grupo1', on_delete=models.CASCADE)
    grupo2 = models.ForeignKey(Grupo, related_name='permuta_grupo2', on_delete=models.CASCADE)
