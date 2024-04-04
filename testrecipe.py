# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import os
from pathlib import Path

from cpl.ui import Frame, FrameSet
from typing import Any, Dict

from cpl import core
from cpl import ui
from cpl import dfs
from cpl.core import Msg

from pyesorex.pyesorex import Pyesorex

# +
from typing import Any, Dict

# Import the required PyCPL modules
import cpl.ui


# Define our "Hello, world!" recipe as a class which inherits from
# the PyCPL class cpl.ui.PyRecipe
class HelloWorld(cpl.ui.PyRecipe):
    # The information about the recipe needs to be set. The base class
    # cpl.ui.PyRecipe provides the class variables to be set.
    # The recipe name must be unique, because it is this name which is
    # used to identify a particular recipe among all installed recipes.
    # The name of the python source file where this class is defined
    # is not at all used in this context.
    _name = "helloworld"
    _version = "1.0"
    _author = "U.N. Owen"
    _email = "unowen@somewhere.net"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "PyCPL version of 'hello, world!'"
    _description = (
        "This is the PyCPL version of the well known hello, world program.\n"
        + "It says hello to each input file in the input set-of-frames."
    )

    # Our recipe class also needs to provide the run() method with the
    # correct arguments and return values.
    #
    # As inputs the run method must accept a cpl.ui.FrameSet, and a dictionary
    # that contains the parameters of the recipe.
    # In this example the rcipe does not have any recipe parameters, but the
    # function still has to accept the dictionary as second argument.
    #
    # When the recipe is done, it has to return the produced product files in
    # another cpl.ui.FrameSet object. The current example will not create any
    # output data, so that it will have to return an empty cpl.ui.FrameSet.
    def run(
        self, frameset: cpl.ui.FrameSet, settings: Dict[str, Any]
    ) -> cpl.ui.FrameSet:
        fn_output = "MASTER_FLAT.fits"
        headers = []
        images = core.ImageList()
        for frame in frameset:
            # There needs to be at least one frame with group RAW or CALIB
            # otherwise the file cannot be saved.
            frame.group = ui.Frame.FrameGroup.RAW
            print(f"Hello, {frame.file}!")
            header = core.PropertyList.load(frame.file, position=0)
            print("headers loaded")
            image = core.Image.load(frame.file, extension=0)
            print("image loaded")
            headers.append(header)
            print("headers appended")
            images.append(image)
            print("image appended")

        print("combining")
        combined_image = images.collapse_median_create()
        print("combined")

        
        params = ui.ParameterList(            (
                ui.ParameterEnum(
                   name="metis_det_dark.stacking.method",
                   context="metis_det_dark",
                   description="Name of the method used to combine the input images",
                   default="average",
                   alternatives=("add", "average", "median"),
                ),
            )
        )
        print("params set")
        product_properties = core.PropertyList()
        product_properties.append(
            # Apparently having a PRO CATG is amust
            core.Property("ESO PRO CATG", core.Type.STRING, r"MASTER_FLAT")
        )
        print("HB", len(frameset))
        dfs.save_image(
            frameset,
            params,
            frameset,
            combined_image,
            self.name,
            product_properties,
            f"demo/{self.version!r}",
            fn_output,
            header=header,
        )
        print("saved")

        # Register the created product
        product_frames = ui.FrameSet()
        product_frames.append(
            ui.Frame(
                file=fn_output,
                tag="MASTER_FLAT",
                group=ui.Frame.FrameGroup.PRODUCT,
                level=ui.Frame.FrameLevel.FINAL,
                frameType=ui.Frame.FrameType.IMAGE,
            )
        )

        return product_frames
        # return cpl.ui.FrameSet()
# -

# frame1 = Frame(file="../pico_data/20230522T183858.0.pico.flat.fits", tag="FLAT")
# frame2 = Frame(file="../pico_data/20230522T184437.0.pico.flat.fits", tag="FLAT")
# frameset = FrameSet([frame1, frame2])


pathfiles = Path("./SampleData/Observatoriumspraktikum/Landolt_Field/")
picofiles = list(pathfiles.glob("*.fits"))

frames = [
    Frame(file=str(fn), tag="FLAT")
    for fn in picofiles
]
frameset = FrameSet(frames)

myhw = HelloWorld()
myhw.run(frameset, {})





