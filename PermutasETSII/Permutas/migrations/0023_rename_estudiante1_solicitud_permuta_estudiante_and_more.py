# Generated by Django 5.0.6 on 2024-07-01 21:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Permutas', '0022_asignatura_curso'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solicitud_permuta',
            old_name='estudiante1',
            new_name='estudiante',
        ),
        migrations.RenameField(
            model_name='solicitud_permuta',
            old_name='grupo1',
            new_name='grupo_actual',
        ),
    ]
