# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Offset the edges of all Apertures of a Honeybee Room or Face by a certain distance.
_
This is useful for translating between interfaces that expect the window
frame to be included within or excluded from the geometry of the Aperture.
For example, EnergyPlus expects Aperture geometry to be for only the glass
portion of the window while IES-VE expects the Aperture geometry to include
the frame.
_
Note that this component also has usefulness to simply repair cases where
Apertures extend pas their parent Face or overlap with one another. In this
situation, the offset input can be set to zero and the repair_ boolean set to
True to only run the repair operation.
-

    Args:
        _hb_objs: A list of honeybee Rooms or Faces for which Apertures will have their
            edges offset. This can also be an entire honeybee Model for which
            all Rooms will have Apertures offset.
        _offset: A number for the distance with which the edges of each Aperture will
            be offset from the original geometry. Positive values will
            offset the geometry outwards and negative values will offset the
            geometries inwards.
        repair_: A bool to note whether invalid Apertures and Doors should be fixed
            after performing the initial offset operation. This repair process
            involves two steps. First, sub-faces that extend past their parent
            Face are trimmed with the parent and will have their edges offset
            towards the inside of the Face. Second, any sub-faces that overlap
            or touch one another will be unioned into a single Aperture or
            Door. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Honeybee Face, Room or Model with Apertures offset.
"""

ghenv.Component.Name = 'HB Offset Aperture Edges'
ghenv.Component.NickName = 'OffsetApertures'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.face import Face
    from honeybee.room import Room
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def offset_face(face):
    """Offset and repair the Apertures of a Face."""
    if _offset != 0:
        orig_area = [ap.area for ap in face.apertures]
        face.offset_aperture_edges(_offset, tolerance)
        for ap, o_area in zip(face.apertures, orig_area):
            if ap.is_operable:
                try:
                    op_area = ap.properties.energy.vent_opening.fraction_area_operable
                    new_op_area = (o_area / ap.area) * op_area
                    new_op_area = 1 if new_op_area > 1 else new_op_area
                    ap.properties.energy.vent_opening.fraction_area_operable = new_op_area
                except AttributeError:
                    pass  # no operable area assigned
    if repair_:
        face.fix_invalid_sub_faces(
            True, True, offset_distance=tolerance * 5, tolerance=tolerance)
    


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # loop through the input objects and add apertures
    for obj in hb_objs:
        if isinstance(obj, Model):
            for room in obj.rooms:
                for face in room.faces:
                    if face.has_sub_faces:
                        offset_face(face)
        elif isinstance(obj, Room):
            for face in obj.faces:
                if face.has_sub_faces:
                    offset_face(face)
        elif isinstance(obj, Face):
            if obj.has_sub_faces:
                offset_face(obj)
        else:
            raise TypeError(
                'Input _hb_objs must be a Model, Room or Face. Not {}.'.format(type(obj)))