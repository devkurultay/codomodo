# Generated by Django 4.1.4 on 2023-01-09 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='passed',
            field=models.BooleanField(default=False),
        ),
    ]