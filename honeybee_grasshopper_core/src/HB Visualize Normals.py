# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get aligned points and vectors to preview the normal direction of any Honeybee
geometry object the Rhino scene, including all sub-faces and assigned shades.
-

    Args:
        _hb_objs: A Honeybee Model, Room, Face, Shade, Aperture, or Door for which
            points and vectors will be output in the Rhino scene to show the
            object's orientation.

    Returns:
        points: Points that lie at the center of each surface of the connected _hb_objs.
            These should be connected to the "Anchor" input of a native Grasshopper
            "Vector Display" component.
        vectors: Normal vectors for each surface of the connected _hb_objs. These
            should be connected to the "Vector" input of a native Grasshopper
            "Vector Display" component.
"""

ghenv.Component.Name = 'HB Visualize Normals'
ghenv.Component.NickName = 'VizNorm'
ghenv.Component.Message = '1.6.2'
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
    from honeybee.units import parse_distance_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import units_system
    from ladybug_rhino.fromgeometry import from_point3d, from_vector3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# tolerance for computing the pole of inaccessibility
p_tol = parse_distance_string('0.01m', units_system())


def point_on_face(f_geo):
    """Get a point that lies on a Face3D."""
    return f_geo.center if f_geo.is_convex else f_geo.pole_of_inaccessibility(p_tol)


def add_door(door, points, vectors):
    """Add Door normals."""
    points.append(from_point3d(point_on_face(door.geometry)))
    vectors.append(from_vector3d(door.normal))
    for shd in door.shades:
        points.append(from_point3d(point_on_face(shd.geometry)))
        vectors.append(from_vector3d(shd.normal))

def add_aperture(aperture, points, vectors):
    """Add Aperture normals."""
    points.append(from_point3d(point_on_face(aperture.geometry)))
    vectors.append(from_vector3d(aperture.normal))
    for shd in aperture.shades:
        points.append(from_point3d(point_on_face(shd.geometry)))
        vectors.append(from_vector3d(shd.normal))

def add_face(face, points, vectors):
    """Add Face normals."""
    points.append(from_point3d(point_on_face(face.geometry)))
    vectors.append(from_vector3d(face.normal))
    for ap in face.apertures:
        add_aperture(ap, points, vectors)
    for dr in face.doors:
        add_door(dr, points, vectors)
    for shd in face.shades:
        points.append(from_point3d(point_on_face(shd.geometry)))
        vectors.append(from_vector3d(shd.normal))

def add_room(room, points, vectors):
    """Add Room normals."""
    for face in room.faces:
        add_face(face, points, vectors)
    for shd in room.shades:
        points.append(from_point3d(point_on_face(shd.geometry)))
        vectors.append(from_vector3d(shd.normal))

def add_model(model, points, vectors):
    """Add Model normals."""
    for room in model.rooms:
        add_room(room, points, vectors)
    for face in model.orphaned_faces:
        add_face(face, points, vectors)
    for ap in model.orphaned_apertures:
        add_aperture(ap, points, vectors)
    for dr in model.orphaned_doors:
        add_door(door, points, vectors)
    for shd in model.orphaned_shades:
        points.append(from_point3d(point_on_face(shd.geometry)))
        vectors.append(from_vector3d(shd.normal))


if all_required_inputs(ghenv.Component):
    # list of rhino geometry to be filled with content
    points = []
    vectors = []

    # loop through all objects and add them
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Room):
            add_room(hb_obj, points, vectors)
        elif isinstance(hb_obj, Face):
            add_face(hb_obj, points, vectors)
        elif isinstance(hb_obj, Aperture):
            add_aperture(hb_obj, points, vectors)
        elif isinstance(hb_obj, Door):
            add_door(hb_obj, points, vectors)
        elif isinstance(hb_obj, Shade):
            points.append(from_point3d(hb_obj.center))
            vectors.append(from_vector3d(hb_obj.normal))
        elif isinstance(hb_obj, Model):
            add_model(hb_obj, points, vectors)
        else:
            raise TypeError(
                'Unrecognized honeybee object type: {}'.format(type(hb_obj)))
