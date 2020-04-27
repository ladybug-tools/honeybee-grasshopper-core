# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Honeybee Face
-

    Args:
        _geo: Rhino Brep geometry.
        _name_: Text to set the name for the Face and to be incorporated into
            unique Face identifier. If the name is not provided, a random name
            will be assigned.
        _type_: Text for the face type. The face type will be used to set the
            material and construction for the surface if they are not assigned
            through the inputs below. The default is automatically set based
            on the normal direction of the Face (up being RoofCeiling, down
            being Floor and vertically-oriented being Wall).
            Choose from the following:
                - Wall
                - RoofCeiling
                - Floor
                - AirBoundary
        _bc_: Text for the boundary condition of the face. The boundary condition
            is also used to assign default materials and constructions as well as
            the nature of heat excahnge across the face in energy simulation.
            Default is Outdoors unless all vertices of the geometry lie below
            the below the XY plane, in which case it will be set to Ground.
            Choose from the following:
                - Outdoors
                - Ground
                - Adiabatic
        ep_constr_: Optional text for the Face's energy construction to be looked
            up in the construction library. This can also be a custom OpaqueConstruction
            object. If no energy construction is input here, the face type and
            boundary condition will be used to assign a default.
        rad_mod_: Optional text for the Face's radiance modifier to be looked
            up in the modifier library. This can also be a custom modifier object.
            If no radiance modifier is input here, the face type and boundary
            condition will be used to assign a default.
    
    Returns:
        report: Reports, errors, warnings, etc.
        face: Honeybee faces. These can be used directly in radiance simulations
            or can be added to a Honeybee room for energy simulation.
"""

ghenv.Component.Name = "HB Face"
ghenv.Component.NickName = 'Face'
ghenv.Component.Message = '0.2.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import uuid

try:  # import the core honeybee dependencies
    from honeybee.face import Face
    from honeybee.facetype import face_types
    from honeybee.boundarycondition import boundary_conditions
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
except ImportError as e:
    if ep_constr_ is not None:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    if rad_mod_ is not None:
        raise ValueError('rad_mod_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    faces = []  # list of faces that will be returned

    # set default name, type, and boundary condition
    name = clean_and_id_string(_name_) if _name_ is not None else str(uuid.uuid4())
    if _type_ is not None and _type_ not in face_types:
        _type_ = face_types.by_name(_type_)
    if _bc_ is not None and _bc_ not in boundary_conditions:
        _bc_ = boundary_conditions.by_name(_bc_)

    # create the Faces
    i = 0  # iterator to ensure each face gets a unique name
    for geo in _geo:
        for lb_face in to_face3d(geo):
            hb_face = Face('{}_{}'.format(name, i), lb_face, _type_, _bc_)
            if _name_ is not None:
                hb_face.display_name = '{}_{}'.format(_name_, i)

            # try to assign the energyplus construction
            if ep_constr_ is not None:
                if isinstance(ep_constr_, str):
                    ep_constr_ = opaque_construction_by_identifier(ep_constr_)
                hb_face.properties.energy.construction = ep_constr_

            # try to assign the radiance modifier
            if rad_mod_ is not None:
                if isinstance(rad_mod_, str):
                    rad_mod_ = modifier_by_identifier(rad_mod_)
                hb_face.properties.radiance.modifier = rad_mod_

            faces.append(hb_face)  # collect the final Faces
            i += 1  # advance the iterator