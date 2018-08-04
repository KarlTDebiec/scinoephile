#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.__init__.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### CLASSES ###################################
class CLToolBase(object):
    """ Base for command line tools """

    # region Instance Variables
    help_message = ("Base for common line tools")

    # endregion

    # region Builtins
    def __init__(self, verbosity=1, interactive=False, **kwargs):
        """

        Args:
            verbosity (int): Level of verbose output
            interactive (bool): Show IPython prompt
            kwargs (dict): Additional keyword arguments
        """
        self.verbosity = verbosity
        self.interactive = interactive

    # endregion

    # region Properties
    @property
    def directory(self):
        """str: Path to this Python file"""
        if not hasattr(self, "_directory"):
            import os
            self._directory = os.path.dirname(os.path.realpath(__file__))
        return self._directory

    @property
    def interactive(self):
        """bool: Present IPython prompt after processing subtitles"""
        if not hasattr(self, "_interactive"):
            self._interactive = False
        return self._interactive

    @interactive.setter
    def interactive(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._interactive = value

    @property
    def verbosity(self):
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        if not isinstance(value, int) and value >= 0:
            raise ValueError()
        self._verbosity = value

    # endregion Properties

    # region Class Methods
    @classmethod
    def construct_argparser(cls, parser=None):
        """
        Prepares argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        if parser is None:
            parser = argparse.ArgumentParser(description=cls.help_message)

        # General
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument("-v", "--verbose", action="count",
                               dest="verbosity", default=1,
                               help="enable verbose output, may be specified "
                                    "more than once")
        verbosity.add_argument("-q", "--quiet", action="store_const",
                               dest="verbosity", const=0,
                               help="disable verbose output")
        parser.add_argument("-i", "--interactive", action="store_true",
                            dest="interactive",
                            help="present IPython prompt")

        return parser

    @classmethod
    def validate_args(cls, parser, args):
        """
        Validates arguments

        Args:
            parser (argparse.ArgumentParser): Argument parser
            args (argparse.Namespace): Arguments
        """
        pass

    # endregion

    @classmethod
    def main(cls):
        """ Parses and validates arguments, constructs and calls object """

        parser = cls.construct_argparser()
        args = parser.parse_args()
        cls.validate_args(parser, args)
        if hasattr(cls, "__call__"):
            cls(**vars(args))()