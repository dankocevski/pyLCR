# pyLCR

A python interface to the Fermi-LAT Light Curve Repository

https://fermi.gsfc.nasa.gov/ssc/data/access/lat/LightCurveRepository/index.html

## Installation

### Requirements

- Python >= 3.5
- numpy >= 1.17.3

### How to Install

Installing the package using pip

`pip install <path to pyLCR>/pyLCR`

### How to Uninstall

Uninstalling the package using pip

`pip uninstall pyLCR`

## Usage

Downloading data for a specific source

`data = pyLCR.getLightCurveData('4FGL J0001.2-0747', cadence='daily', flux_type='photon', index_type='fixed')`

Note that the cadence refers to the binning timescale, with the options including 'daily', 'weekly', or 'monthly'. The flux_type refers to the units in which the flux is returned, with the options including 'photon' flux in units of photons cm<sup>-2</sup> sm<sup>-1m</sup> or 'energy' flux in units of MeV cmm<sup>-2m</sup> sm<sup>-1m</sup>. The index_type refers to whether the spectral index of the source was 'fixed' or 'free' during the spectral fit.
