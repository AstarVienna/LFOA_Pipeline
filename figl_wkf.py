from edps import task, data_source, classification_rule

# Classification rules
bias_class = classification_rule("BIAS", {"IMAGETYP": "bias"})
dark_class = classification_rule("DARK", {"IMAGETYP": "dark"})

# Data Sources
raw_bias = (data_source("BIAS")
            .with_classification_rule(bias_class)
            .with_grouping_keywords(["DATE-OBS"])
            .with_match_keywords(["DATEOBS"])
            .build())
raw_darks = (data_source("DARK")
            .with_classification_rule(dark_class)
            .with_grouping_keywords(["mjd-obs"])
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