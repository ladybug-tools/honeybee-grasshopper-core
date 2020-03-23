[![Build Status](https://travis-ci.org/ladybug-tools/honeybee-grasshopper-core.svg?branch=master)](https://travis-ci.org/ladybug-tools/honeybee-grasshopper-core)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# honeybee-grasshopper-core
:honeybee: :green_book: Core Honeybee plugin for Grasshopper (aka. honeybee[+]).

This repository contains all "core" Grasshopper components for the honeybee plugin
(aka. those components that are shared across all extensions). The package includes
both the userobjects (`.ghuser`) and the Python source (`.py`). Note that this
library only possesses the Grasshopper components and, in order to run the plugin,
the core libraries must be installed (see dependencies).

# Dependencies
The honeybee-grasshopper plugin has the following dependencies (other than Rhino/Grasshopper):

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-dotnet](https://github.com/ladybug-tools/ladybug-dotnet)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [ladybug-grasshopper](https://github.com/ladybug-tools/ladybug-grasshopper)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)

# Extensions
The honeybee-grasshopper plugin has the following extensions:

* honeybee-grasshopper-radiance
* [honeybee-grasshopper-energy]((https://github.com/ladybug-tools/honeybee-grasshopper-energy)
