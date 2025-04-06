# tests/test_first.py

import os
import pytest
from astropy.coordinates import SkyCoord
from survey_configs.first import FirstQuery
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


def test_format_coord_for_query(test_coord):
    fq = FirstQuery(coord=test_coord, download_path="/tmp", size_arcmin=5.0)
    formatted = fq.format_coord_for_query()
    assert isinstance(formatted, str)
    assert "+" in formatted or "-" in formatted


def test_create_rquery_directories():
    """Ensure required directory structure is created."""
    base_dir = os.path.expanduser("~/RQUERY")
    first_path = os.path.join(base_dir, "FIRST")
    vlass_path = os.path.join(base_dir, "VLASS")

    os.makedirs(first_path, exist_ok=True)
    os.makedirs(vlass_path, exist_ok=True)

    assert os.path.isdir(first_path)
    assert os.path.isdir(vlass_path)

def test_create_rquery_test_dir():
    """Ensure required directory structure is created."""
    base_dir = os.path.expanduser("~/RQUERY/tests/full_image/")

    os.makedirs(base_dir, exist_ok=True)

    assert os.path.isdir(base_dir)
    

def test_first_download_full(test_coord): 
    """Test full download of a fitsfile."""
    download_path_full='~/RQUERY/tests/full_image/'
    full_path = os.path.expanduser(download_path_full)
    fq = FirstQuery(coord=test_coord, download_path=full_path, size_arcmin=5)
    file_path = fq.download_image()

    assert os.path.isfile(file_path)

    # Path to the dataset FITS file (relative to this test file)
    test_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(test_dir, "datasets", "J105007+304037.fits")

    # Check that both files are the same
    with fits.open(file_path) as downloaded, fits.open(dataset_path) as expected:
        # Compare primary HDU data
        print('Comparing downloaded file to expected file...')
        assert_array_equal(downloaded[0].data, expected[0].data)

    # Path to secondary test file, expected to be different patch of sky
    dataset_path = os.path.join(test_dir, "datasets", "J103007+304037.fits")
    # Check that both files are different
    with fits.open(file_path) as downloaded, fits.open(dataset_path) as expected:
        # Compare primary HDU data
        assert_array_different(downloaded[0].data, expected[0].data)
            
        


