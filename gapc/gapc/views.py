# gapc/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse, Http404
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from .models import Asteroid, Observation
from datetime import datetime
from urllib.parse import urljoin


from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from .models import Asteroid

from astropy.io.votable.tree import VOTableFile, Resource, Table, Field
from astropy.table import Table as AstroTable
from astropy.io import fits
from django.conf import settings
import os
from django.contrib.auth.decorators import login_required

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy as np

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from astropy.io import fits
from io import BytesIO
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting
import matplotlib.pyplot as plt
import base64
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def preview_fits_image(request, filename):
    """
    Render a page to preview a given FITS file as an image.
    """
    # Construct the full path to the FITS file
    fits_file_path = os.path.join(settings.FITS_DIR, 'processed', filename)

    # Check if the FITS file exists
    if not os.path.exists(fits_file_path):
        raise Http404(f"FITS file '{filename}' not found.")

    try:
        # Open the FITS file
        with fits.open(fits_file_path) as hdul:
            data = hdul[0].data  # Assume the image data is in the first HDU
            if data is None:
                raise ValueError("No image data found in FITS file.")

            # Normalize the data for display
            #data = np.log10(data - np.min(data) + 1)

            # Generate the image using Matplotlib
            plt.figure(figsize=(8, 8))  # Optional: Adjust figure size
            plt.imshow(data, cmap='gray', origin='lower')
            plt.axis('off')  # Remove axes for cleaner image
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0)
            plt.close()  # Close the figure to free resources
            buffer.seek(0)
            image_data = buffer.getvalue()

        # Encode the image as base64 for rendering in HTML
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        return render(request, 'fits_preview.html', {'image_data': encoded_image, 'filename': filename})

    except Exception as e:
        logger.error(f"Error generating preview for FITS file '{filename}': {e}")
        return HttpResponse("Error generating preview for FITS file.", status=500)
    
def download_fits(request, filename):
    """ Download a processed FITS file. """
    
    if '..' in filename or '/' in filename or '\\' in filename:
        raise Http404("Invalid file name.")
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'fits/processed', filename)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/fits')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        raise Http404(f"FITS file '{filename}' not found.")

def export_votable(request, obs_id):
    """
    Export an observation as a VOTable with metadata, including semantic annotations (UCDs) and descriptions.
    """
    # Retrieve the observation object
    observation = get_object_or_404(Observation, obs_id=obs_id)
    
    # Construct the full path to the FITS file
    fits_file_path = os.path.join(settings.FITS_DIR, 'processed', observation.filename)

    # Log debug information
    logger.info(f"Attempting to export VOTable for FITS file at: {fits_file_path}")
    
    # Check if the FITS file exists
    if not os.path.exists(fits_file_path):
        logger.error(f"File not found: {fits_file_path}")
        return HttpResponse(f"FITS file '{observation.filename}' not found in the processed directory.", status=404)

    try:
        # Open the FITS file and extract header information
        with fits.open(fits_file_path) as hdul:
            header = hdul[0].header

            date_obs = header.get('DATE-OBS', 'N/A')
            naxis1 = header.get('NAXIS1', 'N/A')
            naxis2 = header.get('NAXIS2', 'N/A')
            temperature = header.get('TEMPERAT', 'N/A')
            exptime = header.get('EXPTIME', 'N/A')
            exposure = header.get('EXPOSURE', 'N/A')
            ra = header.get('RA', 'N/A')
            dec = header.get('DEC', 'N/A')

    except Exception as e:
        logger.error(f"Error reading FITS file header: {e}")
        return HttpResponse("Error processing the FITS file header.", status=500)

    # Create the VOTable structure
    votable = VOTableFile()
    resource = Resource()
    votable.resources.append(resource)
    votable_table = Table(votable)
    resource.tables.append(votable_table)
    
    # Define table fields with UCDs and detailed descriptions
    fields = [
        {
            'name': 'date_obs',
            'datatype': 'char',
            'ucd': 'time.start',
            'description': 'The starting date and time of the observation in ISO 8601 format'
        },
        {
            'name': 'naxis1',
            'datatype': 'int',
            'ucd': 'meta.number',
            'description': 'The number of pixels along the x-axis (image width)'
        },
        {
            'name': 'naxis2',
            'datatype': 'int',
            'ucd': 'meta.number',
            'description': 'The number of pixels along the y-axis (image height)'
        },
        {
            'name': 'temperature',
            'datatype': 'float',
            'ucd': 'phys.temperature',
            'description': 'The temperature of the camera sensor in degrees Celsius'
        },
        {
            'name': 'exptime',
            'datatype': 'float',
            'ucd': 'time.duration',
            'description': 'The total exposure time for the observation in seconds'
        },
        {
            'name': 'exposure',
            'datatype': 'float',
            'ucd': 'time.duration',
            'description': 'The effective exposure duration in seconds'
        },
        {
            'name': 'ra',
            'datatype': 'char',
            'ucd': 'pos.eq.ra',
            'description': 'The Right Ascension coordinate of the observation in HH:MM:SS format'
        },
        {
            'name': 'dec',
            'datatype': 'char',
            'ucd': 'pos.eq.dec',
            'description': 'The Declination coordinate of the observation in DD:MM:SS format'
        },
        {
            'name': 'fits_link',
            'datatype': 'char',
            'ucd': 'meta.ref.url',
            'description': 'A URL link to download the associated FITS file for this observation'
        }
    ]
    
    # Populate fields in the VOTable
    for field in fields:
        arraysize = "*" if field['datatype'] == 'char' else None
        votable_field = Field(
            votable, 
            name=field['name'], 
            datatype=field['datatype'], 
            arraysize=arraysize, 
            ucd=field['ucd']
        )
        votable_table.fields.append(votable_field)
        
        # Add description as a child element
        if 'description' in field:
            votable_field.description = field['description']
    
    # Initialize table data
    votable_table.create_arrays(1)  # Create a table with one row
    
    # Populate the table with extracted metadata
    fits_link = f"{request.build_absolute_uri(settings.MEDIA_URL)}fits/processed/{observation.filename}"
    votable_table.array[0] = (
        date_obs,
        naxis1,
        naxis2,
        temperature,
        exptime,
        exposure,
        ra,
        dec,
        fits_link
    )
    
    # Create HTTP response with VOTable XML
    response = HttpResponse(content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="observation_{obs_id}.xml"'
    votable.to_xml(response)
    
    # Log success
    logger.info(f"Successfully generated VOTable for observation {obs_id}")
    
    return response

class Catalog(TemplateView):
    """ Retrieve the catalog of asteroids. """

    template_name = 'catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve query parameters
        search_query = self.request.GET.get('search', '')
        selected_classification = self.request.GET.get('classification', '')

        # Filter asteroids based on search and classification
        queryset = Asteroid.objects.all()

        if search_query:
            queryset = queryset.filter(
                Q(provisional_name__icontains=search_query) |
                Q(official_name__icontains=search_query) |
                Q(target_class__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        if selected_classification:
            queryset = queryset.filter(target_class=selected_classification)


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
        return context

class AsteroidDetail(TemplateView):
    """ Retrieve the observations of a specific asteroid. """

    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asteroid = get_object_or_404(Asteroid, provisional_name=self.kwargs['target_name'])
        context['asteroid'] = asteroid
        context['observations'] = asteroid.observations.all()
        context['MEDIA_URL'] = settings.MEDIA_URL  # Include MEDIA_URL for templates
        return context