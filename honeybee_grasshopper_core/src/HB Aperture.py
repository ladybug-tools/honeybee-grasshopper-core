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
        _name_: A name for the Aperture. If the name is not provided a random
            name will be assigned
        operable_: Boolean to note whether the Aperture can be opened for ventilation.
            Default: False.
        ep_constr_: Optional text for the Aperture's energy construction to be looked
            up in the construction library. This can also be a custom WindowConstruction
            object. If no energy construction is input here, a default will be
            assigned based on the properties of the parent face that the Aperture
            is assigned to (ie. whether the Face is a RoofCeiling, whether it has
            a Surface boundary condition, etc.)
        rad_mat_: Optional text for the Aperture's radiance material to be looked
            up in the material library. This can also be a custom material object.
            If no radiance material is input here, a default will be assigned
            based on the properties of the parent face that the Aperture is
            assigned to (ie. whether the Face is a RoofCeiling, whether it has a
            Surface boundary condition, etc.)
    
    Returns:
        report: Reports, errors, warnings, etc.
        apertures: Honeybee apertures. These can be used directly in radiance
            simulations or can be added to a Honeybee face for energy simulation.
"""

ghenv.Component.Name = "HB Aperture"
ghenv.Component.NickName = 'Aperture'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

import uuid

try:
    from honeybee.aperture import Aperture
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.constructions import window_construction_by_name
except ImportError:
    pass  # honeybee-energy is not installed and ep_constr_ will not be avaialble


if all_required_inputs(ghenv.Component):
    apertures = []  # list of apertures that will be returned
    
    # set default name
    name = _name_ if _name_ is not None else str(uuid.uuid4())
    
    # create the individual Apertures
    for i, lb_face in enumerate(to_face3d(_geo)):
        hb_ap = Aperture('{}{}'.format(name, i), lb_face, is_operable=operable_)
        
        # try to assign the energyplus construction
        if ep_constr_ is not None:
            try:
                if isinstance(ep_constr_, str):
                    ep_constr_ = window_construction_by_name(ep_constr_)
                hb_ap.properties.energy.construction = ep_constr_
            except (NameError, AttributeError):
                raise ValueError('honeybee-energy is not installed but '
                                 'ep_constr_ has been specified.')
        
        # collect the final Apertures
        apertures.append(hb_ap)