# RadioQuery

RadioQuery is a Python package designed for querying radio survey images such as FIRST and VLASS. This package is organized into survey-specific modules and provides an easy-to-use interface for downloading FITS files.

## Installation

**Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/radioquery.git
   cd radioquery
   pip install .
```
Note: During installation, the following directories will be created automatically in your home directory:

    ~/RQUERY/FIRST

    ~/RQUERY/VLASS

    ~/RQUERY/tests

The root path can be updated in `setup.py` prior to installation. 
## Requirements

    Python 3.x
    astropy >=6.0.1
    requests
    numpy <2
    pytest


# Example Usage: FIRST Survey
Below is an example of how to use the FirstQuery class from the survey_configs.first module to download a FITS file from the FIRST survey:
```
from astropy.coordinates import SkyCoord 
from radioquery.survey_configs.first import FirstQuery
import os

# Define a target coordinate (ICRS)
coord = SkyCoord(ra='10h50m07.270s', dec='30d40m37.52s', frame='icrs')

# Set the download path (the ~ will be expanded to your home directory)
download_path = os.path.expanduser("~/RQUERY/FIRST")

# Create an instance of FirstQuery with a 5 arcmin image size
fq = FirstQuery(coord=coord, download_path=download_path, size_arcmin=5)

# Download the image and get the file path
file_path = fq.download_image()
print("Downloaded FITS file saved at:", file_path)
```

A typical `FIRST` fitsfile is << 1 MB for a 5 arcmin cutout. The script automatically queries https://third.ucllnl.org/cgi-bin/firstcutout and downloads the file to the specified download path. The sample `FITS` file should show something like the following: 

<img src="images/sample_first.png" alt="RadioQuery FIRST" width="200" height="200">


# Directory Structure
After insallation, the structure of the repository should be the following: 
```graphql
radioquery/
├── radioquery/             
│   ├── __init__.py         
│   ├── survey_configs/
│   │   ├── __init__.py
│   │   ├── first.py
│   │   └── vlass.py # Comming soon!
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── setup.py
├── requirements.txt
└── README.md
