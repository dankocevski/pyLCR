import os
import urllib
import json
import numpy
import io
import sys

from .Sources import sources


class LightCurve():
    """
    An dictionary object used to store the light curve data as numpy array that are accessible through key value pairs

    """ 

    def __init__(self): 
        self.met = numpy.array([])
        self.met_detections = numpy.array([])
        self.met_upperlimits = numpy.array([]) 
        self.ts = numpy.array([])
        self.flux = numpy.array([])
        self.flux_upper_limits = numpy.array([])
        self.flux_error = numpy.array([])  
        self.photon_index = numpy.array([])
        self.photon_index_interval = numpy.array([])
        self.fit_tolerance = numpy.array([])
        self.fit_convergence = numpy.array([]) 
        self.dlogl = numpy.array([])
        self.EG = numpy.array([])
        self.GAL = numpy.array([]) 
        self.bin_id = numpy.array([]) 

        self.source = None
        self.flux_type =  None
        self.index_type = None
        self.cadence = None
        self.ts_min = None

    def get_info(self):
        """
        Display light curve information 

        """ 

        print('Source name: %s' % self.source)
        print('Cadence: %s' % self.cadence)
        print('Flux type: %s' % self.flux_type)
        print('Photon index fit type: %s' % self.index_type)
        print('Minimum detection TS: %s' % self.ts_min)
        print('')
        print('Number of bins: %s' % len(self.met))
        print('Number of detections: %s (%.2f%%)' % (len(self.flux), (100*len(self.flux)/len(self.met))))
        print('Number of upper limits: %s (%.2f%%)' % (len(self.flux_upper_limits), (100*len(self.flux_upper_limits)/len(self.met))))
        print('Number of non-convergant fits: %s (%.2f%%)' % (len(numpy.where(self.fit_convergence != 0)[0]), (100*len(numpy.where(self.fit_convergence != 0)[0])/len(self.met))))


def getLightCurve(source, cadence='daily', flux_type='photon', index_type='fixed', ts_min=4, verbose=False):
    """Download data from the light curve repository

    Arguments:
        source (str):           A 4FGL catalog name, e.g. '4FGL J0001.2-0747'
        cadence (str):          Specifies the requested light curve cadence. Options include: 'daily', 'weekly', and 'monthly'
        flux_type (str):        Specifies the requested flux type. Options include 'photon' and 'energy'
        index_type (str):       Specifies the spectral index freedom during fit. Options include 'free' and 'fixed'
        ts_min (int):           The minimum likelihood ratio test statistic for which a flux estimate is reported as opposed to an upper limit.

    Returns:
        A key-value pair dictionary containing numpy arrays of light curve data

    """

    if source not in sources:
        print("\nError: %s is not a source that is tracked by the LCR." % source)
        return

    if 'daily' not in cadence and 'weekly' not in cadence and 'monthly' not in cadence:
        print("\nError: Unrecognized cadence.")
        print("\nThe cadence keyword specifies the requested light curve cadence. Options include: 'daily', 'weekly', and 'monthly'")
        return 

    if 'photon' not in flux_type and 'energy' not in flux_type:
        print("\nError: Unrecognized flux type.")
        print("\nThe flux_type keyword specifies the requested flux type. Options include 'photon' and 'energy'")
        return

    if 'fixed' not in index_type and 'free' not in flux_type:
        print("\nError: Unrecognized spectral index type.")
        print("\nThe index_type keyword specifies the spectral index freedom during fit. Options include 'free' and 'fixed'")
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

            if verbose == True:
                print("")
                print(url)

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


    # Store all the data in a light curve object
    lightCurve = LightCurve()

    # Extract the MET values
    met_all = numpy.array(data['ts'])[:,0]
    met_detections = numpy.array(data['flux'])[:,0]
    met_upperlimits = numpy.array(data['flux_upper_limits'])[:,0]

    # Create detection and nondetection indices (not currently used)
    detections = numpy.where(numpy.in1d(met_all, met_detections))[0]
    upperlimits = numpy.where(numpy.in1d(met_all, met_upperlimits))[0]

    # Add the data to the lightCurve object
    # lightCurve['ts'] = numpy.array(data['ts'])[:,0], numpy.array(data['ts'])[:,1]
    # lightCurve['flux'] = numpy.array(data['flux'])[:,0], numpy.array(data['flux'])[:,1]
    # lightCurve['flux_upper_limits'] = numpy.array(data['flux_upper_limits'])[:,0], numpy.array(data['flux_upper_limits'])[:,1]
    # lightCurve['flux_error'] = numpy.array(data['flux_error'])[:,0], numpy.array(data['flux_error'])[:,1]
    # lightCurve['photon_index'] = numpy.array(data['photon_index'])[:,0], numpy.array(data['photon_index'])[:,1]
    # lightCurve['photon_index_interval'] = numpy.array(data['photon_index_interval'])[:,0], numpy.array(data['photon_index_interval'])[:,1]
    # lightCurve['fit_tolerance'] = numpy.array(data['fit_tolerance'])[:,0], numpy.array(data['fit_tolerance'])[:,1]
    # lightCurve['fit_convergence'] = numpy.array(data['fit_convergence'])[:,0], numpy.array(data['fit_convergence'])[:,1]
    # lightCurve['dlogl'] = numpy.array(data['ts'])[:,0], numpy.array(data['dlogl'])
    # lightCurve['EG'] = numpy.array(data['ts'])[:,0], numpy.array(data['EG'])
    # lightCurve['GAL'] = numpy.array(data['ts'])[:,0], numpy.array(data['GAL'])
    # lightCurve['bin_id'] = numpy.array(data['ts'])[:,0], numpy.array(data['bin_id'])

    # lightCurve['met'] = numpy.array(data['ts'])[:,0]
    # lightCurve['met_detections'] = numpy.array(data['flux'])[:,0]
    # lightCurve['met_upperlimits'] = numpy.array(data['flux_upper_limits'])[:,0]
    # lightCurve['ts'] = numpy.array(data['ts'])[:,1]
    # lightCurve['flux'] = numpy.array(data['flux'])[:,1]
    # lightCurve['flux_upper_limits'] = numpy.array(data['flux_upper_limits'])[:,1]
    # lightCurve['flux_error'] = numpy.array(data['flux_error'])[:,1]
    # lightCurve['photon_index'] = numpy.array(data['photon_index'])[:,1]
    # lightCurve['photon_index_interval'] = numpy.array(data['photon_index_interval'])[:,1]
    # lightCurve['fit_tolerance'] = numpy.array(data['fit_tolerance'])[:,1]
    # lightCurve['fit_convergence'] = numpy.array(data['fit_convergence'])[:,1]
    # lightCurve['dlogl'] = numpy.array(data['dlogl'])
    # lightCurve['EG'] = numpy.array(data['EG'])
    # lightCurve['GAL'] = numpy.array(data['GAL'])
    # lightCurve['bin_id'] = numpy.array(data['bin_id'])

    lightCurve.met = numpy.array(data['ts'])[:,0]
    lightCurve.met_detections = numpy.array(data['flux'])[:,0]
    lightCurve.met_upperlimits = numpy.array(data['flux_upper_limits'])[:,0]
    lightCurve.ts = numpy.array(data['ts'])[:,1]
    lightCurve.flux = numpy.array(data['flux'])[:,1]
    lightCurve.flux_upper_limits = numpy.array(data['flux_upper_limits'])[:,1]
    lightCurve.flux_error = numpy.array(data['flux_error'])[:,1:]
    lightCurve.photon_index = numpy.array(data['photon_index'])[:,1]
    lightCurve.photon_index_interval = numpy.array(data['photon_index_interval'])[:,1]
    lightCurve.fit_tolerance = numpy.array(data['fit_tolerance'])[:,1]
    lightCurve.fit_convergence = numpy.array(data['fit_convergence'])[:,1]
    lightCurve.dlogl = numpy.array(data['dlogl'])
    lightCurve.EG = numpy.array(data['EG'])
    lightCurve.GAL = numpy.array(data['GAL'])
    lightCurve.bin_id = numpy.array(data['bin_id'])

    lightCurve.source = source
    lightCurve.cadence = cadence
    lightCurve.flux_type = flux_type
    lightCurve.index_type = index_type
    lightCurve.ts_min = ts_min


    return lightCurve

