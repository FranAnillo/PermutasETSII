# Generated by Django 5.0.6 on 2024-06-11 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Permutas', '0012_estudiante_domicilio_estudiante_provincia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='permuta',
            name='estado',
            field=models.CharField(choices=[('solicitada', 'Solicitada'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], default=0, max_length=10),
            preserve_default=False,
        ),
    ]
