# gapc/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from .models import Asteroid, Observation
from datetime import datetime


from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from .models import Asteroid

from astropy.io.votable.tree import VOTableFile, Resource, Table, Field
from astropy.table import Table as AstroTable
from astropy.io import fits
from django.conf import settings
import os


import numpy as np

def export_votable(request, obs_id):
    # Retrieve the observation object
    observation = get_object_or_404(Observation, obs_id=obs_id)
    
    # Construct the full path to the FITS file
    fits_file_path = os.path.join(settings.FITS_DIR, observation.filename)
    
    # Check if the FITS file exists
    if not os.path.exists(fits_file_path):
        return HttpResponse(f"FITS file '{observation.filename}' not found.", status=404)
    
    # Open the FITS file and extract header information
    with fits.open(fits_file_path) as hdul:
        header = hdul[0].header
        date_obs = header.get('DATE-OBS', 'N/A')
        instrument = header.get('INSTRUME', 'Unknown')
        temperature = header.get('TEMPERAT', np.nan)
        exposure_time = header.get('EXPTIME', np.nan)
        ra = header.get('RA', 'N/A')
        dec = header.get('DEC', 'N/A')
    
    # Create VOTable structure
    votable = VOTableFile()
    resource = Resource()
    votable.resources.append(resource)
    votable_table = Table(votable)
    resource.tables.append(votable_table)
    
    # Define table fields
    fields = [
        ('date_obs', 'char', 'Date and time of the observation'),
        ('instrument', 'char', 'Instrument used for the observation'),
        ('temperature', 'float', 'Camera temperature in Celsius'),
        ('exposure_time', 'float', 'Exposure time in seconds'),
        ('ra', 'char', 'Right Ascension'),
        ('dec', 'char', 'Declination')
    ]
    
    for field_name, datatype, description in fields:
        arraysize = "*" if datatype == 'char' else None
        votable_table.fields.append(Field(votable, name=field_name, datatype=datatype, arraysize=arraysize, description=description))
    votable_table.create_arrays(1)  # Create a table with one row
    
    # Populate table data with FITS header information
    votable_table.array[0] = (
        date_obs,
        instrument,
        temperature,
        exposure_time,
        ra,
        dec
    )
    
    # Create HTTP response with VOTable XML
    response = HttpResponse(content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="observation_{obs_id}.xml"'
    votable.to_xml(response)
    
    return response

class Catalog(TemplateView):
    template_name = 'catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve query parameters
        search_query = self.request.GET.get('search', '')
        selected_classification = self.request.GET.get('classification', '')
        order_by_date = self.request.GET.get('order', 'desc')  # Default to descending order

        # Filter asteroids based on search and classification
        queryset = Asteroid.objects.all()

        if search_query:
            queryset = queryset.filter(
                Q(provisional_name__icontains=search_query) |
                Q(official_name__icontains=search_query) |
                Q(target_description__icontains=search_query) |
                Q(target_class__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        if selected_classification:
            queryset = queryset.filter(target_class=selected_classification)

        # Apply sorting based on the order_by_date option
        if order_by_date == 'asc':
            queryset = queryset.order_by('target_discovery_date')
        else:
            queryset = queryset.order_by('-target_discovery_date')

        # Get unique classification choices from the database, handle NoneType values, and remove duplicates
        classifications = (
            Asteroid.objects.values_list('target_class', flat=True)
            .distinct()
        )
        classifications = sorted(
            {cls if cls is not None else "Undefined" for cls in classifications}
        )

        context['asteroids'] = queryset
        context['search_query'] = search_query
        context['selected_classification'] = selected_classification
        context['classifications'] = classifications
        context['order_by_date'] = order_by_date
        return context

class AsteroidDetail(TemplateView):
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Use 'provisional_name' to get the asteroid instance
        asteroid = get_object_or_404(Asteroid, provisional_name=self.kwargs['target_name'])

        context['asteroid'] = asteroid
        context['observations'] = asteroid.observations.all()
        return context