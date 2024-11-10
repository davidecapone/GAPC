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