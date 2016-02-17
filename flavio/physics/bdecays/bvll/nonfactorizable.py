import flavio
import numpy as np
from flavio.classes import AuxiliaryQuantity, Implementation
from flavio.physics.bdecays.common import meson_quark
from flavio.physics.bdecays.wilsoncoefficients import wctot_dict
from flavio.physics.common import conjugate_par, conjugate_wc, add_dict

r"""Functions for spectator scattering corrections to $B\to V\ell^+\ell^-$ decays.

This includes weak annihilation, chromomagnetic contributions, and light
quark-loop spectator scattering.
"""


# Auxiliary quantities and implementations

# function needed for the QCD factorization implementation (see qcdf.py)
def ha_qcdf_function(B, V, lep):
    scale = flavio.config.config['renormalization scale']['bvll']
    label = meson_quark[(B,V)] + lep + lep # e.g. bsmumu, bdtautau
    def function(wc_obj, par_dict, q2, cp_conjugate):
        par = par_dict.copy()
        if cp_conjugate:
            par = conjugate_par(par)
        wc = wctot_dict(wc_obj, label, scale, par)
        if cp_conjugate:
            wc = conjugate_wc(wc)
        flavio.physics.bdecays.bvll.qcdf.helicity_amps_qcdf(q2, wc, par_dict, B, V, lep)
    return function

# loop over hadronic transitions and lepton flavours
# BTW, it is not necessary to loop over tau: for tautau final states, the minimum
# q2=4*mtau**2 is so high that QCDF is not valid anymore anyway!
for had in [('B0','K*0'), ('B+','K*+'), ('B0','rho0'), ('B+','rho+'), ('Bs','phi'), ]:
    for l in ['e', 'mu', ]:
        process = had[0] + '->' + had[1] + l+l # e.g. B0->K*0mumu
        quantity = process + ' spectator scattering'
        a = AuxiliaryQuantity(name=quantity, arguments=['q2', 'cp_conjugate'])
        a.description = ('Contribution to ' + process + ' helicity amplitudes from'
                        'non-factorizable spectator scattering.')

        # Implementation: QCD factorization
        iname = process + ' QCDF'
        i = Implementation(name=iname, quantity=quantity,
                       function=ha_qcdf_function(B=had[0], V=had[1], lep=l))
        i.set_description("QCD factorization")