# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Honeybee Rooms from solids (closed Rhino polysurfaces).
-

    Args:
        _geo: A list of closed Rhino polysurfaces to be converted into Rooms.
        _name_: A list of names for the Rooms. If a single name is input here,
            it will be used as the base name for all of the connected polysurfaces.
        _program_: Text for the program of the Rooms (to be looked up in the
            ProgramType library) such as that output from the "HB List Programs"
            component. This can also be a custom ProgramType object. If no program
            is input here, the Rooms will have a generic office program.
        _constr_set_: Text for the construction set of the Rooms, which is used
            to assign all default energy constructions needed to create an energy
            model. Text should refer to a ConstructionSet within the library) such
            as that output from the "HB List Construction Sets" component. This
            can also be a custom ConstructionSet object. If nothing is input here,
            the Rooms will have a generic construction set that is not sensitive to
            the Rooms's climate or building energy code.
        conditioned_: Boolean to note whether the Rooms have heating and cooling
            systems.
        _roof_angle_: Cutting angle for roof from Z axis in degrees. Default: 30.
        _run: Set to True to run the component and create Honeybee Rooms.
    
    Returns:
        report: Reports, errors, warnings, etc.
        rooms: Honeybee rooms. These can be used directly in energy and radiance
            simulations.
"""

ghenv.Component.Name = "HB Room from Solid"
ghenv.Component.NickName = 'RoomSolid'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

# document-wide counter to generate new unique Room names
import scriptcontext
try:
    counter = scriptcontext.sticky["room_count"]
except KeyError:  # first time that the component is running
    scriptcontext.sticky["room_count"] = 1

try:  # import the core honeybee dependencies
    from honeybee.room import Room
    from honeybee.facetype import get_type_from_normal
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.togeometry import to_polyface3d
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.programtypes import program_type_by_name, office_program
    from honeybee_energy.lib.constructionsets import construction_set_by_name
    from honeybee_energy.idealair import IdealAirSystem
except ImportError:
    pass  # honeybee-energy is not installed and ep_constr_ will not be avaialble


if all_required_inputs(ghenv.Component) and _run is True:
    rooms = []
    for i, geo in enumerate(_geo):
        
        # get the name for the Room
        if _name_ == []:  # make a default Room name
            name = "Room_{}".format(counter)
            scriptcontext.sticky["room_count"] += 1
        else:
            name = '{}_{}'.format(_name_[0], i + 1)
        
        # create the room
        roof_angle = _roof_angle_ if _roof_angle_ is not None else 30
        room = Room.from_polyface3d(name, to_polyface3d(geo), roof_angle)
        
        # check that the Room geometry is closed.
        if not room.check_solid(tolerance, angle_tolerance, False):
            give_warning(ghenv.Component, 'Input _geo is not a closed volume.\n'
                         'Room volume must be closed to access most honeybee features.\n'
                         'Preview the output Room to see the holes in your model.')
        
        # try to assign the program
        if _program_ is not None:
            try:
                if isinstance(_program_, str):
                    _program_ = program_type_by_name(_program_)
                room.properties.energy.program_type = _program_
            except (NameError, AttributeError):
                raise ValueError('honeybee-energy is not installed but '
                                 '_program_ has been specified.')
        else:
            try:
                room.properties.energy.program_type = office_program
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed
        
        # try to assign the construction set
        if _constr_set_ is not None:
            try:
                if isinstance(_constr_set_, str):
                    _constr_set_ = construction_set_by_name(_constr_set_)
                room.properties.energy.construction_set = _constr_set_
            except (NameError, AttributeError):
                raise ValueError('honeybee-energy is not installed but '
                                 '_constr_set_ has been specified.')
        
        # try to assign an ideal air system
        if conditioned_:
            try:
                room.properties.energy.hvac = IdealAirSystem()
            except (NameError, AttributeError):
                raise ValueError('honeybee-energy is not installed but '
                                 'conditioned_ has been set to True.')
        if conditioned_ is None:  # set it to be conditioned by default
            try:
                room.properties.energy.hvac = IdealAirSystem()
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed
        
        rooms.append(room)