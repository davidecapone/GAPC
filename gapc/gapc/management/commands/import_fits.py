import os
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from gapc.models import Asteroid, Observation, Instrument
from astropy.io import fits
from datetime import datetime
from django.utils import timezone

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
        
        # Check if the FITS directory is empty
        if not os.listdir(settings.FITS_DIR):
            logger.info(f"Directory '{settings.FITS_DIR}' is empty!")
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
            logger.info(f"'{asteroid}' created!") if created else logger.info(f"'{asteroid}' already exists...")
            
            fits_file_path = os.path.join(settings.FITS_DIR, filename)

            with fits.open(fits_file_path) as hdul:
                header = hdul[0].header
                data = hdul[0].data

                if 'DATE-OBS' not in header:
                    logger.error(f"DATE-OBS header keyword not found in {filename}")
                    continue

                # Parse the DATE-OBS header keyword                
                datetime_obs = self.parse_date_obs_str(
                    header.get('DATE-OBS')
                )
                datetime_obs = timezone.make_aware(
                    datetime_obs, 
                    timezone.get_current_timezone()
                )

                # Update discovery date if needed
                if not asteroid.target_discovery_date or datetime_obs < asteroid.target_discovery_date:
                    asteroid.target_discovery_date = datetime_obs
                    asteroid.save()

                # Extract other observation data
                exposure_time = header.get('EXPTIME', 0.0)
                instrument_name = header.get('INSTRUME', 'Unknown')
                ra_str = header.get('RA', '00:00:00.0')
                dec_str = header.get('DEC', '00:00:00.0')
                temperature = header.get('TEMPERAT', None)
                temperature = round(temperature, 3) if temperature else None

                if instrument_name == 'Unknown':
                    instrument_name = "Alta U9000"

                # Get or create the instrument entry in the database
                instrument, inst_created = Instrument.objects.get_or_create(
                    name=instrument_name,
                    defaults={
                        'manufacturer': "Apogee Imaging Systems",  # Set default manufacturer if needed
                        'max_exposure_time': 60000.0,  # Default values (update based on actual specs)
                        'min_exposure_time': 1.0,
                        'pixel_size': "12 x 12 microns"
                    }
                )

                if inst_created:
                    logger.info(f" '{instrument}' created with default values.")
                else:
                    logger.info(f" '{instrument}' already exists.")

                # Check if observation exists based on asteroid and datetime_obs
                observation, obs_created = Observation.objects.get_or_create(
                    asteroid=asteroid,
                    date_obs=datetime_obs,
                    defaults={
                        'instrument': instrument,
                        'exposure_time': exposure_time,
                        'ra': ra_str,
                        'dec': dec_str,
                        'filename': filename,
                        'temperature': temperature
                    }
                )

                if obs_created:
                    logger.info(f" '{observation}' created!")
                else:
                    logger.info(f" '{observation}' already exists...")


    def parse_date_obs_str(self, date_obs_str: str) -> datetime:
        date_formats = [
            '%Y-%m-%dT%H:%M:%S.%f',  # 'yyyy-mm-ddTHH:MM:SS.sss'
            '%Y-%m-%dT%H:%M:%S',     # 'yyyy-mm-ddTHH:MM:SS'
            '%Y-%m-%d',              # 'yyyy-mm-dd'
            '%y/%m/%d'               # 'yy/mm/dd' (deprecated format)
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(date_obs_str, date_format)
            except ValueError:
                pass

        logger.error(f"Unrecognized DATE-OBS format: {date_obs_str}")
        raise ValueError(f"Unrecognized DATE-OBS format: {date_obs_str}")