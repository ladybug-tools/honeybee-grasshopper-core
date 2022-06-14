# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add skylight apertures to a Honeybee Face or Room given a ratio of aperture area
to face area.
_
Note that this component will only add Apertures to Faces that are Roofs and have
an Outdoors boundary condition.
-

    Args:
        _hb_objs: A list of honeybee Rooms or Faces to which skylight Apertures
            will be added based on the inputs.
        _ratio: A number between 0 and 1 for the ratio between the area of
            the apertures and the area of the parent face.
        _x_dim_: The x dimension of the grid cells as a number. (Default: 3 meters)
        _y_dim_: The y dimension of the grid cells as a number. Default is None,
            which will assume the same cell dimension for y as is set for x.
        operable_: An optional boolean to note whether the generated Apertures
            can be opened for ventilation. Default: False.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Honeybee Face or Room with skylight Apertures generated
            from the input parameters.
"""

ghenv.Component.Name = 'HB Skylights by Ratio'
ghenv.Component.NickName = 'SkylightsByRatio'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.facetype import RoofCeiling
    from honeybee.room import Room
    from honeybee.face import Face
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def can_host_apeture(face):
    """Test if a face is intended to host apertures (according to this component)."""
    return isinstance(face.boundary_condition, Outdoors) and \
        isinstance(face.type, RoofCeiling)


def assign_apertures(face, rat, xd, yd, op):
    """Assign apertures to a Face based on a set of inputs."""
    face.apertures_by_ratio_gridded(rat, xd, yd)

    # try to assign the operable property
    if op:
        for ap in face.apertures:
            ap.is_operable = op


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # set defaults for any blank inputs
    if _x_dim_ is None and _x_dim_ is None:
        conversion = conversion_to_meters()
        _x_dim_ = _x_dim_ if _x_dim_ is None else 3.0 / conversion
    elif _x_dim_ is None:
        _x_dim_ == _y_dim_

    # loop through the input objects and add apertures
    for obj in hb_objs:
        if isinstance(obj, Room):
            for face in obj.faces:
                if can_host_apeture(face):
                    assign_apertures(face, _ratio, _x_dim_, _y_dim_, operable_)
        elif isinstance(obj, Face):
            if can_host_apeture(obj):
                assign_apertures(obj, _ratio, _x_dim_, _y_dim_, operable_)
        else:
            raise TypeError(
                'Input _hb_objs must be a Room or Face. Not {}.'.format(type(obj)))
