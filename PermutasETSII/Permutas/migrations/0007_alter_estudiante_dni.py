# Generated by Django 5.0.6 on 2024-06-11 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Permutas', '0006_estudiante_dni_permuta_asignatura'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudiante',
            name='dni',
            field=models.CharField(max_length=9, unique=True),
        ),
    ]
