# Generated by Django 5.0.6 on 2024-06-17 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Permutas', '0015_asignatura_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='permuta',
            name='aceptada_1',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permuta',
            name='aceptada_2',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='asignatura',
            name='codigo',
            field=models.IntegerField(unique=True),
        ),
    ]