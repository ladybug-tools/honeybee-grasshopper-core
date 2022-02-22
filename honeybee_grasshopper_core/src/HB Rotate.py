# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Rotate any Honeybee geometry object or a Model by an angle.
-

    Args:
        _hb_objs: Any Honeybee geometry object (eg. Room, Face, Aperture, Door or
            Shade) to be rotated by an angle. This can also be a Honeybee Model
            object to be rotated.
        _angle: An angle for rotation in degrees.
        _origin_: A Point3D for the origin around which the object will be rotated.
            If None,  it will be rotated from each object's center point unless
            the input object is a Model, in which case, it will be rotated from
            the world origin (0, 0, 0).
        _axis_: A Vector3D axis representing the axis of rotation. If None, the
            axis will be a Z-vector (0, 0, 1) and the object will be rotated
            within the XY plane.
        prefix_: Optional text string that will be inserted at the start of the
            identifiers and display names of all transformed objects, their child
            objects, and their adjacent Surface boundary condition objects. This
            is particularly useful in workflows where you duplicate and edit a
            starting object and then want to combine it with the original object
            into one Model (like making a model of repeated rooms) since all
            objects within a Model must have unique identifiers. It is recommended
            that this prefix be short to avoid maxing out the 100 allowable
            characters for honeybee identifiers. If None, no prefix will be
            added to the input objects and all identifiers and display names
            will remain the same. Default: None.
    
    Returns:
        hb_objs: The input _hb_objs that has been rotated by the input angle.
"""

ghenv.Component.Name = "HB Rotate"
ghenv.Component.NickName = 'Rotate'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "6"

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.pointvector import Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_point3d, to_vector3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    hb_objs = [obj.duplicate() for obj in _hb_objs]  # duplicate the initial objects
    
    # set the default origin
    if _origin_ is not None:
        pt = to_point3d(_origin_)
    else:
        pt = []
        for obj in hb_objs:
            origin = obj.center if not isinstance(obj, Model) else Point3D(0, 0, 0)
            pt.append(origin)
    
    # rotate all of the objects
    if _origin_ is None and _axis_ is None:
        for i, obj in enumerate(hb_objs):
            obj.rotate_xy(_angle, pt[i])
    elif _origin_ is not None and _axis_ is None:
        for obj in hb_objs:
            obj.rotate_xy(_angle, pt)
    elif _origin_ is not None and _axis_ is not None:
        _axis_ = to_vector3d(_axis_)
        for obj in hb_objs:
            obj.rotate(_axis_, _angle, pt)
    else:
        _axis_ = to_vector3d(_axis_)
        for i, obj in enumerate(hb_objs):
            obj.rotate(_axis_, _angle, pt[i])
    
    # add the prefix if specified
    if prefix_ is not None:
        for obj in hb_objs:
            obj.add_prefix(prefix_)