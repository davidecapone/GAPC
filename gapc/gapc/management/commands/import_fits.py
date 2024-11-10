import os
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from gapc.models import Asteroid
from astropy.io import fits
from datetime import datetime

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

        # Loop through all files in the FITS directory
        for filename in os.listdir(settings.FITS_DIR):

            if not filename.endswith(('fits', 'fit')):
                continue

            # Extract the asteroid name from the filename
            asteroid_name = filename.split('_')[0]

            # Get or create the asteroid entry in the database
            asteroid, created = Asteroid.objects.get_or_create(
                target_name=asteroid_name
            )

            if created:
                logger.info(f"Asteroid '{asteroid_name}' created!")
            else:
                logger.info(f"Asteroid '{asteroid_name}' already exists!")
            
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
                
                date_obs = self.parse_date_obs_str(header.get('DATE-OBS'))

                if not asteroid.target_discovery_date:
                    # If the asteroid discovery date is not set, set it to the observation date
                    asteroid.target_discovery_date = self.parse_date_obs_str(header['DATE-OBS'])
                    asteroid.save()

                if date_obs < asteroid.target_discovery_date:
                    # If the observation date is earlier than the discovery date, update the discovery date
                    asteroid.target_discovery_date = date_obs
                    asteroid.save()

    def parse_date_obs_str(self, date_obs_str: str) -> datetime:
        date_formats = [
            '%Y-%m-%dT%H:%M:%S.%f',  # 'yyyy-mm-ddTHH:MM:SS.sss'
            '%Y-%m-%dT%H:%M:%S',     # 'yyyy-mm-ddTHH:MM:SS'
            '%Y-%m-%d',              # 'yyyy-mm-dd'
            '%y/%m/%d'               # 'yy/mm/dd' (deprecated format)
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(date_obs_str, date_format).date()
            except ValueError:
                pass

        logger.error(f"Unrecognized DATE-OBS format: {date_obs_str}")
        raise ValueError(f"Unrecognized DATE-OBS format: {date_obs_str}")