# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct any Honeybee geometry object into all of its constituent Honeybee objects.
_
This is useful for editing auto-generated child objects separately from their parent.
For example, if you want to move all of the overhangs that were auto-generated for
a Room downward in order to turn them into light shelves, this component can give
you all of such shades. Then you can move the shades and assign them back to the
original shade-less Room object.
-

    Args:
        _hb_obj: A Honeybee Room, Face, Aperture, Door or Shade to be deconstructed
             into its constituent objects. Note that, Doors and Shades do not have
             sub-objects assigned to them and the original object will be output.
    
    Returns:
        faces: All of the Face objects that make up the input _hb_obj. This includes
            Faces that make up input Rooms as well as any input orphaned Faces.
        apertures: All of the Aperture objects that make up the input _hb_obj.
            This includes any Apertures assigned to input Rooms or Faces as well
            as any input orphaned Apertures.
        doors: All of the Door objects that make up the input _hb_obj. This includes
            any Doors assigned to input Rooms or Faces as well as any input
            orphaned Doors.
        shades: All of the Shade objects that make up the input _hb_obj. This includes
            any Shades assigned to input Rooms, Faces or Apertures as well as any
            input orphaned Shades.
"""

ghenv.Component.Name = "HB Deconstruct Object"
ghenv.Component.NickName = 'DecnstrObj'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the core honeybee dependencies
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.shade import Shade
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

def deconstruct_door(door, doors, shades):
    """Deconstruct Door object."""
    doors.append(door)
    for shd in door.shades:
        shades.append(shd)

def deconstruct_aperture(aperture, apertures, shades):
    """Deconstruct Aperture object."""
    apertures.append(aperture)
    for shd in aperture.shades:
        shades.append(shd)

def deconstruct_face(face, faces, apertures, doors, shades):
    """Deconstruct Face object."""
    faces.append(face)
    for ap in face.apertures:
        deconstruct_aperture(ap, apertures, shades)
    for dr in face.doors:
        deconstruct_door(dr, doors, shades)
    for shd in face.shades:
        shades.append(shd)

def deconstruct_room(room, faces, apertures, doors, shades):
    """Deconstruct Room object."""
    for face in room.faces:
        deconstruct_face(face, faces, apertures, doors, shades)
    for shd in room.shades:
        shades.append(shd)


if all_required_inputs(ghenv.Component):
    # lists of to be filled with component objects
    faces = []
    apertures = []
    doors = []
    shades = []
    
    # deconstruct objects
    if isinstance(_hb_obj, Room):
        deconstruct_room(_hb_obj, faces, apertures, doors, shades)
    elif isinstance(_hb_obj, Face):
        deconstruct_face(_hb_obj, faces, apertures, doors, shades)
    elif isinstance(_hb_obj, Aperture):
        deconstruct_aperture(_hb_obj, apertures, shades)
    elif isinstance(_hb_obj, Door):
        deconstruct_door(_hb_obj, doors, shades)
    elif isinstance(_hb_obj, Shade):
        shades.append(_hb_obj)
    else:
        raise TypeError(
            'Unrecognized honeybee object type: {}'.format(type(_hb_obj)))