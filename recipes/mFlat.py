import cpl.core
import cpl.ui
import cpl.dfs
import cpl.drs
import re

from typing import Any, Dict

class FlatProcess(cpl.ui.PyRecipe):
    _name = "flat_processor"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Basic Flat processor"
    _description = "This recipe takes a number of raw flat frames, subtracts the bias and produces a master flat."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters = cpl.ui.ParameterList(
            (
                cpl.ui.ParameterEnum(
                    name = "mflat.stacking.method",
                    context = "mflat",
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
    

        output_file = "MASTER_FLAT.fits"

        raw_flat_frames = cpl.ui.FrameSet()
        bias_frame = None
        dark_frame = None
        product_frames = cpl.ui.FrameSet()

        for frame in frameset:
            if frame.tag == "FLAT":
                frame.group = cpl.ui.Frame.FrameGroup.RAW
                raw_flat_frames.append(frame)
            elif frame.tag == "MASTER_BIAS":
                frame.group = cpl.ui.Frame.FrameGroup.CALIB
                bias_frame = frame
            elif frame.tag == "MASTER_DARK":
                frame.group = cpl.ui.Frame.FrameGroup.CALIB
                dark_frame = frame
            else:
                cpl.core.Msg.warning(
                    component=self.name,
                    message=f"Got frame {frame.file!r} with unexpected tag {frame.tag!r}, ignoring."
                )

        if len(raw_flat_frames) == 0:
            cpl.core.Msg.error(
                self.name,
                f"No raw frames in frameset."
            )
        
        processed_flat_images = cpl.core.ImageList()

        cpl.core.Msg.warning(
            self.name,
            f"Loading calib files."
        )

        if bias_frame:
            bias_image = cpl.core.Image.load(bias_frame.file)

        cpl.core.Msg.warning(
            self.name,
            f"Loading dark."
        )

        if dark_frame:
            dark_image = cpl.core.Image.load(dark_frame.file)

        cpl.core.Msg.warning(
            self.name,
            f"Preparing flat field."
        )
        for idx, frame in enumerate(raw_flat_frames):
            if idx == 0:
                header = cpl.core.PropertyList.load(frame.file, 0)
                pattern = r'value\s+:\s+(\d+)'
                exp_time_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "EXPTIME", False)
                exp_time = exp_time_list.dump(show=False)
                match = re.search(pattern, exp_time)
                dark_image.multiply_scalar(float(match.group(1)))

            raw_flat_image = cpl.core.Image.load(frame.file)

            raw_flat_image.subtract(bias_image)
            raw_flat_image.subtract(dark_image)
            median = raw_flat_image.get_median()
            raw_flat_image.divide_scalar(median)
            processed_flat_images.insert(idx, raw_flat_image)

        combined_image = None

        method = self.parameters["mflat.stacking.method"].value

        if method == "mean":
            combined_image = processed_flat_images.collapse_create()
        elif method == "median":
            combined_image = processed_flat_images.collapse_median_create()

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
                tag="MASTER_FLAT",
                group=cpl.ui.Frame.FrameGroup.CALIB,
            )
        )

        return product_frames