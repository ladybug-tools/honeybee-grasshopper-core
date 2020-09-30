# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Honeybee Model, which can be sent for simulation.
-

    Args:
        rooms_: A list of honeybee Rooms to be added to the Model. Note that at
            least one Room is necessary to make a simulate-able energy model.
        faces_: A list of honeybee Faces to be added to the Model. Note that
            faces without a parent Room are not allowed for energy models.
        shades_: A list of honeybee Shades to be added to the Model.
        apertures_: A list of honeybee Apertures to be added to the Model. Note
            that apertures without a parent Face are not allowed for energy models.
        doors_: A list of honeybee Doors to be added to the Model. Note
            that doors without a parent Face are not allowed for energy models.
        _name_: Text to be used for the name and identifier of the Model. If no
            name is provided, it will be "unnamed".
    
    Returns:
        report: Reports, errors, warnings, etc.
        model: A Honeybee Model object possessing all of the input geometry
            objects.
"""

ghenv.Component.Name = "HB Model"
ghenv.Component.NickName = 'Model'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.typing import clean_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import units_system, tolerance, angle_tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def check_all_geo_none():
    """Check whether all of the geometry inputs to this component are None."""
    return all(obj_list == [] or obj_list == [None] for obj_list in
               (rooms_, faces_, shades_, apertures_, doors_))


if all_required_inputs(ghenv.Component) and not check_all_geo_none():
    # set a default name and get the Rhino Model units
    name = clean_string(_name_) if _name_ is not None else 'unnamed'
    units = units_system()

    # create the model
    model = Model(name, rooms_, faces_, shades_, apertures_, doors_,
                  units=units, tolerance=tolerance, angle_tolerance=angle_tolerance)
    if _name_ is not None:
        model.display_name = _name_
