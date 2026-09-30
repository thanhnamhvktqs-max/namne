"""Phan 4: chay bo sung de dien kin cac o bang (moi hang co du chi tieu)."""
import sys, copy, pickle
import numpy as np
sys.path.insert(0, '.')
import gsim
import common as C

E = C.exc(); T = E['T']; wd = E['wd']; L = E['log']; tu = L['tu']
cfgL = dict(gsim.LADDER)
R4 = {}
DT = C.DT
mmW = (T >= C.WIN[0]) & (T < C.WIN[1])


def band(x, f1=10, f2=30):
    x = x - x.mean(); X = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), DT)
    return float(np.sum(X[(f >= f1) & (f <= f2)]) / np.sum(X) * 100)


# ---- Bang 3.4: moi he so chay du ba bai thu (bac thang, toc do khong doi, dai 10-30 Hz)
sweep = {'yaw': {'Kpt': [6.0, 9.5, 13.0], 'Kpw': [0.25, 0.28, 0.40], 'Kiw': [0.0, 0.5, 1.0]},
         'pitch': {'Kpt': [20.0, 38.0, 50.0], 'Kpw': [0.10, 0.15, 0.25], 'Kiw': [0.0, 0.5, 1.0]}}
A = {'yaw': 5.0, 'pitch': 3.0}
Ts = np.arange(0, 2.5, DT); Tk = np.arange(0, 5.0, DT)
base_c = gsim.config(**cfgL['cascade'])
full = {}
for ax in gsim.AX:
    full[ax] = {}
    for par, vals in sweep[ax].items():
        full[ax][par] = []
        for v in vals:
            g = copy.deepcopy(gsim.GAINS_FINAL); g[ax][par] = v
            c = dict(base_c); c['gains'] = g
            ref = {a: np.where(Ts >= 0.5, A[a], 0.0) for a in gsim.AX}
            r = gsim.simulate(c, Ts, {a: np.zeros_like(Ts) for a in gsim.AX}, theta_ref=ref, plant=gsim.PLANT, seed=3)
            sm = C.step_metrics(Ts, A[ax] - r[ax]['e'], A[ax], 0.5)
            w = np.where(Tk >= 1.0, 8.0, 0.0)
            r = gsim.simulate(c, Tk, {a: (w if a == ax else np.zeros_like(Tk)) for a in gsim.AX}, plant=gsim.PLANT, seed=3)
            e = r[ax]['e']; mm = Tk >= 1.0
            sm['Je'] = float(np.sum(np.abs(e[mm])) * DT)
            r = gsim.simulate(gsim.config(gains=g), T, wd, plant=gsim.PLANT, seed=1)
            sm['band'] = band(r[ax]['e'][mmW])
            sm['v'] = v
            full[ax][par].append(sm)
            print(ax, par, v, {k: round(x, 3) for k, x in sm.items()})
R4['cascade_full'] = full

# ---- Bang 3.2: giu tinh voi mo hinh danh dinh
cal0 = copy.deepcopy(gsim.CAL); cal0['yaw']['dscale'] = 0.0; cal0['pitch']['dscale'] = 0.0
Th = np.arange(0, 6.0, DT)
rh = gsim.simulate(gsim.config(**cfgL['hoan_thien']), Th, {a: np.zeros_like(Th) for a in gsim.AX},
                   plant=gsim.PLANT, cal=cal0, seed=5)
R4['nom_hold'] = {}
for ax in gsim.AX:
    e = rh[ax]['e'][Th > 2][::10]
    R4['nom_hold'][ax] = float(np.std(e))
print('nom hold', R4['nom_hold'])

# ---- Bang 3.8: bai thu mau IMU2 loi cho gioi han co dinh 165
Tg = np.arange(0, 1.2, DT)
acc = {ax: [] for ax in gsim.AX}
for s in range(1, 7):
    c = gsim.config(**cfgL['gioi_han']); c.update(limit='fixed', umax_fixed=165.0); c['glitch'] = (250, 253, 600.0)
    r = gsim.simulate(c, Tg, {a: np.zeros_like(Tg) for a in gsim.AX}, plant=gsim.PLANT_REPLAY, seed=s)
    for ax in gsim.AX:
        acc[ax].append((np.abs(r[ax]['e'][240:]).max(), np.abs(r[ax]['u']).max()))
R4['glitch165'] = {ax: dict(epk=float(np.mean([a[0] for a in acc[ax]])), upk=float(np.mean([a[1] for a in acc[ax]]))) for ax in gsim.AX}
print('glitch165', R4['glitch165'])

# ---- Bang 3.14: toc do khung mang quanh cac lan doi chieu (+-0,3 s)
mlog = C.log_mask(*C.WIN); t_l = tu[mlog]
R4['rev_w'] = {}
for ax in gsim.AX:
    w_l = np.interp(t_l, T, wd[ax])
    pk, idx = C.reversal_events(t_l, w_l, E['elog'][ax][mlog])
    n = int(0.3 / np.median(np.diff(t_l)))
    seg = np.concatenate([w_l[max(0, i - n):i + n] for i in idx])
    R4['rev_w'][ax] = dict(rms=float(np.sqrt(np.mean(seg ** 2))), peak=float(np.mean([np.abs(w_l[max(0, i - n):i]).max() for i in idx])))
print('rev_w', R4['rev_w'])
pickle.dump(R4, open('results4.pkl', 'wb'))
print('xong')
