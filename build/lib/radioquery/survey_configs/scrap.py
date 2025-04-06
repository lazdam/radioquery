from astropy.coordinates import SkyCoord 
from radioquery.survey_configs.first import FirstQuery
import os

# Define a target coordinate (ICRS)
coord = SkyCoord(ra='10h50m07.270s', dec='-30d40m37.52s', frame='icrs')

# Set the download path (the ~ will be expanded to your home directory)
download_path = os.path.expanduser("~/RQUERY/FIRST")

# Create an instance of FirstQuery with a 5 arcmin image size
fq = FirstQuery(coord=coord, download_path=download_path, size_arcmin=5)

# Download the image and get the file path
file_path, success = fq.download_image()

print('Success:', success)