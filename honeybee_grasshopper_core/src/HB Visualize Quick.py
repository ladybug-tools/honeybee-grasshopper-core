# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Quickly preview any Honeybee geometry object within the Rhino scene.
_
Sub-faces and assigned shades will not be included in the output, allowing for
a faster preview of large lists of objects but without the ability to check the
assignment of child objects.
-

    Args:
        _hb_objs: A Honeybee Model, Room, Face, Shade, Aperture, or Door to be previewed
            in the Rhino scene.
    
    Returns:
        geo: The Rhino version of the Honeybee geometry object, which will be
            visible in the Rhino scene.
"""

ghenv.Component.Name = "HB Visualize Quick"
ghenv.Component.NickName = 'VizQuick'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the core honeybee dependencies
    from honeybee.face import Face
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3d, from_polyface3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    geo = []
    
    # loop through all objects and add them
    for hb_obj in _hb_objs:
        try:  # Face, Shade, Aperture, or Door
            if isinstance(hb_obj, Face):
                geo.append(from_face3d(hb_obj.punched_geometry))
            else:
                geo.append(from_face3d(hb_obj.geometry))
        except AttributeError:  # probably a Room
            try:
                geo.append(from_polyface3d(hb_obj.geometry))
            except AttributeError:  # it's a whole Model
                for room in hb_obj.rooms:
                    geo.append(from_polyface3d(room.geometry))
                for face in hb_obj.orphaned_faces:
                    geo.append(from_face3d(face.punched_geometry))
                for ap in hb_obj.orphaned_apertures:
                    geo.append(from_face3d(ap.geometry))
                for dr in hb_obj.orphaned_doors:
                    geo.append(from_face3d(dr.geometry))
                for shd in hb_obj.orphaned_shades:
                    geo.append(from_face3d(shd.geometry))