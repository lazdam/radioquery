from astropy.coordinates import SkyCoord,Angle
import astropy.units as u
from radioquery.survey_configs.vlass import VlassQuery  # Adjust this import if your module is in a subpackage

def test_find_nearest_file(tmp_path):
    """
    Test that find_nearest_file returns the expected file name from a dummy configuration.
    """
    # Create a temporary configuration file with several candidate lines.
    config_data = """
[IMG] J105000+300000_qle123Imedian.fits 2025-02-17 08:35 106M
[IMG] J105047+303000_qle123Imedian.fits 2025-02-17 08:35 106M
[IMG] J095000+250000_qle123Imedian.fits 2025-02-17 08:35 106M
"""
    config_file = tmp_path / "filtered_medians.txt"
    config_file.write_text(config_data)
    
    # Set a query coordinate that should select the second candidate.
    query_coord = SkyCoord(ra='10h50m07.270s', dec='30d40m37.52s', frame='icrs')
    download_path = str(tmp_path / "downloads")
    vq = VlassQuery(coord=query_coord, download_path=download_path, overwrite=True)
    
    best_file, sep = vq.find_nearest_file(config_path=str(config_file))
    
    # Expect that the candidate with RA "105047" and Dec "+303000" is chosen.
    assert best_file == "J105047+303000_qle123Imedian.fits"
    # Also, the separation (in degrees) should be a Quantity less than 1 degree.
    assert sep.deg < 1.0


def test_download_image_no_download(monkeypatch, tmp_path):
    """
    Test download_image when the separation is above the threshold.
    In this case, _download_file should not be called and download_image returns None.
    """
    dummy_filename = "dummy_file.fits"
    dummy_sep = Angle(3.0*u.deg) # Above max threshold

    def fake_find_nearest_file(config_path=""):
        return dummy_filename, dummy_sep

    def fake_download_file(name_of_file, base_url=''):
        # This should not be called.
        return str(tmp_path / name_of_file)

    query_coord = SkyCoord(ra='10h50m07.270s', dec='30d40m37.52s', frame='icrs')
    download_path = str(tmp_path / "downloads")
    vq = VlassQuery(coord=query_coord, download_path=download_path, overwrite=True)

    monkeypatch.setattr(vq, "find_nearest_file", fake_find_nearest_file)
    monkeypatch.setattr(vq, "_download_file", fake_download_file)

    # Call download_image with a max_sep less than dummy_sep so no download should occur.
    result = vq.download_image(max_sep=2.5)
    # When separation exceeds max_sep, download_image does not call _download_file and returns None.
    assert result[1] == 0
