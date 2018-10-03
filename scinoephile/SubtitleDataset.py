#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.SubtitleDataset.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import CLToolBase
from IPython import embed


################################### CLASSES ###################################
class SubtitleDataset(CLToolBase):
    """
    Represents a collection of subtitles

    Design for loading and saving data
        Dataset
            read method passes infile to SubtitleSeries.load
            write method passes outfile to SubtitleSeries.save
        SubtitleSeries
            load class method passes open infile and subs to from_file
            save method passes open outfile and subs to to_file
            from_file identifies format and passes open infile and subs to Format.from_file
            to_file identifies format and passes open outfile and subs to Format.to_file
        Format
            from_file class method loads from open infile into provided subs
            to_file class method writes from provided subs to open outfile

    TODO:
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of subtitles")

    # endregion

    # region Builtins

    def __init__(self, infile=None, outfile=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if infile is not None:
            self.infile = infile
        if outfile is not None:
            self.outfile = outfile

        # Temporary manual configuration for testing
        self.infile = \
            "/Users/kdebiec/Dropbox/code/subtitles/" \
            "youth/" \
            "Youth.en-US.srt"
        self.outfile = \
            "/Users/kdebiec/Dropbox/code/subtitles/" \
            "youth/" \
            "youth.hdf5"

    def __call__(self):
        """ Core logic """

        # Input
        if self.infile is not None:
            self.read()

        # Output
        if self.outfile is not None:
            self.write()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Public Properties

    @property
    def infile(self):
        """str: Path to input file"""
        if not hasattr(self, "_infile"):
            self._infile = None
        return self._infile

    @infile.setter
    def infile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._infile = value

    @property
    def outfile(self):
        """str: Path to output file"""
        if not hasattr(self, "_outfile"):
            self._outfile = None
        return self._outfile

    @outfile.setter
    def outfile(self, value):
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
        self._outfile = value

    @property
    def subtitles(self):
        """pandas.core.frame.DataFrame: Subtitles"""
        if not hasattr(self, "_subtitles"):
            self._subtitles = self._series_class(verbosity=self.verbosity)
        return self._subtitles

    @subtitles.setter
    def subtitles(self, value):
        if value is not None:
            if not isinstance(value, self._series_class):
                raise ValueError()
        self._subtitles = value

    # endregion

    # region Private Properties

    @property
    def _series_class(self):
        from scinoephile import SubtitleSeries

        return SubtitleSeries

    # endregion

    # region Public Methods

    def read(self, infile=None):
        from os.path import expandvars

        # Process arguments
        if infile is not None:
            infile = expandvars(infile)
        elif self.infile is not None:
            infile = self.infile
        else:
            raise ValueError()

        # Load infile
        if self.verbosity >= 1:
            print(f"Reading subtitles from '{infile}'")
        self.subtitles = self._series_class.load(infile)
        self.subtitles.verbosity = self.verbosity

    def write(self, outfile=None):
        from os.path import expandvars

        # Process argments
        if outfile is not None:
            outfile = expandvars(outfile)
        elif self.outfile is not None:
            outfile = self.outfile
        else:
            raise ValueError()

        # Write outfile
        if self.verbosity >= 1:
            print(f"Writing subtitles to '{outfile}'")
        self.subtitles.save(outfile)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    SubtitleDataset.main()
