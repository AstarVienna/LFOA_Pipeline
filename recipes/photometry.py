import cpl.core
import cpl.ui
import cpl.dfs
import cpl.drs
import re

from typing import Any, Dict

import numpy as np


class Photometry(cpl.ui.PyRecipe):
    _name = "photometry"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Basic photometry analysis"
    _description = "This recipe calculates the magnitude of the star via aperture photometry."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters = cpl.ui.ParameterList(
            (cpl.ui.ParameterValue(
                    name = "test.phot",
                    context = "phot",
                    description = "Test Parameter",
                    default = "Test"
                ),
            ),
        )

    def run(self, frameset: cpl.ui.FrameSet, settings: Dict[str, Any]) -> cpl.ui.FrameSet:

        output_file = "SCIENCE_FRAME.fits"
        output_frame = cpl.ui.FrameSet()
        mag_v_land = 13.691
        mag_r_land = 13.367

        zp_r = None
        zp_v = None

        pattern_doub = r'value\s+:\s+(\d+)'
        pattern_strg = r"value\s+:\s+'(\w+)'"
        pattern_fil = r"value\s+:\s+'(\w+\s\w)'"
        
        # Assume the brightest Standard star is used

        for frame in frameset:
            frame.group = cpl.ui.Frame.FrameGroup.RAW
            obj_typ_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "OBJTYP", False)
            obj_typ = obj_typ_list.dump(show=False)
            match_obj = re.search(pattern_strg, obj_typ).group(1) # type: ignore
            exp_time_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "EXPTIME", False)
            exp_time = cpl.core.PropertyList.dump(exp_time_list, show=False)
            match_exp = float(re.search(pattern_doub, exp_time).group(1)) # type: ignore
            if match_obj == "Landold":
                input_image = cpl.core.Image.load(frame.file)
                apertures = cpl.drs.Apertures.extract_sigma(input_image, 6.0)
                brightness = apertures.get_flux(1)
                m_inst = -2.5*np.log10(brightness/match_exp)
                filter_typ_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "FILTER", False)
                filter_typ = filter_typ_list.dump(show=False)
                match_filter = re.search(pattern_fil, filter_typ).group(1) # type: ignore
                if match_filter == "Bessel R":
                    zp_r = mag_r_land - m_inst
                elif match_filter == "Bessel V":
                    zp_v = mag_v_land - m_inst
        for frame in frameset:
            frame.group = cpl.ui.Frame.FrameGroup.RAW
            obj_typ_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "OBJTYP", False)
            obj_typ = obj_typ_list.dump(show=False)
            match_obj = re.search(pattern_strg, obj_typ).group(1) # type: ignore
            exp_time_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "EXPTIME", False)
            exp_time = cpl.core.PropertyList.dump(exp_time_list, show=False)
            match_exp = float(re.search(pattern_doub, exp_time).group(1)) # type: ignore
            if match_obj == "Supernova":
                input_image = cpl.core.Image.load(frame.file)
                apertures = cpl.drs.Apertures.extract_sigma(input_image, 6.0)   
                brightness = apertures.get_flux(1)
                filter_typ_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "FILTER", False)
                filter_typ = filter_typ_list.dump(show=False)
                match_filter = re.search(pattern_fil, filter_typ).group(1) # type: ignore
                if match_filter == "Bessel R":
                    mag = -2.5 * np.log10(brightness / match_exp) + zp_r
                elif match_filter == "Bessel V":
                    mag = -2.5 * np.log10(brightness / match_exp) + zp_v

                product_properties = cpl.core.PropertyList()
                product_properties.append(
                    cpl.core.Property("MAGNITUDE", mag))
                product_properties.append(
                    cpl.core.Property("ESO PRO CATG", cpl.core.Type.STRING, r"OBJECT_REDUCED")) 

                cpl.dfs.save_image(
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
            cpl.ui.Frame(
                file=output_file,
                tag="SCIENCE_FRAME",
                group=cpl.ui.Frame.FrameGroup.PRODUCT,
                level=cpl.ui.Frame.FrameLevel.FINAL,
                frameType=cpl.ui.Frame.FrameType.IMAGE,
            )
        )
        return output_frame