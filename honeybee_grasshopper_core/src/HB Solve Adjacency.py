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
        ep_constr_: Optional text for an energy construction to be used for all
            adjacent Faces found in the process of solving adjacency. This text
            will be used to look up a construction in the opaque construction library.
            This can also be a custom OpaqueConstruction object. If no energy
            construction is input here, the default will be assigned using the
            Rooms' ConstructionSet.
        ep_glz_constr_: Optional text for an energy construction to be used for all
            adjacent Apertures found in the process of solving adjacency. This text
            will be used to look up a construction in the window construction library.
            This can also be a custom WindowConstruction object. If no energy
            construction is input here, the default will be assigned using the
            Rooms' ConstructionSet.
        rad_mat_: Optional text for a radiance material to be used for all
            adjacent Faces found in the process of solving adjacency. This text
            will be used to look up a material in the material library. This can
            also be a custom material object. If no radiance material is input here,
            the default will be assigned using the Rooms' ModifierSet.
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
    from honeybee.room import Room
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.constructions import opaque_construction_by_name, \
        window_construction_by_name
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.construction.window import WindowConstruction
except ImportError as e:
    if ep_constr_ is not None:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif ep_glz_constr_ is not None:
        raise ValueError('ep_glz_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif adiabatic_ is not None:
        raise ValueError('adiabatic_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    import honeybee_radiance
except ImportError as e:
    if rad_mat_ is not None:
        raise ValueError('rad_mat_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    adj_rooms = [room.duplicate() for room in _rooms] # duplicate the initial objects
    
    # solve adjacnecy
    adj_info = Room.solve_adjacency(adj_rooms, tolerance)
    
    # try to assign the energyplus construction
    if ep_constr_ is not None:
        if isinstance(ep_constr_, str):  # get construction from library
            ep_constr_ = opaque_construction_by_name(ep_constr_)
        # check to be sure the reversed order of materials matches
        rev_constr = ep_constr_
        if not ep_constr_.is_symmetric:
            rev_constr = OpaqueConstruction(
                '{}_Rev'.format(ep_constr_.name),
                 [mat for mat in reversed(ep_constr_.materials)])
        # assign the construction to the faces
        for face_pair in adj_info['adjacent_faces']:
            face_pair[0].properties.energy.construction = ep_constr_
            face_pair[1].properties.energy.construction = rev_constr
    
    # try to assign the glazing energyplus construction
    if ep_glz_constr_ is not None:
        if isinstance(ep_glz_constr_, str):  # get construction from library
            ep_glz_constr_ = window_construction_by_name(ep_glz_constr_)
        # check to be sure the reversed order of materials matches
        rev_constr = ep_glz_constr_
        if not ep_glz_constr_.is_symmetric:
            rev_constr = WindowConstruction(
                '{}_Rev'.format(ep_glz_constr_.name),
                [mat for mat in reversed(ep_glz_constr_.materials)])
        # assign the construction to the faces
        for ap_pair in adj_info['adjacent_apertures']:
            ap_pair[0].properties.energy.construction = ep_glz_constr_
            ap_pair[1].properties.energy.construction = rev_constr
    
    # try to assign the adiabatic boundary condition
    if adiabatic_:
        for face_pair in adj_info['adjacent_faces']:
            face_pair[0].boundary_condition = boundary_conditions.adiabatic
            face_pair[1].boundary_condition = boundary_conditions.adiabatic
    
    # report all of the adjacency information
    for adj_face in adj_info['adjacent_faces']:
        print('"{}" is adjacent to "{}"'.format(adj_face[0], adj_face[1]))