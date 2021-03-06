# README.md (diagnostic_primers)

## Table of Contents

1. [Note for Users](#usernote)
2. [Note for Developers](#devnotenote)
3. [Overview](#overview)
	1. [Walkthrough](#walkthrough)
4. [Usage](#usage)
	1. [`pdp.py config`](#config)
	2. [`pdp.py prodigal`](#prodigal)
	3. [`pdp.py eprimer3`](#eprimer3)
	4. [`pdp.py blastscreen`](#blastscreen)
	5. [`pdp.py primersearch`](#primersearch)
	6. [`pdp.py classify`](#classify)

## NOTE FOR USERS<a id="usernote"></a>

The default branch for this repository is a development branch: `diagnostic_primers`. If you are looking for code to reproduce work in Pritchard *et al.* (2012) or Pritchard *et al.* (2013), please checkout the `master` branch, or download [release v0.1.3](https://github.com/widdowquinn/find_differential_primers/tree/v0.1.3).

* `diagnostic_primers`: 

[![codecov](https://codecov.io/gh/widdowquinn/find_differential_primers/branch/diagnostic_primers/graph/badge.svg)](https://codecov.io/gh/widdowquinn/find_differential_primers)
[![Code Health](https://landscape.io/github/widdowquinn/find_differential_primers/diagnostic_primers/landscape.svg?style=flat)](https://landscape.io/github/widdowquinn/find_differential_primers/diagnostic_primers)
[![Build Status](https://travis-ci.org/widdowquinn/find_differential_primers.svg?branch=diagnostic_primers)](https://travis-ci.org/widdowquinn/find_differential_primers)

* `master`: 

[![codecov](https://codecov.io/gh/widdowquinn/find_differential_primers/branch/master/graph/badge.svg)](https://codecov.io/gh/widdowquinn/find_differential_primers)
[![Code Health](https://landscape.io/github/widdowquinn/find_differential_primers/master/landscape.svg?style=flat)](https://landscape.io/github/widdowquinn/find_differential_primers/master)
[![Build Status](https://travis-ci.org/widdowquinn/find_differential_primers.svg?branch=master)](https://travis-ci.org/widdowquinn/find_differential_primers)

## NOTE FOR DEVELOPERS<a id="devnotenote"></a>

The default master branch for development is `diagnostic_primers`. We would appreciate contributions *via* pull request, especially if you follow the guidelines on the [wiki](https://github.com/widdowquinn/find_differential_primers/wiki).

* Current test coverage (`diagnostic_primers`): [https://codecov.io/gh/widdowquinn/find_differential_primers/list/diagnostic_primers](https://codecov.io/gh/widdowquinn/find_differential_primers/list/diagnostic_primers)

## Overview<a id="overview"></a>
This program performs automated finding of discriminatory (real-time) PCR or qPCR primers that distinguish among genomes or other biological sequences of interest. It is also useful for the identification of metabarcoding marker sequences that can discriminate within a subset of bacterial genomes.

**To work correctly, some third-party packages/programs must be installed.**

### Required Third-party Packages

* [`Primer3`]() **VERSION 1.1.4**: `Primer3` is the tool used to design primers. For compatibility with `EMBOSS`, version 1 of the software is essential.
* [`EMBOSS`](): This suite of tools is used to interact with `Primer3` and to perform *in silico* cross-hybridisation checks with `primersearch`. It is essential.
* [`BLAST+`](): This tool is used to screen primers against a database of off-target sequences with the `blastscreen` command.
* [`prodigal`](): This program is used to identify candidate CDS features when using the `prodigal` subcommand.
* [`MAFFT`](): This is required to align amplicon sequences, when using the `extract` subcommand

### Recent changes

The new version of `diagnostic_primers` (formerly `find_differential_primers`) now uses a subcommand model, like the tools `git` and `subversion`. These execute the following subtasks, some or all of which may be required to perform a specific primer/marker design run.

* `config`: Process/validate the configuration file and stitch input contig fragments/replace ambiguity symbols as necessary.
* `prodigal`/`prod`: Predict CDS locations on the input sequences
* `eprimer3`/`e3`: Design amplifying primers on the input sequences
* `blastscreen`/`bs`: Filter designed primers against a database of negative examples
* `primersearch`/`ps`: Filter designed primers on their ability to amplify each input sequence
* `classify`/`cl`: Classify designed primers by specificity for each class of input sequence
* `extract`/`ex`: Extract amplicon sequences corresponding to diagnostic primer sets
* `plot`/`pl`: Generate useful graphical output for interpretation of results

Each of these subcommands has specific help, accessible with `pdp.py <subcommand> -h` or `pdp.py <subcommand> --help`.

## Walkthrough <a id="walkthrough"></a>

In this section, we will walk through an analysis from defining a config file to producing a diagnostic primer set result. All the files required for this analysis can be found in the subdirectory `tests/walkthrough`.

### 1. Producing and validating the config file

We will begin with a small set of bacterial genomes: three *Pectobacterium* species. These are defined as `.fasta` sequences in the directory `tests/walkthrough/sequences`:

```bash
$ ls tests/walkthrough/sequences/
GCF_000011605.1.fasta	GCF_000291725.1.fasta	GCF_000749845.1.fasta
```

A basic config file defining the three genomes is provided as `tests/walkthrough/pectoconf.tab` in tab-separated tabular format. Four columns are indicated: `name`; `classes` (comma-separated); `FASTA location`; and `features`. At this point we don't have any features defined (these are used to direct primer design to specified regions of the genome), so this column contains only the symbol `-` to mark it empty.

Comment lines start with `#` as the first character. These are ignored in the analysis

```text
# Pectobacterium genomes downloaded from GenBank/NCBI; genomovars inferred from ANIm
# Annotated Pba: genomovar 1
Pba_SCRI1043	Pectobacterium,atrosepticum_NCBI,gv1	tests/walkthrough/sequences/GCF_000011605.1.fasta	-
# Annotated Pwa: genomovars 2, 3
Pwa_CFBP_3304	Pectobacterium,wasabiae_NCBI,gv2	tests/walkthrough/sequences/GCF_000291725.1.fasta	-
# Annotated Pb	: genomovar 7
Pbe_NCPPB_2795	Pectobacterium,betavasculorum_NCBI,gv7	tests/walkthrough/sequences/GCF_000749845.1.fasta	-
```

To confirm that the config file is correctly-formatted, we use the `pdp.py config --validate` command:

```bash
$ pdp.py config --validate tests/walkthrough/pectoconf.tab
WARNING: Validation problems
    Pbe_NCPPB_2795 requires stitch (tests/walkthrough/sequences/GCF_000749845.1.fasta)
    Pwa_CFBP_3304 requires stitch (tests/walkthrough/sequences/GCF_000291725.1.fasta)
    Pwa_CFBP_3304 has non-N ambiguities (tests/walkthrough/sequences/GCF_000291725.1.fasta)
```

This tells us that the first two genome files are in multiple parts so must be concatenated for this analysis, and that the second file also has ambiguity base symbols that are not `N`, so these must be replaced accordingly for the analysis to proceed.

### 2. Fix sequences for analysis

The `pdp.py config` command can fix input genomes so they can be analysed, with the `--fix_sequences` argument. This writes new sequences, with the necessary changes (stitching, replacing ambiguity symbols) having been made. We require a new config file that points at the fixed sequences, and we specify the path to this new file with the argument `--fix_sequences <NEWCONFIG>.json`. 

```bash
$ pdp.py config --fix_sequences tests/walkthrough/fixed.json \
                tests/walkthrough/pectoconf.tab
```

This writes corrected sequences to the `tests/walkthrough/sequences` subdirectory, and a new config file to `tests/walkthrough/fixed.json` (in JSON format, which is how `pdp.py` prefers to receive configuration files) pointing to them:

```bash
$ tree tests/walkthrough/
tests/walkthrough/
├── fixed.json
├── pectoconf.tab
└── sequences
    ├── GCF_000011605.1.fasta
    ├── GCF_000291725.1.fasta
    ├── GCF_000291725.1_concat.fas
    ├── GCF_000291725.1_concat_noambig.fas
    ├── GCF_000749845.1.fasta
    └── GCF_000749845.1_concat.fas
```

### 3. Defining CDS features on each genome (optional)

For prokaryotic genomes, we can use a genecaller to predict gene features with the `pdp.py prodigal` command. This generates predicted sequences and a GFF file describing them that can be used to define feature locations on each genome. In the primer design stage, we can take those into account and retain only primers that amplify within CDS regions.

To use the genecaller, we must provide an appropriate config file (the `fixed.json` config file), and the path to a new config file that will contain information about the predicted features (we'll call this `fixed_with_features.json`). We will tell `prodigal` to place the predicted gene locations in the subdirectory `tests/walkthrough/prodigal`:

```bash
pdp.py prodigal --outdir tests/walkthrough/prodigal \
                tests/walkthrough/fixed.json \
                tests/walkthrough/fixed_with_features.json
```

The new directory containing genecaller output is created for us, as is the new config file:

```bash
$ tree tests/walkthrough/
tests/walkthrough/
├── fixed.json
├── fixed_with_features.json
├── pectoconf.tab
├── prodigal
│   ├── GCF_000011605.1.features
│   ├── GCF_000011605.1.gff
│   ├── GCF_000291725.1_concat_noambig.features
│   ├── GCF_000291725.1_concat_noambig.gff
│   ├── GCF_000749845.1_concat.features
│   └── GCF_000749845.1_concat.gff
└── sequences
[…]
```

### 4. Design primers to each genome in bulk

Using the most informative config file (`fixed_with_features.json`) we can design primers to each input genome with the EMBOSS `ePrimer3` package. At a minimum, we need to give the `pdp.py eprimer3` command the input config file, and the path to an output config file that will contain information about the primer description files for each genome.

We will also use the `--outdir` argument to tell `pdp.py` where to put the `ePrimer3` output files:

```bash
$ pdp.py eprimer3 --outdir tests/walkthrough/eprimer3 \
                  tests/walkthrough/fixed_with_features.json \
                  tests/walkthrough/with_primers.json
```

This places the output of `ePrimer3` into its own directory, and generates JSON files that describe the primers for each of the genomes.

```bash
$ tree tests/walkthrough/
tests/walkthrough/
├── eprimer3
│   ├── GCF_000011605.1.eprimer3
│   ├── GCF_000011605.1_named.eprimer3
│   ├── GCF_000011605.1_named.json
│   ├── GCF_000291725.1_concat_noambig.eprimer3
│   ├── GCF_000291725.1_concat_noambig_named.eprimer3
│   ├── GCF_000291725.1_concat_noambig_named.json
│   ├── GCF_000749845.1_concat.eprimer3
│   ├── GCF_000749845.1_concat_named.eprimer3
│   └── GCF_000749845.1_concat_named.json
├── fixed.json
├── fixed_with_features.json
├── pectoconf.tab
├── prodigal
[…]
├── sequences
[…]
└── with_primers.json
```

### 5. Screen primers against `BLASTN` database (optional)

Now that primers have been designed, they can be screened against a `BLASTN` database to identify and filter out any primers that have potential cross-amplification. In general, we advise that this step is used not to demonstrate potential for cross-hybridisation/amplification, but to exclude primers that have *any* theoretical potential for off-target binding. That is, we recommend this process to aid a negative screen.

The screen is performed with the `blastscreen` subcommand, and requires us to provide the location of a suitable BLASTN database (there is a BLASTN *E. coli* genome sequence in the subdirectory `tests/walkthrough/blastdb/`) with the argument `--db`. We also place the BLAST output in the `tests/walkthrough/blastn` subdirectory. The input config file that we use is the `with_primers.json` file, having locations of the unscreened primer files, and we specify that the command writes a new config file called `screened.json` that points to a reduced set of primers, with the potentially cross-hybridising sequences excluded.

No sequences are deleted as a result of this action.

```bash
$ pdp.py blastscreen --db tests/walkthrough/blastdb/e_coli_screen.fna \
                     --outdir tests/walkthrough/blastn \
                     tests/walkthrough/with_primers.json \
                     tests/walkthrough/screened.json
```

This screen produces the new subdirectory `tests/walkthrough/blastn` that contains all the primer sequences in FASTA format, and the tabular output of the BLAST search. New files are added to the `eprimer3` subdirectory, describing the reduced sets of primers, post-screening.

```bash
$ tree tests/walkthrough/
tests/walkthrough/
├── blastdb
│   ├── e_coli_screen.fna.nhr
│   ├── e_coli_screen.fna.nin
│   └── e_coli_screen.fna.nsq
├── blastn
│   ├── GCF_000011605.1_primers.fasta
│   ├── GCF_000011605.1_primers.tab
│   ├── GCF_000291725.1_concat_noambig_primers.fasta
│   ├── GCF_000291725.1_concat_noambig_primers.tab
│   ├── GCF_000749845.1_concat_primers.fasta
│   └── GCF_000749845.1_concat_primers.tab
├── eprimer3
│   ├── GCF_000011605.1.eprimer3
│   ├── GCF_000011605.1_named.eprimer3
│   ├── GCF_000011605.1_named.json
│   ├── GCF_000011605.1_named_screened.fasta
│   ├── GCF_000011605.1_named_screened.json
│   ├── GCF_000291725.1_concat_noambig.eprimer3
│   ├── GCF_000291725.1_concat_noambig_named.eprimer3
│   ├── GCF_000291725.1_concat_noambig_named.json
│   ├── GCF_000291725.1_concat_noambig_named_screened.fasta
│   ├── GCF_000291725.1_concat_noambig_named_screened.json
│   ├── GCF_000749845.1_concat.eprimer3
│   ├── GCF_000749845.1_concat_named.eprimer3
│   ├── GCF_000749845.1_concat_named.json
│   ├── GCF_000749845.1_concat_named_screened.fasta
│   └── GCF_000749845.1_concat_named_screened.json
[…]
├── fixed.json
├── fixed_with_features.json
├── pectoconf.tab
├── prodigal
[…]
├── sequences
[…]
└── with_primers.json
```

The new configuration file can be used in the `primersearch` cross-hybridisation detection stage.

### 6a. Test primers against input sequences for crosshybridisation with `primersearch`

To identify which primers might be diagnostically useful for any of our classes, we must test whether they potentially amplify the other genomes from the input set. In this example, we will use the `EMBOSS` tool `primersearch` to check whether any of the primers we designed (and screened against the `BLAST` database also have potential to amplify any of the other input sequences.

To do this we need to pass the appropriate `.json` config file, and specify a directory to hold `primersearch` output, as well as a new config file that will hold data about our crosshybridisation screen.

```bash
pdp.py primersearch \
       --outdir tests/walkthrough/primersearch \
       tests/walkthrough/screened.json \
       tests/walkthrough/primersearch.json
```

The new directory `tests/walkthrough/primersearch` is produced, containing a new primer file (with extension `.tab`; this was needed for `primersearch`) and `.json` file for each input sequence. In addition, there is a new `.primersearch` file for each comparison of primer sequence set against one of the input genome sequences.

```bash
$ tree tests/walkthrough
tests/walkthrough
[...]
├── primersearch
│   ├── Pba_SCRI1043_primers.tab
│   ├── Pba_SCRI1043_primersearch.json
│   ├── Pba_SCRI1043_ps_Pbe_NCPPB_2795.primersearch
│   ├── Pba_SCRI1043_ps_Pwa_CFBP_3304.primersearch
│   ├── Pbe_NCPPB_2795_primers.tab
│   ├── Pbe_NCPPB_2795_primersearch.json
│   ├── Pbe_NCPPB_2795_ps_Pba_SCRI1043.primersearch
│   ├── Pbe_NCPPB_2795_ps_Pwa_CFBP_3304.primersearch
│   ├── Pwa_CFBP_3304_primers.tab
│   ├── Pwa_CFBP_3304_primersearch.json
│   ├── Pwa_CFBP_3304_ps_Pba_SCRI1043.primersearch
│   └── Pwa_CFBP_3304_ps_Pbe_NCPPB_2795.primersearch
├── primersearch.json
[...]
```

The new `primersearch.json` config file contains information about this crosshybridisation screen, and can be used for identification of diagnostic primer sequence sets.

### 7. Classify the primers by diagnostic capability with `classify`

To extract useful information from `primersearch` output, and classify the primer sets by their ability to amplify only genomes belonging to a specific named group in the configuration file, we use the `classify` subcommand. This examines the `primersearch` output and reports back diagnostic primer sets.

We pass the `.json` file produced by the `primersearch` run, and the path to a directory for the output of the `classify` subcommand:

```bash
pdp.py classify \
       tests/walkthrough/primersearch.json \
       tests/walkthrough/classify
```

The new directory contains `.json` and `.ePrimer3` format files for each set of primers diagnostic to a given class, and summary information in `summary.tab` and `results.json` files.

```bash
$ tree tests/walkthrough/classify
tests/walkthrough/classify
├── atrosepticum_NCBI_primers.ePrimer3
├── atrosepticum_NCBI_primers.json
├── betavasculorum_NCBI_primers.ePrimer3
├── betavasculorum_NCBI_primers.json
├── gv1_primers.ePrimer3
├── gv1_primers.json
├── gv2_primers.ePrimer3
├── gv2_primers.json
├── gv7_primers.ePrimer3
├── gv7_primers.json
├── Pectobacterium_primers.ePrimer3
├── Pectobacterium_primers.json
├── results.json
├── summary.tab
├── wasabiae_NCBI_primers.ePrimer3
└── wasabiae_NCBI_primers.json
```


## Usage<a id="usage"></a>


### `pdp.py config`<a id="config"></a>

The `config` subcommand handles interactions with the configuration file for a primer design run. Configuration files can be provided in one of two formats:

1. `<config>.tab`: a plain text, tab-separated file descrbing the input data in a table of multiple columns [as defined below](#config_tab_format). This is intended to be an easily human-readable file, that can be prepared and edited in a spreadsheet application such as Google Sheets, or Microsoft Excel. `pdp.py config` will recognise `.tab` or `.conf` as a file extension.
2. `<config>.json`: a JSON format file describing the input data. This is not intended to be human-readable, but can be converted to and from the `.tab` format using `pdp.py` config. Further steps in the primer design process require that the configuration is provided in JSON format.

#### Converting between `.tab` and JSON format config files

**1. `.tab` to JSON**

Provide the path to the output JSON file as an argument to `--to_json`, and the path to the `.tab` config file as input:

```bash
pdp.py config --to_json <OUTPUT>.json <INPUT>.tab
```

**2. JSON to `tab`**

Provide the path to the output `.tab` file as an argument to `--to_tab`, and the path to the JSON config file as input:

```bash
pdp.py config --to_tab <OUTPUT>.tab <INPUT>.json
```

#### Validate a config file

`pdp.py` can examine the contents of a config file and determine whether it conforms to the required specification, and whether the sequences used for input require stitching, or replacement of ambiguity codons. To validate a config file, use the `--validate` flag:

```bash
$ pdp.py config --validate <INFILE>.tab
$ pdp.py config --validate <INFILE>.json
```

#### Repair input sequences

For use with this primer design tool, the input sequences must be concatenated, and cannot contain non-`N` ambiguity base symbols. `pdp.py` can nondestructively repair input sequences by stitching sequence fragments/contigs together, and replacing all ambiguity symbols with `N`.

```bash
pdp.py config --fix_sequences <REPAIRED>.json <INPUT>.[tab|json]
```

The repaired sequences are written to new files in the same directory as the input file, with one of the following suffixes:

* `_concat`: the sequence was concatenated
* `_noambig`: the sequence had ambiguity symbols replaced
* `_concat_noambig`: the sequence was concatenated, and ambiguity symbols were replaced

such that an input file `<SEQUENCE>.fas` may be repaired to generate the file `<SEQUENCE>_concat_noambig.fas` in the same directory as the original file, and a new config file pointing to the modified sequences is written to `<REPAIRED>.json`.

### `pdp.py prodigal`<a id="prodigal"></a>

The `prodigal` (or `prod`) subcommand runs the [`prodigal`](https://github.com/hyattpd/Prodigal) prokaryotic gene feature-calling package on the sequences listed in the passed configuration file. A new configuration file, specifying the location of the feature file for each input sequence, is written to the specified output file location.

#### Default feature prediction

`prodigal` feature prediction is run on the sequences listed in `<INPUT>.json`, and a new config file written to `<OUTPUT>.json` with the locations of the feature predictions indicated.

```bash
pdp.py prodigal <INPUT>.json <OUTPUT>.json
```

To overwrite existing output, pass the `-f` or `--force` argument:

```bash
pdp.py prodigal --force <INPUT>.json <OUTPUT>.json
```

#### Specify location to write `prodigal` predictions

By default, `pdp.py` writes output to the subdirectory `prodigal`. To put the feature predictions in another location, pass the directory you want to place the `prodigal` output (here, `<OUTDIR>`) as the `--outdir` argument (and use the `-f`/`--force` argument to overwrite existing output):

```bash
pdp.py prodigal --outdir <OUTDIR> <INPUT>.json <OUTPUT>.json
```

#### Specify the location of the `prodigal` executable

By default `pdp.py` will look for `prodigal` in your `$PATH`. A different executable can be specified with the `--prodigal` argument:

```bash
pdp.py prodigal --prodigal <PATH_TO_PRODIGAL> <INPUT>.json <OUTPUT>.json
```

### `pdp.py eprimer3`<a id="eprimer3"></a>

The `eprimer3` command runs primer prediction on each of the input sequences listed in the passed input configuration file. The tool used by `pdp.py` is the [EMBOSS `ePrimer3` package](http://bioinf.ibun.unal.edu.co/cgi-bin/emboss/help/eprimer3). A new configuration file is written describing the locations of the predicted primers.


#### Default primer prediction

Primer prediction is run on the sequences listed in `<INPUT>.json`, and the new config file written to `<OUTPUT>.json`.

```bash
pdp.py eprimer3 <INPUT>.json <OUTPUT>.json
```

#### Change the number of predicted primers per input sequence

By default only 10 primers are predicted per sequence. This is a choice made for speed of testing, and is unlikely to be enough to useful for designing diagnostic primers for a prokaryotic genome. Overall runtime increases exponentially with the number of primers that need to be tested for cross-hybridisation, and a suitable choice of value will depend strongly on the dataset being used. To specify the number of primers to be designed for each input sequence, use the `--numreturn` argument. For example, to design 2000 primers per input sequence, use:

```bash
pdp.py eprimer3 --numreturn 2000 <INPUT>.json <OUTPUT>.json
```

#### Change primer design parameters

All parameters for `eprimer3` are available to be changed at the command line. There are a large number of these arguments, and they are all described in the help text (use: `pdp.py eprimer3 -h`), but some useful examples are listed below:

**Specify primer lengths**

To specify an optimal primer oligo size, and an acceptable (minimum/maximum) range of sizes, use the `--osize`, `--minsize`, `--maxsize` arguments, e.g.:

```bash
pdp.py eprimer3 --osize 25 --minsize 20 --maxsize 30 <INPUT>.json <OUTPUT>.json
```

**Specify primer thermodynamics**

To specify optimal, minimum and maximum melting temperatures (Tm) for the predicted primers, use the `--opttm`, `--mintm`, and `--maxtm` arguments, e.g.:

```bash
pdp.py eprimer3 --opttm 65 --mintm 62 --maxtm 68 <INPUT>.json <OUTPUT>.json
```

**Specify amplicon lengths**

To specify an optimal amplicon size, and an acceptable (minimum/maximum) range of sizes, use the `--psizeopt`, `--psizemin`, `--psizemax` arguments, e.g.:

```bash
pdp.py eprimer3 --psizeopt 200 --psizemin 190 --psizemax 210 <INPUT>.json <OUTPUT>.json
```

#### Specify location to write primer prediction output

By default, `pdp.py` writes output to the subdirectory `eprimer3`. To put the primer predictions in another location, pass the directory you want to place the output (here, `<OUTDIR>`) as the `--outdir` argument (and use the `-f`/`--force` argument to overwrite existing output):

```bash
pdp.py eprimer3 --outdir <OUTDIR> <INPUT>.json <OUTPUT>.json
```

#### Specify the location of the `eprimer3` executable

By default `pdp.py` looks for the EMBOSS `eprimer3` executable in your `$PATH`, but its location can be specified with the `--eprimer3` argument:

```
pdp.py eprimer3 --eprimer3 <PATH_TO_EPRIMER3> <INPUT>.json <OUTPUT>.json
```

### `pdp.py blastscreen`<a id="blastscreen"></a>

The `blastscreen` command screens predicted primers against a local `BLASTN` nucleotide database. Primer pairs for which at least one member produces a match in the `BLAST` database are excluded. The tool used by `pdp.py` is a [local `BLAST+` installation](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download). `BLAST` output is written to a new directory, and a new configuration file is written describing the primer sets that pass the screen (i.e. have no matches in the database).

#### Basic screening

The `BLAST` database to screen the primers described in `<INPUT>.json` against is passed as `<BLASTDB>`. The `BLAST` results are written to the directory `<BLASTOUT>`, and the new config file written to `<OUTPUT>.json`.

```bash
pdp.py blastscreen --db <BLASTDB> --outdir <BLASTOUT> <INPUT>.json <OUTPUT>.json
```

The default database is `nr` and the default output directory is `blastn`.

#### Controlling sensitivity

A single argument `--maxaln` is used to control sensitivity of primer matching. This describes the maximum number of identities allowed in the `BLAST` match before the primer pair is excluded (default=`15`).

```bash
pdp.py blastscreen --db <BLASTDB> --outdir <BLASTOUT> --maxaln 25 <INPUT>.json <OUTPUT>.json
```

#### Specify the location of the `BLAST+` executable

The location of the `BLAST+` executable can be provided with the `--blastn` argument.

```bash
pdp.py blastscreen --db <BLASTDB> --outdir <BLASTOUT> --blastn <BLASTNPATH> <INPUT>.json <OUTPUT>.json
```

#### Control the number of threads used

The `BLAST` screen is parallelised on as many threads as are available, by default. The number of worker threads can be controlled with the `-w` argument.

```bash
pdp.py blastscreen --db <BLASTDB> --outdir <BLASTOUT> -w 4 <INPUT>.json <OUTPUT>.json
```

#### Use the SGE/OGE scheduler

The `BLAST` screen can be parallelised using a Sun Grid Engine variant, such as Son of Grid Engine, Open Grid Engine, or Univa Grid Engine. To specify this scheduler, use the `-s` argument with the value `SGE`.

```bash
pdp.py blastscreen --db <BLASTDB> --outdir <BLASTOUT> -s SGE <INPUT>.json <OUTPUT>.json
```

### `pdp.py primersearch`<a id="primersearch"></a>

The `primersearch` command performs *in silico* hybridisation of predicted primers against each of the input genomes, so that cross-hybridising primers can be identified. The tool used by `pdp.py` is the [EMBOSS `primersearch` tool](http://emboss.sourceforge.net/apps/cvs/emboss/apps/primersearch.html). `primersearch` output is written to a new directory, and a new configuration file is written describing the cross-hybridisation results.

#### Basic cross-hybridisation

The configuration file describing primers to use is passed as `<INPUT>.json`, and the path to the new output directory containing `primersearch` output is passed as `<OUTDIR>`. The path to write the new configuration file describing cross-hybridisation information is provided as `<OUTPUT>.json`.

```bash
pdp.py primersearch --outdir <OUTDIR> <INPUT>.json <OUTPUT>.json
```

#### Controlling sensitivity

A single argument `--mismatchpercent` is used to control the sensitivity with which `primersearch` thinks primers cross-hybridise. This describes the maximum percentage of mismatches (in the range `[0, 1]`) allowed in the primer match before `primersearch` considers that hybridisation is not possible. The default value is `0.1`.

```bash
pdp.py primersearch --outdir <OUTDIR> --mismatchpercent 0.25 <INPUT>.json <OUTPUT>.json
```

#### Specify the location of the `primersearch` executable

The location of the `primersearch` executable can be provided with the `--primersearch` argument.

```bash
pdp.py primersearch --outdir <OUTDIR> --primersearch <PSPATH> <INPUT>.json <OUTPUT>.json
```

#### Control the number of threads used

By default, cross-hybridisation is parallelised on as many threads as are available. The number of worker threads can be controlled with the `-w` argument.

```bash
pdp.py primersearch --outdir <OUTDIR> -w 4 <INPUT>.json <OUTPUT>.json
```

#### Use the SGE/OGE scheduler

The cross-hybridisation screen can also be parallelised using a Sun Grid Engine variant, such as Son of Grid Engine, Open Grid Engine, or Univa Grid Engine. To specify this scheduler, use the `-s` argument with the value `SGE`.

```bash
pdp.py primersearch --outdir <OUTDIR> -s SGE <INPUT>.json <OUTPUT>.json
```


### `pdp.py classify`<a id="classify"></a>

The `classify` command takes the output from the `primersearch` step, and identifies primer sets that uniquely amplify each of the target groups defined in the corresponding `.json` configuration file.

#### Basic classification

The configuration file describing primers and their PrimerSearch results is passed as `<INPUT>.json`, and the path to the new output directory that will contain the sets of primers predicted to be specific to each group, and summary information as `<OUTDIR>`.

```bash
pdp.py classify <INPUT>.json <OUTDIR>
```

This will produce a summary tab-separated plain text table (`summary.tab`), a JSON format file describing the complete set of results (`results.json`), and then a pair of `.json` and `.ePrimer3` format files for each defined group for which predicted diagnostic primers could be derived.




## FURTHER INFORMATION:
For further technical information, please read the comments contained within the top of each '*.py' file as well as the Supporting Information (['Methods S1' document](doi:10.1371/journal.pone.0034498.s006)) of [doi:10.1371/journal.pone.0034498](http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0034498).

## CONTRIBUTORS
* [Leighton Pritchard](https://github.com/widdowquinn)
* [Benjamin Leopold](https://github.com/cometsong)
* [Michael Robeson](https://github.com/mikerobeson)
* [Rory McLeod](https://github.com/rory-mcleod)

## CITATIONS
Please refer to the following for methodological details:

* Pritchard L _et al._ (2012) "Alignment-Free 
Design of Highly Discriminatory Diagnostic Primer Sets for _Escherichia coli_ O104:H4 Outbreak Strains." _PLoS ONE_ **7**(4): e34498. [doi:10.1371/journal.pone.0034498](http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0034498) - _Method description and application to human bacterial pathogens, sub-serotype resolution_
* Pritchard L _et al._ (2013) "Detection of phytopathogens of the genus _Dickeya_ using a PCR primer 
prediction pipeline for draft bacterial genome sequences." _Plant Pathology_, **62**, 587-596
[doi:10.1111/j.1365-3059.2012.02678.x](http://onlinelibrary.wiley.com/doi/10.1111/j.1365-3059.2012.02678.x/full) - _Application to plant pathogens, species-level resolution_
