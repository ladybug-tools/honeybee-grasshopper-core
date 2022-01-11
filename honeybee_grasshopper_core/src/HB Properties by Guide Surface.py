# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set the properties of room Faces using (a) guide surface(s) or polysurface(s).
_
Faces that are touching and coplanar with the guide surface will get their
properties changed to match the inputs.
_
This is useful for colelctively setting the properties of spatially aligned Faces,
like setting Faces along a given stretch of a parti wall to be adiabatic.
-

    Args:
        _rooms: Honeybee Rooms which will have their Face boundary conditions set
            based on the guide surface(s).
        _guide: Rhino Breps or Meshes that represent the guide surfaces.
        type_: Text for the face type. The face type will be used to set the
            material and construction for the surface if they are not assigned
            through the inputs below.
            Choose from the following:
                - Wall
                - RoofCeiling
                - Floor
                - AirBoundary
        bc_: Text for the boundary condition of the face. The boundary condition
            is also used to assign default materials and constructions as well as
            the nature of heat excahnge across the face in energy simulation.
            Choose from the following:
                - Outdoors
                - Ground
                - Adiabatic
        ep_constr_: Optional text for the Face's energy construction to be looked
            up in the construction library. This can also be a custom
            OpaqueConstruction object.
        rad_mod_: Optional text for the Face's radiance modifier to be looked
            up in the modifier library. This can also be a custom modifier
            object.

    Returns:
        rooms: The input Rooms with their Face properties changed.
"""

ghenv.Component.Name = 'HB Properties by Guide Surface'
ghenv.Component.NickName = 'GuideSurface'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.facetype import face_types
    from honeybee.boundarycondition import boundary_conditions
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
except ImportError as e:
    if ep_constr_ is None:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    if rad_mod_ is None:
        raise ValueError('rad_mod_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    # process the inputs
    rooms = [room.duplicate() for room in _rooms]  # duplicate to avoid editing input
    guide_faces = [g for geo in _guide for g in to_face3d(geo)]  # convert to lb geometry
    if type_ is not None and type_ not in face_types:
        type_ = face_types.by_name(type_)
    if bc_ is not None and bc_ not in boundary_conditions:
        bc_ = boundary_conditions.by_name(bc_)
    if isinstance(ep_constr_, str):
        ep_constr_ = opaque_construction_by_identifier(ep_constr_)
    if isinstance(rad_mod_, str):
        rad_mod_ = modifier_by_identifier(rad_mod_)

    # loop through the rooms and set the face properties
    for room in rooms:
        select_faces = room.faces_by_guide_surface(
            guide_faces, tolerance=tolerance, angle_tolerance=angle_tolerance)
        for hb_face in select_faces:
            if type_ is not None:
                hb_face.type = type_
            if bc_ is not None:
                hb_face.boundary_condition = bc_
            if ep_constr_ is not None:
                hb_face.properties.energy.construction = ep_constr_
            if rad_mod_ is not None:
                hb_face.properties.radiance.modifier = rad_mod_
