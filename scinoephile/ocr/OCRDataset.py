#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.OCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import OCRCLToolBase
from IPython import embed


################################### CLASSES ###################################
class OCRDataset(OCRCLToolBase):
    """
    Represents a collection of character images

    8bit grayscale to 2bit grayscale:
        0 -> 00
        85 -> 01
        170 -> 10
        256 -> 11

    Todo:
      - [ ] Document
      - [ ] Implement other image data types (8 bit and 1 bit)
    """

    # region Instance Variables

    help_message = ("Represents a collection of character images")

    # endregion

    # region Builtins

    def __init__(self, input_hdf5=None, input_image_dir=None, output_hdf5=None,
                 output_image_dir=None, image_mode=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if input_hdf5 is not None:
            self.input_hdf5 = input_hdf5
        if input_image_dir is not None:
            self.input_image_dir = input_image_dir
        if output_hdf5 is not None:
            self.output_hdf5 = output_hdf5
        if output_image_dir is not None:
            self.output_image_dir = output_image_dir
        if image_mode is not None:
            self.image_mode = image_mode

    def __call__(self):
        """ Core logic """
        pass

    # endregion

    # region Public Properties

    @property
    def specs(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_specs"):
            import pandas as pd

            self._specs = pd.DataFrame({
                c: pd.Series([], dtype=self._spec_dtypes[c])
                for c in self._spec_columns})
        return self._specs

    @specs.setter
    def specs(self, value):
        # Todo: Validate
        self._specs = value
        if hasattr(self, "_specs_set_"):
            delattr(self, "_specs_set_")

    @property
    def data(self):
        """numpy.ndarray(bool): Character image data"""
        if not hasattr(self, "_data"):
            import numpy as np

            self._data = np.zeros((0, self._data_size), self._data_dtype)
        return self._data

    @data.setter
    def data(self, value):
        import numpy as np

        if not isinstance(value, np.ndarray):
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[1] != self._data_size:
            raise ValueError(self._generate_setter_exception(value))
        if value.dtype != self._data_dtype:
            raise ValueError(self._generate_setter_exception(value))
        self._data = value

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
                    raise ValueError(self._generate_setter_exception(value))
            if value == "8bit":
                raise NotImplementedError()
            elif value == "1bit":
                raise NotImplementedError()
            elif value not in ["2bit"]:
                raise ValueError(self._generate_setter_exception(value))

        self._image_mode = value

    @property
    def input_hdf5(self):
        """str: Path to input hdf5 file"""
        if not hasattr(self, "_input_hdf5"):
            self._input_hdf5 = None
        return self._input_hdf5

    @input_hdf5.setter
    def input_hdf5(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._input_hdf5 = value

    @property
    def input_image_dir(self):
        """str: Path to input image directory"""
        if not hasattr(self, "_input_image_dir"):
            self._input_image_dir = None
        return self._input_image_dir

    @input_image_dir.setter
    def input_image_dir(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._input_image_dir = value

    @property
    def output_hdf5(self):
        """str: Path to output hdf5 file"""
        if not hasattr(self, "_output_hdf5"):
            self._output_hdf5 = None
        return self._output_hdf5

    @output_hdf5.setter
    def output_hdf5(self, value):
        from os import access, getcwd, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
            elif isfile(value) and not access(value, R_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif dirname(value) == "" and not access(getcwd(), W_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif not access(dirname(value), W_OK):
                raise ValueError(self._generate_setter_exception(value))
        self._output_hdf5 = value

    @property
    def output_image_dir(self):
        """str: Path to directory for output character images"""
        if not hasattr(self, "_output_image_dir"):
            self._output_image_dir = None
        return self._output_image_dir

    @output_image_dir.setter
    def output_image_dir(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._output_image_dir = value

    # endregion

    # region Private Properties

    @property
    def _spec_columns(self):
        """list(str): Character image specification columns"""
        raise NotImplementedError()

    @property
    def _spec_dtypes(self):
        """list(str): Character image specification columns"""
        raise NotImplementedError()

    @property
    def _specs_set(self):
        if not hasattr(self, "_specs_set_"):
            self._specs_set_ = set(map(tuple, self.specs.values))
        return self._specs_set_

    @property
    def _data_size(self):
        """int: Size of a single image within arrays"""
        if self.image_mode == "8bit":
            return 6400
        elif self.image_mode == "2bit":
            return 12800
        elif self.image_mode == "1bit":
            return 6400

    @property
    def _data_dtype(self):
        """type: Numpy dtype of image arrays"""
        import numpy as np

        if self.image_mode == "8bit":
            return np.int8
        elif self.image_mode == "2bit":
            return np.bool
        elif self.image_mode == "1bit":
            return np.bool

    # endregion

    # region Public Methods

    def add_images(self, specs, data):
        import numpy as np

        new = specs.apply(
            lambda x: tuple(x.values) not in self._specs_set,
            axis=1).values
        if new.sum() >= 1:
            self.specs = self.specs.append(specs.loc[new],
                                           ignore_index=True, sort=False)
            self.data = np.append(self.data, data[new], axis=0)

    def data_to_image(self, data):
        import numpy as np
        from PIL import Image

        if self.image_mode == "8bit":
            raise NotImplementedError()
        elif self.image_mode == "2bit":
            raw = np.zeros((self._data_size // 2), np.uint8)
            raw[np.logical_and(data[0::2] == False, data[1::2] == True)] = 85
            raw[np.logical_and(data[0::2] == True, data[1::2] == False)] = 170
            raw[np.logical_and(data[0::2] == True, data[1::2] == True)] = 255
            raw = raw.reshape((int(np.sqrt(raw.size)), int(np.sqrt(raw.size))))
            image = Image.fromarray(raw, mode="L")
        elif self.image_mode == "1bit":
            raise NotImplementedError()

        return image

    def image_to_data(self, image):
        import numpy as np

        if self.image_mode == "8bit":
            data = np.array(image).flatten()
        elif self.image_mode == "2bit":
            raw = np.array(image).flatten()
            data = np.zeros((2 * raw.size), np.bool)
            data[0::2][np.logical_or(raw == 170, raw == 255)] = True
            data[1::2][np.logical_or(raw == 85, raw == 255)] = True
        elif self.image_mode == "1bit":
            raise NotImplementedError()

        return data

    def read_hdf5(self):
        import pandas as pd
        import h5py
        import numpy as np


        # TODO: Validate that hdf5 file can be read

        if self.verbosity >= 1:
            print(f"Reading data from '{self.input_hdf5}'")
        with h5py.File(self.input_hdf5) as hdf5_infile:
            if "specs" not in hdf5_infile:
                raise ValueError()
            if "data" not in hdf5_infile:
                raise ValueError()

            # Load configuration (Todo: Validate that mode matches current)
            self.image_mode = hdf5_infile.attrs["mode"]

            # Load specs
            formatter = self._get_hdf5_input_spec_formatter(
                hdf5_infile["specs"].dtype.names)
            char_image_specs = pd.DataFrame(
                data=list(map(formatter,
                              np.array(hdf5_infile["specs"]))),
                index=range(hdf5_infile["specs"].size),
                columns=hdf5_infile["specs"].dtype.names)

            # Load data
            char_image_data = np.array(hdf5_infile["data"])

        self.add_images(char_image_specs, char_image_data)

    def read_image_dir(self):
        import numpy as np
        from PIL import Image
        from scinoephile.ocr import convert_8bit_grayscale_to_2bit

        # TODO: Validate that directory can be read

        if self.verbosity >= 1:
            print(f"Reading images from '{self.input_image_dir}'")

        # Prepare list of infiles
        infiles = self._list_image_dir_input_files(self.input_image_dir)

        # Prepare specs
        specs = self._get_image_dir_input_specs(infiles)

        # Prepare data
        data = np.zeros((len(infiles), self._data_size), self._data_dtype)
        for i, infile in enumerate(infiles):
            image = Image.open(infile)
            if self.image_mode == "8bit":
                pass
            elif self.image_mode == "2bit":
                image = convert_8bit_grayscale_to_2bit(image)
            elif self.image_mode == "1bit":
                raise NotImplementedError()
            data[i] = self.image_to_data(image)

        self.add_images(specs, data)

    def show_data_old(self, data):
        def data_to_image(data):
            import numpy as np
            from PIL import Image

            raw = np.zeros((6400), np.uint8)
            bit1 = data[:6400]
            bit2 = data[6400:]
            raw[np.logical_and(np.logical_not(bit2), bit1)] = 85
            raw[np.logical_and(bit2, np.logical_not(bit1))] = 170
            raw[np.logical_and(bit2, bit1)] = 255
            raw = raw.reshape((int(np.sqrt(raw.size)), int(np.sqrt(raw.size))))
            image = Image.fromarray(raw, mode="L")

            return image

        data_to_image(data).show()

    def show_data(self, data):
        self.data_to_image(data).show()

    def show_chars(self, indexes, columns=None):
        import numpy as np
        from PIL import Image

        # Process arguments
        if isinstance(indexes, int):
            indexes = [indexes]
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= self.data.shape[0]):
            raise ValueError()
        if columns is None:
            columns = indexes.size
            rows = 1
        else:
            rows = int(np.ceil(indexes.size / columns))

        # Draw image
        image = Image.new("L", (columns * 100, rows * 100), 255)
        for i, index in enumerate(indexes):
            column = (i // columns)
            row = i - (column * columns)
            char_image = self.data_to_image(self.data[index])
            image.paste(char_image,
                        (100 * row + 10,
                         100 * column + 10,
                         100 * (row + 1) - 10,
                         100 * (column + 1) - 10))
        image.show()

    def write_hdf5(self):
        import h5py
        import numpy as np

        if self.verbosity >= 1:
            print(f"Writing data to '{self.output_hdf5}'")
        with h5py.File(self.output_hdf5) as hdf5_outfile:
            # Remove preexisting data
            if "data" in hdf5_outfile:
                del hdf5_outfile["data"]
            if "specs" in hdf5_outfile:
                del hdf5_outfile["specs"]

            # Save configuration
            hdf5_outfile.attrs["mode"] = self.image_mode

            # Save specs
            # Todo: Check if 'columns.values' can just be 'columns'
            formatter = self._get_hdf5_output_spec_formatter(
                self.specs.columns.values)
            dtypes = self._get_hdf5_spec_dtypes(
                self.specs.columns.values)
            hdf5_outfile.create_dataset(
                "specs",
                data=np.array(list(map(formatter, self.specs.values)),
                              dtype=dtypes),
                dtype=dtypes,
                chunks=True,
                compression="gzip")

            # Save data
            hdf5_outfile.create_dataset(
                "data",
                data=self.data,
                dtype=self._data_dtype,
                chunks=True,
                compression="gzip")

    def write_image_dir(self):
        from os import makedirs
        from os.path import dirname, isdir

        if self.verbosity >= 1:
            print(f"Writing images to '{self.output_image_dir}'")
        outfile_path_formatter = self._get_image_dir_outfile_formatter(
            self.specs)
        outfiles = map(outfile_path_formatter, self.specs.iterrows())
        for outfile, data in zip(outfiles, self.data):
            if self.verbosity >= 2:
                print(f"Writing '{outfile}'")
            if not isdir(dirname(outfile)):
                makedirs(dirname(outfile))
            self.data_to_image(data).save(outfile)

    # endregion

    # region Private Methods

    def _get_hdf5_input_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        raise NotImplementedError()

    def _list_image_dir_input_files(self, path):
        """Provides infiles within path"""
        raise NotImplementedError()

    def _get_image_dir_input_specs(self, infiles):
        """Provides specs of infiles"""
        raise NotImplementedError()

    def _get_hdf5_spec_dtypes(self, columns):
        """Provides spec dtypes compatible with both numpy and h5py"""
        raise NotImplementedError()

    def _get_hdf5_output_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        raise NotImplementedError()

    def _get_image_dir_outfile_formatter(self, specs):
        """Provides formatter for image outfile paths"""
        raise NotImplementedError()

    # endregion