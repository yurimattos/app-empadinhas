# Generated by Django 3.0.9 on 2021-12-05 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0007_auto_20211205_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventario',
            name='status',
            field=models.CharField(default='Pendente', max_length=30),
        ),
    ]
