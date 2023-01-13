# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Honeybee Room from Honeybee Faces.
_
Note that each Room is mapped to a single zone in EnergyPlus/OpenStudio and
should always be a closed volume to ensure correct volumetric calculations and
avoid light leaks in Radiance simulations.
-

    Args:
        _faces: A list of honeybee Faces to be joined together into a Room.
        _name_: Text to set the name for the Room and to be incorporated into
            unique Room identifier. If the name is not provided, a random name
            will be assigned.
        _mod_set_: Text for the modifier set of the Room, which is used
            to assign all default radiance modifiers needed to create a radiance
            model. Text should refer to a ModifierSet within the library) such
            as that output from the "HB List Modifier Sets" component. This
            can also be a custom ModifierSet object. If nothing is input here,
            the Room will have a generic construction set that is not sensitive to
            the Room's climate or building energy code.
        _constr_set_: Text for the construction set of the Room, which is used
            to assign all default energy constructions needed to create an energy
            model. Text should refer to a ConstructionSet within the library) such
            as that output from the "HB List Construction Sets" component. This
            can also be a custom ConstructionSet object. If nothing is input here,
            the Room will have a generic construction set that is not sensitive to
            the Room's climate or building energy code.
        _program_: Text for the program of the Room (to be looked up in the ProgramType
            library) such as that output from the "HB List Programs" component.
            This can also be a custom ProgramType object. If no program is input
            here, the Room will have a generic office program. Note that ProgramTypes
            effectively map to OpenStudio space types upon export to OpenStudio.
        conditioned_: Boolean to note whether the Room has a heating and cooling
            system.

    Returns:
        report: Reports, errors, warnings, etc.
        room: Honeybee room. These can be used directly in energy and radiance
            simulations.
"""

ghenv.Component.Name = "HB Room"
ghenv.Component.NickName = 'Room'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:  # import the core honeybee dependencies
    from honeybee.room import Room
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        building_program_type_by_identifier, office_program
    from honeybee_energy.lib.constructionsets import construction_set_by_identifier
except ImportError as e:
    if _program_ is not None:
        raise ValueError('_program_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif _constr_set_ is not None:
        raise ValueError('_constr_set_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif conditioned_ is not None:
        raise ValueError('conditioned_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier
except ImportError as e:
    if _mod_set_ is not None:
        raise ValueError('_mod_set_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the input objects to avoid editing them
    faces = (face.duplicate() for face in _faces)

    # generate a default name
    if _name_ is None:  # create a default Room name
        display_name = 'Room_{}'.format(document_counter('room_count'))
    else:
        display_name = _name_
    name = clean_and_id_string(display_name)

    # create the Room
    room = Room(name, faces, tolerance, angle_tolerance)
    room.display_name = display_name

    # check that the Room geometry is closed.
    if room.check_solid(tolerance, angle_tolerance, False) != '':
        give_warning(ghenv.Component, 'Input _faces do not form a closed volume.\n'
                     'Room volume must be closed to access most honeybee features.\n'
                     'Preview the output Room to see the holes in your model.')

    # try to assign the modifier set
    if _mod_set_ is not None:
        if isinstance(_mod_set_, str):
            _mod_set_ = modifier_set_by_identifier(_mod_set_)
        room.properties.radiance.modifier_set = _mod_set_

    # try to assign the construction set
    if _constr_set_ is not None:
        if isinstance(_constr_set_, str):
            _constr_set_ = construction_set_by_identifier(_constr_set_)
        room.properties.energy.construction_set = _constr_set_

    # try to assign the program
    if _program_ is not None:
        if isinstance(_program_, str):
            try:
                _program_ = building_program_type_by_identifier(_program_)
            except ValueError:
                _program_ = program_type_by_identifier(_program_)
        room.properties.energy.program_type = _program_
    else:  # generic office program by default
        try:
            room.properties.energy.program_type = office_program
        except (NameError, AttributeError):
            pass  # honeybee-energy is not installed

    # try to assign an ideal air system
    if conditioned_ or conditioned_ is None:  # conditioned by default
        try:
            room.properties.energy.add_default_ideal_air()
        except (NameError, AttributeError):
            pass  # honeybee-energy is not installed