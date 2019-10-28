# honeybee-grasshopper-plugin
:honeybee: :green_book: Honeybee plugin for Grasshopper (aka. honeybee[+]).

This repository contains all Grasshopper components for the honeybee plugin, including both the userobjects (`.ghuser`) and the Python source (`.py`). Note that this library only possesses the Grasshopper components and, in order to run the plugin, the core libraries must be installed to the Rhino `scripts` folder (see dependencies).

# Dependencies
The honeybee-grasshopper plugin has the following dependencies (other than Rhino/Grasshopper):

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-dotnet](https://github.com/ladybug-tools/ladybug-dotnet)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)
* [honeybee-radiance](https://github.com/ladybug-tools/honeybee-radiance)
* [honeybee-energy](https://github.com/ladybug-tools/honeybee-energy)
* [honeybee-energy-standards](https://github.com/ladybug-tools/honeybee-energy-standards)

# Installation
To install the most recent version of the Grasshopper plugin, follow these steps:

1. Clone this repository to your machine.
2. Open the installer.gh in Grasshopper and set the toggle inside to `True`.
3. Restart Rhino + Grasshopper.

Note that following these steps will install the absolute most recent version of the plugin. To install the last stable release, download the components and Installer from [food4rhino](https://www.food4rhino.com/app/ladybug-tools).
