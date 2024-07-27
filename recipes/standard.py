import cpl.core
import cpl.ui
import cpl.dfs
import cpl.drs
import re

from typing import Any, Dict

from numpy import mat

class StandardProcessor(cpl.ui.PyRecipe):
    _name = "standard_processor"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Basic standard star processor"
    _description = "This recipe takes a number of raw science frames and applies basic calibration frames."

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

    def run(self, frameset: cpl.ui.FrameSet, settings: Dict[str, Any]) -> cpl.ui.FrameSet:
        for key, value in settings.items():
            try:
                self.parameters[key].value = value
            except KeyError:
                cpl.core.Msg.warning(
                    self._name,
                    f"Settings includes {key}:{value} but {self} has no parameter named {key}.",
                )

        output_file = "LANDOLD.fits"

        pattern_strg = r"value\s+:\s+'(\w+)'"
        pattern_doub = r"value\s+:\s+(\d+)"
        pattern_fil = r"value\s+:\s+'(\w+\s\w)'"

        raw_science_frames = cpl.ui.FrameSet()
        bias_frame = None
        dark_frame = None
        flat_frame = None
        standard_images = cpl.core.ImageList()
        standard_products = cpl.ui.FrameSet()

        method = self.parameters["mflat.stacking.method"].value

        for frame in frameset:
            if frame.tag == "SCIENCE":
                frame.group = cpl.ui.Frame.FrameGroup.RAW
                raw_science_frames.append(frame)
            elif frame.tag == "MASTER_BIAS":
                frame.group = cpl.ui.Frame.FrameGroup.CALIB
                bias_frame = frame
            elif frame.tag == "MASTER_DARK":
                frame.group = cpl.ui.Frame.FrameGroup.CALIB
                dark_frame = frame
            elif frame.tag == "MASTER_FLAT":
                frame.group = cpl.ui.Frame.FrameGroup.CALIB
                flat_frame = frame
            else:
                cpl.core.Msg.warning(
                    component=self.name,
                    message=f"Got frame {frame.file!r} with unexpected tag {frame.tag!r}, ignoring."
                )

        if len(raw_science_frames) == 0:
            cpl.core.Msg.error(
                self.name,
                f"No raw frames in frameset."
            )

        if bias_frame:
            bias_image = cpl.core.Image.load(bias_frame.file)
        if dark_frame:
            dark_image = cpl.core.Image.load(dark_frame.file)
        if flat_frame:
            flat_image = cpl.core.Image.load(flat_frame.file)


        for idx, frame in enumerate(raw_science_frames):
            if idx == 0:
                exp_time_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "EXPTIME", False)
                exp_time = cpl.core.PropertyList.dump(exp_time_list, show=False)
                match_exp = float(re.search(pattern_doub, exp_time).group(1)) # type: ignore
                filter_typ_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "FILTER", False)
                filter_typ = filter_typ_list.dump(show=True)
                match_filter = re.search(pattern_fil, filter_typ).group(1) # type: ignore
                dark_image.multiply_scalar(match_exp)

                stnd_typ_list = cpl.core.PropertyList.load_regexp(frame.file, 0, "OBJTYP", False)
                stnd_typ = stnd_typ_list.dump(show=False)
                match_stnd = re.search(pattern_strg, stnd_typ).group(1) # type: ignore

            raw_science_image = cpl.core.Image.load(frame.file)
            raw_science_image.subtract(bias_image)
            raw_science_image.subtract(dark_image)
            raw_science_image.divide(flat_image)
            standard_images.append(raw_science_image)

        
        product_properties = cpl.core.PropertyList()
        product_properties.append(
            cpl.core.Property("ESO PRO CATG", cpl.core.Type.STRING, r"OBJECT_REDUCED")
        )
        product_properties.append(
            cpl.core.Property("EXPTIME", match_exp)
        )
        product_properties.append(
            cpl.core.Property("OBJTYP", match_stnd)
        )
        product_properties.append(
            cpl.core.Property("FILTER", match_filter)
        )

        if method == "mean":
            combined_object_image = standard_images.collapse_create()

        elif method == "median":
            combined_object_image = standard_images.collapse_median_create()

        cpl.dfs.save_image(
            frameset,
            self.parameters,
            frameset,
            combined_object_image,
            self.name,
            product_properties,
            f"demo/{self.version!r}",
            output_file,
        )

        standard_products.append(
            cpl.ui.Frame(
                file=output_file,
                tag="STANDARD_FRAME",
                group=cpl.ui.Frame.FrameGroup.FINAL,
            )
        )

        return standard_products

