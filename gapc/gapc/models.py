from django.db import models
from django.utils import timezone

class Asteroid(models.Model):
    STATUS_CHOICES = [("confirmed", "Confirmed"),("not_confirmed", "Not Confirmed"),("pending", "Pending Confirmation")]
    # Provisional name (e.g., ZTF0NiK)
    provisional_name = models.CharField(max_length=100,primary_key=True,
                                        help_text="Provisional name or designation of the asteroid")

    # Official name (e.g., 2022 GO5)
    official_name = models.CharField(max_length=100,unique=True,blank=True,null=True,
                                     help_text="Official name of the asteroid")
    
    # Status of the asteroid
    status = models.CharField(max_length=15,choices=STATUS_CHOICES,default="pending",
                              help_text="Confirmation status of the asteroid")
    
    # Target class of the asteroid
    target_class = models.CharField(max_length=100,blank=True,null=True,
                                    help_text="Classification of the asteroid, e.g., Near-Earth Object, Trojan")
    
    # Whether the asteroid is a Near-Earth Object (NEO)
    is_neo = models.BooleanField(default=False,help_text='Whether the asteroid is a Near-Earth Object (NEO)')

    def __str__(self):
        return f"{self.official_name} ({self.provisional_name})" or self.provisional_name or "Unnamed Asteroid"

    class Meta:
        ordering = ['status', 'official_name', 'provisional_name']
        verbose_name = 'Asteroid'
        verbose_name_plural = 'Asteroids'

class Observation(models.Model):
    # Explicitly define the primary key field
    obs_id = models.AutoField(primary_key=True)  # Add an explicit primary key field
    # Foreign key to the Asteroid model
    asteroid = models.ForeignKey(Asteroid,on_delete=models.CASCADE,related_name='observations',
                                help_text='Asteroid observed',verbose_name='Observed Asteroid')
    
    date_obs = models.DateTimeField(help_text='Date and time of the observation')
    naxis1 = models.IntegerField(help_text='Number of pixels along the x-axis')
    naxis2 = models.IntegerField(help_text='Number of pixels along the y-axis')
    temperat = models.FloatField(null=True,blank=True,help_text='Temperature during observation in Celsius')
    exptime = models.FloatField(help_text='Exposure time in seconds')
    exposure = models.FloatField(help_text='Exposure in seconds')
    # Right Ascension and Declination of the asteroid
    ra = models.CharField(max_length=50,null=True,blank=True,help_text='Right Ascension in HH:MM:SS.s format')
    dec = models.CharField(max_length=50,null=True,blank=True,help_text='Declination in DD:MM:SS.s format')
    # File name of the observation FITS file
    filename = models.CharField(max_length=255,blank=True,null=True,help_text="File name of the observation FITS file")

    def __str__(self):
        asteroid_name = self.asteroid.official_name or self.asteroid.provisional_name or "Unnamed Asteroid"
        local_date_obs = timezone.localtime(self.date_obs)  # Convert to local timezone
        return f"Observation of {asteroid_name} on {local_date_obs}"

    class Meta:
        ordering = ['-date_obs']
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'
        unique_together = ('asteroid', 'date_obs')  # Enforces uniqueness constraint
