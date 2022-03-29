import os
import urllib
import json
import numpy
import io
import sys

from pyLCR.catalog import sources

name = 'pyLCR'
version='0.1.0'

print("\nFermi Light Curve Repository Toolkit v%s" % version)
print("Support Contact: Daniel Kocevski (daniel.kocevski@nasa.gov)\n")


def getLightCurveData(source, cadence='daily', flux_type='photon', index_type='fixed', ts_min=4, return_dictionary=False):
    """Download data from the light curve repository

    Arguments:
        source (str):           A 4FGL catalog name, e.g. '4FGL J0001.2-0747'
        cadence (str):          Specifies the requested light curve cadence. Options include: 'daily', 'weekly', and 'monthly'
        flux_type (str):        Specifies the requested flux type. Options include 'photon' and 'energy'
        index_type (str):       Specifies the spectral index freedom during fit. Options include 'free' and 'fixed'

    Returns:
        A key-value pair dictionary containing the resulting data

    """

    if source not in sources.source_names:
        print("\nError: %s is not a source that is tracked by the LCR." % source)
        return

    if 'daily' not in cadence and 'weekly' not in cadence and 'monthly' not in cadence:
        print("\nError: Invalid cadence.")
        print("\nAvailable cadences include:")
        print("daily\nweekly\nmonthly")
        return 

    if 'photon' not in flux_type and 'energy' not in flux_type:
        print("\nError: Invalid flux type.")
        print("\nAvailable flux types include:")
        print("photon -> Photon Flux in units of photons cm-2 s-1\nenergy -> Energy Flux in units of MeV cm-2 s-1")
        return

    if 'fixed' not in index_type and 'free' not in flux_type:
        print("\nError: Invalid spectral index type.")
        print("\nAvailable spectral index types include:")
        print("fixed\nfree")
        return

    # Create a quoted source
    source_quoted = urllib.parse.quote(source)

    # Create the url template
    url_template = ("https://fermi.gsfc.nasa.gov/ssc/data/access/lat/LightCurveRepository/queryDB.php?typeOfRequest=lightCurveData"
    "&source_name={source_name}&cadence={cadence}&flux_type={flux_type}&index_type={index_type}&ts_min={ts_min}")

    # Fill the url template
    url = url_template.format(**{"source_name": source_quoted,
       "cadence": cadence,
       "flux_type": flux_type,
       "index_type": index_type,
       "ts_min": ts_min})

    # Create a json filename
    filename = '_'.join([source_quoted, cadence, flux_type, index_type, "tsmin" + str(ts_min)])
    filename += ".json"

    print("\nDownloading data for %s..." % source)

    try:

        # Open the url
        with urllib.request.urlopen(url) as response:

            # Parse the downloaded data
            data = json.loads(response.read().decode())

            # Check the http status code to see if the data was downloaded successfully
            code = int(response.code)
            if code >= 200 and code <= 299 and len(data['ts']) > 0:
                print('Done.')

    # Parse the status codes of any failures
    except urllib.error.HTTPError  as e:
        print("HTTP Error.")
        print("Return Code", e.code)

    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print("Return Code", e.reason)

        elif hasattr(e, 'code'):
            print("Return Code", e.code)

    # if return_dictionary == True:

    data['ts'] = numpy.array(data['ts'])
    data['flux'] = numpy.array(data['flux'])
    data['flux_upper_limits'] = numpy.array(data['flux_upper_limits'])
    data['flux_error'] = numpy.array(data['flux_error'])
    data['photon_index'] = numpy.array(data['photon_index'])
    data['photon_index_interval'] = numpy.array(data['photon_index_interval'])
    data['fit_tolerance'] = numpy.array(data['fit_tolerance'])
    data['fit_convergence'] = numpy.array(data['fit_convergence'])
    data['dlogl'] = numpy.array(data['dlogl'])
    data['EG'] = numpy.array(data['EG'])
    data['GAL'] = numpy.array(data['GAL'])
    data['bin_id'] = numpy.array(data['bin_id'])

    return data

