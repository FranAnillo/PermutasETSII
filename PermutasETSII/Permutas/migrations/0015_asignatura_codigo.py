# Generated by Django 5.0.6 on 2024-06-17 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Permutas', '0014_estudiante_poblacion_alter_permuta_estudiante2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='asignatura',
            name='codigo',
            field=models.IntegerField(default=1, max_length=15, unique=True),
            preserve_default=False,
        ),
    ]
