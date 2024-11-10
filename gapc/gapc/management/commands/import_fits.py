import os
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from astropy.io import fits

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import FITS files from media/fits folder to database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        # Check if the FITS directory exists
        if not os.path.exists(settings.FITS_DIR):
            logger.error(f"Directory '{settings.FITS_DIR}' does not exist!")
            return

        logger.info(f"Importing FITS files from '{settings.FITS_DIR}'!")

        for filename in os.listdir(settings.FITS_DIR):

            if not filename.endswith(('fits', 'fit')):
                continue

            logger.info(f'Importing {filename}')

            # Extract the asteroid name from the filename
            asteroid_name = filename.split('_')[0]
            
            # Open the FITS file
            with fits.open(os.path.join(settings.FITS_DIR, filename)) as hdul:
                header = hdul[0].header
                data = hdul[0].data

                # 1 - Extract the asteroid name and other metadata
                # 2 - Get or create asteroid entry in database
                # 3 - Create a new observation entry in the database
                # 4 - Save the observation entry in the database
                # 5 - Save the FITS file in the media folder
                # 6 - Close the FITS file
