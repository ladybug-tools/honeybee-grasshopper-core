# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Reflect any Honeybee geometry object or a Model across a plane.
-

    Args:
        _hb_obj: Any Honeybee geometry object (eg. Room, Face, Aperture, Door or
            Shade) to be reflected across a plane. This can also be a Honeybee
            Model object to be reflected.
        _plane: A Plane across which the object will be reflected.
        prefix_: Optional text string that will be inserted at the start of the
            names of all transformed objects, their child objects, and their
            adjacent Surface boundary condition objects. This is particularly
            useful in workflows where you duplicate and edit a starting object
            and then want to combine it with the original object into one Model
            (like making a model of repeated rooms) since all objects within a
            Model must have unique names. It is recommended that this name be
            short to avoid maxing out the 100 allowable characters for honeybee
            names. If None, no prefix will be added to the input object names
            and all names will remain the same. Default: None.
    
    Returns:
        hb_obj: The input _hb_obj that has been reflected across the input plane.
"""

ghenv.Component.Name = "HB Reflect"
ghenv.Component.NickName = 'Reflect'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "6"

try:
    from ladybug_rhino.togeometry import to_plane
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

if all_required_inputs(ghenv.Component):
    hb_obj = [obj.duplicate() for obj in _hb_obj]  # duplicate the initial objects
    plane = to_plane(_plane)  # translate the plane to ladybug_geometry
    
    # reflect all of the objects
    for obj in hb_obj:
        obj.reflect(plane)
    
    # add the prefix if specified
    if prefix_ is not None:
        for obj in hb_obj:
            obj.add_prefix(prefix_)