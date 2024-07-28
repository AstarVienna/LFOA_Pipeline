import cpl.core
import cpl.ui
import cpl.dfs
import cpl.drs

from typing import Any, Dict

class BiasProcess(cpl.ui.PyRecipe):
    _name = "bias_processor"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Basic Bias processor"
    _description = "This recipe takes a number of raw bias frames and produces a master bias."

    def __init__(self):
        self.parameters = cpl.ui.ParameterList(
            (
                cpl.ui.ParameterEnum(
                    name = "mbias.stacking.method",
                    context = "mbias",
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

        output_file = "MASTER_BIAS.fits"
        
        header = None

        raw_bias_frames = cpl.ui.FrameSet()
        product_frames = cpl.ui.FrameSet()

        for frame in frameset:
            if frame.tag == "BIAS":
                frame.group = cpl.ui.Frame.FrameGroup.RAW
                raw_bias_frames.append(frame)
                cpl.core.Msg.debug(self.name, f"Got raw bias frame: {frame.file}.")
            else:
                 cpl.core.Msg.warning(
                      self.name,
                      f"Got frame {frame.file!r} with unexpected tag {frame.tag!r}, ignoring."
                 )

        if len(raw_bias_frames) == 0:
             cpl.core.Msg.error(
                  self.name,
                  f"No raw frames in frameset."
             )

        header = None
        processed_bias_images = cpl.core.ImageList()

        for idx, frame in enumerate(raw_bias_frames):
            cpl.core.Msg.info(self.name, f"Processing {frame.file!r}...")

            if idx == 0:
                header = cpl.core.PropertyList.load(frame.file, 0)

            cpl.core.Msg.debug(self.name, f"Loading bias image {idx}...")
            raw_bias_image = cpl.core.Image.load(frame.file)

            processed_bias_images.insert(idx, raw_bias_image)

        method = self.parameters["mbias.stacking.method"].value
        cpl.core.Msg.info(self.name, f"Combining bias images using method {method!r}")

        combined_image = None

        if method == "mean":
             combined_image = processed_bias_images.collapse_create()
        
        elif method == "median":
             combined_image = processed_bias_images.collapse_median_create()
        
        else:
            cpl.core.Msg.error(
                  self.name,
                  f"Got unknown stacking method {method!r}. Stopping..."
            )
            return product_frames
        
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
                tag="MASTER_BIAS",
                group=cpl.ui.Frame.FrameGroup.CALIB,
            )
        )

        return product_frames