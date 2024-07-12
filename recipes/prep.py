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
            (
                ui.ParameterEnum(
                    name = "mflat.stacking.method",
                    context = "mflat",
                    description = "Method used for averaging",
                    default = "mean",
                    alternatives = ("mean", "median"),
                ),
            )
        )
    
    def run(self, frameset:ui.FrameSet, settings: Dict[str, Any]) -> ui.FrameSet:

        choosen_frames = ui.FrameSet()
        product_frames = ui.FrameSet()

        output_file = "CHOSEN_FLAT.fits"

        for idx, frame in enumerate(frameset):
            if frame.tag == "FLAT":
                if idx == 0:
                    header = core.PropertyList.load(frame.file, 0)
                frame.group = ui.Frame.FrameGroup.RAW
                raw_flat_image = core.Image.load(frame.file)
                noise, error = drs.detector.get_noise_window(raw_flat_image)
                print(noise)
                if noise < 200:
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
                        output_file[:11]+f"_{idx}"+output_file[11:],
                        header=header,
                        inherit=frame,
                    )

                    product_frames.append(
                        ui.Frame(
                            file=output_file[:11]+f"_{idx}"+output_file[11:],
                            tag="FLAT",
                            group=ui.Frame.FrameGroup.RAW,
                        )
                    )

        return product_frames
    