# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Preview any Honeybee geometry object within the Rhino scene, including all
sub-faces and assigned shades.
-

    Args:
        _hb_objs: A Honeybee Model, Room, Face, Shade, Aperture, or Door to be
            previewed in the Rhino scene.
    
    Returns:
        geo: The Rhino version of the Honeybee geometry object, which will be
            visible in the Rhino scene.
"""

ghenv.Component.Name = "HB Visualize All"
ghenv.Component.NickName = 'VizAll'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.shade import Shade
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.fromgeometry import from_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import Rhino.Geometry as rg


def add_shade(shd, shades):
    """Add Shade geometry to a shades list."""
    shades.append(from_face3d(shd.geometry))

def add_door(door, geo, shades):
    """Add Door geometry to a geo list and shades list."""
    geo.append(from_face3d(door.geometry))
    for shd in door.shades:
        add_shade(shd, shades)

def add_aperture(aperture, geo, shades):
    """Add Aperture geometry to a geo and shades list."""
    geo.append(from_face3d(aperture.geometry))
    for shd in aperture.shades:
        add_shade(shd, shades)

def add_face(face, geo, shades):
    """Add Face geometry to a geo and shades list."""
    geo.append(from_face3d(face.punched_geometry))
    for ap in face.apertures:
        add_aperture(ap, geo, shades)
    for dr in face.doors:
        add_door(dr, geo, shades)
    for shd in face.shades:
        add_shade(shd, shades)

def add_room(room, geo, shades):
    """Add Room geometry to a geo and shades list."""
    face_breps = []
    for face in room.faces:
        add_face(face, face_breps, shades)
    for shd in room.shades:
        add_shade(shd, shades)
    geo.extend(rg.Brep.JoinBreps(face_breps, tolerance))

def add_model(model, geo, shades):
    """Add Model geometry to a geo and shades list."""
    for room in model.rooms:
        add_room(room, geo, shades)
    for face in model.orphaned_faces:
        add_face(face, geo, shades)
    for ap in model.orphaned_apertures:
        add_aperture(ap, geo, shades)
    for dr in model.orphaned_doors:
        add_door(dr, geo, shades)
    for shd in model.orphaned_shades:
        add_shade(shd, shades)


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    geo = []
    shades = []
    
    # loop through all objects and add them
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Room):
            add_room(hb_obj, geo, shades)
        elif isinstance(hb_obj, Face):
            add_face(hb_obj, geo, shades)
        elif isinstance(hb_obj, Aperture):
            add_aperture(hb_obj, geo, shades)
        elif isinstance(hb_obj, Shade):
            add_shade(hb_obj, shades)
        elif isinstance(hb_obj, Door):
            add_door(hb_obj, geo, shades)
        elif isinstance(hb_obj, Model):
            add_model(hb_obj, geo, shades)
        else:
            raise TypeError(
                'Unrecognized honeybee object type: {}'.format(type(hb_obj)))
    
    # group the shade geometry with the other objects
    geo.extend(shades)