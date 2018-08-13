#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.OCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRBase


################################### CLASSES ###################################
class OCRDataset(OCRBase):
    """Dataset for representing a collection of character images"""

    # region Builtins
    def __init__(self, font_names=None, font_sizes=None, font_widths=None,
                 font_x_offsets=None, font_y_offsets=None, hdf5_infile=None,
                 hdf5_outfile=None, image_mode=None, n_chars=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if font_names is not None:
            self.font_names = font_names
        if font_sizes is not None:
            self.font_sizes = font_sizes
        if font_widths is not None:
            self._font_widths = font_widths
        if font_x_offsets is not None:
            self._font_x_offsets = font_x_offsets
        if font_y_offsets is not None:
            self.font_y_offsets = font_y_offsets
        if hdf5_infile is not None:
            self.hdf5_infile = hdf5_infile
        if image_mode is not None:
            self.image_mode = image_mode
        if n_chars is not None:
            self.n_chars = n_chars
        if hdf5_infile is not None:
            self.hdf5_infile = hdf5_infile
        if hdf5_outfile is not None:
            self.hdf5_outfile = hdf5_outfile

        # Initialize
        if self.hdf5_infile is not None:
            self.initialize_from_hdf5()
        else:
            self.initialize_from_scratch()

    # endregion

    # region Properties
    @property
    def char_image_specs_available(self):
        """pandas.DataFrame: Available character image specifications"""
        if not hasattr(self, "_char_image_specs_available"):
            from itertools import product
            import pandas as pd

            self._char_image_specs_available = pd.DataFrame(
                list(product(self.font_names, self.font_sizes,
                             self.font_widths, self.font_x_offsets,
                             self.font_y_offsets)),
                columns=["font", "size", "width", "x_offset", "y_offset"])

        return self._char_image_specs_available

    @char_image_specs_available.setter
    def char_image_specs_available(self, value):
        # Todo: Validate
        self._char_image_specs_available = value

    @property
    def char_image_specs(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_char_image_specs"):
            import pandas as pd

            self._char_image_specs = pd.DataFrame(
                columns=["character", "font", "size", "width", "x_offset",
                         "y_offset"])
        return self._char_image_specs

    @char_image_specs.setter
    def char_image_specs(self, value):
        # Todo: Validate
        self._char_image_specs = value

    @property
    def char_image_data(self):
        """numpy.ndarray(bool): Character image data"""
        return self._char_image_data

    @char_image_data.setter
    def char_image_data(self, value):
        # Todo: Validate
        self._char_image_data = value

    @property
    def figure(self):
        """matplotlib.figure.Figure: Temporary figure used for images"""
        if not hasattr(self, "_figure"):
            from matplotlib.pyplot import figure

            self._figure = figure(figsize=(1.0, 1.0), dpi=80)
        return self._figure

    @property
    def font_names(self):
        """list(str): List of font names"""
        if not hasattr(self, "_font_names"):
            self._font_names = ["Hei"]
        return self._font_names

    @font_names.setter
    def font_names(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [str(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_names = value

    @property
    def font_sizes(self):
        """list(int): List of font sizes"""
        if not hasattr(self, "_font_sizes"):
            self._font_sizes = [60]
        return self._font_sizes

    @font_sizes.setter
    def font_sizes(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_sizes = value

    @property
    def font_widths(self):
        """list(int): List of font border widths"""
        if not hasattr(self, "_font_widths"):
            self._font_widths = [6]
        return self._font_widths

    @font_widths.setter
    def font_widths(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_widths = value

    @property
    def font_x_offsets(self):
        """list(int): List of font x offsets"""
        if not hasattr(self, "_font_x_offsets"):
            self._font_x_offsets = [0]
        return self._font_x_offsets

    @font_x_offsets.setter
    def font_x_offsets(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_x_offsets = value

    @property
    def font_y_offsets(self):
        """list(int): List of font y offsets"""
        if not hasattr(self, "_font_y_offsets"):
            self._font_y_offsets = [0]
        return self._font_y_offsets

    @font_y_offsets.setter
    def font_y_offsets(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_y_offsets = value

    @property
    def hdf5_infile(self):
        """str: Path to input hdf5 file"""
        if not hasattr(self, "_hdf5_infile"):
            self._hdf5_infile = None
        return self._hdf5_infile

    @hdf5_infile.setter
    def hdf5_infile(self, value):
        from os.path import expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError()
            else:
                value = expandvars(value)
                if not isfile(value):
                    raise ValueError()
        self._hdf5_infile = value

    @property
    def hdf5_outfile(self):
        """str: Path to output hdf5 file"""
        if not hasattr(self, "_hdf5_outfile"):
            self._hdf5_outfile = None
        return self._hdf5_outfile

    @hdf5_outfile.setter
    def hdf5_outfile(self, value):
        from os import access, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError()
            else:
                value = expandvars(value)
                if isfile(value) and not access(value, R_OK):
                    raise ValueError()
                elif not access(dirname(value), W_OK):
                    raise ValueError()
        self._hdf5_outfile = value

    @property
    def image_data_size(self):
        """int: Size of a single image within arrays"""
        if self.image_mode == "8bit":
            return 6400
        elif self.image_mode == "2bit":
            return 12800

    @property
    def image_data_dtype(self):
        """type: Numpy dtype of image arrays"""
        import numpy as np

        if self.image_mode == "8bit":
            return np.int8
        elif self.image_mode == "2bit":
            return np.bool

    @property
    def image_mode(self):
        """str: Image mode"""
        if not hasattr(self, "_image_mode"):
            self._image_mode = "2bit"
        return self._image_mode

    @image_mode.setter
    def image_mode(self, value):
        if value is not None:
            if not isinstance(value, str):
                try:
                    value = str(value)
                except Exception as e:
                    raise ValueError()
            if value not in ["2bit"]:
                raise ValueError()
        self._font_names = value

    @property
    def n_chars(self):
        """int: Number of characters to generate images of"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 100
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if not isinstance(value, int) and value is not None:
            try:
                value = int(value)
            except Exception as e:
                raise ValueError()
        if value < 1 and value is not None:
            raise ValueError()
        self._n_chars = value

    # endregion

    # region Methods
    def generate_char_image(self, character, font="Hei", size=60, width=5,
                            x_offset=0, y_offset=0, tmpfile="/tmp/zysyzm.png"):
        from os import remove
        from matplotlib.font_manager import FontProperties
        from matplotlib.patheffects import Stroke, Normal
        from PIL import Image
        from zysyzm.ocr import (convert_8bit_grayscale_to_2bit, trim_image,
                                resize_image)

        # Draw initial image with matplotlib
        self.figure.clear()
        fp = FontProperties(family=font, size=size)
        text = self.figure.text(x=0.5, y=0.475, s=character,
                                ha="center", va="center",
                                fontproperties=fp,
                                color=(0.67, 0.67, 0.67))
        text.set_path_effects([Stroke(linewidth=width,
                                      foreground=(0.00, 0.00, 0.00)),
                               Normal()])
        self.figure.savefig(tmpfile, dpi=80, transparent=True)

        # Reload with pillow to trim, resize, and adjust color
        img = trim_image(Image.open(tmpfile).convert("L"), 0)
        img = resize_image(img, (80, 80), x_offset, y_offset)
        remove(tmpfile)

        # Convert to configured format
        if self.image_mode == "8bit":
            pass
        elif self.image_mode == "2bit":
            img = convert_8bit_grayscale_to_2bit(img)

        return img

    def generate_char_image_data(self, **kwargs):
        import numpy as np

        img = self.generate_char_image(**kwargs)

        if self.image_mode == "8bit":
            data = np.array(img)
        elif self.image_mode == "2bit":
            raw = np.array(img)
            data = np.append(np.logical_or(raw == 85, raw == 256).flatten(),
                             np.logical_or(raw == 170, raw == 256).flatten())
        else:
            data = None

        return data

    def initialize_from_hdf5(self):
        import pandas as pd
        import h5py
        import numpy as np

        def clean_spec_for_pandas(row):
            """
            Processes specification so that pandas
            """
            return tuple([chr(row[0])] + list(row)[1:])

        if self.verbosity >= 1:
            print(f"Reading data from '{self.hdf5_infile}'")
        with h5py.File(self.hdf5_infile) as hdf5_infile:
            if "char_image_specs" not in hdf5_infile:
                raise ValueError()
            if "char_image_data" not in hdf5_infile:
                raise ValueError()

            # Load configuration
            self.image_mode = hdf5_infile.attrs["mode"]

            # Load character image data
            self.char_image_data = np.array(hdf5_infile["char_image_data"])

            # Load character image specification
            self.char_image_specs = pd.DataFrame(
                index=range(self.char_image_data.shape[0]),
                columns=self.char_image_specs.columns.values)
            self.char_image_specs[:] = list(map(
                clean_spec_for_pandas,
                np.array(hdf5_infile["char_image_specs"])))

    def initialize_from_scratch(self):
        import pandas as pd
        import numpy as np

        # Prepare empty arrays
        self.char_image_specs = pd.DataFrame(
            index=range(self.n_chars),
            columns=self.char_image_specs.columns.values)
        self.char_image_data = np.zeros((self.n_chars, self.image_data_size),
                                        dtype=self.image_data_dtype)

        # Fill in arrays with specs and data
        for i, char in enumerate(self.chars[:self.n_chars]):
            row = self.char_image_specs_available.loc[0].to_dict()
            row["character"] = char
            self.char_image_specs.loc[i] = row
            self.char_image_data[i] = self.generate_char_image_data(**row)

    def save_to_hdf5(self):
        import h5py
        import numpy as np

        def clean_spec_for_hdf5(row):
            """
            Processes specification so that numpy and h5py will accept it
            - Unpacked into a tuple so that numpy can build a record array
            - Characters converted from unicode strings to integers. hdf5 and
              numpy's unicode support do not cooperate well, and this is the
              least painful solution.
            """
            return tuple([ord(row[0])] + list(row[1:]))

        if self.verbosity >= 1:
            print(f"Saving data to '{self.hdf5_outfile}'")
        with h5py.File(self.hdf5_outfile) as hdf5_outfile:
            # Remove prior data
            if "char_image_data" in hdf5_outfile:
                del hdf5_outfile["char_image_data"]
            if "char_image_specs" in hdf5_outfile:
                del hdf5_outfile["char_image_specs"]

            # Save configuration
            hdf5_outfile.attrs["mode"] = self.image_mode

            # Save character image specifications
            char_image_specs = list(map(clean_spec_for_hdf5,
                                        self.char_image_specs.values))
            dtypes = list(zip(self.char_image_specs.columns.values,
                              ["i4", "S10", "i1", "i1", "i1", "i1"]))
            char_image_specs = np.array(char_image_specs, dtype=dtypes)
            hdf5_outfile.create_dataset("char_image_specs",
                                        data=char_image_specs, dtype=dtypes,
                                        chunks=True, compression="gzip")

            # Save character image data
            hdf5_outfile.create_dataset("char_image_data",
                                        data=self.char_image_data,
                                        dtype=self.image_data_dtype,
                                        chunks=True, compression="gzip")

    # endregion