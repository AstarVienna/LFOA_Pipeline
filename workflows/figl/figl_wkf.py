from edps import task, data_source, classification_rule
from . import figl_rules as rules

# Classification rules
bias_class = classification_rule("BIAS", {"IMAGETYP": "bias"})
dark_class = classification_rule("DARK", {"IMAGETYP": "dark"})
prep_class = classification_rule("FLAT", {"IMAGETYP": "flat"})
science_class = classification_rule("SCIENCE", {"IMAGETYP": "object"})
noise_level = classification_rule("FLAT", rules.low_noise)

# Data Sources
raw_bias = (data_source("BIAS")
            .with_classification_rule(bias_class)
            .with_grouping_keywords(["DATE-OBS"])
            .with_match_keywords(["ORIGIN"])
            .build())
raw_darks = (data_source("DARK")
            .with_classification_rule(dark_class)
            .with_grouping_keywords(["DATE-OBS"])
            .with_match_keywords(["ORIGIN"])
            .build())
raw_prep = (data_source("FLAT")
            .with_classification_rule(prep_class)
            .with_grouping_keywords(["DATE-OBS"])
            .with_match_keywords(["ORIGIN", "FILTER", "EXPTIME"])
            .build())
raw_science = (data_source("SCIENCE")
              .with_classification_rule(science_class)
              .with_grouping_keywords(["DATE-OBS"])
              .build())
# Process Task
bias_task = (task("bias")
            .with_recipe("mbias_processor")
            .with_main_input(raw_bias)
            .build())

dark_task = (task("dark")
            .with_recipe("dark_processor")
            .with_main_input(raw_darks)
            .with_associated_input(bias_task)
            .build())
prep_task = (task("prep")
            .with_recipe("raw_prep")
            .with_main_input(raw_prep)
            #.with_output_filter(noise_level)
            .build())

flat_task = (task("flat")
            .with_recipe("flat_processor")
            .with_main_input(prep_task)
            .with_associated_input(bias_task)
            .with_associated_input(dark_task)
            .build())

science_task = (task("science")
                .with_recipe("science_processor")
                .with_main_input(raw_science)
                .with_associated_input(bias_task)
                .with_associated_input(dark_task)
                .with_associated_input(flat_task)
                .build())

photometry_task = (task("photometry")
                   .with_recipe("photometry")
                   .with_main_input(science_task)
                   .build())