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

def plotLightCurveData(lightCurveData, logCenter=False, MET=None, useMJD=False, ylim=None, triggerMET=None, triggerMJD=None, ylog=False, xlog=False, ymin=None, \
    ymax=None, xmin=None, xmax=None, removeTicks=1, savefig=True, showPlot=False, plotTS=False, plotIndex=False, plotFreeIndexFit=False, verbose=False, extension='.png'):
    """Plot data from the light curve repository

    Arguments:
        lightCurveData (dict):              '
        logCenter (BOOL):          
        MET (int):        
        useMJD (BOOL):       
        ylim (list):         
        triggerMET (int):         
        ylog (BOOL):         
        xlog (BOOL):         

    Returns:
        None

    """
    
    # Extract likelihood ratio test statistic
    ts = lightCurveData['ts']

    # Extact the tmin and tmax of the analysis 
    tmin = lightCurveData['tmin']
    tmax = lightCurveData['tmax']

    # Extract the spectral flux and index values
    if plotFreeIndexFit == False:

        # Results from a likelihood fit where spectral index of the source of interest was left free to vary
        photon_index = lightCurveData['photon_index']
        photon_index_error = lightCurveData['photon_index_error']
        photon_flux = lightCurveData['photon_flux']
        photon_flux_error = lightCurveData['photon_flux_error']
        energy_flux = lightCurveData['energy_flux'] 
        energy_flux_error = lightCurveData['energy_flux_error']

    else:

        # Results from a likelihood fit where spectral index of the source of interest was fixed
        photon_index = lightCurveData['photon_index2']
        photon_index_error = lightCurveData['photon_index_error2']
        photon_flux = lightCurveData['photon_flux2']
        photon_flux_error = lightCurveData['photon_flux_error2']
        energy_flux = lightCurveData['energy_flux2'] 
        energy_flux_error = lightCurveData['energy_flux_error2']        

    # Extract the photon and energy upper limits
    photon_flux_upper_limit = lightCurveData['photon_flux_upper_limit']
    energy_flux_upper_limit = lightCurveData['energy_flux_upper_limit']

    # Get the duration
    # dt = numpy.array([tmax[1] - tmin[0]] * len(tmax))
    dt = tmax - tmin

    # Determine which timebins have detections 
    detections = numpy.where(ts >= ts_min)
    nondetections = numpy.where(ts < ts_min)

    # Get the time bin centers
    if logCenter == True:
        timebin_center = (tmin*tmax)**0.5 
    else:
        # timebin_center = tmin + (tmin+tmax)*0.5
        timebin_center = tmin+(tmax-tmin)

    # Convert everything to a relative time if an MET is specified
    if MET is not None:
        timebin_center = timebin_center - MET

    # Convert the timebins to MJD
    elif useMJD == True:

        # Convert dt into days
        dt = dt / 86400.0

        MJDs = []

        for timebin in timebin_center:
            MJD = computeMJD(timebin)
            MJDs.append(MJD)

        timebin_center = numpy.array(MJDs)

    # Create two subplots sharing the x axes
    if plotTS == True and plotIndex == True:
        f, (ax, ax2, ax3) = plot.subplots(3, sharex=True, sharey=False, figsize=[12,12])
    elif plotTS == False and plotIndex == True:
        f, (ax, ax3) = plot.subplots(2, sharex=True, sharey=False, figsize=[12,9])
    elif plotTS == True and plotIndex == False:
        f, (ax, ax2) = plot.subplots(2, sharex=True, sharey=False, figsize=[12,9])
    elif plotTS == False and plotIndex == False:
        f, (ax) = plot.subplots(1, sharex=True, sharey=False, figsize=[12,6])

    # Adjust the two plots so that there is no space between them
    if plotTS == True or plotIndex == True:
        f.subplots_adjust(hspace=0)

    # Calculate the x errors
    x_errors = (dt[detections]/2.)

    # Plot the flux values
    ax.scatter(timebin_center[detections], photon_flux[detections], marker='o', s=25, edgecolors='black', color='#3e4d8b', linewidths=0.5)

    # Plot the upper limits
    ax.scatter(timebin_center[nondetections], photon_flux_upper_limit[nondetections], marker='v', s=25, edgecolors='black', color='#3e4d8b', linewidths=0.5, alpha=0.6)

    # Don't let the error bars affect the plot scale
    ax.set_autoscale_on(False)

    # Plot the error bars
    ax.errorbar(timebin_center[detections], photon_flux[detections], xerr=[dt[detections]/2., dt[detections]/2.], yerr=photon_flux_error[detections], fmt='none', markersize=5, color='#3e4d8b', ecolor='#3e4d8b', markeredgecolor='black', label='Photon Flux', capsize=0, alpha=0.6)

    # Set the y-axis range
    if ylog == True:
        ymax=numpy.median(photon_flux[detections])*100
        ymin=numpy.median(photon_flux[detections])/100
        ax.set_ylim(ymin, ymax)

    elif ymin is None and ymax is None:
        ymax=numpy.median(photon_flux[detections])*10
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
    minorLocator = AutoMinorLocator()
    ax.xaxis.set_minor_locator(minorLocator)

    # Set the y-axis minor tick frequency
    minorLocator = AutoMinorLocator()        
    ax.yaxis.set_minor_locator(minorLocator)

    # Set a minimum y value
    if ylog == False:
        ax.set_ylim(bottom=0)

    else:
        if ylim is not None:
            ax.set_ylim(ylim)
        else:
            ax.set_ylim(bottom=numpy.median(photon_flux[detections]/100))

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
    ax.set_title(source_name, fontsize=12)

    if plotTS == True or plotIndex == True:

        # Hide the last tick label
        yticks = ax.get_yticks()
        yticks = yticks[1:-1*removeTicks]
        ax.set_yticks(yticks)


    if plotTS == True:
        ax2.scatter(timebin_center, ts, marker='o', s=25, edgecolors='black', color='#3e4d8b', linewidths=0.5)
        ax2.errorbar(timebin_center, ts, xerr=[dt/2., dt/2.], yerr=numpy.zeros(len(ts)), fmt='none', markersize=5, color='#3e4d8b', ecolor='#3e4d8b', markeredgecolor='black', capsize=0, alpha=0.6)

        ax2.set_ylabel('TS')

        # Set up the x-axis label
        if useMJD == True:
            ax2.set_xlabel('Time (MJD)')
        else:
            ax2.set_xlabel('Time (sec)')

        # Hide the last tick label
        yticks = ax2.get_yticks()
        yticks = yticks[1:-1*removeTicks]
        ax2.set_yticks(yticks)

        ax2.set_yscale('log')
        ax2.set_ylim(0.1,max(ts)*2)


    if plotIndex == True:
        ax3.scatter(timebin_center, photon_index, marker='o', s=25, edgecolors='black', color='#3e4d8b', linewidths=0.5)
        ax3.errorbar(timebin_center[detections], photon_index[detections], xerr=[dt[detections]/2., dt[detections]/2.], yerr=photon_index_error[detections], fmt='none', markersize=5, color='#3e4d8b', ecolor='#3e4d8b', markeredgecolor='black', capsize=0, alpha=0.6)

        ax3.set_ylabel(r'$\Gamma$')

        # Set up the x-axis label
        if useMJD == True:
            ax3.set_xlabel('Time (MJD)')
        else:
            ax3.set_xlabel('Time (sec)')

        # Hide the last tick label
        yticks = ax3.get_yticks()
        yticks = yticks[1:-1*removeTicks]
        ax3.set_yticks(yticks)

        finite = numpy.isfinite(photon_index)
        photon_index_median = numpy.median(photon_index[finite])
        photon_index_std = numpy.std(photon_index[finite])

        ymin_ax3 = photon_index_median - 5*photon_index_std
        ymax_ax3 = photon_index_median + 5*photon_index_std

        ax3.set_ylim(ymin_ax3, ymax_ax3)


    if savefig == True:

        # Replace any spaces in the source name with underscores
        source_name_underscore = source_name.replace(' ', '_')

        # Define the filename
        filename = 'photon_flux_' + source_name_underscore + '_' + cadence + extension

        # Save the plot
        print('\nSaving photon flux plot to:\n%s' % filename)
        plot.savefig(filename, bbox_inches='tight', dpi=96)


    if showPlot == True:
        plot.show()

    plot.close()

    return

##########################################################################################


