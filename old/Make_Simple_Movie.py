#!/net/Jessica.Luo/miniconda3/bin/python

import os, subprocess, tarfile
from glob import glob
import numpy as np
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs

import warnings
warnings.filterwarnings('ignore')

seconds_per_day=60.*60.*24.
seconds_per_year=365.*seconds_per_day
carbon_molar_mass=12.011
cobalt_c_2_n = 106./16.

#--
path_root='/archive/Jessica.Luo/gz_test/MOM6_SIS2_COBALT'
case,machine_target='OM4p5_CORE2_IAF_gzCOBALT-020920','gfdl.ncrc4-intel16-prod'

phyto_varlist = ['di', 'smp', 'lgp']
zoo_varlist = ['smz', 'mdz', 'lgz', 'smt', 'lgt']

tmpdir = '/work/Jessica.Luo/tmp/'+case
if not os.path.exists(tmpdir):
    os.mkdir(tmpdir)
    print('created directory: '+tmpdir)
else:
    print('temporary directory exists: '+tmpdir)

#--
yrs=['1982']
mmdd='0101'
tar_path=os.path.join(path_root, case, machine_target, 'history')
files=[glob(os.path.join(tar_path,yr)+'*.nc.tar')[0] for yr in yrs]

[subprocess.call(['dmget', f]) for f in files]

#---
FORCE_EXTRACT=False

for i,yr in enumerate(yrs):
    tmp_prefix=tmpdir+'/'+yr+mmdd
    test_file=tmp_prefix+'.ocean_cobalt_omip_tracers_month_z.nc'
    
    if not os.path.isfile(test_file) or FORCE_EXTRACT:
        print('extracting: '+files[i])
        tarfile.open(files[i]).extractall(path=tmpdir)
    else:
        print('already extracted: '+files[i])
        
    files_in_dir=glob(tmp_prefix+'*.nc')

diagTypes = ['ocean_cobalt_omip_daily'] 
open_files = [tmp_prefix + '.' + x + '.nc' for x in diagTypes]
grid_file=tmpdir+'/'+yr+mmdd+'.ocean_static.nc'
ds=xr.open_mfdataset(open_files, combine='by_coords')
grid=xr.open_dataset(grid_file)

variable='mesozoo_200'
var_log10mgCm3=np.log10(ds[variable] * 1000 * carbon_molar_mass)
var_log10mgCm3.compute()

name='Mesozooplankton'
savename='Mov_zmesozoo_'

#name='Pelagic Tunicates'
#savename='Mov_ztunicate_'

for tt in np.arange(365):
    fig=plt.figure(figsize=(14,5.5))
    ax=plt.axes(projection=ccrs.Robinson(central_longitude=300.0))
    cs=ax.pcolormesh(grid.geolon.values, grid.geolat.values, var_log10mgCm3.isel(time=tt), 
         transform=ccrs.PlateCarree(), vmin=-0.5,vmax=4, cmap="magma")
    lb=plt.colorbar(cs)
    lb.set_label(name+', 200 m biomass\n(log10 mg C m-2)')
    plt.title(name+', '+ str(var_log10mgCm3.isel(time=tt).time.values)[0:10])
    plt.savefig('plots/'+savename+"{0:0=3d}".format(tt)+'.png', dpi=150)
    plt.close(fig)

