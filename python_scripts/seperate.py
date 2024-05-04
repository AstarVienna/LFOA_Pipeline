import sys
from astropy.io import fits
import os

def separate_data_cube(input_file):
    # Open the data cube FITS file
    with fits.open(input_file) as hdul:
        data = hdul[0].data
        header = hdul[0].header
    
    # Create a directory to store individual files
    output_dir = os.path.splitext(input_file)[0]
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each slice of the data cube as an individual FITS file
    for i in range(data.shape[0]):
        output_file = os.path.join(output_dir, f"Flat_{i+1}.fits")
        hdu = fits.PrimaryHDU(data[i], header)
        hdul = fits.HDUList([hdu])
        hdul.writeto(output_file)
        print(f"Saved {output_file}")
        
    print("Separation complete.")

if __name__ == "__main__":
    # Check if the path to the data cube FITS file is provided
    if len(sys.argv) != 2:
        print("Please provide the path to the data cube FITS file as a command-line argument.")
        print("Example: python separate_data_cube.py /path/to/your/data_cube.fits")
    else:
        input_file = sys.argv[1]
        separate_data_cube(input_file)
