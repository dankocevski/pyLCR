import sys
import numpy
import matplotlib.pylab as plot
import matplotlib.ticker as mtick
from matplotlib.ticker import AutoMinorLocator
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import time
import datetime
import os
import glob

##########################################################################################

def computeDate(MET):

    if MET>252460801: MET=MET-1 # 2008 leap second
    if MET>157766400: MET=MET-1 # 2005 leap second
    if MET>362793601: MET=MET-1 # 2012 leap second
    if MET>457401601: MET=MET-1 # 2015 leap second
    if MET>504921601: MET=MET-1 # 2016 leap second
    metdate  = datetime.datetime(2001, 1, 1,0,0,0)
    dt=datetime.timedelta(seconds=MET)
    date=metdate + dt
    yy=date.year
    mm=date.month
    dd=date.day
    hr=date.hour
    mi=date.minute
    ss=date.second
    fff=(float(ss+60.*mi+3600.*hr)/86.4)/1000.0

    return date, fff


##########################################################################################

def getCurrentMET():

    date = datetime.datetime.now()
    metdate = datetime.datetime(2001, 1, 1, 0, 0, 0)
    difference=date-metdate
    MET=(difference).days*86400.+(difference).seconds
    if date.year>2005: MET+=1 # 2005 leap second
    if date.year>2008: MET+=1 # 2008 leap second
    if (date.month >= 7 and date.year == 2012) or (date.year > 2012): MET+=1 # 2012 leap second
    if (date.month >= 7 and date.year == 2015) or (date.year > 2015): MET+=1 # 2015 leap second
    if date.year>2016: MET+=1 # 2016 leap second

    return MET

##########################################################################################

def computeMJD(MET, returnFraction=True):

    # Get the date and fraction of day for the given MET
    date, fraction = computeDate(MET)

    # Calculate the number of days since January 1, 4713 BC
    # JD = date.toordinal() + 1721424.5
    JD = date.toordinal() + 1721425

    # Calculate the number of days since November 17, 1858
    # MJD = JD - 2400000.5
    MJD = JD - 2400001

    if returnFraction == True:
        MJD = MJD + fraction

    return MJD

##########################################################################################

def plotLightCurve(lightCurve, logCenter=False, MET=None, useMJD=False, ylim=None, triggerMET=None, triggerMJD=None, ylog=False, xlog=False, ymin=None, \
    ymax=None, xmin=None, xmax=None, removeTicks=1, savefig=False, showPlot=True, plotTS=False, plotIndex=False, extension='.png'):
    """Plot data from the light curve repository

    Arguments:
        lightCurveData (Obj):       An instance of the LightCurve class            
        logCenter (BOOL):           Whether to use logarithmic bin centers. Default = False         
        MET (int):                  Reference MET. Default = None
        useMJD (BOOL):              Specifies whether the y-axis should be in units of MJD. Default = False
        ylim (list):                Specifies a limit on the y-axis
        triggerMET (int):           Specifies a trigger MET to highlight on the plot. Default = None
        triggerMJD (int):           Specifies a trigger MJD to highlight on the plot. Default = None
        ylog (BOOL):                Enables y-axis logarithmic scaling. Default = False
        xlog (BOOL):                Enables c-axis logarithmic scaling. Default = False
        ymin (float):               Specifies a lower limit on the y-axis. Default = None
        ymax (float):               Specifies a upper limit on the y-axis. Default = None
        xmin (float):               Specifies a lower limit on the x-axis. Default = None
        xmax (float):               Specifies an upper limit on the x-axis. Default = None
        removeTicks (int):          Specifies the number of ticks to remove from the y-axis on multi-axis plots, Default = 1
        savefig (BOOL):             Specifies whether the plot should be saved to disk. Default = False
        showPlot (BOOL):            Specifies whether the plot should be displayed to screen. Default = True
        plotTS (BOOL):              Specifies whether the TS should be displayed on a seperate plot pane. Default = False
        plotIndex (BOOL):           Specifies whether the photon inde should be displayed on a seperate plot pane. Default = False
        extension (str):            Specifies whether the format of the saved plot image. Default = 'png''

    Returns:
        None

    """
    
    # Extract the source name
    source = lightCurve.source

    # Extract likelihood ratio test statistic
    ts = lightCurve.ts

    # Extact the tmin and tmax of the analysis 
    met = lightCurve.met

    # Determine which timebins have detections 
    met_detections = lightCurve.met_detections
    met_upperlimits = lightCurve.met_upperlimits

    # Get the spectral information
    flux_type = lightCurve.flux_type
    index_type = lightCurve.index_type 
    photon_index = lightCurve.photon_index
    photon_index_error = photon_index - lightCurve.photon_index_interval

    # Extract the flux information
    flux = lightCurve.flux
    flux_upper_limit = lightCurve.flux_upper_limits

    # Extracting the flux error and placing it in the proper format
    flux_error = flux - lightCurve.flux_error[:,0]

    # Determine the bin size
    cadence = lightCurve.cadence

    # Quantify the cadence
    if 'daily' in cadence:
        duration = 259200
    elif 'weekly' in candence:
        duration = 604800
    elif 'monthly' in cadence:
        duration = 2592000

    # Get the bin widths
    tmin = met - duration
    tmax = met + duration

    # Create the plot label
    label = flux_type + ' Flux'

    # Get the duration
    dt = tmax-tmin


    # Convert the timebins to MJD
    if useMJD == True:

        # Convert dt and x errors into days
        dt = dt / 86400.0
        x_errors = (duration / 2.0) / 86400.0

        # Create lists to store the converted time bins
        MJDs = []
        MJDs_detections = []
        MJDs_upperlimits = []

        # Convert all of the time bins
        for timebin in met:
            MJDs.append(computeMJD(timebin))

        # Convert time bins for the detections
        for timebin in met_detections:
            MJDs_detections.append(computeMJD(timebin))

        # Convert time bins for the nondetections
        for timebin in met_upperlimits:
            MJDs_upperlimits.append(computeMJD(timebin))

        # Vectorize the arrays
        timebins = numpy.array(MJDs)
        timebins_detections = numpy.array(MJDs_detections)
        timebins_upperlimits = numpy.array(MJDs_upperlimits)

        # Convert the triggerMET if no triggerMJD was specified
        if triggerMET == True and triggerMJD == False:
            triggerMJD = computeMJD(triggerMET)

    else:

        # Calculate the x errors
        x_errors = duration/2.0

        # Get the time bin centers
        timebins = met
        timebins_detections = met_detections
        timebins_upperlimits = met_upperlimits

        # Convert everything to a relative time if an MET is specified
        if MET is not None:
            timebins = timebins - MET
            timebins_detections = timebins_detections - MET
            timebins_upperlimits = timebins_upperlimits - MET


    # Create two subplots sharing the x axes
    if plotTS == True and plotIndex == True:
        f, (ax, ax2, ax3) = plot.subplots(3, sharex=True, sharey=False, figsize=[18,12])
    elif plotTS == False and plotIndex == True:
        f, (ax, ax3) = plot.subplots(2, sharex=True, sharey=False, figsize=[18,9])
    elif plotTS == True and plotIndex == False:
        f, (ax, ax2) = plot.subplots(2, sharex=True, sharey=False, figsize=[18,9])
    elif plotTS == False and plotIndex == False:
        f, (ax) = plot.subplots(1, sharex=True, sharey=False, figsize=[18,6])

    # Adjust the two plots so that there is no space between them
    # if plotTS == True or plotIndex == True:
    #     f.subplots_adjust(hspace=0)

    # Plot the flux values
    ax.scatter(timebins_detections, flux, marker='o', s=25, edgecolors='black', color='#3e4d8b', linewidths=0.5)

    # Plot the upper limits
    ax.scatter(timebins_upperlimits, flux_upper_limit, marker='v', s=25, edgecolors='black', color='#3e4d8b', linewidths=0.5, alpha=0.6)

    # Don't let the error bars affect the plot scale
    ax.set_autoscale_on(False)

    # Plot the error bars
    ax.errorbar(timebins_detections, flux, xerr=x_errors, yerr=numpy.transpose(flux_error), fmt='none', markersize=5, color='#3e4d8b', ecolor='#3e4d8b', markeredgecolor='black', label=label, capsize=0, alpha=0.6)

    # Set the y-axis range
    if ylog == True:
        ymax=numpy.median(flux)*100
        ymin=numpy.median(flux)/100
        ax.set_ylim(ymin, ymax)

    elif ymin is None and ymax is None:
        ymax=numpy.median(flux)*10
        ymin=0
        ax.set_ylim(ymin, ymax)

    else:
        ax.set_ylim(ymin, ymax)


    # Calculate the x-axis range
    if xmin is None:
        xmin = min(tmin)
        if useMJD is True:
            xmin = computeMJD(xmin)

    if xmax is None:
        xmax = getCurrentMET()
        if useMJD is True:
            xmax = computeMJD(xmax)

    # Set the x-axis range
    ax.set_xlim(xmin, xmax)

    # Set the format of the y-axis to scientific notation
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))

    # Set the x-axis minor tick frequency
    # minorLocator = AutoMinorLocator()
    # ax.xaxis.set_minor_locator(minorLocator)

    # # Set the y-axis minor tick frequency
    # minorLocator = AutoMinorLocator()        
    # ax.yaxis.set_minor_locator(minorLocator)

    # Set a minimum y value
    if ylog == False:
        ax.set_ylim(bottom=0)

    else:
        if ylim is not None:
            ax.set_ylim(ylim)
        else:
            ax.set_ylim(bottom=numpy.median(flux/100))

    # Annotate the MET of interest
    if triggerMET is not None:
        ax.plot([triggerMET, triggerMET], [ax.get_ylim()[0],ax.get_ylim()[1]], linestyle='--', color='darkred')

    if triggerMJD is not None:
        ax.plot([triggerMJD, triggerMJD], [ax.get_ylim()[0],ax.get_ylim()[1]], linestyle='--', color='darkred')

    # Set a log scale
    if ylog == True:
        ax.set_yscale('log')

    if xlog == True:
        ax.set_xscale('log')

    # Set up the x-axis label
    if useMJD == True:
        ax.set_xlabel('Time (MJD)')
    else:
        ax.set_xlabel('Time (sec)')

    # Setup the y-axis label
    ax.set_ylabel(r'Photons cm$^{-2}$ s$^{-1}$')

    # Set the plot title
    ax.set_title(source, fontsize=12)

    # Create the TS plot pane
    if plotTS == True:
        ax2.scatter(timebins, ts, marker='o', s=25, edgecolors='black', color='#3e4d8b', linewidths=0.5)
        ax2.errorbar(timebins, ts, xerr=x_errors, yerr=numpy.zeros(len(ts)), fmt='none', markersize=5, color='#3e4d8b', ecolor='#3e4d8b', markeredgecolor='black', capsize=0, alpha=0.6)

        ax2.set_ylabel('TS')

        # Set up the x-axis label
        if useMJD == True:
            ax2.set_xlabel('Time (MJD)')
        else:
            ax2.set_xlabel('Time (sec)')

        ax2.set_yscale('log')

    # Create the photon index plot pane
    if plotIndex == True:
        ax3.scatter(timebins_detections, photon_index, marker='o', s=25, edgecolors='black', color='#3e4d8b', linewidths=0.5)
        ax3.errorbar(timebins_detections, photon_index, xerr=x_errors, yerr=photon_index_error, fmt='none', markersize=5, color='#3e4d8b', ecolor='#3e4d8b', markeredgecolor='black', capsize=0, alpha=0.6)

        # Set the y-label
        ax3.set_ylabel(r'$\Gamma$')

        # Set up the x-axis label
        if useMJD == True:
            ax3.set_xlabel('Time (MJD)')
        else:
            ax3.set_xlabel('Time (sec)')

        # Set the format of the y-axis to scientific notation
        ax3.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))


    if savefig == True:

        # Replace any spaces in the source name with underscores
        source_underscore = source.replace(' ', '_')

        # Define the filename
        filename = 'photon_flux_' + source_underscore + '_' + cadence + extension

        # Save the plot
        print('\nSaving photon flux plot to:\n%s' % filename)
        plot.savefig(filename, bbox_inches='tight', dpi=96)

    # Show the plot
    if showPlot == True:
        plot.show()

    plot.close()

    return

##########################################################################################


