# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get the edges of a Model's envelope grouped based on the objects they adjoin.
_
The edges returned by this component will only exist along the exterior
envelope of the Model's rooms as defined by the contiguous volume across
all interior adjacencies. In this way, edges that adjoin two honeybee rooms
will only be represented once in the list (and not twice for the two rooms).
_
The lengths of the resulting edges are useful for evaluating thermal bridges
across the model.
-

    Args:
        _model: A honeybee Model with rooms for which adjacencies have been solved.
        ex_coplanar_: Boolean to note whether edges falling between two coplanar Faces
            in the building envelope should be included in the result (False) or
            excluded from it (True). (Default: False).

    Returns:
        ext_apertures: A list of line segments for the borders around exterior apertures.
        ext_doors: A list of line segments for the borders around exterior doors.
        roofs_to_walls: A list of line segments where roofs meet exterior walls (or floors).
            Note that both the roof Face and the wall/floor Face must be next to one
            another in the model's outer envelope and have outdoor boundary conditions for
            the edge to show up in this list.
        slabs_to_walls: A list of line segments where ground floor slabs meet exterior
            walls or roofs. Note that the floor Face must have a ground boundary
            condition and the wall or roof Face must have an outdoor boundary
            condition for the edge between the two Faces to show up in this list.
        exp_floors_to_walls: A list of line segments where exposed floors meet exterior
            walls. Note that both the wall Face and the floor Face must be next
            to one another in the model's outer envelope and have outdoor boundary
            conditions for the edge to show up in this list.
        ext_walls_to_walls: A list of line segments where exterior walls meet one another.
            Note that both wall Faces must be next to one another in the model's
            outer envelope and have outdoor boundary conditions for the edge to
            show up in this list.
        roof_ridges: A list of line segments where exterior roofs meet one another.
            Note that both roof Faces must be next to one another in the model's
            outer envelope and have outdoor boundary conditions for the edge to
            show up in this list.
        exp_floors_to_floors: A list of line segments where exposed floors meet one another.
            Note that both floor Faces must be next to one another in the model's
            outer envelope and have outdoor boundary conditions for the edge to
            show up in this list.
        underground: A list of line segments where underground Faces meet one another.
            Note that both Faces must be next to one another in the model's
            outer envelope and have ground boundary conditions for the edge
            to show up in this list.
"""

ghenv.Component.Name = 'HB Envelope Edges'
ghenv.Component.NickName = 'EnvelopeEdges'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.fromgeometry import from_linesegment3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))



if all_required_inputs(ghenv.Component):
    # get the edges of the envelope components
    assert isinstance(_model, Model), 'Expected Honeybee Model. Got {}.'.format(type(_model))
    roofs_to_walls, slabs_to_walls, exp_floors_to_walls, ext_walls_to_walls, \
        roof_ridges, exp_floors_to_floors, underground = \
        _model.classified_envelope_edges(exclude_coplanar=ex_coplanar_)

    # translate edges to Rhino lines
    ext_apertures = [from_linesegment3d(lin) for lin in _model.exterior_aperture_edges]
    ext_doors = [from_linesegment3d(lin) for lin in _model.exterior_door_edges]
    roofs_to_walls = [from_linesegment3d(lin) for lin in roofs_to_walls]
    slabs_to_walls = [from_linesegment3d(lin) for lin in slabs_to_walls]
    exp_floors_to_walls = [from_linesegment3d(lin) for lin in exp_floors_to_walls]
    ext_walls_to_walls = [from_linesegment3d(lin) for lin in ext_walls_to_walls]
    roof_ridges = [from_linesegment3d(lin) for lin in roof_ridges]
    exp_floors_to_floors = [from_linesegment3d(lin) for lin in exp_floors_to_floors]
    underground = [from_linesegment3d(lin) for lin in underground]
