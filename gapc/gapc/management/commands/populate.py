"""
This script is a Django management command that imports FITS (Flexible Image Transport System) files 
from a specified directory into the Django database. For each FITS file, it extracts relevant metadata 
(e.g., observation date, instrument used, exposure time, and temperature) and creates or updates database 
records for asteroids, observations, and instruments.

Processed files are moved to a 'processed' folder within the input directory to prevent duplicate imports. 
The script also allows users to specify a custom input directory using the '--input' argument.
"""
import os
import logging
import shutil

from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from gapc.models import Asteroid, Observation, Instrument
from astropy.io import fits

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Supported FITS file extensions
SUPPORTED_FITS_EXTENSIONS = ('fits', 'fit')

class Command(BaseCommand):
    help = 'Import FITS files from media/fits folder to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            default=settings.FITS_DIR,
            help='Path to the directory containing FITS files (defaults to settings.FITS_DIR)'
        )


    def handle(self, *args, **options):
        """Main handler function to start the FITS import process."""
        fits_dir = options['input']

        # Create a 'processed' directory to move processed files
        processed_dir = os.path.join(fits_dir, 'processed')
        os.makedirs(processed_dir, exist_ok=True)

        if not os.path.isdir(fits_dir) or not os.listdir(fits_dir):
            logger.info(f"Directory '{fits_dir}' does not exist or is empty!")
            return

        logger.info(f"Starting FITS file import from '{fits_dir}'")
        self.import_fits_files(fits_dir, processed_dir)
        logger.info("FITS file import completed!")


    def import_fits_files(self, directory, processed_dir):
        """Iterates over FITS files in the directory and processes them."""
        for filename in os.listdir(directory):
            if filename.lower().endswith(SUPPORTED_FITS_EXTENSIONS):
                # Process the FITS file
                self.process_fits_file(
                    os.path.join(directory, filename)
                )
                # Move the processed file to the 'processed' directory
                shutil.move(
                    os.path.join(directory, filename),
                    os.path.join(processed_dir, filename)
                )
            else:
                logger.debug(f"Skipped non-FITS file: {filename}")

    def process_fits_file(self, fits_file_path):
        """Processes a single FITS file."""
        asteroid_name = self.get_asteroid_name_from_filename(fits_file_path)
        asteroid = self.get_or_create_asteroid(asteroid_name)

        with fits.open(fits_file_path) as hdul:
            header = hdul[0].header
            date_obs = self.parse_date_obs(header.get('DATE-OBS'))
            if date_obs is None:
                logger.error(f"Invalid DATE-OBS value in {fits_file_path}")
                return
        
            self.create_or_update_observation(header, asteroid, date_obs, fits_file_path)

    def get_asteroid_name_from_filename(self, filename):
        """Extracts the asteroid name from the filename."""
        return os.path.basename(filename).split('_')[0]

    def get_or_create_asteroid(self, name):
        """Retrieves or creates an asteroid instance by name."""
        asteroid, created = Asteroid.objects.get_or_create(target_name=name)
        if created:
            logger.info(f"Created asteroid: {name}")
        return asteroid
    
    def get_or_create_instrument(self, name):
        """Retrieves or creates an instrument instance."""
        if name == 'Unknown':
            name = "Alta U9000"  # Default instrument if unknown

        instrument, created = Instrument.objects.get_or_create(
            name=name,
            defaults={
                'manufacturer': "Apogee Imaging Systems",  
                'max_exposure_time': 60000.0,  
                'min_exposure_time': 1.0,
                'pixel_size': "12 x 12 microns"
            }
        )

        if created:
            logger.info(f"Created instrument with default values: {instrument}")
        return instrument

    def create_or_update_observation(self, header, asteroid, date_obs, filename):
        """Creates or updates an observation based on FITS header data."""
        instrument = self.get_or_create_instrument(header.get('INSTRUME', 'Unknown'))
        observation, created = Observation.objects.get_or_create(
            asteroid=asteroid,
            date_obs=date_obs,
            defaults={
                'instrument': instrument,
                'exposure_time': header.get('EXPTIME', 0.0),
                'ra': header.get('RA', '00:00:00.0'),
                'dec': header.get('DEC', '00:00:00.0'),
                'filename': os.path.basename(filename),
                'temperature': self.get_rounded_temperature(header.get('TEMPERAT')),
            }
        )
        if created:
            logger.info(f"Created observation: {observation}")
        else:
            logger.info(f"Observation already exists for date: {date_obs}")

    def get_rounded_temperature(self, temp):
        """Rounds the temperature to three decimals if present."""
        return round(temp, 3) if temp is not None else None
    
    def parse_date_obs(self, date_obs_str):
        """Parses the DATE-OBS field into a timezone-aware datetime object."""
        if not date_obs_str:
            return None
        for date_format in ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%y/%m/%d']:
            try:
                datetime_obj = datetime.strptime(date_obs_str, date_format)
                return timezone.make_aware(datetime_obj, timezone.get_current_timezone())
            except ValueError:
                continue
        logger.error(f"Unrecognized DATE-OBS format: {date_obs_str}")
        return None