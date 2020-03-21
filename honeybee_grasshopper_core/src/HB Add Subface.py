# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def check_and_add_sub_face(face, sub_faces):
    """Check whether a sub-face is valid for a face and, if so, add it."""
    for sf in sub_faces:
        if face.geometry.is_sub_face(sf.geometry, tolerance, angle_tolerance):
            if isinstance(sf, Aperture):  # the sub-face is an Aperture
                face.add_aperture(sf)
            else:  # the sub-face is a Door
                face.add_door(sf)


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_obj = _hb_obj.duplicate()
    sub_faces = (sf.duplicate() for sf in _sub_faces)
    
    if isinstance(hb_obj, Face):
        check_and_add_sub_face(hb_obj, _sub_faces)
    elif isinstance(hb_obj, Room):
        for face in hb_obj.faces:
            check_and_add_sub_face(face, _sub_faces)
    else:
        raise TypeError('Expected Honeybee Face or Room. '
                        'Got {}.'.format(type(hb_obj)))