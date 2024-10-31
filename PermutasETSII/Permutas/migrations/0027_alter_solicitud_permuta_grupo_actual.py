# Generated by Django 5.0.6 on 2024-08-06 10:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Permutas', '0026_alter_solicitud_permuta_grupo_actual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitud_permuta',
            name='grupo_actual',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solicitudes_permuta', to='Permutas.grupo'),
        ),
    ]
