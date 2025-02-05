# Generated by Django 4.1.4 on 2022-12-26 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_submission_output'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='input_should_contain_error_msg',
            field=models.CharField(blank=True, max_length=255, verbose_name='Error text shown when the input does not contain a required item'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='input_should_not_contain_error_msg',
            field=models.CharField(blank=True, max_length=255, verbose_name='Error text shown when the input contains an unwanted item'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='output_should_contain_error_msg',
            field=models.CharField(blank=True, max_length=255, verbose_name='Error text shown when the output does not contain a required item'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='output_should_not_contain_error_msg',
            field=models.CharField(blank=True, max_length=255, verbose_name='Error text shown when the output contains an unwanted item'),
        ),
    ]
