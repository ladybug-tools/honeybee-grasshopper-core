# honeybee-grasshopper-plugin
:honeybee: :green_book: Core hHoneybee plugin for Grasshopper (aka. honeybee[+]).

This repository contains all "core" Grasshopper components for the honeybee plugin
(aka. those components that are shared across all extensions). The package includes
both the userobjects (`.ghuser`) and the Python source (`.py`). Note that this
library only possesses the Grasshopper components and, in order to run the plugin,
the core libraries must be installed to the Rhino `scripts` folder (see dependencies).

# Dependencies
The honeybee-grasshopper plugin has the following dependencies (other than Rhino/Grasshopper):

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-dotnet](https://github.com/ladybug-tools/ladybug-dotnet)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)

# Extensions
The honeybee-grasshopper plugin has the following extensions:

* honeybee-grasshopper-radiance
* honeybee-grasshopper-energy

# Installation
To install the most recent version of the Grasshopper plugin, follow these steps:

1. Clone this repository to your machine.
2. Open the installer.gh in Grasshopper and set the toggle inside to `True`.
3. Restart Rhino + Grasshopper.

Note that following these steps will install the absolute most recent version of
the plugin. To install the last stable release, download the components and Grasshopper
file installer from [food4rhino](https://www.food4rhino.com/app/ladybug-tools).
