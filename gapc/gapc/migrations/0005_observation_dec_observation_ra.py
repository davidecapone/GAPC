# Generated by Django 5.1.2 on 2024-11-11 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gapc', '0004_alter_observation_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='dec',
            field=models.FloatField(blank=True, help_text='Declination of the observation in degrees', null=True),
        ),
        migrations.AddField(
            model_name='observation',
            name='ra',
            field=models.FloatField(blank=True, help_text='Right Ascension of the observation in degrees', null=True),
        ),
    ]
