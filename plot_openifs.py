#
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import cmocean

# Directory
ddir = '/gxfs_work1/geomar/smomw352/esm-slask/oifs-test-3/outdata/oifs/19790101/'

# Frequency
freq = '6h'

# Plot time average
times = slice('1979-01-01','1979-01-31')

# Which variables to plot
variables = ['t']

# Which level (if pressure level data)
plevel = 85000 # [Pa]

# Find data
sfc = ddir + 'ECE3_'+freq+'_*_regular_sfc.nc'
pl  = ddir + 'ECE3_'+freq+'_*_regular_pl.nc'

# Open files
print(sfc)
try:
    ds_sfc = xr.open_mfdataset(sfc,combine='by_coords')
    print(' Found surface variables ')
    sfc_variables = list(ds_sfc.keys())
    print(sfc_variables)
    sfc_ok = True
except:
    print(' No '+freq+' surface fields found ')
    sfc_ok = False

print(pl)
try:
    ds_pl  = xr.open_mfdataset(pl,combine='by_coords')
    pl_variables = list(ds_pl.keys())
    print(' Found pressure-level variables ')
    print(pl_variables)
    pl_ok = True
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
            data = ds_sfc[variable]
    if pl_ok:
        if variable in pl_variables:
            pl_plot = True
            data = ds_pl[variable]

    if sfc_plot:
        # Slice time and average over time
        zplot = data.sel(time_counter = times).mean('time_counter')
        
    if pl_plot:
        # Slice pressure level and time
        zplot = data.sel(pressure_levels = plevel).sel(time_counter = times).mean('time_counter')

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
        zplot.plot.pcolormesh(ax=ax,vmin=253,vmax=293,cmap=cmocean.cm.thermal)

        # Draw coastlines in plot
        ax.coastlines()
        # Set map extent (lonmin, lonmax, latmin, latmax)
        ax.set_extent([-80,20,30,80])
        # Set aspect to none so that colorbar scales with plot
        ax.set_aspect('auto', adjustable=None)

        figname = 'plots/%s.png' % (variable,)
        fig.savefig(figname,format='png',dpi=300)

plt.show()
