# Generated by Django 5.1.2 on 2024-11-21 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gapc', '0004_rename_exposure_time_observation_exptime_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='naxis1',
            field=models.IntegerField(default=0, help_text='Number of pixels along the x-axis'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='observation',
            name='naxis2',
            field=models.IntegerField(default=0, help_text='Number of pixels along the y-axis'),
            preserve_default=False,
        ),
    ]