from django.db import models
from django.utils import timezone
from django.conf import settings


class Instrument(models.Model):

    name = models.CharField(
        primary_key=True,
        max_length=100, 
        help_text="Name of the instrument, e.g., Alta U9000"
    )

    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        help_text="Manufacturer of the instrument"
    )

    max_exposure_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Maximum exposure time in milliseconds"
    )

    min_exposure_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Minimum exposure time in milliseconds"
    )

    pixel_size = models.CharField(
        max_length=20, 
        blank=True,
        null=True,
        help_text="Pixel size in microns, e.g., 12 x 12 microns"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Instrument'
        verbose_name_plural = 'Instruments'


class Asteroid(models.Model):

    CLASS_CHOICES = [
        ("neo", "Near-Earth Object"),
        ("comet", "Comet"),
        ("asteroid", "Asteroid"),
        ("trojan", "Trojan"),
        ("undefined", "Undefined"),
    ]

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

    target_discovery_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date and time of discovery'
    )

    target_class = models.CharField(
        max_length=50,
        choices=CLASS_CHOICES,
        blank=True,
        default="undefined",
        help_text='Classification of the asteroid'
    )

    target_size = models.FloatField(
        null=True,
        blank=True,
        help_text='Size of the asteroid in kilometers'
    )

    def __str__(self):
        return f"Asteroid {self.target_name}"
    
    class Meta:
        ordering = ['target_name']
        verbose_name = 'Asteroid'
        verbose_name_plural = 'Asteroids'


class Observation(models.Model):

    obs_id = models.AutoField(primary_key=True)  # Add an explicit primary key field

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

    instrument = models.ForeignKey(
        Instrument, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        help_text="Instrument used for the observation"
    )


    exposure_time = models.FloatField(
        help_text='Exposure time in seconds'
    )

    ra = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Right Ascension in HH:MM:SS.s format'
    )

    dec = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Declination in DD:MM:SS.s format'
    )

    temperature = models.FloatField(
        null=True,
        blank=True,
        help_text='Temperature during observation in Celsius'
    )

    filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="File name of the observation FITS file"
    )

    def __str__(self):
        local_date_obs = timezone.localtime(self.date_obs)  # Convert to local timezone
        return f"Observation of {self.asteroid.target_name} on {local_date_obs}"

    class Meta:
        ordering = ['-date_obs']
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'
        unique_together = ('asteroid', 'date_obs')  # Enforces uniqueness constraint
