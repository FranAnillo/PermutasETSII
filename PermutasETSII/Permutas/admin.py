from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Asignatura, Estudiante, Grupo, Permuta
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Registrar modelos en el admin
admin.site.register(Asignatura)
admin.site.register(Estudiante)
admin.site.register(Grupo)
admin.site.register(Permuta)

@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    # Definir permisos personalizados
    permisos = [
        ('add_permuta', 'Can add permuta'),
        ('change_permuta', 'Can change permuta'),
        ('delete_permuta', 'Can delete permuta'),
        ('view_permuta', 'Can view permuta'),
    ]
    
    # Crear o actualizar permisos
    content_type = ContentType.objects.get_for_model(Permuta)
    for codename, name in permisos:
        Permission.objects.get_or_create(codename=codename, name=name, content_type=content_type)
    
    # Definir grupos y asignar permisos
    groups = {
        'Estudiante': ['add_permuta', 'change_permuta', 'delete_permuta', 'view_permuta'],
        'Admin': [
            'add_user', 'change_user', 'delete_user', 'view_user',
            'add_permuta', 'change_permuta', 'delete_permuta', 'view_permuta'
        ],
    }
    
    for group_name, permissions in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)
        for perm in permissions:
            permission = Permission.objects.get(codename=perm)
            group.permissions.add(permission)
        group.save()