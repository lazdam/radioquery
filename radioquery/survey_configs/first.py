from astropy.coordinates import SkyCoord
from astropy import units as u
import os
import requests
import warnings

class FirstQuery:
    def __init__(self, coord: SkyCoord, download_path: str, size_arcmin: float):
        self.coord = coord
        self.download_path = download_path
        self.size_arcmin = size_arcmin

    def format_coord_for_query(self) -> str:
        """Formats the coordinate for FIRST image query as 'RA+DEC' string with no delimiters."""
        # Format the RA as hours with 2 decimal places for seconds
        ra_str = self.coord.ra.to_string(unit=u.hour, sep=" ", precision=2)
        
        # Format the Dec with a sign and 2 decimal places for seconds
        dec_str = self.coord.dec.to_string(unit=u.deg, sep=" ", precision=2, alwayssign=True)
        
        return f"{ra_str} {dec_str}"
    
    def format_coord_for_saving(self) -> str: 
        # Format the RA as hours with 2 decimal places for seconds
        ra_str = self.coord.ra.to_string(unit=u.hour, sep="", precision=2)
         # Format the Dec with a sign and 2 decimal places for seconds
        dec_str = self.coord.dec.to_string(unit=u.deg, sep="", precision=2, alwayssign=True)

        return f"J{ra_str}{dec_str}"

    def download_image(self) -> str:
        """Query the FIRST cutout service and download the image as a FITS file using a POST request."""
            
        base_url = "https://third.ucllnl.org/cgi-bin/firstcutout"
        coord_str = self.format_coord_for_query()
        # Prepare the form fields exactly as expected by the service:
        params = {
            "RA": coord_str,            # RA field contains both RA and Dec
            "Dec": "",               # Dec field is hidden and left empty
            "Equinox": "J2000",      # Default equinox
            "ImageSize": str(int(self.size_arcmin)),  # Image size in arcminutes
            "ImageType": 'FITS File',       # Must be "FITS File" to get the raw FITS file
            "MaxInt": 10,  # Maximum intensity for scaling
            "Epochs": "",            # Hidden field (left empty)
            "Fieldname": "",         # Hidden field (left empty)
            ".cgifields": "ImageType"  # Tells the server which field is being used for image type
        }
        print("Submitting the following POST parameters:")
        for key, value in params.items():
            print(f"{key}:{value}")
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            os.makedirs(self.download_path, exist_ok=True)
            file_path = os.path.join(self.download_path, f"FIRST_{self.format_coord_for_saving()}.fits")
            with open(file_path, "wb") as f:
                f.write(response.content)
            if not self.check_filesize(file_path): 
                print(f"Download successful, file saved as '{file_path}'")
            else: 
                os.remove(file_path)
                OSError("Error downloading cutout. Filesize was very small (<1KB), likely no data exists for this field.")
        else:
            raise OSError("Error downloading cutout. HTTP status code:", response.status_code)
        
        if os.path.exists(file_path): 
            return file_path, 1
        else: 
            return file_path, 0

    def check_filesize(self, file_path: str) -> None:
        """Check the size of the downloaded file and warn if it's less than 1 KB."""
        file_size = os.path.getsize(file_path)
        if file_size < 1024:  # 1 KB = 1024 bytes
            warnings.warn(
                f"Warning: Downloaded file size is {file_size} bytes, which is less than 1 KB. "
                "This might indicate an incomplete or erroneous download.",
                UserWarning
            )
            return 1
        else: 
            return 0
