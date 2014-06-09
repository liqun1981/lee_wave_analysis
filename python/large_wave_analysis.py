# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 16:48:46 2014

@author: jc3e13
"""

import scipy.signal as sig
import scipy.optimize as op
import matplotlib.pyplot as plt
import pylab as pyl
import numpy as np
import emapex
import pickle


try:

    print("Floats {} and {}.".format(E76.floatID, E77.floatID))

except NameError:
    
    reload(emapex)

    E76 = emapex.EMApexFloat('../../data/EM-APEX/allprofs11.mat', 4976)
    E76.apply_w_model('../../data/EM-APEX/4976_fix_p0k0M_fit_info.p')

    E77 = emapex.EMApexFloat('../../data/EM-APEX/allprofs11.mat', 4977)
    E77.apply_w_model('../../data/EM-APEX/4977_fix_p0k0M_fit_info.p')

    for Float, fstr in zip([E76, E77], ['76', '77']):
        with open('../../data/EM-APEX/49'+fstr+'_N2_ref_100dbar.p', 'rb') as f:
            N2_ref = pickle.load(f)
            setattr(Float, 'N2_ref', N2_ref)
            setattr(Float, 'strain_z', (Float.N2 - N2_ref)/N2_ref)
            Float.update_profiles()


def plane_wave(x, A, k, phase, C):
    return A*np.cos*(2*np.pi(k*x + phase)) + C

dz = 5.
dk = 1./dz

E76_hpids = np.arange(27, 34)
E77_hpids = np.arange(23, 30)

var_names = ['rWw']  #['rU_abs', 'rV_abs', 'rWw']

for Float, hpids in zip([E76, E77], [E76_hpids, E77_hpids]):

    for pfl in Float.get_profiles(hpids):

        z = getattr(pfl, 'rz')

        for name in var_names:

            var = getattr(pfl, name)
            N = var.size

            # Try fitting plane wave.
            popt, __ = op.curve_fit(plane_wave, z, var, 
                                    p0=[0.1, 0.01, np.pi, 0.])
            mfit = popt[1]
            
            plt.figure()
            plt.subplot(1, 2, 1)            
            
            plt.plot(var, z, plane_wave(z, *popt), z)
            plt.xticks(rotation=45)
            plt.xlabel('$W_w$ (m s$^{-1}$)')
            plt.ylabel('$z$ (m)')
            title = ("{}: Float {}, profile {}\nm_fit {:1.2e} m$^{{-1}}$"
                     "\nlambda_fit {:4.0f} m"
                     "").format(name, Float.floatID, pfl.hpid, mfit, 1./mfit)
            plt.title(title)
            print(title)

            plt.subplot(1, 2, 2)
            # Try calculating power spectral density.
            Pzz, ms = plt.psd(var, NFFT=N//2, Fs=dk,
                              noverlap=int(0.2*N//2),
                              detrend=pyl.detrend_linear)
            mmax = ms[Pzz.argmax()]
            title = ("{}: Float {}, profile {}\nm_max {:1.2e} m$^{{-1}}$"
                     "\nlambda_max {:4.0f} m"
                     "").format(name, Float.floatID, pfl.hpid, mmax, 1./mmax)
            ylim = plt.ylim()
            plt.plot(2*[mmax], ylim, 'r', 2*[mfit], ylim, 'g')
            plt.title(title)
            plt.xlabel('$m$ (m$^{-1}$)')
            print(title)
