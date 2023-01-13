# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Quickly preview any Honeybee geometry object as a wire frame within the Rhino
scene, including all sub-faces and assigned shades.
-

    Args:
        _hb_objs: A Honeybee Model, Room, Face, Shade, Aperture, or Door to be previewed
            as a wire frame in the Rhino scene.
    
    Returns:
        geo: The Rhino wireframe version of the Honeybee geometry object, which
            will be visible in the Rhino scene.
"""

ghenv.Component.Name = 'HB Visualize Wireframe'
ghenv.Component.NickName = 'VizWireF'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.shade import Shade
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3d_to_wireframe
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def add_door(door, geo):
    """Add Door geometry to a geo list."""
    geo.extend(from_face3d_to_wireframe(door.geometry))
    for shd in door.shades:
        geo.extend(from_face3d_to_wireframe(shd.geometry))

def add_aperture(aperture, geo):
    """Add Aperture geometry to a geo list."""
    geo.extend(from_face3d_to_wireframe(aperture.geometry))
    for shd in aperture.shades:
        geo.extend(from_face3d_to_wireframe(shd.geometry))

def add_face(face, geo):
    """Add Face geometry to a geo list."""
    geo.extend(from_face3d_to_wireframe(face.geometry))
    for ap in face.apertures:
        add_aperture(ap, geo)
    for dr in face.doors:
        add_door(dr, geo)
    for shd in face.shades:
        geo.extend(from_face3d_to_wireframe(shd.geometry))

def add_room(room, geo):
    """Add Room geometry to a geo list."""
    for face in room.faces:
        add_face(face, geo)
    for shd in room.shades:
        geo.extend(from_face3d_to_wireframe(shd.geometry))

def add_model(model, geo):
    """Add Model geometry to a geo list."""
    for room in model.rooms:
        add_room(room, geo)
    for face in model.orphaned_faces:
        add_face(face, geo)
    for ap in model.orphaned_apertures:
        add_aperture(ap, geo)
    for dr in model.orphaned_doors:
        add_door(dr, geo)
    for shd in model.orphaned_shades:
        geo.extend(from_face3d_to_wireframe(shd.geometry))


if all_required_inputs(ghenv.Component):
    # list of rhino geometry to be filled with content
    geo = []
    
    # loop through all objects and add them
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Room):
            add_room(hb_obj, geo)
        elif isinstance(hb_obj, Face):
            add_face(hb_obj, geo)
        elif isinstance(hb_obj, Aperture):
            add_aperture(hb_obj, geo)
        elif isinstance(hb_obj, Door):
            add_door(hb_obj, geo)
        elif isinstance(hb_obj, Shade):
            geo.extend(from_face3d_to_wireframe(hb_obj.geometry))
        elif isinstance(hb_obj, Model):
            add_model(hb_obj, geo)
        else:
            raise TypeError(
                'Unrecognized honeybee object type: {}'.format(type(hb_obj)))