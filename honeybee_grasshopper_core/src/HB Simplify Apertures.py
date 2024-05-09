# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Simplify the Apertures assigned to Honeybee Rooms or Faces to be as few as
possible while still maintaining approximately the same overall Aperture area.
_
By default, this component will only simplify Apertures in convex Faces by 
reducing them to a ratio represented with one or two clean Apertures.
For models without many concave Faces, this process usually produces a
fast-simulating result that matches the original window area exactly. However,
this operation will also change the placement of Apertures within a Face,
which may make it unsuitable for modeling the impact of Shades on Apertures
or for evaluating daylight.
_
For cases with concave Faces (which is typical for Roofs/Skylights) or when it
is desirable to keep Apertures in the same location within the parent Face,
the Apertures can be simplified by specifying a merge_dist_, which will join
together Apertures in close proximity to one another rather than reducing
them to a ratio.
-

    Args:
        _hb_objs: A list of honeybee Rooms or Faces to which Apertures will be
            simplified. This can also be an entire honeybee Model for
            which all Rooms will have Apertures simplified.
        merge_dist_: Distance between Apertures and/or Doors at which point they will be
            merged into a single Aperture. When unspecified, only Apertures within
            convex faces will be reduced to a ratio. This will match the
            original Aperture area exactly but it will change the placement of
            Apertures within the Face, which can make it unsuitable for modeling
            the impact of Shades on Apertures. When a value is specified here,
            concave Faces will be addressed and Apertures will remain where
            they are in the parent Face. The overall Aperture area may be a
            little larger thanks to merging across gaps that are less than or
            equal to the value specified but the result will be suitable
            for evaluating the impact of Shades or simulating daylight.
        del_interior_: Boolean to note whether the simplification process should remove
            all interior Apertures with a Surface boundary condition (True) or
            an attempt will be made to reset adjacencies after Apertures
            have been simplified/rebuilt (False). (Default: False).
        ignore_skylights_: Boolean to note whether the simplification process should ignore
            all skylights and leave them as they are. (Default: False).
        ignore_windows_: Boolean to note whether the simplification process should ignore
            all windows and leave them as they are. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Honeybee Face, Room or Model with Apertures simplified.
"""

ghenv.Component.Name = 'HB Simplify Apertures'
ghenv.Component.NickName = 'SimplifyAps'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Surface, boundary_conditions
    from honeybee.facetype import Wall, RoofCeiling
    from honeybee.face import Face
    from honeybee.room import Room
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def can_simplify_apeture(face):
    """Test if a face is intended to have its Apertures simplified."""
    if ignore_skylights_ and isinstance(face.type, RoofCeiling):
        return False
    elif ignore_windows_ and isinstance(face.type, Wall):
        return False
    return True


def simplify_face(face):
    """Simplify the Apertures of a Face."""
    if can_simplify_apeture(face):
        if merge_dist_ is None:
            if face.geometry.is_convex:
                face.apertures_by_ratio(face.aperture_ratio, tolerance)
        else:
            face.merge_neighboring_sub_faces(merge_dist_, tolerance)


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # loop through the input objects and collect all of the faces
    faces = []
    for obj in hb_objs:
        if isinstance(obj, Model):
            for room in obj.rooms:
                for face in room.faces:
                    if face.has_sub_faces:
                        faces.append(face)
        elif isinstance(obj, Room):
            for face in obj.faces:
                if face.has_sub_faces:
                    faces.append(face)
        elif isinstance(obj, Face):
            if obj.has_sub_faces:
                faces.append(obj)
        else:
            raise TypeError(
                'Input _hb_objs must be a Model, Room or Face. Not {}.'.format(type(obj)))

    # remove interior windows or build a list of adjacencies to reset
    face_adj_pairs = []
    if del_interior_:
        del_i = []
        for i, face in enumerate(faces):
            if isinstance(face.boundary_condition, Surface):
                face.remove_sub_faces()
                del_i.append(i)
        for di in reversed(del_i):
            faces.pop(di)
    else:
        adj_dict = {}
        for face in faces:
            if isinstance(face.boundary_condition, Surface):
                bc_obj_id = face.boundary_condition.boundary_condition_object
                try:  # assume that we already found the adjacent pair
                    adj_obj = adj_dict[bc_obj_id]
                    face_adj_pairs.append((face, adj_obj))
                except KeyError:  # we have not found the pair yet
                    adj_dict[face.identifier] = face
                face.boundary_condition = boundary_conditions.outdoors

    # simplify the Apertures
    for face in faces:
        simplify_face(face)

    # reset the adjacencies
    for face_1, face_2 in face_adj_pairs:
        face_1.set_adjacency(face_2)
