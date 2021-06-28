#
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import cmocean

# Base directory for all runs
base_dir = '/gxfs_work1/geomar/smomw352/esm-slask/'

# Experiment and folder for control
control_exp = 'oifs-test-3'
control_end = '19790101'
control_times = slice('1979-01-01','1979-01-01')
control_dir = '%s/%s/outdata/oifs/%s/' % (base_dir,control_exp,control_end)

# Perturbation experiments
exps = ['oifs-test-3', 'oifs-test-3']
ends = ['19790102','19790103']
times = [slice('1979-01-02','1979-01-02'), slice('1979-01-03','1979-01-03')]
dirs = []
for i, (exp,end) in enumerate( zip(exps,ends) ):
    dirs.append( '%s/%s/outdata/oifs/%s/' % (base_dir,exp,end) )

# Add control to end of lists
exps.append(control_exp)
ends.append(control_end)
times.append(control_times)
dirs.append(control_dir)

# Frequency
freq = '6h'

# Which variables to plot
variables = ['t']

# Which level (if pressure level data)
plevel = 85000 # [Pa]

#
# Find data
#

ds_sfc = []
ds_pl = []

for i, (exp,ddir) in enumerate( zip(exps,dirs) ):

    sfc = ddir + 'ECE3_'+freq+'_*_regular_sfc.nc'
    pl  = ddir + 'ECE3_'+freq+'_*_regular_pl.nc'

    # Open files
    print(sfc)
    try:
        _ds = xr.open_mfdataset(sfc,combine='by_coords')
        print(' Found surface variables ')
        sfc_variables = list(_ds.keys())
        print(sfc_variables)
        sfc_ok = True
        ds_sfc.append( _ds )
    except:
        print(' No '+freq+' surface fields found ')
        sfc_ok = False
    
    print(pl)
    try:
        _ds  = xr.open_mfdataset(pl,combine='by_coords')
        pl_variables = list(_ds.keys())
        print(' Found pressure-level variables ')
        print(pl_variables)
        pl_ok = True
        ds_pl.append( _ds )
    except:
        print(' No '+freq+' pressure level data found ')
        pl_ok = False

#
# Make some plots
#
for variable in variables:

    pl_plot = False
    sfc_plot = False
    
    if sfc_ok: 
        if variable in sfc_variables:
            sfc_plot = True
    if pl_ok:
        if variable in pl_variables:
            pl_plot = True
    
    # Get data from control exp
    if sfc_plot:
        # Slice time and average over time
        zplot_c = ds_sfc[-1][variable].sel(time_counter = control_times).mean('time_counter')

    if pl_plot:
        # Slice pressure level and time
        zplot_c = ds_pl[-1][variable].sel(pressure_levels = plevel).sel(time_counter = control_times).mean('time_counter')

    for i, (exp,time_slice) in enumerate( zip(exps[:-1],times[:-1]) ):
        
        if sfc_plot:            
            z = ds_sfc[i][variable].sel(time_counter = time_slice).mean('time_counter')
        
        if pl_plot:
            print(ds_pl[i][variable])
            z = ds_pl[i][variable].sel(pressure_levels = plevel).sel(time_counter = time_slice).mean('time_counter')

        # Interpolate control to exp 
        z0 = zplot_c.interp_like(z)
        # Subtract control from exp
        zplot = z - z0

        if sfc_plot or pl_plot:
            fig, ax = plt.subplots(1,1,subplot_kw={'projection':ccrs.PlateCarree()})
            # Plot pcolormesh (best for auto)
            #zplot.plot(ax=ax))
            
            # Plot contours
            # You can tune the number of contours etc
            #zplot.plot.contourf(ax=ax,levels=21)
            #zplot.plot.contour(ax=ax,levels=20,colors='k')

            # Plot pcolormesh with specified colormap
            # See list of colormaps https://matplotlib.org/cmocean/
            zplot.plot.pcolormesh(ax=ax,vmin=-5,vmax=5,cmap=cmocean.cm.balance)
            
            # Draw coastlines in plot
            ax.coastlines()
            # Set map extent (lonmin, lonmax, latmin, latmax)
            ax.set_extent([-80,20,30,80])
            # Set aspect to none so that colorbar scales with plot
            ax.set_aspect('auto', adjustable=None)
            
            figname = 'plots/%s_%s-%s.png' % (variable,exp,control_exp)
            fig.savefig(figname,format='png',dpi=300)

plt.show()
