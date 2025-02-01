# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Separate and group Honeybee Faces, Apertures, Doors and Shades by any attribute
that the objects possess.
_
This can be used to group faces by construction, modifier, etc.
-

    Args:
        _hb_objs: An array of honeybee Rooms, Faces, Apertures, Doors or Shades
            to be separated by their attributes in the Rhino scene.
        _attribute: Text for the name of the Face attribute with which the
            Faces should be labeled. The Honeybee "Face Attributes" component
            lists all of the core attributes of the room. Also, each Honeybee
            extension (ie. Radiance, Energy) includes its own component that
            lists the Face attributes of that extension.
        value_: An optional value of the attribute that can be used to filter
            the output rooms. For example, if the input attribute is "Azimuth"
            a value for the orientation of the Face can be plugged in here
            (eg. "180" for south-facing) in order to get Faces with only
            this oreintation.

    Returns:
        values: A list of values with one attribute value for each branch of the
            output hb_objs.
         hb_objs: A data tree of honeybee faces and sub-faces with each branc
            of the tree representing a different attribute value.
"""

ghenv.Component.Name = "HB Faces by Attribute"
ghenv.Component.NickName = 'FacesByAttr'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '2 :: Organize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.colorobj import ColorFace
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any faces from input Rooms or Models
    faces = []
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Room):
            faces.extend(hb_obj.faces)
            faces.extend(hb_obj.shades)
        elif isinstance(hb_obj, Room):
            faces.append(hb_obj)
        elif isinstance(hb_obj, Model):
            for room in hb_obj.rooms:
                faces.extend(room.faces)
                faces.extend(room.shades)
            faces.extend(hb_obj.orphaned_faces)
            faces.extend(hb_obj.orphaned_apertures)
            faces.extend(hb_obj.orphaned_doors)
            faces.extend(hb_obj.orphaned_shades)
            faces.extend(hb_obj.shade_meshes)
        else:
            msg = 'Expected Face, Room or Model. Got {}.'.format(type(hb_obj))
            raise TypeError(msg)

    # use the ColorFace object to get a set of attributes assigned to the faces
    color_obj = ColorFace(faces, _attribute)

    # loop through each of the hb_objs and get the attribute
    if len(value_) == 0:
        values = color_obj.attributes_unique
        hb_objs = [[] for val in values]
        for atr, face in zip(color_obj.attributes, color_obj.flat_faces):
            atr_i = values.index(atr)
            hb_objs[atr_i].append(face)
    else:
        values = [atr for atr in color_obj.attributes_unique if atr in value_]
        hb_objs = [[] for val in values]
        for atr, face in zip(color_obj.attributes, color_obj.flat_faces):
            if atr in values:
                atr_i = values.index(atr)
                hb_objs[atr_i].append(face)
    hb_objs = list_to_data_tree(hb_objs)
