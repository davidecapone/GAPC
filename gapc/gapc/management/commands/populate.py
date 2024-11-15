import os
import csv
import logging
import shutil
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from gapc.models import Asteroid, Observation, Instrument
from astropy.io import fits
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPPORTED_FITS_EXTENSIONS = ('fits', 'fit')
MAPPINGS_FILE = os.path.join(settings.MEDIA_ROOT, 'mappings.csv')  # Adjust path as necessary

class Command(BaseCommand):
    help = 'Import FITS files from a specified directory into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            default=settings.FITS_DIR,
            help='Path to the directory containing FITS files (defaults to settings.FITS_DIR)'
        )
        parser.add_argument(
            '--processed',
            type=str,
            default=os.path.join(settings.FITS_DIR, 'processed'),
            help='Path to move processed files (defaults to "processed")'
        )

    def handle(self, *args, **options):
        fits_dir = options['input']
        processed_dir = options['processed']
        os.makedirs(processed_dir, exist_ok=True)

        if not os.path.isdir(fits_dir) or not os.listdir(fits_dir):
            logger.info(f"Directory '{fits_dir}' does not exist or is empty!")
            return

        # Load mappings from CSV
        mappings = self.load_mappings(MAPPINGS_FILE)

        logger.info(f"Starting FITS file import from '{fits_dir}'")
        self.import_fits_files(fits_dir, processed_dir, mappings)
        logger.info("FITS file import completed!")

    def load_mappings(self, mappings_file):
        """Load provisional-to-official name mappings from a CSV file."""
        mappings = {}
        try:
            with open(mappings_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    mappings[row['Provisional Name']] = row['Official Name']
            logger.info(f"Loaded {len(mappings)} asteroid mappings.")
        except FileNotFoundError:
            logger.warning(f"Mappings file '{mappings_file}' not found. All asteroids will be set as 'not_confirmed'.")
        return mappings

    def import_fits_files(self, directory, processed_dir, mappings):
        files = [
            filename for filename in os.listdir(directory)
            if filename.lower().endswith(SUPPORTED_FITS_EXTENSIONS)
        ]

        for filename in tqdm(files, desc="Processing FITS files", unit="file"):
            fits_file_path = os.path.join(directory, filename)
            self.process_fits_file(fits_file_path, mappings)

            shutil.move(fits_file_path, os.path.join(processed_dir, filename))

    def process_fits_file(self, fits_file_path, mappings):
        provisional_name = self.get_provisional_name_from_filename(fits_file_path)
        asteroid = self.get_or_create_asteroid(provisional_name, mappings)

        with fits.open(fits_file_path) as hdul:
            header = hdul[0].header
            date_obs = self.parse_date_obs(header.get('DATE-OBS'))
            if date_obs is None:
                logger.error(f"Invalid DATE-OBS value in {fits_file_path}")
                return

            self.create_or_update_observation(header, asteroid, date_obs, fits_file_path)

    def get_provisional_name_from_filename(self, filename):
        """Extracts the provisional name from the filename."""
        return os.path.basename(filename).split('_')[0]

    def get_or_create_asteroid(self, provisional_name, mappings):
        """Retrieves or creates an asteroid instance, setting the official name if available."""
        official_name = mappings.get(provisional_name)
        status = 'confirmed' if official_name else 'not_confirmed'
        asteroid, created = Asteroid.objects.get_or_create(
            provisional_name=provisional_name,
            defaults={
                'official_name': official_name,
                'status': status
            }
        )
        if created:
            if official_name:
                logger.info(f"Created asteroid: Provisional={provisional_name}, Official={official_name}, Status={status}")
            else:
                logger.info(f"Created asteroid with provisional name: {provisional_name}, Status={status}")
        return asteroid

    def create_or_update_observation(self, header, asteroid, date_obs, filename):
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

    def get_rounded_temperature(self, temp):
        return round(temp, 3) if temp is not None else None

    def parse_date_obs(self, date_obs_str):
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