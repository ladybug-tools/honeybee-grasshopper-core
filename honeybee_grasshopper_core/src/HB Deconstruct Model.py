# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a Honeybee Model object into all of its constituent Honeybee objects.
-

    Args:
        _model: A Honeybee Model to be deconstructed into into its constituent
            objects (Rooms, Faces, Apertures, Doors Shades).
    
    Returns:
        rooms: All of the Room objects contained within the input Model.
        faces: All of the orphaned Face objects within the input Model.
            This only oncludes parent-less Faces and does not include any Faces
            that belong to a Room.
        apertures: All of the orphaned Aperture objects within the input Model.
            This only oncludes parent-less Apertures and does not include any
            Apertures that belong to a Face.
        doors: All of the orphaned Door objects within the input Model.
            This only oncludes parent-less Doors and does not include any Doors
            that belong to a Face.
        shades: All of the orphaned Shade objects within the input Model.
            This only oncludes parent-less Shades and does not include any Shades
            that belong to an Aperture, Face, or Room.
"""

ghenv.Component.Name = "HB Deconstruct Model"
ghenv.Component.NickName = 'DeconstructModel'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the honeybee dependencies
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_model, Model), \
        'Input _model must be a Model. Got {}'.format(type(_model))

    rooms = _model.rooms
    faces = _model.orphaned_faces
    apertures = _model.orphaned_apertures
    doors = _model.orphaned_doors
    shades = _model.orphaned_shades
