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

            # Check the file extension
            if not filename.endswith(('fits', 'fit')):
                continue

            # Assuming the asteroid name is the first part of the filename
            asteroid_name = filename.split('_')[0]

            # Get or create the asteroid entry in the database
            asteroid, created = Asteroid.objects.get_or_create(
                target_name=asteroid_name
            )

            # Log the creation of the asteroid entry
            logger.info(f"Asteroid '{asteroid_name}' created!") if created else logger.info(f"Asteroid '{asteroid_name}' already exists...")
            
            # Open the FITS file
            with fits.open(os.path.join(settings.FITS_DIR, filename)) as hdul:
                header = hdul[0].header
                data = hdul[0].data

                if 'DATE-OBS' not in header:
                    logger.error(f"DATE-OBS header keyword not found in {filename}")
                    continue

                # Parse the DATE-OBS header keyword                
                date_obs = self.parse_date_obs_str(header.get('DATE-OBS'))

                # Update the target_discovery_date if it is not set 
                if not asteroid.target_discovery_date:
                    asteroid.target_discovery_date = date_obs
                    asteroid.save()
                # Update the target_discovery_date if the new date is earlier
                if date_obs < asteroid.target_discovery_date:
                    asteroid.target_discovery_date = date_obs
                    asteroid.save()


                # Create an observation entry in the database
                exposure_time = header.get('EXPTIME', 0.0)
                instrument_name = header.get('INSTRUME', 'Unknown')

                observation, obs_created = Observation.objects.get_or_create(
                    obs_id=obs_id,
                    asteroid=asteroid,
                    date_obs=date_obs,
                    instrument_name=instrument_name,
                    exposure_time=exposure_time
                )

                

                

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