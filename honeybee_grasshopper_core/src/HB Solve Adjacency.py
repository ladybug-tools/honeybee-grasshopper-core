# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Solve adjacencies between a series of honeybee Rooms.
_
Note that rooms must have matching faces in order for them to be discovered as
adjacent.
-

    Args:
        _rooms: A list of honeybee Rooms for which adjacencies will be solved.
        ep_int_constr_: Optional construction subset list from the "HB Interior
            Construction Subset" component. This will be used to assign custom
            constructions for the adjacent Faces, Apertures, and Doors found
            in the process of solving adjacency. Note that None values in the
            input list correspond to constructions that will not change from
            the default. If no energy construction is assigned to a given Face
            type, Aperture or Door type, the default interior constructions
            will be assigned using the adjacent Rooms' ConstructionSet.
        rad_int_mat_: Optional material subset list. This will be used to assign
            custom radiance materials for the adjacent Faces, Apertures, and
            Doors found in the process of solving adjacency. Note that None values
            in the input list correspond to materials that will not change from
            the default. If no energy construction is assigned to a given Face
            type, Aperture or Door type, the default interior materials
            will be assigned using the adjacent Rooms' ModifierSet.
        adiabatic_: Set to True to have all of the adjacencies discovered by this
            component set to an adiabatic boundary condition. If False, a Surface
            boundary condition will be used for all adjacencies. Note that adabatic
            conditions are not allowed if interior windows are assigned to interior
            faces. Default: False.
        _run: Set to True to run the component and solve adjacencies.
    
    Returns:
        report: Reports, errors, warnings, etc.
        adj_rooms: The input Honeybee Rooms with adjacencies solved between
            matching Faces.
"""

ghenv.Component.Name = "HB Solve Adjacency"
ghenv.Component.NickName = 'SolveAdj'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import boundary_conditions
    from honeybee.facetype import Wall, RoofCeiling, Floor
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.construction.window import WindowConstruction
except ImportError as e:
    if len(ep_int_constr_) != 0:
        raise ValueError('ep_int_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif adiabatic_ is not None:
        raise ValueError('adiabatic_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    import honeybee_radiance
except ImportError as e:
    if len(rad_int_mat_) != 0:
        raise ValueError('rad_int_mat_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


def reversed_opaque_constr(construction):
    """Get a version of a given OpaqueConstruction that is reversed."""
    if construction.is_symmetric:
        return construction
    return OpaqueConstruction('{}_Rev'.format(ep_constr_.name),
                              [mat for mat in reversed(ep_constr_.materials)])


def reversed_window_constr(construction):
    """Get a version of a given WindowConstruction that is reversed."""
    if construction.is_symmetric:
        return construction
    return WindowConstruction('{}_Rev'.format(ep_constr_.name),
                              [mat for mat in reversed(ep_constr_.materials)])


def apply_constr_to_face(adjacent_faces, construction, face_type):
    """Apply a given construction to adjacent faces of a certain type."""
    rev_constr = reversed_opaque_constr(construction)
    for face_pair in adjacent_faces:
        if isinstance(face_pair[0].type, face_type):
            face_pair[0].properties.energy.construction = construction
            face_pair[1].properties.energy.construction = rev_constr
        elif isinstance(face_pair[1].type, face_type):
            face_pair[1].properties.energy.construction = construction
            face_pair[0].properties.energy.construction = rev_constr


def apply_constr_to_door(adjacent_doors, construction, is_glass):
    """Apply a given construction to adjacent doors of a certain type."""
    rev_constr = reversed_window_constr(construction) if is_glass else \
        reversed_opaque_constr(construction)
    for dr_pair in adjacent_doors:
        if dr_pair[0].is_glass is is_glass:
            dr_pair[1].properties.energy.construction = construction
            dr_pair[0].properties.energy.construction = rev_constr


def apply_ep_int_constr(adj_info, ep_int_constr):
    """Apply the interior construction subset list to adjacent objects."""
    assert len(ep_int_constr) == 6, 'Input ep_int_constr_ is not valid.'
    
    if ep_int_constr[0] is not None:
        apply_constr_to_face(adj_info['adjacent_faces'], ep_int_constr[0], Wall)
    if ep_int_constr[1] is not None:
        apply_constr_to_face(adj_info['adjacent_faces'], ep_int_constr[1], RoofCeiling)
    if ep_int_constr[2] is not None:
        apply_constr_to_face(adj_info['adjacent_faces'], ep_int_constr[2], Floor)
    if ep_int_constr[3] is not None:
        rev_constr = reversed_window_constr(ep_int_constr[3])
        for ap_pair in adj_info['adjacent_apertures']:
            ap_pair[1].properties.energy.construction = ep_int_constr[3]
            ap_pair[0].properties.energy.construction = rev_constr
    if ep_int_constr[4] is not None:
        apply_constr_to_door(adj_info['adjacent_doors'], ep_int_constr[4], False)
    if ep_int_constr[5] is not None:
        apply_constr_to_door(adj_info['adjacent_doors'], ep_int_constr[5], True)


if all_required_inputs(ghenv.Component) and _run:
    adj_rooms = [room.duplicate() for room in _rooms] # duplicate the initial objects
    
    # solve adjacnecy
    adj_info = Room.solve_adjacency(adj_rooms, tolerance)
    
    # try to assign the energyplus constructions if specified
    if len(ep_int_constr_) != 0:
        apply_ep_int_constr(adj_info, ep_int_constr_)
    
    # try to assign the adiabatic boundary condition
    if adiabatic_:
        for face_pair in adj_info['adjacent_faces']:
            face_pair[0].boundary_condition = boundary_conditions.adiabatic
            face_pair[1].boundary_condition = boundary_conditions.adiabatic
    
    # report all of the adjacency information
    for adj_face in adj_info['adjacent_faces']:
        print('"{}" is adjacent to "{}"'.format(adj_face[0], adj_face[1]))