from cpl import core, ui, dfs, drs

from typing import Any, Dict

import numpy as np
from recipes.figl_functions import *

class Photometry(ui.PyRecipe):
    _name = "photometry"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Basic photometry analysis"
    _description = "This recipe calculates the magnitude of the star via aperture photometry."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters = ui.ParameterList(
            (
            ),
        )

    def run(self, frameset: ui.FrameSet, settings: Dict[str, Any]) -> ui.FrameSet:

        object_frame = ui.FrameSet()
        standard_frame = ui.FrameSet()      

        mag_v_land = 13.691
        mag_r_land = 13.367

        pattern = r'value\s+:\s+(\d+)'
        
        # Assume the brightest Standard star is used

        for frame in frameset:
            match_obj = obj(frame.file)
            match_exp = exp(frame.file)
            if match_obj == "Landold":
                input_image = core.Image.load(frame.file)
                apertures = drs.Apertures.extract_sigma(input_image, 6.0)
                brightness = apertures.get_flux(1)
                m_inst = -2.5*np.log10(brightness/match_exp)
                match_filter = filter_match(frame.file)
                if match_filter == "Bessel R":
                    ZP_R = mag_r_land - m_inst
                elif match_filter == "Bessel V":
                    ZP_V = mag_v_land - m_inst
            if match_obj == "Supernova":
                input_image = core.Image.load(frame.file)
                apertures = drs.Apertures.extract_sigma(input_image, 6.0)   
                brightness = apertures.get_flux(1)
                



        product_properties = core.PropertyList()
        product_properties.append(
            core.Property("FLUX", f"{brightness}"))
        product_properties.append(
            core.Property("ESO PRO CATG", core.Type.STRING, r"OBJECT_REDUCED")
        )    

        dfs.save_image(
            frameset,
            self.parameters,
            frameset,
            input_image,
            self.name,
            product_properties,
            f"demo/{self.version!r}",
            output_file,
        )

        output_frame.append(
            ui.Frame(
                file=output_file,
                tag="SCIENCE_FRAME",
                group=ui.Frame.FrameGroup.PRODUCT,
                level=ui.Frame.FrameLevel.FINAL,
                frameType=ui.Frame.FrameType.IMAGE,
            )
        )
        return output_frame