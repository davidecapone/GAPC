from django.db import models

class Asteroid(models.Model):

    target_name = models.CharField(
        primary_key=True,
        max_length=100,
        unique=True,
        help_text='Official name or designation of the asteroid'
    )

    target_description = models.TextField(
        blank=True,
        help_text='Brief description of the asteroid'
    )

    target_discovery_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date of discovery'
    )

    target_class = models.CharField(
        max_length=50,
        blank=True,
        help_text='Classification of the asteroid'
    )

    target_size = models.FloatField(
        null=True,
        blank=True,
        help_text='Size of the asteroid in kilometers'
    )


    def __str__(self):
        return self.target_name
    
    class Meta:
        ordering = ['target_name']
        verbose_name = 'Asteroid'
        verbose_name_plural = 'Asteroids'


class Observation(models.Model):

    obs_id = models.CharField(
        primary_key=True,
        max_length=300,
        unique=True,
        help_text='Unique identifier for the observation'
    )

    asteroid = models.ForeignKey(
        Asteroid,
        on_delete=models.CASCADE,
        related_name='observations',
        help_text='Asteroid observed',
        verbose_name='Observed Asteroid'
    )

    date_obs = models.DateTimeField(
        help_text='Date and time of the observation'
    )

    instrument_name = models.CharField(
        blank=True,
        max_length=100,
        help_text='Name of the instrument used'
    )

    exposure_time = models.FloatField(
        help_text='Exposure time in seconds'
    )


    def __str__(self):
        return f"Observation {self.obs_id} of {self.asteroid.target_name} on {self.date_obs}"

    class Meta:
        ordering = ['-date_obs']
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'