# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add a Honeybee Aperture or Door to a parent Face or Room.
-

    Args:
        _hb_obj: A Honeybee Face or a Room to which the _sub_faces should be added.
        _sub_faces: A list of Honeybee Apertures and/or Doors that will be added
            to the input _hb_obj.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_obj: The input Honeybee Face or a Room with the input _sub_faces added
            to it.
"""

ghenv.Component.Name = "HB Add Subface"
ghenv.Component.NickName = 'AddSubface'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
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

already_added_ids = set()  # track whether a given sub-face is already added
indoor_faces = {}


def add_sub_face(face, sub_face):
    """Add a sub-face (either Aperture or Door) to a parent Face."""
    if isinstance(sub_face, Aperture):  # the sub-face is an Aperture
        face.add_aperture(sub_face)
    else:  # the sub-face is a Door
        face.add_door(sub_face)


def check_and_add_sub_face(face, sub_faces):
    """Check whether a sub-face is valid for a face and, if so, add it."""
    for i, sf in enumerate(sub_faces):
        if face.geometry.is_sub_face(sf.geometry, tolerance, angle_tolerance):
            if isinstance(face.boundary_condition, Surface):
                try:
                    indoor_faces[face.identifier][1].append(sf)
                except KeyError:  # the first time we're encountering the face
                    indoor_faces[face.identifier] = [face, [sf]]
                sf_ids[i] = None
            else:
                if sf.identifier in already_added_ids:
                    sf = sf.duplicate()  # make sure the sub-face isn't added twice
                    sf.add_prefix('Ajd')
                already_added_ids.add(sf.identifier)
                sf_ids[i] = None
                add_sub_face(face, sf)


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_obj = [obj.duplicate() for obj in _hb_obj]
    sub_faces = [sf.duplicate() for sf in _sub_faces]
    sf_ids = [sf.identifier for sf in sub_faces]

    # check and add the sub-faces
    for obj in hb_obj:
        if isinstance(obj, Face):
            check_and_add_sub_face(obj, sub_faces)
        elif isinstance(obj, Room):
            for face in obj.faces:
                check_and_add_sub_face(face, sub_faces)
        else:
            raise TypeError('Expected Honeybee Face or Room. '
                            'Got {}.'.format(type(obj)))

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
            print msg
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

    # if any of the sub-faces were not added, give a warning
    unmatched_ids = [sf_id for sf_id in sf_ids if sf_id is not None]
    msg = 'The following sub-faces were not matched with any parent Face:' \
        '\n{}'.format('\n'.join(unmatched_ids))
    if len(unmatched_ids) != 0:
        print msg
        give_warning(ghenv.Component, msg)
