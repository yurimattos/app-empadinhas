# Generated by Django 3.0.9 on 2021-12-05 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lojas', '0002_auto_20211124_0837'),
        ('inventario', '0002_auto_20211205_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipodecontagem',
            name='lojas',
            field=models.ManyToManyField(blank=True, null=True, related_name='tipos_de_contagens', to='lojas.Lojas'),
        ),
    ]
