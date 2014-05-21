# -*- coding: utf-8 -*-
"""
Created on Thu May 15 12:07:00 2014

@author: jc3e13
"""

import emapex
import vertical_velocity_model as vvm
import numpy as np
import plotting_functions as pf
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import os
import pickle

reload(vvm)
reload(pf)


def assess_vvm_fit(Float, save_id=''):
    """ """

    vfi = Float.__vfi
    hpids = vfi.hpids
    floatID = Float.floatID
    s = os.sep
    save_dir = '..'+s+'figures'+s+'vertical_velocity_analysis'

    # Histogram of vertical water velocity.
    Ww = Float.rWw.flatten(order='F')

    Ww_mean = np.nanmean(Ww)
    Ww_std = np.nanstd(Ww)

    plt.figure(figsize=(3, 3))
    bins = np.arange(-0.15, 0.155, 0.005)
    Ww_hist, bins, patches = plt.hist(Ww, bins=bins, histtype='stepfilled')
    plt.setp(patches, 'facecolor', 'b', 'alpha', 0.75)
    plt.xlim(np.min(bins), np.max(bins))
    plt.xlabel('$W_w$ (m s$^{-1}$)')
    title_str = ("Float {}, mean = {:1.2e} m s$^{{-1}}$, std = {:1.2e} "
                 "m s$^{{-1}}$").format(floatID, Ww_mean, Ww_std)
    plt.title(title_str)
    name = save_id + '_ww_histogram.pdf'
    fname = os.path.join(save_dir, name)
    plt.savefig(fname, format='pdf', bbox_inches='tight')

    # Time series of different velocity measures.
    hpid1 = hpids[0]

    plt.figure(figsize=(6, 3))
    N = 4
    time, Ww = Float.get_timeseries(np.arange(hpid1, hpid1+N), 'rWw')
    __, Wz = Float.get_timeseries(np.arange(hpid1, hpid1+N), 'rWz')
    __, Ws = Float.get_timeseries(np.arange(hpid1, hpid1+N), 'rWs')
    plt.plot(time, Ww)
    plt.plot(time, Wz)
    plt.plot(time, Ws)
    plt.ylabel('$W_w$, $W_f$, $W_s$ (m s$^{-1}$)')
    plt.xlabel('Time')
    title_str = ("Float {}, half profiles {}").format(floatID, hpids[0:N])
    plt.title(title_str)
    plt.legend(['$W_w$', '$W_f$', '$W_s$'])
    name = save_id + '_ww_wf_w0_timeseries.pdf'
    fname = os.path.join(save_dir, name)
    plt.savefig(fname, format='pdf', bbox_inches='tight')
    # Distance section of water velocity.

#    dist_section(Float, np.arange(1, 1000), 'rWw')
#    plt.xlabel('Distance (km)')
#    plt.ylabel('Depth (m)')
#    plt.xlim(np.min(Float.dist), np.max(Float.dist))
#    title_str = ("Float {}").format(floatID)
#    plt.title(title_str)
#    cbar = plt.colorbar(orientation='horizontal')
#    cbar.set_label('$W_w$ (m s$^{-1}$)')

    # Parameter estimates and correlations.

    pnames = ['$V_0$', '$CA$', r'$\alpha_p$', '$p_0$', r'$\alpha_k$', '$k_0$',
              '$M$']
    N = len(pnames)
    ticks = np.arange(0.5, N, 1)
    plt.figure(figsize=(3, 3))
    plt.pcolormesh(vfi.pcorr, cmap=plt.get_cmap('PiYG'))
    cbar = plt.colorbar()
    cbar.set_label('Correlation')
    plt.clim(-1, 1)
    plt.xticks(ticks, pnames)
    plt.yticks(ticks, pnames)
    title_str = ("Float {}").format(floatID)
    plt.title(title_str)
    name = save_id + '_param_corr.pdf'
    fname = os.path.join(save_dir, name)
    plt.savefig(fname, format='pdf', bbox_inches='tight')

    plt.figure(figsize=(7, 7))
    pps = pd.DataFrame(vfi.ps, columns=pnames)
    axs = pd.tools.plotting.scatter_matrix(pps, hist_kwds={'bins': 12})
    formatter = ticker.ScalarFormatter(useOffset=False)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-1, 2))

    for i in xrange(N):
        for j in xrange(N):

            axs[i, j].xaxis.set_major_formatter(formatter)
            axs[i, j].yaxis.set_major_formatter(formatter)

            if i == j:
                y = np.array(axs[i, j].get_ylim())
                x = np.array([vfi.p[i], vfi.p[i]])
                axs[i, j].plot(x, y, 'r-')
                x = np.array([vfi.params0[i], vfi.params0[i]])
                axs[i, j].plot(x, y, 'g-')

    name = save_id + '_param_matrix_scatter.pdf'
    fname = os.path.join(save_dir, name)
    plt.savefig(fname, format='pdf', bbox_inches='tight')

#    fig, axs = plt.subplots(N, N)#, sharex='col', sharey='row')
#    for i in xrange(N):
#        for j in xrange(N):
#            if i == j:
#                dat, bins, patches = axs[i, j].hist(vfi.ps[:, i])
#                plt.setp(patches, 'facecolor', 'b', 'alpha', 0.75)
#                axs[i, j].set_xlim(np.min(bins), np.max(bins))
#            else:
#                axs[i, j].scatter(vfi.ps[:, i], vfi.ps[:, j])
#
#            if i == N-1:
#                axs[i, j].set_xlabel(pnames[j])
#
#            if j == 0:
#                axs[i, j].set_ylabel(pnames[i])

    plt.draw()
    plt.show()

    name = save_id + '_fit_info.p'
    fname = os.path.join(save_dir, name)
    with open(fname, 'wb') as f:
        pickle.dump(vfi, f)

try:
    print("Floats {} and {}.".format(E76.floatID, E77.floatID))
except NameError:
    E76 = emapex.EMApexFloat('../../data/EM-APEX/allprofs11.mat', 4976)
    E77 = emapex.EMApexFloat('../../data/EM-APEX/allprofs11.mat', 4977)


model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [None, None, None, None, None, None, None]
vvm.fitter(E76, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E76, str(E76.floatID))
print(E76.__vfi.p)

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [None, None, None, None, None, None, None]
vvm.fitter(E77, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E77, str(E77.floatID))
print(E77.__vfi.p)

###############################################################################

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [None, None, None, None, 1.156e-6, None, 27.179]
vvm.fitter(E76, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E76, str(E76.floatID)+'_fix_alphakM')
print(E76.__vfi.p)

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [None, None, None, None, 1.156e-6, None, 27.179]
vvm.fitter(E77, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E77, str(E77.floatID)+'_fix_alphakM')
print(E77.__vfi.p)

###############################################################################

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [3e-2, None, None, None, None, 16., 27.179]
vvm.fitter(E76, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E76, str(E76.floatID)+'_fix_k0V0M')
print(E76.__vfi.p)

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [3e-2, None, None, None, None, 16., 27.179]
vvm.fitter(E77, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E77, str(E77.floatID)+'_fix_k0V0M')
print(E77.__vfi.p)

###############################################################################

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [None, None, None, None, 1.156e-6, 16., 27.179]
vvm.fitter(E76, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E76, str(E76.floatID)+'_fix_alphakk0M')
print(E76.__vfi.p)

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [None, None, None, None, 1.156e-6, 16., 27.179]
vvm.fitter(E77, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E77, str(E77.floatID)+'_fix_alphakk0M')
print(E77.__vfi.p)

###############################################################################

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [3e-2, None, 3.76e-6, None, 1.156e-6, 16., 27.179]
vvm.fitter(E76, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E76, str(E76.floatID)+'_fix_alphakk0V0alphapM')
print(E76.__vfi.p)

model = '1'
cf_key = 'diffsq'
params0 = np.array([3e-2, 5e-2, 3e-6, 4e+2, 1e-6, 16., 27.179])
fixed = [3e-2, None, 3.76e-6, None, 1.156e-6, 16., 27.179]
vvm.fitter(E77, params0, fixed, model=model, profiles='all', cf_key=cf_key)
assess_vvm_fit(E77, str(E77.floatID)+'_fix_alphakk0V0alphapM')
print(E77.__vfi.p)
