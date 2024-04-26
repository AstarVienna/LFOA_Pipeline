import sys
import glob
from astropy.io import fits
import numpy as np

def subtract_bias(dark_files, bias_file):
    if len(dark_files) == 0:
        print("No dark files provided.")
        return

    with fits.open(bias_file) as bias_hdul:
        bias_data = bias_hdul[0].data

        for dark_file in dark_files:
            with fits.open(dark_file) as dark_hdul:
                dark_data = dark_hdul[0].data

                # Subtract the bias data from the dark data
                subtracted_data = dark_data - bias_data

                # Create a new HDU with the subtracted data
                hdu = fits.PrimaryHDU(subtracted_data)

                # Save the subtracted dark data to a new file
                output_file = dark_file.replace('.fits', '_d_subtracted.fits')
                hdul = fits.HDUList([hdu])
                hdul.writeto(output_file)
                print(f"Subtracted dark file saved: {output_file}")

if __name__ == "__main__":
    # Check if the dark files, bias file are provided
    if len(sys.argv) < 3:
        print("Please provide at least one dark file, the bias file.")
        print("Example: python subtract_dark.py dark_*.fits master_bias.fits")
    else:
        dark_pattern = sys.argv[1]
        bias_file = sys.argv[2]

        # Use glob to expand the dark file pattern into a list of matching files
        dark_files = glob.glob(dark_pattern)

        subtract_bias(dark_files, bias_file)
