#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""subcmd_eprimer3.py

Provides the eprimer3 subcommand for pdp.py

(c) The James Hutton Institute 2017-18

Author: Leighton Pritchard
Contact: leighton.pritchard@hutton.ac.uk

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

Copyright (c) 2017-18 The James Hutton Institute
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

import os

from diagnostic_primers import eprimer3

from ..tools import (create_output_directory, load_config_json, log_clines,
                     run_parallel_jobs)


def subcmd_eprimer3(args, logger):
    """Run ePrimer3 to design primers for each input sequence."""
    # Determine config input type
    configtype = os.path.splitext(args.infilename)[-1][1:]
    if configtype not in ('tab', 'json', 'conf'):
        logger.error("Expected config file to end in .conf, .json or .tab " +
                     "got %s (exiting)", configtype)
        raise SystemExit(1)

    if configtype in ('tab', 'conf'):
        raise ValueError("eprimer3 subcommand requires JSON config file")
    coll = load_config_json(args, logger)

    # Check if output exists and if we should overwrite
    create_output_directory(args.eprimer3_dir, args.eprimer3_force, logger)

    # Build command-lines for ePrimer3 and run
    # This will write 'bare' ePrimer3 files, with unnamed primer pairs
    logger.info('Building ePrimer3 command lines...')
    clines = eprimer3.build_commands(coll, args.eprimer3_exe,
                                     args.eprimer3_dir, vars(args))
    pretty_clines = [str(c).replace(' -', ' \\\n          -') for c in clines]
    log_clines(pretty_clines, logger)
    run_parallel_jobs(clines, args, logger)

    # Load bare ePrimer3 data for each input sequence, and write JSON
    # representation with named primer sets
    # Record the path to the JSON representation in the PDPData object
    for gcc in coll.data:
        ep3file = gcc.cmds['ePrimer3'].outfile
        logger.info("Loading primers from ePrimer3 output %s", ep3file)
        primers = eprimer3.load_primers(ep3file, fmt='eprimer3')
        # Write named ePrimer3
        outfname = os.path.splitext(ep3file)[0] + '_named.eprimer3'
        logger.info('Writing named primer sequences to %s' % outfname)
        eprimer3.write_primers(primers, outfname, fmt='ep3')
        # Write named JSON
        outfname = os.path.splitext(ep3file)[0] + '_named.json'
        logger.info('Writing primer JSON sequences to %s' % outfname)
        eprimer3.write_primers(primers, outfname, fmt='json')
        gcc.primers = outfname

    logger.info('Writing new config file to %s' % args.outfilename)
    coll.write_json(args.outfilename)
    return 0
