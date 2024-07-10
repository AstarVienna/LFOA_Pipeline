from cpl import core, ui, dfs, drs

from typing import Any, Dict

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
            (),
        )
    
    def run(self, frameset:ui.FrameSet, settings: Dict[str, Any]) -> ui.FrameSet:

        choosen_frames = ui.FrameSet()
        product_frames = ui.FrameSet()

        for frame in frameset:
            if frame.tag == "FLAT":
                frame.group = ui.Frame.FrameGroup.RAW
                raw_flat_image = core.Image.load(frame.file)
                noise, error = drs.detector.get_noise_window(raw_flat_image)
                if noise < 63:
                    choosen_frames.append(frame)

                    product_properties = core.PropertyList()
                    product_properties.append(
                        core.Property("NOISE", f"{noise}"))
                    product_properties.append(
                        core.Property("ESO PRO CATG", core.Type.STRING, r"OBJECT_REDUCED")
                    )    

                    dfs.save_image(
                        frameset,
                        self.parameters,
                        frameset,
                        raw_flat_image,
                        self.name,
                        product_properties,
                        f"demo/{self.version!r}",
                        frame.file,
                    )

                    product_frames.append(
                        ui.Frame(
                            file=frame.file,
                            tag="FLAT",
                            group=ui.Frame.FrameGroup.CALIB,
                        )
                    )

        return product_frames
    