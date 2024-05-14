import cpl.core
import cpl.ui
import cpl.dfs
import cpl.drs
import re

from typing import Any, Dict

class DarkProcess(cpl.ui.PyRecipe):
    _name = "dark_processor"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Basic Dark processor"
    _description = "This recipe takes a number of raw dark frames, subtracts the bias and produces a master dark."

    def __init__(self):
        self.parameters = cpl.ui.ParameterList(
            (
                cpl.ui.ParameterEnum(
                    name = "mdark.stacking.method",
                    context = "mdark",
                    description = "Method used for averaging",
                    default = "mean",
                    alternatives = ("mean", "median"),
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
        
        output_file = "MASTER_DARK.fits"
        
        raw_Dark_Frames = cpl.ui.FrameSet()
        bias_frame = None
        match = None
        product_frames = cpl.ui.FrameSet()

        for frame in frameset:
            if frame.tag == "DARK":
                frame.group = cpl.ui.Frame.FrameGroup.RAW
                raw_Dark_Frames.append(frame)
            elif frame.tag == "MASTER_BIAS":
                frame.group = cpl.ui.Frame.FrameGroup.CALIB
                bias_frame = frame
            else:
                cpl.core.Msg.warning(
                    self.name,
                    f"Got frame {frame.file!r} with unexpected tag {frame.tag!r}, ignoring."
                )
        
        if len(raw_Dark_Frames) == 0:
            cpl.core.Msg.error(
                self.name,
                f"No raw frames in frameset."
            )

        processed_dark_images = cpl.core.ImageList()

        if bias_frame:
            bias_image = cpl.core.Image.load(bias_frame.file)

        for idx, frame in enumerate(raw_Dark_Frames):
            if idx == 0:
                header = cpl.core.PropertyList.load(frame.file, 0)
                pattern = r'value\s+:\s+(\d+)'
                exp_time_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "EXPTIME", False)
                exp_time = exp_time_list.dump(show=False)
                match = re.search(pattern, exp_time)
            raw_dark_image = cpl.core.Image.load(frame.file)

            raw_dark_image.subtract(bias_image)

            processed_dark_images.insert(idx, raw_dark_image)

        combined_image = None

        method = self.parameters["mdark.stacking.method"].value

        if method == "mean":
            combined_image = processed_dark_images.collapse_create()
        elif method == "median":
            combined_image = processed_dark_images.collapse_median_create()

        combined_image.divide_scalar(float(match.group(1)))

        product_properties = cpl.core.PropertyList()
        product_properties.append(
            cpl.core.Property("ESO PRO CATG", cpl.core.Type.STRING, r"OBJECT_REDUCED")
        )

        cpl.core.Msg.info(self.name, f"Saving product file as {output_file!r}.")

        cpl.dfs.save_image(
            frameset,
            self.parameters,
            frameset,
            combined_image,
            self.name,
            product_properties,
            f"demo/{self.version!r}",
            output_file,
            header=header,
        )

        product_frames.append(
            cpl.ui.Frame(
                file=output_file,
                tag="MASTER_DARK",
                group=cpl.ui.Frame.FrameGroup.CALIB,
            )
        )

        return product_frames
    


