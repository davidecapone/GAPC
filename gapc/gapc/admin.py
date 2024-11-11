from django.contrib import admin
from .models import Asteroid, Observation

admin.site.register(Asteroid)
admin.site.register(Observation)