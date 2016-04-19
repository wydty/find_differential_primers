#!/usr/bin/env python3
#
# predict_diagnostic_primers.py
#
# This script aids prediction of diagnostic PCR primers from nucleotide 
# sequence files, where sequence files are associated with group/class
# identifiers
# 
# (c) The James Hutton Institute 2016
# Author: Leighton Pritchard
#
# Contact:
# leighton.pritchard@hutton.ac.uk
#
# Leighton Pritchard,
# Information and Computing Sciences,
# James Hutton Institute,
# Errol Road,
# Invergowrie,
# Dundee,
# DD6 9LH,
# Scotland,
# UK
#
# The MIT License
#
# Copyright (c) 2016 The James Hutton Institute
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import sys
import time
import traceback

from argparse import ArgumentParser

from diagnostic_primers import process

# Report last exception as string
def last_exception():
    """ Returns last exception as a string, or use in logging.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return ''.join(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback))

# Process command-line
def parse_cmdline(args):
    """Parse command-line arguments for script.

    The script offers a single main parser, with subcommands for the actions:

    process - process/check input data (stitch fragments/fix sequence problems)
    prodigal - run Prodigal to predict CDS features, and update .conf file
    eprimer3 - run ePrimer3 to predict primer pairs, and update .conf file
    check_blast - check/filter designed primers against negative example
                  BLAST database
    primersearch - check/filter designed primers against complete genome
                   negative examples
    classify - classify designed primers against input genome/classes
    """
    # Main parent parser
    parser_main = ArgumentParser(prog="pdp.py")
    subparsers = parser_main.add_subparsers(title="subcommands",
                                            description="valid subcommands",
                                            help="additional help")

    # A 'common' parser, with the shared commands for all subcommands
    parser_common = ArgumentParser(add_help=False)
    parser_common.add_argument("infilename",
                               help="Path to configuration file")
    parser_common.add_argument("-l", "--logfile", dest="logfile",
                               action="store", default=None,
                               help="Logfile location")
    parser_common.add_argument("-v", "--verbose", action="store_true",
                               dest="verbose", default=False,
                               help="report progress to log")

    # Subcommand parsers
    parser_process = subparsers.add_parser('process', aliases=['pr'],
                                           parents=[parser_common])
    parser_prodigal = subparsers.add_parser('prodigal',
                                            parents=[parser_common])
    parser_eprimer3 = subparsers.add_parser('eprimer3', aliases=['e3'],
                                            parents=[parser_common])
    parser_blastcheck = subparsers.add_parser('blastcheck', aliases=['bc'],
                                              parents=[parser_common])
    parser_primersearch = subparsers.add_parser('primersearch',
                                                aliases=['ps'],
                                                parents=[parser_common])
    parser_classify = subparsers.add_parser('classify', aliases=['cl'],
                                            parents=[parser_common])
    
    # Config file processing options - subcommand process
    parser_process.add_argument("outfilename",
                               help="Path to write new configuration file")
    parser_process.add_argument('--validate', action="store_true",
                                dest='validate', default=False,
                                help="Validate config file, then exit")

    # Parse arguments
    return parser_main.parse_args()



###
# Run as script
if __name__ == '__main__':

    # Parse command-line
    assert len(sys.argv) > 1, "pdp.py requires a valid subcommand"
    args = parse_cmdline(sys.argv)
    subcmd = sys.argv[1]

    # Set up logging
    logger = logging.getLogger('pdp.py: %s' % time.asctime())
    t0 = time.time()
    logger.setLevel(logging.DEBUG)
    err_handler = logging.StreamHandler(sys.stderr)
    err_formatter = logging.Formatter('%(levelname)s: %(message)s')
    err_handler.setFormatter(err_formatter)

    # Was a logfile specified? If so, use it
    if args.logfile is not None:
        try:
            logstream = open(args.logfile, 'w')
            err_handler_file = logging.StreamHandler(logstream)
            err_handler_file.setFormatter(err_formatter)
            err_handler_file.setLevel(logging.INFO)
            logger.addHandler(err_handler_file)
        except:
            logger.error("Could not open %s for logging" %
                         args.logfile)
            logger.error(last_exception())
            sys.exit(1)

    # Do we need verbosity?
    if args.verbose:
        err_handler.setLevel(logging.INFO)
    else:
        err_handler.setLevel(logging.WARNING)
    logger.addHandler(err_handler)

    # Report arguments, if verbose
    logger.info("Processed arguments: %s" % args)
    logger.info("command-line: %s" % ' '.join(sys.argv))

    # PROCESS
    # If we're running the process operation, the goal is to parse the input
    # config file, verify that the config file can be read, report some basic
    # information back (if verbose), and clean up sequence data by stitching it
    # and replacing ambiguity symbols with 'N'.
    # If sequence data needs to be stitched, or symbols replaced, then new
    # sequence files are produced and written (if --validate is not in
    # operation)
    # A new config file, pointing to the revised files, is written out (if
    # --validate is not in operation).
    if subcmd == 'process':
        # Load config file
        try:
            gc = process.load_collection(args.infilename, name="pdp.py")
        except:
            logger.error("Could not parse config file %s (exiting)" % 
                         args.infilename)
            logger.error(last_exception())
            sys.exit(1)
        logger.info("Parsed config file %s: %d sequences in %d groups" %
                    (args.infilename, len(gc), len(gc.groups())))
        logger.info("Diagnostic groups:\n%s" %
                    '\n'.join(["\t%s" % g for g in gc.groups()]))
        # Do sequences need to be stitched?
        print([g.needs_stitch for g in gc.data])
        



    # Exit as if all is well
    sys.exit(0)
