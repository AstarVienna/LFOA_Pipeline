from cpl import core, ui, dfs, drs

from typing import Any, Dict

from ..recipes.figl_functions import *

import re

class RawPrep(ui.PyRecipe):
    _name = "raw_prep"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Recipe for preparing raw fits files for processing"
    _description = "This recipe takes a number of raw frames and prepares them for processing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters = ui.ParameterList(
            (
                ui.ParameterValue(
                    name = "prep.low.noise",
                    context = "prep",
                    description = "Maximum value of accepted noise",
                    default = 125.0
                ),
            )
        )
    
    def run(self, frameset:ui.FrameSet, settings: Dict[str, Any]) -> ui.FrameSet:
        for key, value in settings.items():
            try:
                self.parameters[key].value = value
            except KeyError:
                    core.Msg.warning(
                        self._name,
                        f"Settings includes {key}:{value} but {self} has no parameter named {key}.",
                    )
        
        choosen_frames = ui.FrameSet()
        product_frames = ui.FrameSet()

        output_file = "CHOSEN_FLAT.fits"

        for idx, frame in enumerate(frameset):
            if frame.tag == "FLAT":
                if idx == 0:
                    header = core.PropertyList.load(frame.file, 0)
                    match = exp(frame.file)
                frame.group = ui.Frame.FrameGroup.RAW
                raw_flat_image = core.Image.load(frame.file)
                noise, error = drs.detector.get_noise_window(raw_flat_image)
                core.Msg.info(
                    self.name,
                    "Choosing Flats."
                )
                product_properties = core.PropertyList()
                product_properties.append(
                    core.Property("NOISE", noise))
                product_properties.append(
                    core.Property("ESO PRO CATG", core.Type.STRING, r"OBJECT_REDUCED"))
                product_properties.append(
                    core.Property("EXPTIME", core.Type.STRING, f"{match}"))
                dfs.save_image(
                    frameset,
                    self.parameters,
                    frameset,
                    raw_flat_image,
                    self.name,
                    product_properties,
                    f"demo/{self.version!r}",
                    output_file[:11]+f"_{idx}"+output_file[11:],
                    inherit=frame,  
                )
                if noise < self.parameters['prep.low.noise'].value:
                    product_frames.append(
                        ui.Frame(
                            file=output_file[:11]+f"_{idx}"+output_file[11:],
                            tag="CHOOSEN_FLAT",
                            group=ui.Frame.FrameGroup.RAW,
                        )
                    )
                product_frames.append(
                        ui.Frame(
                            file=output_file[:11]+f"_{idx}"+output_file[11:],
                            tag="FLAT",
                            group=ui.Frame.FrameGroup.RAW,
                        )
                    )

        return product_frames
    