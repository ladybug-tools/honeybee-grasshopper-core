# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add a Honeybee Aperture or Door to a parent Face or Room.
-

    Args:
        _hb_obj: A Honeybee Face or a Room to which the _sub_faces should be added.
            This can also be an entire Honeybee Model in which case Apertures
            will be added to all FAces of the Model (including both Room Faces
            and orphaned Faces).
        _sub_faces: A list of Honeybee Apertures and/or Doors that will be added
            to the input _hb_obj.
        project_dist_: An optional number to be used to project the Aperture/Door geometry
            onto parent Faces. If specified, then Apertures within this distance
            of the parent Face will be projected and added. Otherwise,
            Apertures/Doors will only be added if they are coplanar and fully
            bounded by a parent Face.

    Returns:
        report: Reports, errors, warnings, etc.
        hb_obj: The input Honeybee Face or a Room with the input _sub_faces added
            to it.
        unmatched: A list of any Apertures or Doors that could not be matched and
            assigned to a parent Face.
"""

ghenv.Component.Name = "HB Add Subface"
ghenv.Component.NickName = 'AddSubface'
ghenv.Component.Message = '1.8.2'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

import math

try:  # import the core honeybee dependencies
    from ladybug_geometry.bounding import overlapping_bounding_boxes
    from ladybug_geometry.geometry3d.face import Face3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.boundarycondition import Surface, boundary_conditions
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

a_tol_min = math.radians(angle_tolerance)  # min tolerance for projection
a_tol_max = math.pi - angle_tolerance  # max tolerance for projection
already_added_ids = set()  # track whether a given sub-face is already added
indoor_faces = {}


def add_sub_face(face, sub_face):
    """Add a sub-face (either Aperture or Door) to a parent Face."""
    if isinstance(sub_face, Aperture):  # the sub-face is an Aperture
        face.add_aperture(sub_face)
    else:  # the sub-face is a Door
        face.add_door(sub_face)


def check_and_add_sub_face(face, sub_faces, dist):
    """Check whether a sub-face is valid for a face and, if so, add it."""
    for i, sf in enumerate(sub_faces):
        if overlapping_bounding_boxes(face.geometry, sf.geometry, dist):
            sf_to_add = None
            if project_dist_ is None:  # just check if it is a valid subface
                if face.geometry.is_sub_face(sf.geometry, tolerance, angle_tolerance):
                    sf_to_add = sf
            else:
                ang = sf.normal.angle(face.normal)
                if ang < a_tol_min or ang > a_tol_max:
                    clean_pts = [face.geometry.plane.project_point(pt)
                                 for pt in sf.geometry.boundary]
                    sf = sf.duplicate()
                    sf._geometry = Face3D(clean_pts)
                    sf_to_add = sf

            if sf_to_add is not None:  # add the subface to the parent
                if isinstance(face.boundary_condition, Surface):
                    try:
                        indoor_faces[face.identifier][1].append(sf)
                    except KeyError:  # the first time we're encountering the face
                        indoor_faces[face.identifier] = [face, [sf]]
                    unmatched_sfs[i] = None
                else:
                    if sf.identifier in already_added_ids:
                        sf = sf.duplicate()  # make sure the sub-face isn't added twice
                        sf.add_prefix('Ajd')
                    already_added_ids.add(sf.identifier)
                    unmatched_sfs[i] = None
                    add_sub_face(face, sf)


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_obj = [obj.duplicate() for obj in _hb_obj]
    sub_faces = [sf.duplicate() for sf in _sub_faces]
    unmatched_sfs = sub_faces[:]  # copy the input list

    # gather all of the parent Faces to be checked
    rel_faces = []
    for obj in hb_obj:
        if isinstance(obj, Face):
            rel_faces.append(obj)
        elif isinstance(obj, (Room, Model)):
            rel_faces.extend(obj.faces)
        else:
            raise TypeError('Expected Honeybee Face, Room or Model. '
                            'Got {}.'.format(type(obj)))
    dist = tolerance if project_dist_ is None else project_dist_
    for face in rel_faces:
        check_and_add_sub_face(face, sub_faces, dist)

    # for any Faces with a Surface boundary condition, add subfaces as a pair
    already_adj_ids = set()
    for in_face_id, in_face_props in indoor_faces.items():
        if in_face_id in already_adj_ids:
            continue
        face_1 = in_face_props[0]
        try:
            face_2 = indoor_faces[face_1.boundary_condition.boundary_condition_object][0]
        except KeyError as e:
            msg = 'Adding sub-faces to faces with interior (Surface) boundary ' \
                'conditions\nis only possible when both adjacent faces are in ' \
                'the input _hb_obj.\nFailed to find {}, which is adjacent ' \
                'to {}.'.format(e, in_face_id)
            print(msg)
            raise ValueError(msg)
        face_1.boundary_condition = boundary_conditions.outdoors
        face_2.boundary_condition = boundary_conditions.outdoors
        for sf in in_face_props[1]:
            add_sub_face(face_1, sf)
            sf2 = sf.duplicate()  # make sure the sub-face isn't added twice
            sf2.add_prefix('Ajd')
            add_sub_face(face_2, sf2)
        face_1.set_adjacency(face_2)
        already_adj_ids.add(face_2.identifier)

    # if a project_dist_ was specified, trim the apertures with the Face geometry
    if project_dist_ is not None:
        for face in rel_faces:
            if face.has_sub_faces:
                face.fix_invalid_sub_faces(
                    trim_with_parent=True, union_overlaps=False,
                    offset_distance=tolerance * 5, tolerance=tolerance)

    # if any of the sub-faces were not added, give a warning
    unmatched = [sf for sf in unmatched_sfs if sf is not None]
    unmatched_ids = [sf.display_name for sf in unmatched]
    msg = 'The following sub-faces were not matched with any parent Face:' \
        '\n{}'.format('\n'.join(unmatched_ids))
    if len(unmatched_ids) != 0:
        print msg
        give_warning(ghenv.Component, msg)
