# Generated by Django 4.2.1 on 2023-06-12 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DApp', '0006_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='Hash',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
