from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Grado, Asignatura, Estudiante, Grupo, Permuta

class GradoModelTest(TestCase):

    def setUp(self):
        self.grado = Grado.objects.create(nombre="Ingeniería Informática")

    def test_grado_creation(self):
        self.assertEqual(self.grado.nombre, "Ingeniería Informática")
        self.assertEqual(str(self.grado), 'Ingeniería Informática')

class AsignaturaModelTest(TestCase):

    def setUp(self):
        self.grado = Grado.objects.create(nombre="Ingeniería Informática")
        self.asignatura = Asignatura.objects.create(nombre="Matemáticas", grado=self.grado)

    def test_asignatura_creation(self):
        self.assertEqual(self.asignatura.nombre, "Matemáticas")
        self.assertEqual(self.asignatura.grado, self.grado)
        self.assertEqual(str(self.asignatura), 'Matemáticas')

class EstudianteModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.grado = Grado.objects.create(nombre="Ingeniería Informática")
        self.estudiante = Estudiante.objects.create(
            user=self.user,
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@example.com",
            dni="12345678A",
            grado=self.grado,
            domicilio="Calle Falsa 123",
            provincia="Madrid",
            poblacion="Madrid",
            telefono="+34123456789"
        )

    def test_estudiante_creation(self):
        self.assertEqual(self.estudiante.nombre, "Juan")
        self.assertEqual(self.estudiante.apellido, "Pérez")
        self.assertEqual(self.estudiante.email, "juan.perez@example.com")
        self.assertEqual(str(self.estudiante), 'Perfil de testuser')
class GrupoModelTest(TestCase):

    def setUp(self):
        self.grado = Grado.objects.create(nombre="Ingeniería Informática")
        self.asignatura = Asignatura.objects.create(nombre="Matemáticas", grado=self.grado)
        self.grupo = Grupo.objects.create(numero_grupo=1, limite_estudiantes=30, tipo_grupo='teoria', asignatura=self.asignatura)

    def test_grupo_creation(self):
        self.assertEqual(self.grupo.numero_grupo, 1)
        self.assertEqual(self.grupo.limite_estudiantes, 30)
        self.assertEqual(self.grupo.tipo_grupo, 'teoria')
        self.assertEqual(self.grupo.asignatura, self.asignatura)




class PermutaModelTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='12345')
        self.user2 = User.objects.create_user(username='testuser2', password='12345')
        self.grado = Grado.objects.create(nombre="Ingeniería Informática")
        self.estudiante1 = Estudiante.objects.create(
            user=self.user1,
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@example.com",
            dni="12345678A",
            grado=self.grado,
            domicilio="Calle Falsa 123",
            provincia="Madrid",
            poblacion="Madrid",
            telefono="+34123456789"
        )
        self.estudiante2 = Estudiante.objects.create(
            user=self.user2,
            nombre="Ana",
            apellido="García",
            email="ana.garcia@example.com",
            dni="87654321B",
            grado=self.grado,
            domicilio="Calle Verdadera 456",
            provincia="Barcelona",
            poblacion="Barcelona",
            telefono="+34987654321"
        )
        self.asignatura = Asignatura.objects.create(nombre="Matemáticas", grado=self.grado)
        self.grupo1 = Grupo.objects.create(numero_grupo=1, limite_estudiantes=30, tipo_grupo='teoria', asignatura=self.asignatura)
        self.grupo2 = Grupo.objects.create(numero_grupo=2, limite_estudiantes=30, tipo_grupo='practica', asignatura=self.asignatura)
        self.permuta = Permuta.objects.create(
            estudiante1=self.estudiante1,
            estudiante2=self.estudiante2,
            grupo1=self.grupo1,
            grupo2=self.grupo2,
            asignatura=self.asignatura,
            estado='solicitada'
        )

    def test_permuta_creation(self):
        self.assertEqual(self.permuta.estudiante1, self.estudiante1)
        self.assertEqual(self.permuta.estudiante2, self.estudiante2)
        self.assertEqual(self.permuta.grupo1, self.grupo1)
        self.assertEqual(self.permuta.grupo2, self.grupo2)
        self.assertEqual(self.permuta.asignatura, self.asignatura)
        self.assertEqual(self.permuta.estado, 'solicitada')

    def test_permuta_clean(self):
        with self.assertRaises(ValidationError):
            permuta_invalid = Permuta(
                estudiante1=self.estudiante1,
                estudiante2=self.estudiante1,
                grupo1=self.grupo1,
                grupo2=self.grupo2,
                asignatura=self.asignatura,
                estado='solicitada'
            )
            permuta_invalid.clean()

