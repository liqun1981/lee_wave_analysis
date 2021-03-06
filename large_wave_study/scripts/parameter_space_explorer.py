# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 14:43:24 2014

@author: jc3e13
"""

import os
import glob
import itertools
import pickle
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
# from matplotlib.colors import LogNorm
# from matplotlib.ticker import LogFormatterMathtext

import emapex
import float_advection_routines as far
import utils
import gravity_waves as gw


try:
    print("Floats {} and {} exist!.".format(E76.floatID, E77.floatID))
except NameError:
    E76 = emapex.load(4976)
    E77 = emapex.load(4977)

# %% Script params.

# Bathymetry file path.
bf = os.path.abspath(glob.glob('/noc/users/jc3e13/storage/smith_sandwell/topo_*.img')[0])
# Figure save path.
sdir = '../figures/parameter_space_explorer'
if not os.path.exists(sdir):
    os.makedirs(sdir)
# Universal figure font size.
matplotlib.rc('font', **{'size': 9})

# %% ##########################################################################

# Parameters to check.
Xs = np.arange(-10000., 11000., 1000.)
Ys = np.arange(-10000., 11000., 1000.)
Zs = np.arange(-6000., 6500., 500.)
Phases = np.linspace(0., 2.*np.pi, 10)

params = far.default_params
params['z_0'] = -1600.
pfl = E76.get_profiles(32)
use = ~np.isnan(pfl.zef) & (pfl.zef < -400.)
bscale = 250.

zf = pfl.zef[use]
uf = pfl.interp(zf, 'zef', 'U_abs')
vf = pfl.interp(zf, 'zef', 'V_abs')
wf = pfl.interp(zf, 'zef', 'Ww')
bf = bscale*pfl.interp(zf, 'z', 'b')

ps = []
cost = []

for LX, LY, LZ, Phase in itertools.product(Xs, Ys, Zs, Phases):

    ps.append((LX, LY, LZ, Phase))

    if LX == 0. or LY == 0. or LZ == 0.:
        cost.append(1e10)
        continue

    X = far.model_verbose(LX, LY, LZ, Phase, params)

    um = np.interp(zf, X.r[:, 2], X.u[:, 0])
    vm = np.interp(zf, X.r[:, 2], X.u[:, 1])
    wm = np.interp(zf, X.r[:, 2], X.u[:, 2])
    bm = bscale*np.interp(zf, X.r[:, 2], X.b)

    c = np.std(um - uf) + np.std(vm - vf) + np.std(wm - wf) + np.std(bm - bf)
    cost.append(c)

    print(LX, LY, LZ, Phase, c)

with open('pfl32_param_search_cost.p', 'wb') as f:
    pickle.dump(c, f)

with open('pfl32_param_search_params.p', 'wb') as f:
    pickle.dump(ps, f)


# %% Search using cost determined by fit to data


def w_model(params, data):

    X, Y, Z, phase_0 = params

    time, dist, depth, U, V, W, B, N, f = data

    k = 2*np.pi/X
    l = 2*np.pi/Y
    m = 2*np.pi/Z

    om = gw.omega(N, k, m, l, f)
    phi_0 = np.max(W)*(N**2 - f**2)*m/(om*(k**2 + l**2 + m**2))

    w = gw.w(dist, 0., depth, time, phi_0, k, l, m, om, N, phase_0=phase_0)

    return w - W


def u_model(params, data):

    X, Y, Z, phase_0 = params

    time, dist, depth, U, V, W, B, N, f = data

    k = 2*np.pi/X
    l = 2*np.pi/Y
    m = 2*np.pi/Z

    om = gw.omega(N, k, m, l, f)
    phi_0 = np.max(W)*(N**2 - f**2)*m/(om*(k**2 + l**2 + m**2))

    u = gw.u(dist, 0., depth, time, phi_0, k, l, m, om, phase_0=phase_0)

    return u - U


def v_model(params, data):

    X, Y, Z, phase_0 = params

    time, dist, depth, U, V, W, B, N, f = data

    k = 2*np.pi/X
    l = 2*np.pi/Y
    m = 2*np.pi/Z

    om = gw.omega(N, k, m, l, f)
    phi_0 = np.max(W)*(N**2 - f**2)*m/(om*(k**2 + l**2 + m**2))

    v = gw.v(dist, 0., depth, time, phi_0, k, l, m, om, phase_0=phase_0)

    return v - V


def b_model(params, data):

    X, Y, Z, phase_0 = params

    time, dist, depth, U, V, W, B, N, f = data

    k = 2*np.pi/X
    l = 2*np.pi/Y
    m = 2*np.pi/Z

    om = gw.omega(N, k, m, l, f)
    phi_0 = np.max(W)*(N**2 - f**2)*m/(om*(k**2 + l**2 + m**2))

    b = gw.b(dist, 0., depth, time, phi_0, k, l, m, om, N, phase_0=phase_0)

    resid = b - B

    return 250.*resid


def full_model(params, data):
    return np.hstack((w_model(params, data),
                      u_model(params, data),
                      v_model(params, data),
                      b_model(params, data)))


# Previously this looked like E76.get_timeseries([31, 32], ) etc. and the below
# bits of code were uncommented.

time, depth = E76.get_timeseries([31, 32], 'z')
__, dist = E76.get_timeseries([31, 32], 'dist_ctd')
timeef, U = E76.get_timeseries([31, 32], 'U')
__, V = E76.get_timeseries([31, 32], 'V')
__, W = E76.get_timeseries([31, 32], 'Ww')
__, B = E76.get_timeseries([31, 32], 'b')
__, N2 = E76.get_timeseries([31, 32], 'N2_ref')

t_split = E76.get_profiles(31).UTC_end

nope = depth > -600.

time = time[~nope]
dist = dist[~nope]
depth = depth[~nope]
W = W[~nope]
B = B[~nope]

N = np.nanmean(np.sqrt(N2))
f = gsw.f(-57.5)

Unope = np.isnan(U)

timeef = timeef[~Unope]
U = U[~Unope]
V = V[~Unope]

U = np.interp(time, timeef, U)
V = np.interp(time, timeef, V)

U[time > t_split] = utils.nan_detrend(depth[time > t_split], U[time > t_split], 2)
U[time < t_split] = utils.nan_detrend(depth[time < t_split], U[time < t_split], 2)
U[U > 0.3] = 0.

V[time > t_split] = utils.nan_detrend(depth[time > t_split], V[time > t_split], 2)
V[time < t_split] = utils.nan_detrend(depth[time < t_split], V[time < t_split], 2)

#U = utils.nan_detrend(depth, U, 2)
#V = utils.nan_detrend(depth, V, 2)

time *= 60.*60.*24
dist *= 1000.
time -= np.min(time)
dist -= np.min(dist)

data = [time, dist, depth, U, V, W, B, N, f]


ps = []
cost = []
Xs = np.arange(-40000., 0., 500.)
Ys = np.arange(-40000., 0., 500.)
Zs = np.arange(-6000., 0., 200.)
Phases = np.linspace(0., 2.*np.pi, 10)

for LX, LY, LZ, Phase in itertools.product(Xs, Ys, Zs, Phases):

    ps.append((LX, LY, LZ, Phase))

    if LX == 0. or LY == 0. or LZ == 0.:
        cost.append(1e10)
        continue

    params = [LX, LY, LZ, Phase]

    c = np.sum(full_model(params, data)**2)
    cost.append(c)

#    print(LX, LY, LZ, Phase, c)

cost = np.asarray(cost)

with open('pfl3132_param_search_cost.p', 'wb') as f:
    pickle.dump(cost, f)

with open('pfl3132_param_search_params.p', 'wb') as f:
    pickle.dump(ps, f)
