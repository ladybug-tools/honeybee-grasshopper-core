[![Build Status](https://travis-ci.com/ladybug-tools/honeybee-grasshopper-core.svg?branch=master)](https://travis-ci.com/ladybug-tools/honeybee-grasshopper-core)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# honeybee-grasshopper-core

:honeybee: :green_book: Core Honeybee plugin for Grasshopper (aka. honeybee[+]).

This repository contains all "core" Grasshopper components for the honeybee plugin
(aka. those components that are shared across all extensions). The package includes
both the userobjects (`.ghuser`) and the Python source (`.py`). Note that this
library only possesses the Grasshopper components and, in order to run the plugin,
the core libraries must be installed (see dependencies).

## Dependencies

The honeybee-grasshopper plugin has the following dependencies (other than Rhino/Grasshopper):

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort)
* [ladybug-display](https://github.com/ladybug-tools/ladybug-display)
* [ladybug-radiance](https://github.com/ladybug-tools/ladybug-radiance)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)

## Other Required Components

The honeybee-grasshopper plugin also requires the Grasshopper components within the
following repositories to be installed in order to work correctly:

* [ladybug-grasshopper](https://github.com/ladybug-tools/ladybug-grasshopper)

## Extensions

The honeybee-grasshopper plugin has the following extensions:

* [honeybee-grasshopper-radiance](https://github.com/ladybug-tools/honeybee-grasshopper-radiance)
* [honeybee-grasshopper-energy](https://github.com/ladybug-tools/honeybee-grasshopper-energy)

## Installation

See the [Wiki of the lbt-grasshopper repository](https://github.com/ladybug-tools/lbt-grasshopper/wiki)
for the installation instructions for the entire Ladybug Tools Grasshopper plugin
(including this repository).
