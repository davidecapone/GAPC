from django.contrib import admin
from .models import Asteroid, Observation, Instrument

admin.site.register(Asteroid)
admin.site.register(Observation)
admin.site.register(Instrument)
