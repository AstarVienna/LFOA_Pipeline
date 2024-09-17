import cpl.core
import cpl.ui
import cpl.dfs
import cpl.drs
import re

from typing import Any, Dict

class RawPrep(cpl.ui.PyRecipe):
    _name = "raw_prep"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Recipe for preparing raw fits files for processing"
    _description = "This recipe takes a number of raw frames and prepares them for processing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters = cpl.ui.ParameterList(
            (
                cpl.ui.ParameterValue(
                    name = "prep.low.noise",
                    context = "prep",
                    description = "Maximum value of accepted noise",
                    default = 126.0
                ),
            )
        )
    
    def run(self, frameset:cpl.ui.FrameSet, settings: Dict[str, Any]) -> cpl.ui.FrameSet:
        for key, value in settings.items():
            try:
                self.parameters[key].value = value
            except KeyError:
                    cpl.core.Msg.warning(
                        self._name,
                        f"Settings includes {key}:{value} but {self} has no parameter named {key}.",
                    )
        
        product_frames = cpl.ui.FrameSet()

        output_file = "FLAT.fits"

        pattern = r'value\s+:\s+(\d+)'

        for idx, frame in enumerate(frameset):
            if frame.tag == "FLAT":
                cpl.core.Msg.debug(self.name, f"Got raw flat frame: {frame.file}.")
                if idx == 0:
                    exp_time_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "EXPTIME", False)
                    exp_time = cpl.core.PropertyList.dump(exp_time_list, show=False)
                    match_exp = float(re.search(pattern, exp_time).group(1)) # type: ignore
                frame.group = cpl.ui.Frame.FrameGroup.RAW
                raw_flat_image = cpl.core.Image.load(frame.file)
                cpl.core.Msg.debug(self.name, f"Ascertaining noise of frame: {frame.file}.")
                noise, error = cpl.drs.detector.get_noise_window(raw_flat_image)
                product_properties = cpl.core.PropertyList()
                product_properties.append(
                    cpl.core.Property("NOISE", noise))
                product_properties.append(
                    cpl.core.Property("ESO PRO CATG", cpl.core.Type.STRING, r"OBJECT_REDUCED"))
                product_properties.append(
                    cpl.core.Property("EXPTIME", match_exp))
                cpl.core.Msg.info(self.name, f"Saving chosen flat as {output_file!r}.")
                cpl.dfs.save_image(
                    frameset,
                    self.parameters,
                    frameset,
                    raw_flat_image,
                    self.name,
                    product_properties,
                    f"demo/{self.version!r}",
                    output_file[:4]+f"_{idx}"+output_file[4:],
                    inherit=frame,  
                )
                if noise < self.parameters['prep.low.noise'].value:
                    product_frames.append(
                        cpl.ui.Frame(
                            file=output_file[:4]+f"_{idx}"+output_file[4:],
                            tag="CHOSEN_FLAT",
                            group=cpl.ui.Frame.FrameGroup.RAW,
                        )
                    )
                if noise > self.parameters['prep.low.noise'].value:
                    product_frames.append(
                            cpl.ui.Frame(
                                file=output_file[:4]+f"_{idx}"+output_file[4:],
                                tag="FLAT",
                                group=cpl.ui.Frame.FrameGroup.RAW,
                            )
                        )

        return product_frames
    