# Generated by Django 5.1.2 on 2024-11-26 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gapc', '0005_observation_naxis1_observation_naxis2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='observation',
            name='instrument',
        ),
        migrations.DeleteModel(
            name='Instrument',
        ),
    ]
