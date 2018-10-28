#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.ImageSubtitleSeries.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import SubtitleSeries
from scinoephile.ocr import ImageSubtitleEvent
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleSeries(SubtitleSeries):
    """
    A series of image-based subtitles
    """

    # region Class Attributes

    event_class = ImageSubtitleEvent

    # endregion

    # region Builtins

    def __init__(self, imgmode=None, **kwargs):
        super().__init__()

        # Store property values
        if imgmode is not None:
            self.imgmode = imgmode

    # endregion

    # region Public Properties

    @property
    def imgmode(self):
        """str: Image mode"""
        if not hasattr(self, "_mode"):
            self._imgmode = "1 bit"
        return self._imgmode

    @imgmode.setter
    def imgmode(self, value):
        if value is not None:
            if not isinstance(value, str):
                try:
                    value = str(value)
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
            if value == "8 bit":
                pass
            elif value == "1 bit":
                pass
            else:
                raise ValueError(self._generate_setter_exception(value))
        # TODO: If changed, change on events

        self._imgmode = value

    # endregion

    # region Public Methods

    def save(self, path, format_=None, **kwargs):
        """
        Saves subtitles to an output file, warning that data will be lost if
        not saved to hdf5

        pysubs2.SSAFile.save expects an open text file, so we open the hdf5
        file here for consistency.
        """

        # Check if hdf5
        if (format_ == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py

            if self.verbosity >= 1:
                print(f"Saving to '{path}' as hdf5")
            with h5py.File(path) as fp:
                self._save_hdf5(fp, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            from warnings import warn
            from pysubs2 import SSAFile

            warn(f"{self.__class__.__name__}'s image data may only be saved"
                 f"to hdf5")
            if self.verbosity >= 1:
                print(f"Saving to '{path}'")
            SSAFile.save(self, path, format_=format_, **kwargs)

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, path, encoding="utf-8", imgmode=None, verbosity=1, **kwargs):
        """
        SSAFile.from_file expects an open text file, so we open hdf5 here
        """

        # Check if hdf5
        if (encoding == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py

            with h5py.File(path) as fp:
                return cls._load_hdf5(fp, imgmode=imgmode,
                                      verbosity=verbosity, **kwargs)
        # Check if sup
        if encoding == "sup" or path.endswith("sup"):
            with open(path, "rb") as fp:
                return cls._load_sup(fp, imgmode=imgmode,
                                     verbosity=verbosity, **kwargs)
        # Otherwise, use SSAFile.from_file
        else:
            with open(path, encoding=encoding) as fp:
                subs = cls.from_file(fp, **kwargs)
                subs.verbosity = verbosity
                return subs

    # endregion

    # region Private Methods

    def _save_hdf5(self, fp, **kwargs):
        """
        Saves subtitles to an output hdf5 file

        .. todo::
          - [ ] Save project info
        """
        import numpy as np

        # Save info, styles and subtitles
        SubtitleSeries._save_hdf5(self, fp, **kwargs)

        # Save images
        if "images" in fp:
            del fp["images"]
        fp.create_group("images")
        fp["images"].attrs["mode"] = self.imgmode
        for i, event in enumerate(self.events):
            if hasattr(event, "data"):
                if event.mode == "8 bit":
                    fp["images"].create_dataset(f"{i:04d}",
                                                data=event.data,
                                                dtype=np.uint8, chunks=True,
                                                compression="gzip")
                elif event.mode == "1 bit":
                    fp["images"].create_dataset(f"{i:04d}",
                                                data=event.data,
                                                dtype=np.bool, chunks=True,
                                                compression="gzip")

    # endregion

    # region Private Class Methods

    @classmethod
    def _load_hdf5(cls, fp, imgmode=None, verbosity=1, **kwargs):
        """
        Loads subtitles from an hdf5 file into a nascent SubtitleSeries

        .. todo::
          - [ ] Load project info
        """
        import numpy as np

        # Load info, styles, and events
        subs = super()._load_hdf5(fp=fp, verbosity=verbosity, **kwargs)

        # Load images
        if "images" in fp and "events" in fp:
            subs.mode = fp["images"].attrs["mode"]
            if imgmode is not None and subs.mode != imgmode:
                raise ValueError()

            for i, event in enumerate(subs.events):
                event.mode = subs.mode
                if subs.mode == "8 bit":
                    event.data = np.array(fp["images"][f"{i:04d}"], np.uint8)
                elif subs.mode == "1 bit":
                    event.data = np.array(fp["images"][f"{i:04d}"], np.bool)

        return subs

    @classmethod
    def _load_sup(cls, fp, imgmode=None, verbosity=1, **kwargs):
        import numpy as np
        from pysubs2.time import make_time

        def read_palette(bytes):
            import numpy as np

            palette = np.zeros((256, 4), np.uint8)
            bytes_index = 0
            while bytes_index < len(bytes):
                color_index = bytes[bytes_index]
                y = bytes[bytes_index + 1]
                cb = bytes[bytes_index + 2]
                cr = bytes[bytes_index + 3]
                palette[color_index, 0] = y + 1.402 * (cr - 128)
                palette[color_index, 1] = y - .34414 * (cb - 128) - .71414 * (cr - 128)
                palette[color_index, 2] = y + 1.772 * (cb - 128)
                palette[color_index, 3] = bytes[bytes_index + 4]
                bytes_index += 5
            palette[255] = [16, 128, 128, 0]

            return palette

        def read_image(bytes, width, height):
            import numpy as np

            img = np.zeros((width * height), np.uint8)
            bytes_index = 0
            pixel_index = 0
            while bytes_index < len(bytes):
                byte_1 = bytes[bytes_index]
                if byte_1 == 0x00:  # 00 | Special behaviors
                    byte_2 = bytes[bytes_index + 1]
                    if byte_2 == 0x00:  # 00 00 | New line
                        bytes_index += 2
                    elif (byte_2 & 0xC0) == 0x40:  # 00 4X XX | 0 X times
                        byte_3 = bytes[bytes_index + 2]
                        n_pixels = ((byte_2 - 0x40) << 8) + byte_3
                        color = 0
                        img[pixel_index:pixel_index + n_pixels] = color
                        pixel_index += n_pixels
                        bytes_index += 3
                    elif (byte_2 & 0xC0) == 0x80:  # 00 8Y XX | X Y times
                        byte_3 = bytes[bytes_index + 2]
                        n_pixels = byte_2 - 0x80
                        color = byte_3
                        img[pixel_index:pixel_index + n_pixels] = color
                        pixel_index += n_pixels
                        bytes_index += 3
                    elif (byte_2 & 0xC0) != 0x00:  # 00 CY YY XX | X Y times
                        byte_3 = bytes[bytes_index + 2]
                        byte_4 = bytes[bytes_index + 3]
                        n_pixels = ((byte_2 - 0xC0) << 8) + byte_3
                        color = byte_4
                        img[pixel_index:pixel_index + n_pixels] = color
                        pixel_index += n_pixels
                        bytes_index += 4
                    else:  # 00 XX | 0 X times
                        n_pixels = byte_2
                        color = 0
                        img[pixel_index:pixel_index + n_pixels] = color
                        pixel_index += n_pixels
                        bytes_index += 2
                else:  # XX | X once
                    color = byte_1
                    img[pixel_index] = color
                    pixel_index += 1
                    bytes_index += 1
            img.resize((height, width))

            return img

        bytes2int = lambda x: int.from_bytes(x, byteorder="big")
        segment_kinds = {0x14: "PDS", 0x15: "ODS", 0x16: "PCS",
                         0x17: "WDS", 0x80: "END"}

        # initialize
        subs = cls(imgmode=imgmode, verbosity=verbosity)
        subs.format = "sup"

        # Parse infile
        sup_bytes = fp.read()
        byte_offset = 0
        start_time = None
        imgdata = None
        palette = None
        compressed_img = None
        if verbosity >= 2:
            print(f"KIND   :     START      TIME      SIZE    OFFSET")
        while True:
            if bytes2int(sup_bytes[byte_offset:byte_offset + 2]) != 0x5047:
                raise ValueError()

            header_offset = byte_offset
            timestamp = bytes2int(sup_bytes[header_offset + 2:header_offset + 6])
            segment_kind = sup_bytes[header_offset + 10]
            content_size = bytes2int(sup_bytes[header_offset + 11: header_offset + 13])
            content_offset = header_offset + 13

            if segment_kind == 0x14:  # Palette
                palette_bytes = sup_bytes[content_offset + 2:content_offset + content_size]
                palette = read_palette(palette_bytes)
            elif segment_kind == 0x15:  # Image
                imgbytes = sup_bytes[content_offset + 11:content_offset + content_size]
                width = bytes2int(sup_bytes[content_offset + 7:content_offset + 9])
                height = bytes2int(sup_bytes[content_offset + 9:content_offset + 11])
                compressed_img = read_image(imgbytes, width, height)
            elif segment_kind == 0x80:  # End
                if start_time is None:
                    start_time = timestamp / 90000
                    imgdata = np.zeros((*compressed_img.shape, 4), np.uint8)
                    for color_index, color in enumerate(palette):
                        imgdata[np.where(compressed_img == color_index)] = color
                else:
                    end_time = timestamp / 90000
                    subs.events.append(cls.event_class(
                        start=make_time(s=start_time),
                        end=make_time(s=end_time),
                        imgmode=imgmode,
                        imgdata=imgdata))

                    start_time = None
                    palette = None
                    compressed_img = None

            if verbosity >= 2:
                print(f"{segment_kinds.get(segment_kind, 'UNKNOWN'):<8s} "
                      f"{hex(segment_kind)}: "
                      f"{header_offset:>9d} "
                      f"{timestamp:>9d} "
                      f"{content_size:>9d} "
                      f"{content_offset:>9d} ")

            byte_offset += 13 + content_size
            if byte_offset >= len(sup_bytes):  # >= 100000:
                break

        return subs

    # endregion
