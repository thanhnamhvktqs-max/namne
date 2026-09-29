"""Phan 3: rang buoc cua K_pw (nhieu lenh, nang luong 10-30 Hz) va su kien dao chieu tren chuoi cau hinh."""
import sys, copy, pickle
import numpy as np
sys.path.insert(0, '.')
import gsim
import common as C

E = C.exc(); T = E['T']; wd = E['wd']; tu = E['log']['tu']
R3 = {}
mm = (T >= C.WIN[0]) & (T < C.WIN[1])


def band(x, f1=10, f2=30):
    x = x - x.mean(); X = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), C.DT)
    return float(np.sum(X[(f >= f1) & (f <= f2)]) / np.sum(X) * 100)


kpw = {}
Th = np.arange(0, 6.0, C.DT)
for ax, vals in [('yaw', [0.25, 0.28, 0.40, 0.60]), ('pitch', [0.10, 0.15, 0.25, 0.40])]:
    kpw[ax] = []
    for v in vals:
        g = copy.deepcopy(gsim.GAINS_FINAL); g[ax]['Kpw'] = v
        c = gsim.config(**dict(gsim.LADDER)['cascade']); c['gains'] = g
        rh = gsim.simulate(c, Th, {a: np.zeros_like(Th) for a in gsim.AX}, plant=gsim.PLANT, seed=5)
        uh = float(np.std(rh[ax]['u'][Th > 2]))
        c2 = gsim.config(gains=g)
        r = gsim.simulate(c2, T, wd, plant=gsim.PLANT, seed=1)
        m = C.replay_metrics(r, ax)
        kpw[ax].append(dict(v=v, u_hold=uh, erms=m['erms'], band=band(r[ax]['e'][mm]), iq=m['iqrms']))
        print(ax, v, round(uh, 4), round(m['erms'], 3), round(kpw[ax][-1]['band'], 2), round(m['iqrms'], 2))
R3['kpw'] = kpw

# su kien dao chieu tren chuoi cau hinh (mo phong tai hien, lay mau nhu log)
R = pickle.load(open('results.pkl', 'rb'))
mlog = C.log_mask(*C.WIN); t_l = tu[mlog]
rev = {}
for name, _ in gsim.LADDER:
    rev[name] = {}
    for ax in gsim.AX:
        e = np.interp(t_l, T, R['ladder_series'][name][ax]['e'])
        w_l = np.interp(t_l, T, wd[ax])
        pk, idx = C.reversal_events(t_l, w_l, e)
        rev[name][ax] = dict(mean=float(pk.mean()), max=float(pk.max()), n=len(pk))
    print(name, {ax: round(rev[name][ax]['mean'], 3) for ax in gsim.AX})
R3['rev_ladder'] = rev
pickle.dump(R3, open('results3.pkl', 'wb'))
print('xong')
