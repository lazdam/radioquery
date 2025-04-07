from astropy.coordinates import SkyCoord
from astropy import units as u
import os
import requests
import warnings

class NvssQuery:
    def __init__(self, coord: SkyCoord, download_path: str, size_arcmin: float, overwrite: bool = False):
        self.coord = coord
        self.download_path = download_path
        self.size_arcmin = size_arcmin
        self.overwrite = overwrite

    def format_coord_for_query(self) -> str:
        """Formats the coordinate for NVSS image query as 'RA','DEC' string with no delimiters."""
        # Format the RA as hours with 2 decimal places for seconds
        ra_str = self.coord.ra.to_string(unit=u.hour, sep=" ", precision=2)
        
        # Format the Dec with a sign and 2 decimal places for seconds
        dec_str = self.coord.dec.to_string(unit=u.deg, sep=" ", precision=2, alwayssign=True)
        
        return f"{ra_str}", f"{dec_str}"
    
    def format_coord_for_saving(self) -> str: 
        # Format the RA as hours with 2 decimal places for seconds
        ra_str = self.coord.ra.to_string(unit=u.hour, sep="", precision=2)
         # Format the Dec with a sign and 2 decimal places for seconds
        dec_str = self.coord.dec.to_string(unit=u.deg, sep="", precision=2, alwayssign=True)

        return f"J{ra_str}{dec_str}"

    def download_image(self) -> str:
        """Query the NVSS cutout service and download the image as a FITS file using a POST request."""
            
        base_url = 'https://www.cv.nrao.edu/cgi-bin/postage.pl'
        ra_str,dec_str = self.format_coord_for_query()
        file_path = os.path.join(self.download_path, f"NVSS_{self.format_coord_for_saving()}.fits")
        
        download=False
        # Check if file already exists. If it does, make sure that overwrite is set to True.
        if (os.path.exists(file_path) and self.overwrite): 
            download=True
            print("File exists but overwrite set to true, will re-download!")

        if not os.path.exists(file_path): 
            print("File does not exist. Beginning download...")
            download=True
        
        if os.path.exists(file_path) and not self.overwrite: 
            print(f"File already exists at {file_path}. Set overwrite to TRUE if you want to re-download.")
            download=False
        
        if download: 
            # Form data payload, adjust these values accordingly
            payload = {
                'Equinox': 'J2000',
                'PolType': 'I',          # Stokes I polarization
                'ObjName': '',
                'RA': ra_str,            # Right Ascension (hh mm ss.ss)
                'Dec': dec_str,          # Declination (dd mm ss.ss)
                'Size': f'{self.size_arcmin/60} {self.size_arcmin/60}', # Desired image size (degrees)
                'Cells': '2.0 2.0',             # Pixel spacing (arcseconds)
                'Type': 'image/x-fits'         # FITS or JPEG
            }
            print("Submitting the following POST parameters:")
            for key, value in payload.items():
                print(f"{key}:{value}")
            response = requests.get(base_url, params=payload)
            
            if response.status_code == 200:
                os.makedirs(self.download_path, exist_ok=True)
                
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
