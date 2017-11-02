import numpy as np 
import os,sys,getopt
import copy


import matplotlib 
matplotlib.use('Agg') 

import matplotlib.pyplot as plt

from utils.cosmoExtractor import findGalaxyAndOrient,rotateVectorsZY
from utils.movie_utils import addPrettyGalaxyToAx,getTemperature
from utils.readsnap import readsnap

def loadDataFromSnapshot(snapdir,snapnum,mode,frame_width,frame_depth):
    if 'r' in mode:
        print "using readsnap to load in data"
        ## assumes the only sort of multi-part snapshot you would have is in cosmological units
        ## if you have a multipart snapshot that isn't in cosmological units pray that h=1, or change
        ## this flag
        res = readsnap(snapdir,snapnum,0,cosmological = 1)

        pos_all = res['p']
        mass_all = res['m']
        temperature_all = getTemperature(res['u'],res['z'][:,1],res['ne'])
        
        thetay,thetaz,frame_center,gindices = findGalaxyAndOrient(snapdir,snapnum,pos_all,res['rho'],
            frame_width,frame_depth)
        
        ## filter and free up memory
        pos = rotateVectorsZY(thetay,thetaz,pos_all[gindices]-frame_center)
        print np.min(pos[:,2]),np.max(pos[:,2])
        raise Exception("STOP")
        frame_center = np.zeros(3) # plot at center of mass
        del pos_all
        mass = mass_all[gindices]
        del mass_all
        temperature = temperature_all[gindices]
        del temperature_all

        mydict = {
            'pos_all':pos,'mass_all':mass,'temperature_all':temperature,
            'HubbleParam':res['hubble'],'time_Myr':res['time'],
            'BoxSize':res['boxsize'],'frame_center' : frame_center
        }
        
    elif 's' in mode:
        print 'using h5py to load in data'
        mydict={}
        raise Exception("Unimplemented!")
    return mydict


def renderGalaxy(ax,snapdir,snapnum,savefig=1,noaxis=0,mode='r',**kwargs):
    # copy the dictionary so we don't mess anything up 
    copydict = copy.copy(kwargs)
    # add in filtered galaxy data

    # make projection map and add to canvas
    print copydict.keys(),'keys passed'

    if 'datadir' not in copydict:
        datadir = snapdir
        copydict['datadir']=snapdir
    else:
        datadir = copydict['datadir']

    try:
        copydict.update(loadDataFromSnapshot(snapdir,snapnum,mode,kwargs['frame_width'],kwargs['frame_depth']))
        ax = addPrettyGalaxyToAx(
            ax,snapdir,snapnum,
            frame_center=np.zeros(3),
            **copydict)

    except IOError:
        ## perhaps we haven't computed the projections yet, force an "overwrite"
        ## load in snapshot data
        copydict.update(loadDataFromSnapshot(snapdir,snapnum,mode,kwargs['frame_width'],kwargs['frame_depth']))
        ax = addPrettyGalaxyToAx(
            ax,snapdir,snapnum,
            overwrite=1,
            **copydict)

    if savefig:
        savefig_args={}
        if 'edgeon' in kwargs and kwargs['edgeon']:
            ax.get_figure().set_size_inches(6,8)
        else:
            ax.get_figure().set_size_inches(6,6)

        if noaxis:
            ax.axis('off')
            ## remove whitespace around the axis, apparently the x/y origin is offset in pixel 
            ## space and so the bounding box doesn't actually reflect the left/bottom edge of the 
            ## axis
            ax.xaxis.set_major_locator(plt.NullLocator())
            ax.yaxis.set_major_locator(plt.NullLocator())
            savefig_args['bbox_inches']='tight'
            savefig_args['pad_inches']=0

        pixels = 1200 if 'pixels' not in kwargs else kwargs['pixels'] 
        image_name = "frame_%3d_%dkpc.png" % (snapnum, 2*kwargs['frame_width'])

        ax.get_figure().savefig(
            os.path.join(datadir,'Plots','GasTwoColour',image_name),
            **savefig_args)

    return ax 


def main(snapdir,snapstart,snapmax,**kwargs):
    for snapnum in xrange(snapstart,snapmax):
        ax = plt.gca()
        renderGalaxy(ax,snapdir,snapnum,
            **kwargs)
        plt.clf()
        

if __name__=='__main__':
    argv = sys.argv[1:]
    opts,args = getopt.getopt(argv,'rs',[
        'snapdir=',
        'snapstart=','snapmax=',
        'pixels=','frame_width=','frame_depth=',
        'theta=','phi=','psi=',
        'edgeon=',
        'min_den=','max_den=','min_temp=','max_temp=','datadir=',
        'noaxis='])

    #options:
    # -r/s = use readsnap or use single snapshot loader
    #--snapdir: place where snapshots live
    #--snapstart : which snapshot to start the loop at
    #--snapmax : which snapshot to end the loop at
    #--frame_width : half width of frame in kpc
    #--frame_depth : half depth of frame in kpc
    #--datadir: place to output frames to

    #--theta,phi,psi : euler angles for rotation
    #--edgeon : flag for sticking a 90 degree edge on rotation underneath 
    #--pixels : how many pixels in each direction to use, defaults to 1200
    #--min/max_den/temp: bottom/top of color scales for density/temperature
    #--noaxis : flag for removing axis and whitespace for just the pretty part


    for i,opt in enumerate(opts):
        if opt[1]=='':
            opts[i]=('mode',opt[0].replace('-'))
        else:
            key = opt[0].replace('-','')
            if key in ['snapdir','datadir']:
                value= opt[1]
            else:
                # turn arguments from strings to whatever
                value = eval(opt[1])
            opts[i]=(key,value)
    main(**dict(opts))

