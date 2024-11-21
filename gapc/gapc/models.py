from django.db import models
from django.utils import timezone


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
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("not_confirmed", "Not Confirmed"),
        ("pending", "Pending Confirmation"),
    ]

    # Provisional name (e.g., ZTF0NiK)
    provisional_name = models.CharField(
        max_length=100,
        primary_key=True,  # Set as the primary key
        help_text="Provisional name or designation of the asteroid"
    )

    # Official name (e.g., 2022 GO5)
    official_name = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Official name of the asteroid"
    )

    # Status of the asteroid
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Confirmation status of the asteroid"
    )

    target_discovery_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date and time of discovery'
    )

    target_class = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Classification of the asteroid, e.g., Near-Earth Object, Trojan"
    )

    is_neo = models.BooleanField(
        default=False,
        help_text='Whether the asteroid is a Near-Earth Object (NEO)'
    )

    def __str__(self):
        return f"{self.official_name} ({self.provisional_name})" or self.provisional_name or "Unnamed Asteroid"

    class Meta:
        ordering = ['status', 'official_name', 'provisional_name']
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

    exptime = models.FloatField(
        help_text='Exposure time in seconds'
    )

    exposure = models.FloatField(
        help_text='Exposure in seconds'
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

    temperat = models.FloatField(
        null=True,
        blank=True,
        help_text='Temperature during observation in Celsius'
    )

    naxis1 = models.IntegerField(
        help_text='Number of pixels along the x-axis'
    )

    naxis2 = models.IntegerField(
        help_text='Number of pixels along the y-axis'
    )

    filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="File name of the observation FITS file"
    )

    def __str__(self):
        asteroid_name = self.asteroid.official_name or self.asteroid.provisional_name or "Unnamed Asteroid"
        local_date_obs = timezone.localtime(self.date_obs)  # Convert to local timezone
        return f"Observation of {asteroid_name} on {local_date_obs}"

    class Meta:
        ordering = ['-date_obs']
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'
        unique_together = ('asteroid', 'date_obs')  # Enforces uniqueness constraint
