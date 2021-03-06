#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_subcmd_config.py

Test config subcommand for pdp.py script

This test suite is intended to be run from the repository root using:

nosetests -v

Individual test classes can be run using, e.g.:

$ nosetests -v tests/test_subcommands.py:TestConfigSubcommand

Each command CMD available at the command-line as pdp.py <CMD> is
tested in its own class (subclassing unittest.TestCase), where the
setUp() method defines input/output files, a null logger (picked up
by nosetests), and a dictionary of command lines, keyed by test name
with values that represent the command-line options.

For each test, command-line options are defined in a Namespace,
and passed as the sole argument to the appropriate subcommand
function from subcommands.py.

(c) The James Hutton Institute 2017
Author: Leighton Pritchard

Contact:
leighton.pritchard@hutton.ac.uk

Leighton Pritchard,
Information and Computing Sciences,
James Hutton Institute,
Errol Road,
Invergowrie,
Dundee,
DD6 9LH,
Scotland,
UK

The MIT License

Copyright (c) 2017 The James Hutton Institute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import json
import logging
import os
import unittest

from argparse import Namespace

from nose.tools import assert_equal, raises

from diagnostic_primers.scripts import subcommands

from tools import (assert_dirfiles_equal, ordered)


class TestConfigSubcommand(unittest.TestCase):
    """Class defining tests of the pdp.py config subcommand."""

    def setUp(self):
        """Set parameters for tests."""
        self.datadir = os.path.join('tests', 'test_input', 'config')
        self.outdir = os.path.join('tests', 'test_output', 'config')
        self.targetdir = os.path.join('tests', 'test_targets', 'config')
        self.tsv_to_json_fname = os.path.join(self.outdir,
                                              'tab_converted_conf.json')
        self.tsv_to_json_target = os.path.join(self.targetdir,
                                               'tab_converted_conf.json')
        self.json_to_tsv_fname = os.path.join(self.outdir,
                                              'json_converted_conf.tab')
        self.json_to_tsv_target = os.path.join(self.targetdir,
                                               'json_converted_conf.tab')
        self.fixed_fname = os.path.join(self.outdir, 'seqfixed_conf.json')
        self.fixed_target = os.path.join(self.targetdir, 'seqfixed_conf.json')

        # null logger instance that does nothing
        self.logger = logging.getLogger('TestConfigSubcommand logger')
        self.logger.addHandler(logging.NullHandler())

        # Dictionary of command-line namespaces
        self.argsdict = {
            'validate_json_good':
            Namespace(
                infilename=os.path.join(self.datadir, 'testconf.json'),
                verbose=True,
                validate=True,
                fix_sequences=False,
                to_json=False,
                to_tab=False),
            'validate_tsv_good':
            Namespace(
                infilename=os.path.join(self.datadir, 'testconf.tab'),
                verbose=True,
                validate=True,
                fix_sequences=False,
                to_json=False,
                to_tab=False),
            'validate_config_bad':
            Namespace(
                infilename=os.path.join(self.datadir, 'testin.conf'),
                verbose=True,
                validate=True,
                fix_sequences=False,
                to_json=False,
                to_tab=False),
            'tab_to_json':
            Namespace(
                infilename=os.path.join(self.datadir, 'testconf.json'),
                verbose=True,
                validate=False,
                fix_sequences=False,
                to_json=self.tsv_to_json_fname,
                to_tab=False),
            'json_to_tab':
            Namespace(
                infilename=os.path.join(self.datadir, 'testconf.tab'),
                verbose=True,
                validate=False,
                fix_sequences=False,
                to_json=False,
                to_tab=self.json_to_tsv_fname),
            'fix_sequences':
            Namespace(
                infilename=os.path.join(self.datadir, 'testconf.json'),
                verbose=True,
                validate=False,
                fix_sequences=self.fixed_fname,
                to_json=False,
                to_tab=False),
            'notconf':
            Namespace(
                infilename=os.path.join(self.datadir, 'testconf.notjson'),
                verbose=True,
                validate=False,
                fix_sequences=self.fixed_fname,
                to_json=False,
                to_tab=False),
        }

    def test_validate_json_good(self):
        """config subcmd validates known good JSON config file."""
        subcommands.subcmd_config(self.argsdict['validate_json_good'],
                                  self.logger)

    def test_validate_tab_good(self):
        """config subcmd validates known good TSV config file."""
        subcommands.subcmd_config(self.argsdict['validate_tsv_good'],
                                  self.logger)

    def test_tsv_to_json(self):
        """config subcmd converts TSV config to JSON."""
        subcommands.subcmd_config(self.argsdict['tab_to_json'], self.logger)
        with open(self.tsv_to_json_fname, 'r') as fh1:
            with open(self.tsv_to_json_target, 'r') as fh2:
                assert_equal(ordered(json.load(fh1)), ordered(json.load(fh2)))

    def test_json_to_tsv(self):
        """config subcmd converts JSON config to TSV."""
        subcommands.subcmd_config(self.argsdict['json_to_tab'], self.logger)
        with open(self.json_to_tsv_fname, 'r') as fh1:
            with open(self.json_to_tsv_target, 'r') as fh2:
                assert_equal(fh1.read(), fh2.read())

    def test_fix_sequences(self):
        """config subcmd fixes sequences and writes JSON."""
        subcommands.subcmd_config(self.argsdict['fix_sequences'], self.logger)

        # Output JSON is correct
        with open(self.fixed_fname, 'r') as fh1:
            with open(self.fixed_target, 'r') as fh2:
                assert_equal(ordered(json.load(fh1)), ordered(json.load(fh2)))

    @raises(SystemExit)
    def test_validate_config_bad(self):
        """config subcmd errors on validating badly-formatted config file."""
        subcommands.subcmd_config(self.argsdict['validate_config_bad'],
                                  self.logger)

    @raises(SystemExit)
    def test_validate_config_bad_suffix(self):
        """config subcmd errors with wrong file extension for config."""
        subcommands.subcmd_config(self.argsdict['notconf'], self.logger)
