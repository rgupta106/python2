#!/usr/bin/env python 

'''
                    Space Telescope Science Institute

Synopsis:  

These are routines for plotting various parameters in of the wind
after these parameters have been saved to an astropy_ascii table
with a routine like astropy


Command line usage (if any):

    usage: plot_wind filename var grid'

Description:  

Primary routines:

    doit

Notes:
                                       
History:

160223  ksl Coding begun
170505  ksl Adapat to Python3

'''

import sys
from astropy.io import ascii
import numpy
import pylab
from scipy.signal import boxcar
from scipy.signal import convolve
import subprocess
from matplotlib import tri
from astropy.io import ascii
from mpl_toolkits.axes_grid1 import make_axes_locatable



def compare_separate(f1='fiducial_agn_master.txt',f2='fiducial_agn_master.txt', var='t_r',grid='ij',inwind='',scale='guess',zmin=-1e50,zmax=1e50,fig_no=5):
    '''
    This routine compares the same variable from two different runs of python, and produces
    Three separate plots. The plots represent the variable in the first file, the variable in the second file and
    the difference between the two
    '''

    x1,y1,xvar1,title,xlabel,ylabel=get_data(f1,var,grid,inwind,scale,zmin,zmax)
    x2,y2,xvar2,title,xlabel,ylabel=get_data(f2,var,grid,inwind,scale,zmin,zmax)
    xdiff=xvar2-xvar1

    root=f1.split('.')
    root=root[0]
    just_plot(x1,y1,xvar1,root,title,xlabel,ylabel,fig_no)

    root=f2.split('.')
    root=root[0]
    just_plot(x2,y2,xvar2,root,title,xlabel,ylabel,fig_no+1)

    root='diff'
    just_plot(x1,y1,xdiff,root,title,xlabel,ylabel,fig_no+2)
    return

def compare(f1='sv_master.txt',f2='sv_master.txt',var='t_r',grid='ij',inwind='',scale='guess',zmin=-1e50,zmax=1e50,fig_no=5):
    '''
    Compare results of two variables within a single plot
    

    The three plots are of from the first file, the second file, and the difference 
    respectively
    '''


    
    x1,y1,xvar1,title,xlabel,ylabel=get_data(f1,var,grid,inwind,scale,zmin,zmax)
    x2,y2,xvar2,title,xlabel,ylabel=get_data(f2,var,grid,inwind,scale,zmin,zmax)
    xdiff=xvar2-xvar1

    

    pylab.figure(fig_no,(18,6))
    pylab.clf()
    pylab.subplot(131)

    ax=pylab.gca()
    cmap=pylab.cm.jet
    cmap.set_bad(color='white')
    im=ax.pcolormesh(x1,y1,xvar1,cmap=cmap)
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    pylab.colorbar(im, cax=cax)
    pylab.tight_layout()


    pylab.subplot(132)

    ax=pylab.gca()
    cmap=pylab.cm.jet
    cmap.set_bad(color='white')
    im=ax.pcolormesh(x2,y2,xvar2,cmap=cmap)
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    pylab.colorbar(im, cax=cax)
    pylab.tight_layout()

    pylab.subplot(133)

    ax=pylab.gca()
    cmap=pylab.cm.jet
    cmap.set_bad(color='white')
    im=ax.pcolormesh(x2,y2,xdiff,cmap=cmap)
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    pylab.colorbar(im, cax=cax)
    pylab.tight_layout()


    pylab.draw()
    
    outroot='Difference_%s.png' % var
    pylab.savefig(outroot)


    return
    

def get_data(filename='fiducial_agn_master.txt', var='t_r',grid='ij',inwind='',scale='guess',zmin=-1e50,zmax=1e50):
    '''
    This routine reads and scales the data from a single variable that is read from an ascii table 
    representation of one or more of the parameters in a windsave file

    '''

    try:
        data=ascii.read(filename)
    except IOError:
        print('Error: file %s does not appear to exist' % filename)
        return

    # data.info()

    # print('options: xyscale %s varscale %s min %g max %g' % (grid,scale,zmin,zmax))


    title=var


    ii=data['i']
    jj=data['j']
    iimax=numpy.max(ii)
    jjmax=numpy.max(jj)
    if grid=='ij':
        x=numpy.array(data['i'])
        y=numpy.array(data['j'])
        xlabel='i'
        ylabel='j'
    elif grid=='log':
        x=numpy.array(data['x']) 
        y=numpy.array(data['z'])
        x=numpy.log10(x)
        y=numpy.log10(y)
        xlabel='log(x)'
        ylabel='log(z)'
    else:
        x=numpy.array(data['x'])
        y=numpy.array(data['z'])
        xlabel='x'
        ylabel='z'

    xvar=numpy.array(data[var])
    xwind=numpy.array(data['inwind'])
    x=x.reshape(iimax+1,jjmax+1)
    y=y.reshape(iimax+1,jjmax+1)
    xvar=xvar.reshape(iimax+1,jjmax+1)
    xwind=xwind.reshape(iimax+1,jjmax+1)


    # now mask out the appropriate data

    if inwind=='all':
        xwind.fill(0) # Keep everything
    elif inwind.count('partial'):
        xwind=numpy.select([xwind<0],[xwind],default=0)

    # Now make the mask regardless
    mask=numpy.ma.make_mask(xwind)





    xvar=numpy.ma.array(xvar,mask=mask)


    vmin=numpy.ma.min(xvar)
    vmax=numpy.ma.max(xvar)



    if vmin<zmin:
        vmin=zmin
    if vmax>zmax:
        vmax=vmax



    if scale=='guess':
        if (vmax-vmin)>1e4:
            scale='log'
    
    # Need this to go from 
    if scale=='log':
        if vmin<vmax/1e10:
            vmin=vmax/1e10
        xvar=numpy.select([xvar>vmin],[xvar],default=vmin)
        xvar=numpy.ma.log10(xvar)
        vmax=numpy.log10(vmax)
        vmin=numpy.log10(vmin)
        title='log '+title

    # Reapply the mask; need to make bad color work
    xvar=numpy.ma.array(xvar,mask=mask)



    


    return x,y,xvar,title,xlabel,ylabel


def just_plot(x,y,xvar,root,title,xlabel,ylabel,fig_no=1):
    '''
    This routine simply is produces a plot of a variable from
    that has been printed to an astropy table with a routine like
    windsave2table.    This function is simply a plotting routine


    '''

    pylab.figure(fig_no,(6,6))
    pylab.clf()
    ax=pylab.gca()
    cmap=pylab.cm.jet
    cmap.set_bad(color='white')
    im=ax.pcolormesh(x,y,xvar,cmap=cmap)
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    pylab.colorbar(im, cax=cax)
    pylab.tight_layout()

    pylab.draw()
    title=title.replace(' ','_')
    if root=='':
        filename=title+'.png'
    else:
        filename='%s_%s.png' %(root,title)
    pylab.savefig(filename)
    return filename



def doit(filename='fiducial_agn.master.txt', var='t_r',grid='ij',inwind='',scale='guess',zmin=-1e50,zmax=1e50,plot_dir=''):
    '''
    Plot a single variable from an astropy table (normally created with windsave2table, with various
    options

    where var is the variable to plot
    where grid can be ij, log, or anything else.  If ij then the plot will be in grid coordinates, if log
        the plot will be in on a log scale in physical coordiantes.  If anything else, the plot will be
        on a linear scale in physical coordiantes
    where scale indicates how the variable should be plotted.  guess tells the routine to make a sensible choice
        linear implies the scale should be linear and log implies a log scale should be used
    where zmin and zmax overide the max and mimimum in the array (assuming these limits are with the range of
        the variable)

    '''

    root=filename.split('.')
    root=root[0]

    x,y,xvar,title,xlabel,ylabel=get_data(filename,var,grid,inwind,scale,zmin,zmax)
    if plot_dir!='':
        root='%s/%s' % (plot_dir,root)
    # print(len(x),len(y),len(xvar))
    plotfile=just_plot(x,y,xvar,root,title,xlabel,ylabel)

    return plotfile

    





# Next lines permit one to run the routine from the command line
if __name__ == "__main__":
    import sys
    if len(sys.argv)>2:
        # doit(int(sys.argv[1]))
        doit(sys.argv[1],sys.argv[2])
    else:
        print('usage: plot_wind filename var grid')
