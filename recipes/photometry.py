from cpl import core, ui, dfs, drs

from typing import Any, Dict

class Photometry(ui.PyRecipe):
    _name = "photometry"
    _version = "0.1"
    _author = "Benjamin Eisele"
    _email = "benjamin.eisele0101@gmail.com"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Basic photometry analysis"
    _description = "This recipe calculates the magnitude of the star via aperture photometry and data from Gaia."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters = ui.ParameterList(
            (
            )
        )

    def run(self, frameset: ui.FrameSet, settings: Dict[str, Any]) -> ui.FrameSet:

        output_file = "SCIENCE_FRAME.fits"

        input_frame = ui.FrameSet()
        output_frame = ui.FrameSet()
        header = None

        for frame in frameset:
            if frame.tag == "SCIENCE_FRAME":
                input_frame.append(frame)
                frame.group = ui.Frame.FrameGroup.CALIB

            else:
                core.Msg.warning(
                    component=self.name,
                    message=f"Got frame {frame.file!r} with unexpected tag {frame.tag!r}, ignoring."
                )

        if len(input_frame) == 0:
            core.Msg.error(
                self.name,
                f"No raw frames in frameset."
            )

        input_image = None

        
        for frame in input_frame:
            header = core.PropertyList.load(frame.file, 0)
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