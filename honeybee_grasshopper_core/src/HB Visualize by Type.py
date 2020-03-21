# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Visualize room geometry in the Rhino scene organized by object and face type.
-

    Args:
        rooms: Honeybee Rooms for which you would like to preview geometry
            in the Rhino scene based on type.
    
    Returns:
        walls: Rhino geometry for the Walls with an Outdoors or Ground boundary
            condition.
        interior_walls: Rhino geometry for the Walls with a Surface or Adiabatic
            boundary condition.
        roofs: Rhino geometry for the RoofCeilings with an Outdoors or Ground
            boundary condition.
        ceilings: Rhino geometry for the RoofCeilings with a Surface or Adiabatic
            boundary condition.
        exterior_floors: Rhino geometry for the Floors with an Outdoors or Ground
            boundary condition.
        interior_floors: Rhino geometry for the Floors with a Surface or Adiabatic
            boundary condition.
        air_walls: Rhino geometry for the AirWalls.
        apertures: Rhino geometry for the Apertures with an Outdoors or Ground
            boundary condition.
        interior_apertures: Rhino geometry for the Apertures with an Surface or
            Adiabatic boundary condition.
        doors: Rhino geometry for the Doors with an Outdoors or Ground boundary
            condition.
        interior_doors: Rhino geometry for the Doors with an Surface or Adiabatic
            boundary condition.
        outdoor_shades: Rhino geometry for the Shades assigned to the outdoors
            of their parent objects.
        indoor_shades: Rhino geometry for the Shades assigned to the indoors
            of their parent objects.
"""

ghenv.Component.Name = "HB Visualize by Type"
ghenv.Component.NickName = 'VizByType'
ghenv.Component.Message = '0.2.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Surface
    from honeybee.facetype import Wall, RoofCeiling, Floor, AirBoundary
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee.boundarycondition import Adiabatic
except ImportError:  # honeybee-energy not installed
    Adiabatic = None  # don't worry about Aidabatic; Surface is the only interior bc


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    walls = []
    interior_walls = []
    roofs = []
    ceilings = []
    exterior_floors = []
    interior_floors = []
    air_walls = []
    apertures = []
    interior_apertures = []
    doors = []
    interior_doors = []
    outdoor_shades = []
    indoor_shades = []
    
    # method to add shades
    def add_shade(hb_obj):
        outdoor_shades.extend([from_face3d(shd.geometry)
                               for shd in hb_obj.outdoor_shades])
        indoor_shades.extend([from_face3d(shd.geometry)
                               for shd in hb_obj.indoor_shades])
    
    # loop through all objects and add them
    for room in _rooms:
        add_shade(room)
        for face in room:
            add_shade(face)
            bc = face.boundary_condition
            type = face.type
            if isinstance(type, Wall):
                if isinstance(bc, (Surface, Adiabatic)):
                    interior_walls.append(from_face3d(face.punched_geometry))
                else:
                    walls.append(from_face3d(face.punched_geometry))
            elif isinstance(type, RoofCeiling):
                if isinstance(bc, (Surface, Adiabatic)):
                    ceilings.append(from_face3d(face.punched_geometry))
                else:
                    roofs.append(from_face3d(face.punched_geometry))
            elif isinstance(type, Floor):
                if isinstance(bc, (Surface, Adiabatic)):
                    interior_floors.append(from_face3d(face.punched_geometry))
                else:
                    exterior_floors.append(from_face3d(face.punched_geometry))
            elif isinstance(type, AirBoundary):
                air_walls.append(from_face3d(face.punched_geometry))
            
            # add the apertures, doors, and shades
            for ap in face.apertures:
                add_shade(ap)
                if isinstance(bc, Surface):
                    interior_apertures.append(from_face3d(ap.geometry))
                else:
                    apertures.append(from_face3d(ap.geometry))
            for dr in face.doors:
                add_shade(dr)
                if isinstance(bc, Surface):
                    interior_doors.append(from_face3d(dr.geometry))
                else:
                    doors.append(from_face3d(dr.geometry))