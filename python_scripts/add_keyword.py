import os
from astropy.io import fits

def add_keyword_to_fits_header(directory, keyword, value, position=None):
    """
    Add a keyword with a string value to the header of all FITS files in a given directory.

    Parameters:
    directory (str): The directory containing the FITS files.
    keyword (str): The keyword to add to the header.
    value (str): The string value of the keyword.
    position (int, optional): The position in the header to insert the keyword. If None, the keyword is added at the end.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".fits"):
            filepath = os.path.join(directory, filename)
            with fits.open(filepath, mode='update') as hdul:
                hdr = hdul[0].header  # Get the header of the primary HDU # type: ignore
                if position is not None:
                    hdr.insert(position, (keyword, value))  # Insert the keyword and value at the specified position
                else:
                    hdr[keyword] = value  # Add the keyword and value to the end of the header
                hdul.flush()  # Save changes to the file
            print(f"Added keyword '{keyword}' with value '{value}' to {filename} at position {position}")

# Example usage
directory = '/home/kali/Sof_Data/Landold-Feld'  # Replace with the path to your FITS files
keyword = 'OBJTYP'
value = 'Landold'
position = 113  # Replace with the desired position, or set to None to add at the end
add_keyword_to_fits_header(directory, keyword, value, position)
