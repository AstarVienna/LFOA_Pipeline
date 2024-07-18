from cpl import core, ui, dfs, drs

from typing import Any, Dict

import numpy as np
import re

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
            obj_typ_list = core.PropertyList.load_regexp(frame.file, 0, "OBJTYP", False)
            obj_typ = obj_typ_list.dump(show=False)
            match_obj = re.search(pattern, obj_type).group(1) # type: ignore
            exp_time_list = core.PropertyList.load_regexp(frame.file, 0, "EXPTIME", False)
            exp_time = core.PropertyList.dump(exp_time_list, show=False)
            match_exp = float(re.search(pattern, exp_time).group(1)) # type: ignore
            if match_obj == "Landold":
                input_image = core.Image.load(frame.file)
                apertures = drs.Apertures.extract_sigma(input_image, 6.0)
                brightness = apertures.get_flux(1)
                m_inst = -2.5*np.log10(brightness/match_exp)
                filter_typ_list = core.PropertyList.load.regexp(frame.file, 0, "FILTER", False)
                filter_typ = filter_typ_list.dump(show=False)
                match_filter = re.search(pattern, filter_typ).group(1) # type: ignore
                if match_filter == "Bessle R":
                    ZP_R = mag_r_land - m_inst
                elif match_filter == "Bessle V":
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