import os
import requests
from bs4 import BeautifulSoup
import csv
import logging
from django.conf import settings
from django.core.management.base import BaseCommand

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_FILE = os.path.join(settings.MEDIA_ROOT, 'mappings.csv')

class Command(BaseCommand):
    help = 'Fetch provisional and official asteroid names and save them to a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://www.birtwhistle.org.uk/NEOCPObjects2022.htm',
            help='URL of the page to scrape asteroid names from'
        )
        parser.add_argument(
            '--output',
            type=str,
            default=DEFAULT_OUTPUT_FILE,
            help='Path to the output CSV file (defaults to settings.MEDIA_ROOT/asteroid_mappings.csv)'
        )
        parser.add_argument(
            '--append',
            action='store_true',
            help='Append new mappings to the existing CSV file instead of overwriting it'
        )

    def handle(self, *args, **options):
        url = options['url']
        output_file = options['output']
        append = options['append']

        logger.info(f"Starting to fetch asteroid mappings from {url}...")
        try:
            mappings = self.fetch_designation_mappings(url)
            self.write_to_csv(mappings, output_file, append)
            logger.info(f"Asteroid mappings saved successfully to {output_file}")
        except Exception as e:
            logger.error(f"Error while creating CSV: {e}", exc_info=True)

    def fetch_designation_mappings(self, url):
        """Fetch and parse the provisional to official designation mappings."""
        logger.info(f"Fetching data from URL: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e}", exc_info=True)
            raise

        logger.info("Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()

        mappings = []
        for line in content.splitlines():
            if '=' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    official_name = parts[0].strip()
                    provisional_part = parts[1].strip().split()
                    if provisional_part:
                        provisional_name = provisional_part[0]
                        mappings.append((provisional_name, official_name))
                        logger.debug(f"Mapping added: {provisional_name} -> {official_name}")
        logger.info(f"Total mappings found: {len(mappings)}")
        return mappings

    def write_to_csv(self, mappings, output_file, append):
        """Write the mappings to a CSV file."""
        mode = 'a' if append else 'w'
        logger.info(f"{'Appending' if append else 'Writing'} mappings to {output_file}...")
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the directory exists
            with open(output_file, mode, newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not append or os.stat(output_file).st_size == 0:  # Write header only if not appending or file is empty
                    writer.writerow(['Provisional Name', 'Official Name'])
                writer.writerows(mappings)
        except Exception as e:
            logger.error(f"Failed to write to {output_file}: {e}", exc_info=True)
            raise