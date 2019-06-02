#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.__init__.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import re
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from os.path import dirname
from sys import modules
from IPython import embed

################################## CONSTANTS ##################################
package_root = dirname(modules[__name__].__file__)


################################## FUNCTIONS ##################################
def embed_kw(verbosity=2, **kwargs):
    """dict: use ``IPython.embed(**embed_kw())`` for more useful prompt"""
    from inspect import currentframe, getframeinfo
    from os.path import dirname
    from sys import modules

    package_root = dirname(modules[__name__].__file__)
    frameinfo = getframeinfo(currentframe().f_back)
    file = frameinfo.filename.replace(package_root, "")
    func = frameinfo.function
    number = frameinfo.lineno - 1
    header = ""
    if verbosity >= 1:
        header = f"IPython prompt in file {file}, function {func}," \
            f" line {number}\n"
    if verbosity >= 2:
        header += "\n"
        with open(frameinfo.filename, "r") as infile:
            lines = [(i, line) for i, line in enumerate(infile)
                     if i in range(number - 5, number + 6)]
        for i, line in lines:
            header += f"{i:5d} {'>' if i == number else ' '} " \
                f"{line.rstrip()}\n"

    return {"header": header}


def in_ipython():
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            # IPython in Jupyter Notebook
            return shell
        elif shell == "InteractiveShellEmbed":
            # IPython in Jupyter Notebook using IPython.embed
            return shell
        elif shell == "TerminalInteractiveShell":
            # IPython in terminal
            return shell
        else:
            # Other
            return False
    except NameError:
        # Not in IPython
        return False


def merge_subtitles(upper, lower):
    def add_event(merged):
        if start != time:
            if upper_text is None:
                merged += [pd.DataFrame.from_records(
                    [(start, time, lower_text)],
                    columns=["start", "end", "lower text"])]
            elif lower_text is None:
                merged += [pd.DataFrame.from_records(
                    [(start, time, upper_text)],
                    columns=["start", "end", "upper text"])]
            else:
                merged += [pd.DataFrame.from_records(
                    [(start, time, upper_text, lower_text)],
                    columns=["start", "end", "upper text", "lower text"])]

    if isinstance(upper, SubtitleSeries):
        upper = upper.get_dataframe()
    if isinstance(lower, SubtitleSeries):
        lower = lower.get_dataframe()

    transitions = []
    for _, event in upper.iterrows():
        transitions += [[event["start"], "upper_start", event["text"]],
                        [event["end"], "upper_end", None]]
    for _, event in lower.iterrows():
        transitions += [[event["start"], "lower_start", event["text"]],
                        [event["end"], "lower_end", None]]
    transitions.sort()

    merged = []

    start = upper_text = lower_text = None
    for time, kind, text in transitions:
        if kind == "upper_start":
            if start is None:
                # Transition from __ -> C_
                pass
            else:
                # Transition from _E -> CE
                add_event(merged)
            upper_text = text
            start = time
        elif kind == "upper_end":
            add_event(merged)
            upper_text = None
            if lower_text is None:
                # Transition from C_ -> __
                start = None
            else:
                # Transition from CE -> _C
                start = time
        elif kind == "lower_start":
            if start is None:
                # Transition from __ -> _E
                pass
            else:
                # Transition from C_ -> CE
                add_event(merged)
            lower_text = text
            start = time
        elif kind == "lower_end":
            add_event(merged)
            lower_text = None
            if upper_text is None:
                # Transition from _E -> __
                start = None
            else:
                # Transition from CE -> E_
                start = time

    merged_df = pd.concat(merged, sort=False, ignore_index=True)[
        ["upper text", "lower text", "start", "end"]]

    synced_df = [merged_df.iloc[0].copy()]
    for index in range(1, merged_df.index.size):
        last = synced_df[-1]
        next = merged_df.iloc[index].copy()
        if last["upper text"] == next["upper text"]:
            if isinstance(last["lower text"], float) and np.isnan(
                    last["lower text"]):
                # Upper started before lower
                last["lower text"] = next["lower text"]
                last["end"] = next["end"]
            elif isinstance(next["lower text"], float) and np.isnan(
                    next["lower text"]):
                # Lower started before upper
                last["end"] = next["end"]
            else:
                # Single upper subtitle given two lower subtitles
                gap = next["start"] - last["end"]
                if gap < 500:
                    # Probably long upper split into two lower
                    last["end"] = next["start"] = last["end"] + (gap / 2)
                # Otherwise, probably upper repeated with different lower
                synced_df += [next]
        elif last["lower text"] == next["lower text"]:
            if isinstance(last["upper text"], float) and np.isnan(
                    last["upper text"]):
                # Lower started before upper
                last["upper text"] = next["upper text"]
                last["end"] = next["end"]
            elif isinstance(next["upper text"], float) and np.isnan(
                    next["upper text"]):
                # Upper started before lower
                if last.end < next["start"]:
                    synced_df += [next]
                else:
                    last["end"] = next["end"]
            else:
                gap = next["start"] - last["end"]
                if gap < 500:
                    # Probably long lower split into two upper
                    last["end"] = next["start"] = last["end"] + (gap / 2)
                # Otherwise, probably lower repeated with different upper
                synced_df += [next]
        else:
            synced_df += [next]

    return pd.DataFrame(synced_df)


################################### CLASSES ###################################
class Base(ABC):
    """Base including convenience methods and properties"""

    # region Builtins

    def __init__(self, verbosity=None, **kwargs):
        """
        Initializes class

        Args:
            verbosity (int): Level of verbose output
            kwargs (dict): Additional keyword arguments
        """

        # Store property values
        if verbosity is not None:
            self.verbosity = verbosity

    # endregion

    # region Properties

    @property
    def embed_kw(self):
        """dict: use ``IPython.embed(**self.embed_kw)`` for more useful prompt"""
        from inspect import currentframe, getframeinfo

        frameinfo = getframeinfo(currentframe().f_back)
        file = frameinfo.filename.replace(package_root, "")
        func = frameinfo.function
        number = frameinfo.lineno - 1
        header = ""

        if self.verbosity >= 1:
            header = f"IPython prompt in file {file}, function {func}," \
                f" line {number}\n"
        if self.verbosity >= 2:
            header += "\n"
            with open(frameinfo.filename, "r") as infile:
                lines = [(i, line) for i, line in enumerate(infile)
                         if i in range(number - 5, number + 6)]
            for i, line in lines:
                header += f"{i:5d} {'>' if i == number else ' '} " \
                    f"{line.rstrip()}\n"

        return {"header": header}

    @property
    def verbosity(self):
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        if not isinstance(value, int) and value >= 0:
            raise ValueError(self._generate_setter_exception(value))
        self._verbosity = value

    # endregion

    # region Private methods

    def _generate_setter_exception(self, value):
        """
        Generates Exception text for setters that are passed invalid values

        Returns:
            str: Exception text
        """
        from inspect import currentframe, getframeinfo

        frameinfo = getframeinfo(currentframe().f_back)
        return f"Property '{type(self).__name__}.{frameinfo.function}' " \
            f"was passed invalid value '{value}' " \
            f"of type '{type(value).__name__}'. " \
            f"Expects '{getattr(type(self), frameinfo.function).__doc__}'."

    # endregion


class CLToolBase(Base, ABC):
    """Base for command line tools"""

    # region Builtins

    @abstractmethod
    def __call__(self):
        """ Core logic """
        pass

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, parser=None):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        if parser is None:
            if hasattr(cls, "helptext"):
                description = cls.helptext
            else:
                try:
                    description = cls.__doc__.split("\n")[1].strip()
                except IndexError:
                    description = cls.__doc__
            parser = argparse.ArgumentParser(description=description)

        # General
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument("-v", "--verbose", action="count",
                               dest="verbosity", default=1,
                               help="enable verbose output, may be specified "
                                    "more than once")
        verbosity.add_argument("-q", "--quiet", action="store_const",
                               dest="verbosity", const=0,
                               help="disable verbose output")

        return parser

    @classmethod
    def validate_args(cls, parser, args):
        """
        Validates arguments provided to an argument parser

        Args:
            parser (argparse.ArgumentParser): Argument parser
            args (argparse.Namespace): Arguments
        """
        pass

    # endregion

    @classmethod
    def main(cls):
        """Parses and validates arguments, constructs and calls object"""

        parser = cls.construct_argparser()
        args = parser.parse_args()
        cls.validate_args(parser, args)
        cls(**vars(args))()


class StdoutLogger(object):
    """Logs print statements to both stdout and file; use with 'with'"""

    # region Builtins

    def __init__(self, outfile, mode, process_carriage_returns=True):
        import sys

        self.process_carriage_returns = process_carriage_returns

        self.file = open(outfile, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __enter__(self):
        pass

    def __exit__(self, _type, _value, _traceback):
        import sys

        sys.stdout = self.stdout
        self.file.close()

        if self.process_carriage_returns:
            from io import open
            from re import sub
            from shutil import copyfile
            from tempfile import NamedTemporaryFile

            with open(self.file.name, "r", newline="\n") as file:
                with NamedTemporaryFile("w") as temp:
                    for i, line in enumerate(file):
                        temp.write(sub("^.*\r", "", line))
                    temp.flush()
                    copyfile(temp.name, f"{file.name}")

    # endregion

    # region Public Methods

    def flush(self):
        self.file.flush()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    # endregion


################################## MODULES ###################################
from scinoephile.SubtitleEvent import SubtitleEvent
from scinoephile.SubtitleSeries import SubtitleSeries
