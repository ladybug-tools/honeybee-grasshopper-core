# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Lablel Honeybee faces and sub-faces with their attributes in the Rhino scene.
_
This can be used as a means to check that correct properties are assigned to
different faces and sub-faces.
-

    Args:
        _hb_obj: Honeybee Faces or Rooms to be labeled with their attributes in
            the Rhino scene.
        _attribute_: Text for the name of the attribute with which the faces or
            sub-faces should be labeled. The Honeybee "Face Attributes" component
            lists all of the core attributes of the room. Also, each Honeybee
            extension (ie. Radiance, Energy) includes its own component that lists
            the face and sub-face attributes of that extension. Default: "name".
        _txt_height_: An optional number for the height of the text in the Rhino
            scene.  The default is auto-calculated based on the dimensions of the
            input geometry.
        _font_: An optional name of a font in which the labels will display. This
            must be a font that is installed on this machine in order to work
            correctly. Default: "Arial".
    
    Returns:
        label_text: The text with which each of the faces or sub-faces are labeled.
        base_pts: The base point for each of the text labels.
        labels: The text objects that are displaying within the Rhino scene.
        wire_frame: A list of curves representing the outlines of the faces or
            sub-faces. This is useful for understanding which geometry elements
            each label corresponds to.
"""

ghenv.Component.Name = "HB Label Faces"
ghenv.Component.NickName = 'LableFaces'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import math

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.plane import Plane
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3d_to_wireframe, from_plane
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# hide the base_pts output from the scene
ghenv.Component.Params.Output[1].Hidden = True


def label_face(face, _attribute_, _font_, label_text, base_pts, labels, wire_frame):
    """Generate labels for a face or sub-face and add it to a list."""
    # get the attribute from the object
    if _attribute_.startswith('properties.'):  # extension attribute
        attributes = _attribute_.split('.')  # get all the sub-attributes
        current_obj = face
        try:
            for attribute in attributes:
                current_obj = getattr(current_obj, attribute)
            face_prop = str(current_obj)  # in case the property is float or int
        except AttributeError as e:
            if 'NoneType' in str(e):  # it's a valid attribute but it's not assigned
                face_prop = 'None'
            else:  # it's not a valid attribute
                face_prop = 'N/A'
    else:  # honeybee-core attribute
        try:
            face_prop = str(getattr(face, _attribute_))
        except AttributeError:
            face_prop = 'N/A'
    
    # get a base plane and text height for the text label
    cent_pt = face.geometry.center  # base point for the text
    base_plane = Plane(face.normal, cent_pt)
    if base_plane.y.z < 0:  # base plane pointing downwards; rotate it
        base_plane = base_plane.rotate(base_plane.n, math.pi, base_plane.o)
    if _txt_height_ is None:  # auto-calculate default text height
        txt_len = len(face_prop) if len(face_prop) > 10 else 10
        largest_dim = max((face.geometry.max.x - face.geometry.min.x),
                           (face.geometry.max.y - face.geometry.min.y))
        txt_h = largest_dim / (txt_len * 2)
    else:
        txt_h = _txt_height_
    
    # move base plane origin a little to avoid overlaps of adjacent labels
    if base_plane.n.x != 0:
        m_vec = base_plane.y if base_plane.n.x < 0 else -base_plane.y
    else:
        m_vec = base_plane.y if base_plane.n.z < 0 else -base_plane.y
    base_plane = base_plane.move(m_vec * txt_h)
    
    # create the text label
    label = text_objects(face_prop, base_plane, txt_h, font=_font_,
                         horizontal_alignment=1, vertical_alignment=3)
    
    # append everything to the lists
    label_text.append(face_prop)
    base_pts.append(from_plane(base_plane))
    labels.append(label)
    wire_frame.append(from_face3d_to_wireframe(face.geometry))


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    label_text = []
    base_pts = []
    labels = []
    wire_frame = []
    
    # set the default attribute and font
    if _attribute_ is None:
        _attribute_ = 'name'
    if _font_ is None:
        _font_ = 'Arial'
    
    # generate the labels
    if not sub_faces_:
        for obj in _hb_obj:
            if isinstance(obj, Room):
                for face in obj.faces:
                    label_face(face, _attribute_, _font_, label_text, base_pts,
                               labels, wire_frame)
            elif isinstance(obj, Face):
                label_face(obj, _attribute_, _font_, label_text, base_pts,
                           labels, wire_frame)
    else:
        for obj in _hb_obj:
            if isinstance(obj, Room):
                for face in obj.faces:
                    for ap in face.apertures:
                        label_face(ap, _attribute_, _font_, label_text, base_pts,
                                   labels, wire_frame)
                    for dr in face.doors:
                         label_face(dr, _attribute_, _font_, label_text, base_pts,
                                    labels, wire_frame)
            elif isinstance(obj, Face):
                for ap in face.apertures:
                    label_face(ap, _attribute_, _font_, label_text, base_pts,
                               labels, wire_frame)
                for dr in face.doors:
                    label_face(dr, _attribute_, _font_, label_text, base_pts,
                               labels, wire_frame)
            elif isinstance(obj, (Aperture, Door)):
                label_face(obj, _attribute_, _font_, label_text, base_pts,
                          labels, wire_frame)