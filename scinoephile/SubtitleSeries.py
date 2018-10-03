#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.SubtitleSeries.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from pysubs2 import SSAFile
from scinoephile import Base
from IPython import embed


################################### CLASSES ###################################
class SubtitleSeries(SSAFile, Base):
    """
    Extension of pysubs2's SSAFile with additional features

    TODO:
      - [ ] Print as a pandas table
      - [ ] Document
    """

    # region Builtins

    def __init__(self, verbosity=None):
        super().__init__()

        if verbosity is not None:
            self.verbosity = verbosity

    def __repr__(self):
        if self.events:
            from pysubs2.time import ms_to_str

            return f"<{self.__class__.__name__} with {len(self):d} events " \
                   f"and {len(self.styles):d} styles, " \
                   f"last timestamp {ms_to_str(max(e.end for e in self)):s}>"
        else:
            return f"<SubtitleSeries with 0 events " \
                   f"and {len(self.styles):d} styles>"

    # endregion

    # region Public Methods

    def save(self, path, format_=None, **kwargs):
        """
        SSAFile.save expects an open text file, so we open hdf5 here
        """

        # Check if hdf5
        if (format_ == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py
            from scinoephile import HDF5Format

            if self.verbosity >= 1:
                print(f"Saving to '{path}' as hdf5")
            with h5py.File(path) as fp:
                HDF5Format.to_file(self, fp, format_=format_,
                                   verbosity=self.verbosity, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            if self.verbosity >= 1:
                print(f"Saving to '{path}'")
            SSAFile.save(self, path, format_=format_, **kwargs)

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, path, encoding="utf-8", verbosity=1, **kwargs):
        """
        SSAFile.from_file expects an open text file, so we open hdf5 here
        """

        # Check if hdf5
        if (encoding == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py
            from scinoephile import HDF5Format

            if verbosity >= 1:
                print(f"Loading from '{path}' as hdf5")
            with h5py.File(path) as fp:
                subs = cls()
                subs.format = "hdf5"
                return HDF5Format.from_file(subs, fp,
                                            verbosity=verbosity, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            if verbosity >= 1:
                print(f"Loading from '{path}'")
            with open(path, encoding=encoding) as fp:
                return cls.from_file(fp, **kwargs)

    # endregion