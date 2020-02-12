[![Build Status](https://travis-ci.com/openpathsampling/openpathsampling-cli.svg?branch=master)](https://travis-ci.com/openpathsampling/openpathsampling-cli)
[![Documentation Status](https://readthedocs.org/projects/openpathsampling-cli/badge/?version=latest)](https://openpathsampling-cli.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/openpathsampling/openpathsampling-cli/badge.svg?branch=master)](https://coveralls.io/github/openpathsampling/openpathsampling-cli?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/0d1ee29e1a05cfcdc01a/maintainability)](https://codeclimate.com/github/openpathsampling/openpathsampling-cli/maintainability)

# OpenPathSampling CLI

*The command line interface to OpenPathSampling*

OpenPathSampling is a powerful and flexible library for path sampling
simulations. However, many users would prefer to interact with an executable on
the command line, instead of writing everything in their own Python script.
Here is that command line tool, including some useful scripts for dealing with
OPS output files.

The CLI is used as a single executable, `openpathsampling`, with multiple
subcommands. We recommend aliasing `openpathsampling` to something simpler (maybe `ops`?) to save typing!

Current categories of subcommands are for simulation running, and for
miscellaneous operations on OPS output files.

**Simulation Commands:**

* `visit-all`:     Run MD to generate initial trajectories
* `equilibrate`:   Run equilibration for path sampling
* `pathsampling`:  Run any path sampling simulation, including TIS variants

**Miscellaneous Commands:**

* `contents`:         List named objects from an OPS .nc file
* `strip-snapshots`:  Remove coordinates/velocities from an OPS storage
* `append`:           add objects from INPUT_FILE  to another file

Full documentation is at https://openpathsampling-cli.readthedocs.io/; a brief
summary is below.


<!-- TODO: add TOC if the contents here get too long
Contents:

* Installation
* Workflow
* Creating your own commands 
-->

## Installation

The OPS CLI can be installed with either ``conda`` or ``pip``:

```bash
conda -c conda-forge install openpathsampling-cli
# or
pip install openpathsampling-cli
```

Note that installing the CLI will also install OpenPathSampling, if you don't
already have it.

## Workflow

**Set up, *then* simulate!** The overall idea is that you will first set up your
simulation, and then use these scripts to run the resulting simulation setup
files. Currently, writing a Python script (or better, using a Jupyter notebook
to set things up interactively) is the best way to do that. Save the necessary
simulation objects to a `setup.nc` file, and then use these scripts to run the
simulation.

## Creating your own commands

Creating your own commands is extremely easy. The OPS CLI uses a plug-in
architecture so that installing your own commands is as easy as putting a
Python file in your `~/.openpathsampling/cli-plugins/` directory. 
We provide a standard set of parameters as decorators, which can (and should)
be re-used to load things from storage. The CLI is built on
[`click`](https://click.palletsprojects.com/), so additional arguments are
easily added using functionality from `click`. See our developer documentation
for details.
