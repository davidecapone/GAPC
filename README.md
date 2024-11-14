# GAPC - Asteroid Observation Catalog

<p align="center" width="100%">
    <img src="assets/gapc.png" width="200" />
</p>

GAPC is a Django-based application designed to manage and catalog observations of asteroids, including metadata from associated FITS files. The project implements astronomical standards, such as VOTable, to facilitate interoperability with other astronomical datasets and tools. GAPC allows users to explore a catalog of asteroids, retrieve observation data, and download metadata in VOTable format, supporting linked open data principles.

## Table of Contents
- [GAPC - Asteroid Observation Catalog](#gapc---asteroid-observation-catalog)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Data standards](#data-standards)
  - [Project Structure](#project-structure)
  - [Installation](#installation)

---

## Features

- **Asteroid Catalog Management**: Maintain and manage a catalog of asteroids with metadata, including discovery dates, classification, and size.
- **Observation Tracking**: Store detailed observations of each asteroid, including date, right ascension (RA), declination (Dec), exposure time, and instrument used.
- **Instrument Integration**: Define instruments (e.g., cameras) with specific metadata, ensuring consistency in observation details.
- **FITS Metadata Extraction**: Automatically extract metadata from FITS files for each observation and store it in the database.
- **VOTable Export**: Export observation data in VOTable format for compatibility with IVOA-compliant tools, supporting interoperability.
- **Search and Filter**: Filter and search the catalog by asteroid name, classification, and discovery date, with ordering options.

---
## Data standards
This project adheres to the following data standards:
- VOTable: The observation data can be exported in VOTable format, providing interoperability with IVOA-compliant tools.
- FITS Metadata Extraction: Metadata from FITS headers (such as DATE-OBS, EXPTIME, RA, DEC) is automatically parsed and stored with each observation.
- Linked Open Data Principles: The catalog is structured to support linked data standards for discoverability and openness.
---

## Project Structure

The main components of the project include:

- `models.py`: Defines database models for asteroids, observations, and instruments.
- `views.py`: Contains the logic for rendering the catalog, filtering, and exporting data.
- `management/commands`: Custom management commands for importing FITS files and processing metadata.
- `templates`: HTML templates for the front-end, including catalog listing, asteroid details, and export options.


---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/GAPC.git
   cd GAPC
   ```

2. **Set up a virtual environment (recommended)**:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   FITS_DIR=/path/to/your/fits/files
   SECRET_KEY=your_secret_key
   ```

5. **Run migrations and start the server**:
   ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
   ```

