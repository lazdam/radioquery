from astropy.coordinates import SkyCoord
import astropy.units as u
import os 
import time 
from tqdm import tqdm

class VlassQuery:
    """
    A class for querying VLASS survey images.

    Parameters
    ----------
    coord : SkyCoord
        An Astropy SkyCoord object representing the RA/Dec of the target.
    download_path : str
        The path where any downloaded files will be stored.
    """
    def __init__(self, coord: SkyCoord, download_path: str, overwrite: bool = False):
        self.coord = coord
        self.download_path = download_path
        self.overwrite = overwrite

    def __repr__(self):
        return f"<VlassQuery: {self.coord.to_string()}>"
    
    def find_nearest_file(self, config_path: str = "vlass_configs/filtered_medians.txt") -> str:
        """
        Reads the VLASS configuration file and finds the file whose sky coordinate
        (extracted from its filename) is closest to the query coordinate.
        
        The search is made more efficient by:
          1. Filtering for files whose RA hour (from the filename) matches the query RA hour.
          2. Further filtering for files whose declination (degree part) matches the query declination degree.
          3. Then, computing the angular separation only for this subset.
        
        Parameters
        ----------
        config_path : str
            Path to the VLASS configuration file.
        
        Returns
        -------
        str
            The filename (e.g., "J000200-013000_qle123Imedian.fits") with the minimum separation.
        
        Raises
        ------
        ValueError
            If no file is found in the configuration file.
        """
        # Determine query RA hour and query declination degree as strings.
        query_ra_hour_str = f"{int(self.coord.ra.hour):02d}"
        query_dec_str = f"{'+' if self.coord.dec.deg >= 0 else '-'}{abs(int(self.coord.dec.deg)):02d}"
        
        min_sep = None
        best_file = None
        
        # Ensure the configuration file path is absolute.
        if not os.path.isabs(config_path):
            config_path = os.path.join(os.path.dirname(__file__), config_path)
        print(config_path)
        

        start = time.time()
        with open(config_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue  # Skip empty lines
                
                # Expected line format:
                # [IMG]    J000200-013000_qle123Imedian.fits    2025-02-17 08:35     106M
                parts = line.strip().split()
                if len(parts) < 2:
                    continue  # Skip malformed lines
                
                file_name = parts[1]
                # Extract the coordinate part: assume it starts with "J" and extends to the first underscore.
                coord_part = file_name.split('_')[0]  # e.g., "J000200-013000"
                if coord_part.startswith("J"):
                    coord_part = coord_part[1:]
                else:
                    continue  # Skip unexpected formats
                
                # Expect the first 6 digits for RA and the next 7 characters for Dec (including the sign).
                if len(coord_part) < 13:
                    continue  # Not enough characters for valid coordinates
                
                ra_str = coord_part[:6]    # e.g., "000200"
                dec_str = coord_part[6:13] # e.g., "-013000"
                
                # Preliminary filtering:
                # 1. Check RA hour: first two digits of ra_str.
                file_ra_hour = ra_str[:2]
                if file_ra_hour != query_ra_hour_str:
                    continue  # Skip if the RA hour doesn't match
                
                # 2. Check declination degree: first three characters of dec_str (sign and two digits).
                file_dec_str = dec_str[0] + dec_str[1:3]
                if file_dec_str != query_dec_str:
                    continue  # Skip if the declination degree doesn't match
                
                # Now, for the filtered candidate, build a SkyCoord.
                ra_formatted = f"{ra_str[0:2]}h{ra_str[2:4]}m{ra_str[4:6]}s"
                dec_formatted = f"{dec_str[0]}{dec_str[1:3]}d{dec_str[3:5]}m{dec_str[5:7]}s"
                try:
                    file_coord = SkyCoord(ra=ra_formatted, dec=dec_formatted, frame='icrs')
                except Exception:
                    continue  # Skip lines that don't parse correctly
                
                # Calculate the separation from the query coordinate.
                sep = self.coord.separation(file_coord)
                if (min_sep is None) or (sep < min_sep):
                    min_sep = sep
                    best_file = file_name
        
        stop = time.time()
        print(f'Search Time: {stop - start} seconds.')
        if best_file is None:
            raise ValueError("No valid VLASS file found in the configuration file.")
        
        return best_file, sep

    def _download_file(self, name_of_file: str, base_url: str = 'https://archive-new.nrao.edu/vlass/quicklook/ql_median_stack/') -> str:
        """
        Downloads the specified VLASS file from the base URL and saves it to the download path.
        
        Parameters
        ----------
        name_of_file : str
            The name of the file to download (e.g., 'J105047+303000_qle123Imedian.fits').
        base_url : str, optional
            The base URL where the files are hosted.
        
        Returns
        -------
        str
            The local file path where the file has been saved.
        
        Raises
        ------
        OSError
            If the HTTP request fails.
        """
        import requests
        
        # Construct the full URL for the file.
        url = base_url + name_of_file
        print(f"Downloading from: {url}")

        # Ensure the download directory exists.
        os.makedirs(self.download_path, exist_ok=True)
        file_path = os.path.join(self.download_path, name_of_file)

        download=False
        # Check if file already exists. If it does, make sure that overwrite is set to True.
        if (os.path.exists(file_path) and self.overwrite): 
            download=True
            print("File exists but overwrite set to true, will re-download!")

        if not os.path.exists(file_path): 
            print("File does not exist. Will begin downloading...")
            download=True
        
        if os.path.exists(file_path) and not self.overwrite: 
            print(f"File already exists at {file_path}. Set overwrite to TRUE if you want to re-download.")
            download=False
        
        # Make the HTTP GET request.
        if download: 
            response = requests.get(url)
            if response.status_code != 200:
                raise OSError(f"Error downloading file {name_of_file}. HTTP status code: {response.status_code}")
            else: 
                # Open the file for writing in binary mode.
                # Write the downloaded content to a file.
                with open(file_path, "wb") as f:
                    f.write(response.content)
                    print(f"Successfully downloaded {file_path}")
        else: 
            print("Did not download any file!")

        return file_path

    def download_image(self, max_sep = 2.5):
        """Wrapper for _download_file."""
        best_file,sep = self.find_nearest_file()
        print("Nearest VLASS file:", best_file, ' at a separation of: ',sep, ' from the input coordinate.')
        print(sep,type(sep))
        file_path = None
        if sep.deg < max_sep:
            file_path = self._download_file(best_file)
            return file_path,1
        
        return file_path,0

        


# Example usage:
if __name__ == "__main__":
    # Define a sample target coordinate.
    coord = SkyCoord(ra='10h50m07.270s', dec='30d40m37.52s', frame='icrs')
    download_path = os.path.expanduser("~/RQUERY/VLASS")
    vq = VlassQuery(coord=coord, download_path=download_path,overwrite=False)
    file_path,success = vq.download_image()