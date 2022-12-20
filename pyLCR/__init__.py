#     Author: Daniel Kocevski (NASA) - April 1st, 2022
#
#     Written for the Fermi-LAT Light Curve Repository
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Version of pyLCR
__version__ = '0.1.0'

from .DataTools import getLightCurve
from .PlottingTools import plotLightCurve
from .PlottingTools import computeDate
from .PlottingTools import getCurrentMET
from .PlottingTools import computeMJD
from .Sources import sources

del DataTools
del PlottingTools
del Sources

print("\nThe Fermi-LAT Light Curve Repository Toolkit v%s" % __version__)
print("Support Contact: Daniel Kocevski (daniel.kocevski@nasa.gov)")
