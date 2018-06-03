import matplotlib.pyplot as plt
import numpy as np 
import h5py

from firestudio.utils.stellar_utils import raytrace_projection,load_stellar_hsml
import firestudio.utils.stellar_utils.make_threeband_image as makethreepic

## Stellar light attenuation projection
def calc_stellar_hsml(x,y,z):
    starhsml = load_stellar_hsml.get_particle_hsml
    h_all = starhsml(x,y,z)
    return h_all

def raytrace_ugr_attenuation(
    x,y,z,
    mstar,ages,metals,
    h_star, 
    gx,gy,gz,
    mgas, gas_metals,
    h_gas,
    pixels = 1200,
    xlim = None, ylim = None, zlim = None
    ):

    ## setup boundaries to cut-out gas particles that lay outside
    ## range
    if xlim is None:
        xlim = [np.min(x),np.max(x)]
    if ylim is None:
        ylim = [np.min(y),np.max(y)]
    if zlim is None:
        zlim = [np.min(z),np.max(z)]

    stellar_raytrace = raytrace_projection.stellar_raytrace


#   band=BAND_ID; # default=bolometric
#   j = [  0,  6,  7,  8,  9, 10, 11, 12, 13,  1,   2,   3,   4,   5] # ordering I'm used to
#   i = [  0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  10,  11,  12,  13] # ordering of this
#   band_standardordering = band
#   band = j[band]
#   if (band > 13): 
#       print 'BAND_ID must be < 13'; 
#       return 0;
#   
#   b=['Bolometric', \
#   'Sloan u','Sloan g','Sloan r','Sloan i','Sloan z', \
#   'Johnsons U','Johnsons B', 'Johnsons V','Johnsons R','Johnsons I', \
#   'Cousins J','Cousins H','Cousins K']
    ## pick color bands by their IDs, see above
    BAND_IDS=[9,10,11]
    #gas_out,out_u,out_g,out_r = stellar_raytrace(
    return stellar_raytrace(
        BAND_IDS,
        x,y,z,
        mstar,ages,metals,
        h_star,
        gx,gy,gz,
        mgas, gas_metals,
        h_gas,
        pixels=pixels,
        xlim=xlim,ylim=ylim,zlim=zlim,
        ADD_BASE_METALLICITY=0.001*0.02,ADD_BASE_AGE=0.0003,
        IMF_SALPETER=0,IMF_CHABRIER=1
    )
def make_threeband_image(ax,
    out_r,out_g,out_u,
    maxden = 1e-3, dynrange = 1.001,
    pixels = 1200,
    noaxis=0):

    image24, massmap = makethreepic.make_threeband_image_process_bandmaps(
        out_r,out_g,out_u,
        maxden=maxden,dynrange=dynrange,pixels=pixels,
        color_scheme_nasa=1,color_scheme_sdss=0)

    ## for some reason it's rotated 90 degrees...? kind of like transposed but different
    ##  need to take the rows of the output image and make them the columns, iteratively,
    ##  for now... 
    #image24=np.rot90(image24,k=1,axes=(0,1))
    return np.transpose(image24,axes=(1,0,2))
    
def get_h_star(xs,ys,zs,savefile=None):
    try:
        if savefile is not None:
            with h5py.File(savefile,'r') as handle:
                return np.array(handle['StarHs'])
        else:
            raise IOError
    except (IOError,KeyError):
        h_star =  calc_stellar_hsml(xs,ys,zs)
        if savefile is not None:
            ## save it for next time!
            with h5py.File(savefile,'a') as handle:
                handle['StarHs']=h_star
        return h_star

def get_bands_out(
    xs,ys,zs,
    mstar,ages,metals,
    h_star,
    gxs,gys,gzs,
    mgas,gas_metals,h_gas,
    savefile=None
    ):
    try:
        if savefile is not None:
            with h5py.File(savefile,'r') as handle:
                return np.array(handle['out_u']),np.array(handle['out_g']),np.array(handle['out_r'])
        else:
            raise IOError
    except (IOError,KeyError):
        gas_out,out_u,out_g,out_r = raytrace_ugr_attenuation(
            xs,ys,zs,
            mstar,ages,metals,
            h_star,
            gxs,gys,gzs,
            mgas,gas_metals,h_gas,
        ) 
        if savefile is not None:
            ## save it for next time!
            with h5py.File(savefile,'a') as handle:
                handle['out_u']=out_u
                handle['out_g']=out_g
                handle['out_r']=out_r

        return out_u,out_g,out_r

def add_scale_bar(final_image,image_length,npix,scale_line_length):
    # Convert to pixels
    length_per_pixel = image_length/ npix
    scale_line_length_px = int(scale_line_length / length_per_pixel)

    # Position in terms of image array indices
    scale_line_x_start = int(0.05 * npix)
    scale_line_x_end = min(scale_line_x_start + scale_line_length_px,npix)
    scale_line_y = int(0.02 * npix)

    # Go through pixels for scale bar, setting them to white
    for x_index in xrange(scale_line_x_start, scale_line_x_end):
        final_image[scale_line_y, x_index, 0] = 1
        final_image[scale_line_y, x_index, 1] = 1
        final_image[scale_line_y, x_index, 2] = 1
        final_image[scale_line_y + 1, x_index, 0] = 1
        final_image[scale_line_y + 1, x_index, 1] = 1
        final_image[scale_line_y + 1, x_index, 2] = 1
        final_image[scale_line_y + 2, x_index, 0] = 1
        final_image[scale_line_y + 2, x_index, 1] = 1
        final_image[scale_line_y + 2, x_index, 2] = 1
        final_image[scale_line_y + 3, x_index, 0] = 1
        final_image[scale_line_y + 3, x_index, 1] = 1
        final_image[scale_line_y + 3, x_index, 2] = 1
        final_image[scale_line_y + 4, x_index, 0] = 1
        final_image[scale_line_y + 4, x_index, 1] = 1
        final_image[scale_line_y + 4, x_index, 2] = 1
        final_image[scale_line_y + 5, x_index, 0] = 1
        final_image[scale_line_y + 5, x_index, 1] = 1
        final_image[scale_line_y + 5, x_index, 2] = 1

    return final_image

def renderStarGalaxy(ax,snapdir,snapnum,savefig=1,noaxis=0,savefile=None,mode='r',fontsize=None,
    scale_bar=1,**kwargs):
    ## we've already been passed open snapshot data
    if ('star_snap' in kwargs) and ('snap' in kwargs):
        star_snap = kwargs['star_snap']
        snap = kwargs['snap']

        ## unpack relevant information
        xs,ys,zs = star_snap['Coordinates'].T
        mstar,ages, metals = star_snap['Masses'],star_snap['AgeGyr'],star_snap['Metallicity'][:,0]
        gxs, gys, gzs, = snap['Coordinates'].T
        mgas,gas_metals, h_gas = snap['Masses'],snap['Metallicity'][:,0],snap['SmoothingLength']

        h_star = get_h_star(xs,ys,zs,savefile if mode =='r' else None)
        
        out_u,out_g,out_r=get_bands_out(
            xs,ys,zs,
            mstar,ages,metals,
            h_star,
            gxs,gys,gzs,
            mgas,gas_metals,h_gas,
            savefile=savefile if mode =='r' else None
            )

        image24=make_threeband_image(ax,out_r,out_g,out_u,dynrange=1e1,noaxis=noaxis)


    image_length = np.max(xs)-np.min(xs)

    if image_length > 15 : 
        scale_line_length = 5
        scale_label_text = r"$\mathbf{5 \, \rm{kpc}}$"

    elif image_length > 1.5 : 
        scale_line_length = 1.0 
        scale_label_text = r"$\mathbf{1 \, \rm{kpc}}$"

    else:
        scale_line_length = .1
        scale_label_text = r"$\mathbf{100 \, \rm{pc}}$"

    ## handle default
    fontsize=8 if fontsize is None else fontsize
    scale_label_position = 0.06 
    pixels = 1200 if 'pixels' not in kwargs else kwargs['pixels']

    if scale_bar:
        image24=add_scale_bar(image24,image_length,pixels,scale_line_length)
        label2 = ax.text(scale_label_position,
            0.03, scale_label_text, fontweight = 'bold', transform = ax.transAxes)
        label2.set_color('white')
        label2.set_fontsize(fontsize*0.75)

    ax.imshow(image24,interpolation='bicubic',origin='lower')#,aspect='normal')
    ax.get_figure().set_size_inches(6,6)
    if noaxis:
        ax.axis('off')

    ## need to load the snapshot data!
    else:
        raise Exception("Unimplemented!")


if __name__ == '__main__':
    print 'running from the command line' 
