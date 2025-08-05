# tests/test_first.py

import os
import pytest
from astropy.coordinates import SkyCoord
from radioquery.survey_configs.lotss import LotssQuery
from astropy.io import fits
from numpy.testing import assert_array_equal
import numpy as np

@pytest.fixture
def test_coord():
    return SkyCoord(ra='10h50m07.270s', dec='30d40m37.52s', frame='icrs')
	
@pytest.fixture
def download_path():
    base_path = os.path.expanduser("~/RQUERY/tests")
    os.makedirs(base_path, exist_ok=True)
    return base_path

def assert_array_different(a, b):
    if np.array_equal(a, b):
        raise AssertionError("Arrays are equal but were expected to be different.")

def test_create_rquery_directories():
    """Ensure required directory structure is created."""
    base_dir = os.path.expanduser("~/RQUERY")
    lotss_path = os.path.join(base_dir, "LOTSS")
    assert os.path.isdir(lotss_path)

def test_create_rquery_test_dir():
    """Ensure required directory structure is created."""
    base_dir = os.path.expanduser("~/RQUERY/tests/full_image/")

    os.makedirs(base_dir, exist_ok=True)

    assert os.path.isdir(base_dir)
    

def test_first_download_full(test_coord): 
    """Test full download of a fitsfile."""
    download_path_full='~/RQUERY/tests/full_image/'
    full_path = os.path.expanduser(download_path_full)
    lq = LotssQuery(coord=test_coord, download_path=full_path, size_arcmin=5, overwrite=True)
    file_path, success = lq.download_image()

    assert os.path.isfile(file_path)

    # Path to the dataset FITS file (relative to this test file)
    test_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(test_dir, "datasets", "LOTSS_J105007.27+304037.52.fits")

    # Check that both files are the same
    with fits.open(file_path) as downloaded, fits.open(dataset_path) as expected:
        # Compare primary HDU data
        print('Comparing downloaded file to expected file...')
        assert_array_equal(downloaded[0].data, expected[0].data)

        


