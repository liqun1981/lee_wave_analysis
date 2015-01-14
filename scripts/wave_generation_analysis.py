# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 16:24:05 2014

@author: jc3e13
"""

# %% Loads and imports.

import numpy as np
import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from mpl_toolkits import basemap as bm
import gsw
import os
import sys
import glob

lib_path = os.path.abspath('../python')
if lib_path not in sys.path:
    sys.path.append(lib_path)

import sandwell
import utils
import emapex
import plotting_functions as pf

try:
    print("Floats {} and {} exist!".format(E76.floatID, E77.floatID))
except NameError:
    E76 = emapex.EMApexFloat('../../data/EM-APEX/allprofs11.mat', 4976)
    E76.apply_w_model('../../data/EM-APEX/4976_fix_p0k0M_fit_info.p')
    E76.apply_strain('../../data/EM-APEX/4976_N2_ref_300dbar.p')
    E76.apply_isopycnal_displacement('../../data/EM-APEX/srho_4976_100mbin.p')
    E77 = emapex.EMApexFloat('../../data/EM-APEX/allprofs11.mat', 4977)
    E77.apply_w_model('../../data/EM-APEX/4977_fix_p0k0M_fit_info.p')
    E77.apply_strain('../../data/EM-APEX/4977_N2_ref_300dbar.p')
    E77.apply_isopycnal_displacement('../../data/EM-APEX/srho_4977_100mbin.p')


# %% Script params.

# Bathymetry file path.
bf = os.path.abspath(glob.glob('../../data/sandwell_bathymetry/topo_*.img')[0])
# Figure save path.
sdir = '../figures/wave_generation_analysis'
if not os.path.exists(sdir):
    os.makedirs(sdir)
# Universal figure font size.
matplotlib.rc('font', **{'size': 9})

################
# START SCRIPT #
################

# %% Float trajectories FULL
# ------------------

lons = np.hstack([Float.lon_start for Float in [E76, E77]])
lats = np.hstack([Float.lat_start for Float in [E76, E77]])

llcrnrlon = np.floor(np.min(lons)) - 1.
llcrnrlat = np.floor(np.min(lats)) - 1.
urcrnrlon = np.ceil(np.max(lons)) + 1.
urcrnrlat = np.ceil(np.max(lats)) + 1.

lon_lat = np.array([llcrnrlon, urcrnrlon+5, llcrnrlat-5, urcrnrlat])

lon_grid, lat_grid, bathy_grid = sandwell.read_grid(lon_lat, bf)
bathy_grid[bathy_grid > 0] = 0

m = bm.Basemap(projection='tmerc', llcrnrlon=llcrnrlon,
               llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon,
               urcrnrlat=urcrnrlat, lon_0=0.5*(llcrnrlon+urcrnrlon),
               lat_0=0.5*(llcrnrlat+urcrnrlat), resolution='f')

fig = plt.figure()
x, y = m(lon_grid, lat_grid)
m.pcolormesh(x, y, bathy_grid, cmap=plt.get_cmap('binary_r'))

for Float, colour in zip([E76, E77], ['b', 'g']):
    x, y = m(Float.lon_start, Float.lat_start)
    m.plot(x, y, colour, linewidth=3, label=Float.floatID)

plt.legend()

m.fillcontinents()
m.drawcoastlines()

r = np.abs((urcrnrlon-llcrnrlon)/(urcrnrlat-llcrnrlat))

if r > 1.:
    Nm = 8
    Np = max(4, np.round(Nm/r))
    orientation = 'horizontal'
elif r < 1.:
    Np = 8
    Nm = max(4, np.round(Nm/r))
    orientation = 'vertical'
else:
    Np = 4
    Nm = 4
    orientation = 'horizontal'

parallels = np.round(np.linspace(llcrnrlat, urcrnrlat, Np), 1)
m.drawparallels(parallels, labels=[1, 0, 0, 0])
meridians = np.round(np.linspace(llcrnrlon, urcrnrlon, Nm), 1)
m.drawmeridians(meridians, labels=[0, 0, 0, 1])

cbar = plt.colorbar(orientation=orientation)
cbar.set_label('Depth (m)')
pf.my_savefig(fig, 'both', 'traj', sdir, fsize='double_col')

# %% Float quivers RIDGE ONLY
# ------------------

# Number of half profiles.
N = 30
N0_76 = 15
N0_77 = 10
hpids = np.empty((N, 2))
hpids[:, 0] = np.arange(N0_76, N0_76+N)
hpids[:, 1] = np.arange(N0_77, N0_77+N)

lons = np.empty_like(hpids)
lats = np.empty_like(hpids)
Us = np.empty_like(hpids)
Vs = np.empty_like(hpids)
Ws = np.empty_like(hpids)

for i, Float in enumerate([E76, E77]):
    __, idxs = Float.get_profiles(hpids[:, i], ret_idxs=True)
    lons[:, i] = Float.lon_gps[idxs]
    lats[:, i] = Float.lat_gps[idxs]

    zef = Float.zef[:, idxs]
    z = Float.z[:, idxs]
    U = Float.U_abs[:, idxs]
    V = Float.V_abs[:, idxs]
    W = Float.Ww[:, idxs]

    for j, (zefpfl, zpfl, Upfl, Vpfl, Wpfl) in enumerate(zip(zef.T, z.T, U.T,
                                                             V.T, W.T)):
        Us[j, i] = np.nanmean(Upfl[(-1400 < zefpfl) & (zefpfl < -100)])
        Vs[j, i] = np.nanmean(Vpfl[(-1400 < zefpfl) & (zefpfl < -100)])
#        Us[j, i] = Upfl
#        Vs[j, i] = Vpfl
        Ws[j, i] = np.nanmax(Wpfl[zpfl < -100])

llcrnrlon = np.floor(np.nanmin(lons)) - .2
llcrnrlat = np.floor(np.nanmin(lats)) - .2
urcrnrlon = np.ceil(np.nanmax(lons)) + .2
urcrnrlat = np.ceil(np.nanmax(lats)) + .2

lon_lat = np.array([llcrnrlon, urcrnrlon, llcrnrlat, urcrnrlat])

lon_grid, lat_grid, bathy_grid = sandwell.read_grid(lon_lat, bf)
bathy_grid[bathy_grid > 0] = 0

m = bm.Basemap(projection='tmerc', llcrnrlon=llcrnrlon,
               llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon,
               urcrnrlat=urcrnrlat, lon_0=0.5*(llcrnrlon+urcrnrlon),
               lat_0=0.5*(llcrnrlat+urcrnrlat), resolution='f')

fig = plt.figure(figsize=(10, 10))
x, y = m(lon_grid, lat_grid)
levels = np.arange(-4000, 0, 500)
CS = m.contour(x, y, bathy_grid, 20, cmap=plt.get_cmap('binary'),
               levels=levels)
plt.clabel(CS, inline=1, fontsize=8, fmt='%1.f')
m.fillcontinents()
m.drawcoastlines()

r = np.abs((urcrnrlon-llcrnrlon)/(urcrnrlat-llcrnrlat))

if r > 1.:
    Nm = 8
    Np = max(3, np.round(Nm/r))

elif r < 1.:
    Np = 8
    Nm = max(3, np.round(Nm/r))

parallels = np.round(np.linspace(llcrnrlat, urcrnrlat, Np), 1)
m.drawparallels(parallels, labels=[1, 0, 0, 0])
meridians = np.round(np.linspace(llcrnrlon, urcrnrlon, Nm), 1)
m.drawmeridians(meridians, labels=[0, 0, 0, 1])

marker = ['o', '*']
label = ['4976', '4977']
color = ['b', 'g']
for i, (lon, lat, U, V, W) in enumerate(zip(lons.T, lats.T, Us.T, Vs.T, Ws.T)):
    x, y = m(lon, lat)
    m.plot(x, y, marker[i], color='y', label=label[i])
    Q = m.quiver(x, y, U, V, W, scale=6, cmap=plt.get_cmap('jet'))
    plt.clim(0, 0.3)
#    for _x, _y, hpid in zip(x, y, hpids[:, i]):
#        plt.annotate("{:1.0f}".format(hpid), xy=(_x, _y),
#                     xytext=(1.03*_x, 1.03*_y), color=color[i])

plt.legend()
qk = plt.quiverkey(Q, 0.5, 0.92, 0.5, r'0.5 m s$^{-1}$', labelpos='N')
cbar = plt.colorbar(orientation='horizontal')
cbar.set_label('Maximum $W$ (m s$^{-1}$)')

# This addition uses the hpids from the upstream flow stuff below.
N = 10
N0_76 = 15
N0_77 = 10
E76_hpids = np.arange(N0_76, N0_76+N)
E77_hpids = np.arange(N0_77, N0_77+N)
__, i76 = E76.get_profiles(E76_hpids, ret_idxs=True)
__, i77 = E76.get_profiles(E77_hpids, ret_idxs=True)
x, y = m(E76.lon_start[i76], E76.lat_start[i76])
m.plot(x, y, 'rx')
x, y = m(E77.lon_start[i77], E77.lat_start[i77])
m.plot(x, y, 'rx')

plt.tight_layout()
pf.my_savefig(fig, 'both', 'quiver_traj', sdir, fsize='double_col')

# %% Upstream flow properties
# ------------------------

N = 10
N0_76 = 15
N0_77 = 10
E76_hpids = np.arange(N0_76, N0_76+N)
E77_hpids = np.arange(N0_77, N0_77+N)

pfls = np.hstack((E76.get_profiles(E76_hpids), E77.get_profiles(E77_hpids)))

fig, axs = plt.subplots(1, 7, sharey=True)
fig.set_size_inches(16, 5)

axs[0].set_ylabel('$z$ (m)')

z_mean = np.arange(-1450, 0, 5)
T_mean = emapex.mean_profile(pfls, 'T', z_return=z_mean)
S_mean = emapex.mean_profile(pfls, 'S', z_return=z_mean)
rho_1_mean = emapex.mean_profile(pfls, 'rho_1', z_return=z_mean)
N2_ref_mean = emapex.mean_profile(pfls, 'N2_ref', z_return=z_mean)
U_abs_mean = emapex.mean_profile(pfls, 'U_abs', z_return=z_mean)
V_abs_mean = emapex.mean_profile(pfls, 'V_abs', z_return=z_mean)
Ww_mean = emapex.mean_profile(pfls, 'Ww', z_return=z_mean)

for pfl in pfls:

    axs[0].plot(pfl.T, pfl.z, color='k', alpha=0.3)
    axs[1].plot(pfl.S, pfl.z, color='k', alpha=0.3)
    axs[2].plot(pfl.rho_1-1000., pfl.z, color='k', alpha=0.3)
    axs[3].plot(np.sqrt(pfl.N2_ref)*1000., pfl.z, color='k', alpha=0.3)
    axs[4].plot(pfl.U_abs*100., pfl.zef, color='k', alpha=0.3)
    axs[5].plot(pfl.V_abs*100., pfl.zef, color='k', alpha=0.3)
    axs[6].plot(pfl.Ww*100., pfl.z, color='k', alpha=0.3)

axs[0].plot(T_mean, z_mean, color='r')
axs[1].plot(S_mean, z_mean, color='r')
axs[2].plot(rho_1_mean-1000., z_mean, color='r')
axs[3].plot(np.sqrt(N2_ref_mean)*1000., z_mean, color='r')
axs[4].plot(U_abs_mean*100., z_mean, color='r')
axs[5].plot(V_abs_mean*100., z_mean, color='r')
axs[6].plot(Ww_mean*100., z_mean, color='r')

xlabels = ['$T$ ($^\circ$C)', '$S$ (-)', '$\sigma_1$ (kg m$^{-3}$)',
           '$N$ (10$^{-3}$ rad s$^{-1}$)', '$u$ (cm s$^{-1}$)',
           '$v$ (cm s$^{-1}$)', '$w$ (cm s$^{-1}$)']

for ax, xlabel in zip(axs, xlabels):
    ax.set_xticks(ax.get_xticks()[::2])
    ax.set_xlabel(xlabel)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation='vertical')
# TODO: Plot mean profiles too!

# Why is this necessary...? I don't know but it has to be done.
axs[0].ticklabel_format(useOffset=False)
plt.tight_layout()

pf.my_savefig(fig, 'both', 'upstream', sdir, fsize='double_col')

# The average flow properties below
z_max = -300.
N_mean = np.nanmean(np.hstack([np.sqrt(pfl.N2_ref)[pfl.z < z_max]
                               for pfl in pfls]))
U_mean = np.nanmean(np.hstack([pfl.U_abs[pfl.zef < z_max] for pfl in pfls]))
V_mean = np.nanmean(np.hstack([pfl.V_abs[pfl.zef < z_max] for pfl in pfls]))
W_mean = np.nanmean(np.hstack([pfl.Ww[pfl.z < z_max] for pfl in pfls]))

print("Mean buoyancy frequency below {:1.0f} m is {:.2E} rad s-1. "
      "The period is {:1.1f} min.".format(z_max, N_mean, 2*np.pi/(60*N_mean)))
print("Mean zonal speed below {:1.0f} m is {:1.2f} m s-1.".format(z_max,
      U_mean))
print("Mean meridional speed below {:1.0f} m is {:1.2f} m s-1.".format(z_max,
      V_mean))
print("Mean vertical speed below {:1.0f} m is {:1.2f} m s-1.".format(z_max,
      W_mean))


# %% Sections in mountain centered coords.

bwr = plt.get_cmap('bwr')
bwr1 = mcolors.LinearSegmentedColormap.from_list(name='red_white_blue',
                                                 colors=[(0, 0, 1),
                                                         (1, 1, 1),
                                                         (1, 0, 0)],
                                                 N=9)
E76_hpids = np.arange(22, 42) # np.arange(31, 33)
E77_hpids = np.arange(17, 37) # np.arange(26, 28)
vars = ['Ww']#, 'U_abs', 'V_abs']
zvars = ['z']#, 'zef', 'zef']
dvars = ['dist_ctd']#, 'dist_ef', 'dist_ef']
texvars = ['$w$']#, '$U$', '$V$']
clims = [(-10., 10.)]#, (-100., 100.), (-100, 100.)]

var_1_vals = np.linspace(-40., 40., 80)
var_2_vals = np.linspace(-1500, 0, 500)
Xg, Zg = np.meshgrid(var_1_vals, var_2_vals)

Wgs = []
ds = []
zs = []

fig = plt.figure(figsize=(7, 5))

for Float, hpids in zip([E76, E77], [E76_hpids, E77_hpids]):

    __, idxs = Float.get_profiles(hpids, ret_idxs=True)

    for var, zvar, dvar, texvar, clim in zip(vars, zvars, dvars, texvars,
                                             clims):

        V = getattr(Float, var)[:, idxs].flatten(order='F')
        z = getattr(Float, zvar)[:, idxs].flatten(order='F')
        d = getattr(Float, dvar)[:, idxs].flatten(order='F')
        zs.append(z.copy())

        tgps = getattr(Float, 'UTC_start')[idxs]
        lon = getattr(Float, 'lon_start')[idxs]
        lat = getattr(Float, 'lat_start')[idxs]
        tctd = getattr(Float, 'UTC')[:, idxs].flatten(order='F')
        nans = np.isnan(d) | np.isnan(tctd)
        tctd = tctd[~nans]
        dctd = d[~nans]
        lonctd = np.interp(tctd, tgps, lon)
        latctd = np.interp(tctd, tgps, lat)
        bathy = sandwell.interp_track(lonctd, latctd, bf)

        d -= dctd[bathy.argmax()]
        ds.append(d.copy())

        nans = np.isnan(d) | np.isnan(z) | np.isnan(V)

#        Wg = griddata((d[~nans], z[~nans]), V[~nans], (Xg, Zg), method='linear')
#        Wgs.append(Wg.copy())

        dctd -= dctd[bathy.argmax()]

        thin = 10
        plt.scatter(d[::thin], z[::thin], s=50, c=V[::thin]*100.,
                    edgecolor='none', cmap=bwr1)


cbar = plt.colorbar(orientation='horizontal', extend='both')
cbar.set_label(texvar+' (cm s$^{-1}$)')
plt.clim(*clim)

plt.xlim(np.nanmin(d), np.nanmax(d))
plt.xlabel('Distance from ridge (km)')
plt.ylabel('$z$ (m)')
#title_str = ("Float {}").format(Float.floatID)
#plt.title(title_str)

plt.fill_between(dctd[::100], bathy[::100], np.nanmin(bathy), color='black',
                 linewidth=2)
plt.ylim(np.nanmin(bathy), np.nanmax(z))

plt.grid()

pf.my_savefig(fig, 'both', 'w_section', sdir, fsize='double_col')


# %% Wave profiles

E76_hpids = [30, 31, 32, 33]
E77_hpids = [25, 26, 27, 28]

pfls = np.hstack((E76.get_profiles(E76_hpids), E77.get_profiles(E77_hpids)))

fig, axm = plt.subplots(len(pfls), 5, sharey='row', sharex='col',
                        figsize=(14, 20))
fig.subplots_adjust(hspace=0.05, wspace=0.1)
rot = 'vertical'
col = 'black'
deg = 1

U_var = 'U'
V_var = 'V'

for pfl, axs in zip(pfls, axm):

    axs[0].set_ylabel('$z$ (m)')
    axs[0].plot(100.*utils.nan_detrend(pfl.zef, getattr(pfl, U_var), deg), pfl.zef, col)
    axs[0].plot(100.*getattr(pfl, U_var), pfl.zef, 'grey')
    axs[0].plot(100.*utils.nan_polyvalfit(pfl.zef, getattr(pfl, U_var), deg), pfl.zef, 'grey')
    axs[1].plot(100.*utils.nan_detrend(pfl.zef, getattr(pfl, V_var), deg), pfl.zef, col)
    axs[1].plot(100.*getattr(pfl, V_var), pfl.zef, 'grey')
    axs[1].plot(100.*utils.nan_polyvalfit(pfl.zef, getattr(pfl, V_var), deg), pfl.zef, 'grey')
    axs[2].plot(100.*pfl.Ww, pfl.z, col)
    axs[3].plot(10000.*pfl.b, pfl.z, col)
    axs[4].plot((pfl.dist_ctd - np.nanmin(pfl.dist_ctd)), pfl.z, col)
    axs[4].annotate("Float {}\nhpid {}".format(pfl.floatID, pfl.hpid[0]),
                    (0.5, -200))

    for ax in axs:
        ax.vlines(0., *ax.get_ylim())
        ax.grid()

for ax in axm[-1, :]:
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=rot)

axm[-1, 0].set_xlabel('$u$ (cm s$^{-1}$)')
axm[-1, 0].set_xlim(-30, 80)
axm[-1, 1].set_xlabel('$v$ (cm s$^{-1}$)')
axm[-1, 1].set_xlim(-30, 30)
axm[-1, 2].set_xlabel('$w$ (cm s$^{-1}$)')
axm[-1, 3].set_xlabel('$b$ ($10^{-4}$ m s$^{-2}$)')
axm[-1, 4].set_xlabel('$x$ (km)')
#pf.my_savefig(fig, 'both', 'all_profiles', sdir, fsize='double_col')

# %% Topography
# ----------

# Number of half profiles.
N = 15
N0_76 = 25
N0_77 = 20
hpids = np.empty((N, 2))
hpids[:, 0] = np.arange(N0_76, N0_76+N)
hpids[:, 1] = np.arange(N0_77, N0_77+N)

lons = np.empty_like(hpids)
lats = np.empty_like(hpids)

for i, Float in enumerate([E76, E77]):
    __, idxs = Float.get_profiles(hpids[:, i], ret_idxs=True)
    lons[:, i] = Float.lon_start[idxs]
    lats[:, i] = Float.lat_start[idxs]

lons = lons.flatten(order='F')
lats = lats.flatten(order='F')
p = np.polyfit(lons, lats, 1)

llcrnrlon = np.nanmin(lons) - .02
llcrnrlat = np.nanmin(lats) - .02
urcrnrlon = np.nanmax(lons) + .02
urcrnrlat = np.nanmax(lats) + .02

lon_lat = np.array([llcrnrlon, urcrnrlon, llcrnrlat, urcrnrlat])

lon_grid, lat_grid, bathy_grid = sandwell.read_grid(lon_lat, bf)
bathy_grid[bathy_grid > 0] = 0

fig = plt.figure()
plt.plot(lons, lats, 'o')
plt.plot(lons, np.polyval(p, lons))
levels = np.arange(-4000, 0, 500)
CS = plt.contour(lon_grid, lat_grid, bathy_grid, 20,
                 cmap=plt.get_cmap('binary'), levels=levels)
plt.clabel(CS, inline=1, fontsize=8, fmt='%1.f')
plt.gca().ticklabel_format(useOffset=False)
plt.xlabel('Longitude')
plt.ylabel('Latitude')

llons = np.linspace(lons.min(), lons.max(), 50)
llats = np.polyval(p, llons)
dist = np.hstack((0, np.cumsum(utils.lldist(llons, llats))))
topo = sandwell.interp_track(llons, llats, bf)

pf.my_savefig(fig, 'both', 'line_over_topo', sdir, fsize='double_col')

fig = plt.figure()

plt.plot(dist, topo, 'r', linewidth=5)
plt.xlabel('Distance (km)')
plt.ylabel('$z$ (m)')
plt.grid()

z = np.linspace(*plt.ylim(), num=10)
xg, zg = np.meshgrid(dist, z)
tg = zg - np.max(topo)
levels = np.arange(-1000, 1, 100)
CS = plt.contour(xg, zg, tg, colors='k', levels=levels)
plt.clabel(CS, inline=1, fontsize=8, fmt='%1.f')

pf.my_savefig(fig, 'topo', 'section', sdir, fsize='double_col')

# %% Characteristics of the flow
# ---------------------------

# The inertial frequency...
lat_mean = np.mean(lats)
f = np.abs(gsw.f(lat_mean))
print("Mean inertial frequency at {:1.1f} degrees is {:.2E} rad s-1. "
      "The period is {:1.1f} hours.".format(lat_mean, f, 2*np.pi/(60*60*f)))

# - $N \approx 2.3 \times 10^{-3}$ rad s$^{-1}$. (Near bottom of profiles
# upstream of the ridge.)
# - $U \approx 0.3$ m s$^{-1}$. (Near bottom of profiles upstream of the
# ridge.)
# - $f \approx 1.2 \times 10^{-4}$ rad s$^{-1}$. (57 degrees south.)
# - $h_0 \approx 2 \times 10^3$ m (Ridge height.)
# - $L \approx 2 \times 10^4$ m (Ridge width.)
#
# Periods of motion.
#
# - Buoyancy period, $T_N \approx 50$ mins.
# - Inertial period, $T_f \approx 14$ hours.

N0 = 0.8e-3
N1 = 1.0e-3
U0 = 0.2
U1 = 0.4
f = 1.2e-4
h0 = 300.
h1 = 1.5e3
L0 = 2e3
L1 = 1e4

# Assuming waves generated have a frequency near N, the horizontal scale is...
L_N0 = 2*np.pi*U0/N1
L_N1 = 2*np.pi*U1/N0
print("Assuming that generated waves have a frequency near N then their "
      "horizontal wavelength should be of order {:1.0f} -- {:1.0f} m.".format(L_N0, L_N1))
# Not assuming this the appropriate frequency is...
om_L0 = 2*np.pi*U0/L1
om_L1 = 2*np.pi*U1/L0
print("Topographic and velocity scales suggest that their frequency is in the "
      "range {:.2E} -- {:.2E} rad s-1.".format(om_L0, om_L1))
Ro0 = U1/(f*L1)
Ro1 = U1/(f*L0)
print("The Rossby number for the flow given a range of length scales is "
      "between {} -- {}.".format(Ro0, Ro1))
Fr0 = U0/(N1*h1)
Fr1 = U1/(N0*h0)
print("The Froude number given a range of height scales is  between {:1.2f} "
      "-- {:1.2f}.".format(Fr0, Fr1))
print("Consequenctly the steepness parameter (1/Fr) is in the range {:1.1f} "
      "-- {:1.1f}.".format(1./Fr1, 1./Fr0))

hc0 = 2*np.pi*0.4*U0/N1
hc1 = 2*np.pi*0.4*U1/N0
print("The height of the obstacle that would have a steepness of 0.4 is "
      "either {:1.0f} m or {:1.0f} m.\n"
      "This depends on a factor of 2 pi and possibly another factor of 2 due "
      "to uncertainty in N.".format(hc0, hc1))
