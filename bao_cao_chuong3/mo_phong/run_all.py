"""Chay toan bo mo phong cho Chuong 3 va luu ket qua (results.pkl)."""
import sys, copy, pickle, time
import numpy as np
sys.path.insert(0, '.')
import gsim, excite
import common as C

R = {}
E = C.exc(); T = E['T']; wd = E['wd']; L = E['log']; tu = L['tu']
cfgL = dict(gsim.LADDER)
t_all = time.time()


def cfg(name, **kw):
    c = gsim.config(**cfgL[name]); c.update(kw); return c


def keep_series(r, axes=gsim.AX, keys=('e', 'u', 'du', 'iq', 'zone', 'rev', 'sat')):
    return {ax: {k: r[ax][k].astype(np.float32) for k in keys} for ax in axes}


# ============================================================ 3.1.3 kiem chung
print('== kiem chung')
val = {}
m = C.log_mask(*C.WIN)
val['log'] = {ax: C.emet(E['elog'][ax][m]) for ax in gsim.AX}
val['log_seg'] = {ax: [C.emet(E['elog'][ax][C.log_mask(a, b)]) for a, b, _ in C.SEG] for ax in gsim.AX}
hm = C.log_mask(*C.HOLD)
val['log_hold'] = {ax: C.emet(E['elog'][ax][hm] - E['elog'][ax][hm].mean()) for ax in gsim.AX}
# kich thich theo doan
val['exc_seg'] = {ax: [dict(rms=float(np.sqrt(np.mean(wd[ax][(T >= a) & (T < b)] ** 2))),
                            peak=float(np.abs(wd[ax][(T >= a) & (T < b)]).max())) for a, b, _ in C.SEG]
                  for ax in gsim.AX}
val['exc_all'] = {ax: dict(rms=float(np.sqrt(np.mean(wd[ax][(T >= C.WIN[0]) & (T < C.WIN[1])] ** 2))),
                           peak=float(np.abs(wd[ax][(T >= C.WIN[0]) & (T < C.WIN[1])]).max())) for ax in gsim.AX}
fin = cfg('hoan_thien')
rv = C.run_replay(fin, keep=True)
val['sim'] = {ax: rv[ax] for ax in gsim.AX}
r1 = rv['_r']
val['sim_seg'] = {ax: [C.replay_metrics(r1, ax, a, b) for a, b, _ in C.SEG] for ax in gsim.AX}
rn = C.run_replay(fin, plant=gsim.PLANT, keep=False)
cal0 = copy.deepcopy(gsim.CAL); cal0['yaw']['dscale'] = 0.0; cal0['pitch']['dscale'] = 0.0
rn0 = C.run_replay(fin, plant=gsim.PLANT, cal=cal0)
val['sim_nom'] = {ax: rn0[ax] for ax in gsim.AX}
val['sim_nom_d'] = {ax: rn[ax] for ax in gsim.AX}
# giu tinh trong mo phong
Th = np.arange(0, 6.0, C.DT)
rh = gsim.simulate(fin, Th, {ax: np.zeros_like(Th) for ax in gsim.AX}, plant=gsim.PLANT_REPLAY, seed=5)
val['sim_hold'] = {}
for ax in gsim.AX:
    e = rh[ax]['e'][(Th > 2)][::10]
    val['sim_hold'][ax] = C.emet(e - e.mean())
R['val'] = val
R['series_final'] = keep_series(r1)
print('  sim', {ax: round(val['sim'][ax]['erms'], 3) for ax in gsim.AX}, 'log', {ax: round(val['log'][ax]['erms'], 3) for ax in gsim.AX})

# ============================================================ chuoi cau hinh tich luy (mo phong tai hien)
print('== chuoi cau hinh')
lad = {}; lad_series = {}
for name, kw in gsim.LADDER:
    out = C.run_replay(gsim.config(**kw), keep=True)
    lad_series[name] = keep_series(out.pop('_r'))
    lad[name] = out
    print('  ', name, {ax: round(out[ax]['erms'], 3) for ax in gsim.AX})
R['ladder'] = lad
R['ladder_series'] = lad_series

# ============================================================ BT1 bac thang, BT2 giu tinh cho moi cau hinh (mo phong tai hien)
print('== bac thang / giu tinh theo cau hinh')
Ts = np.arange(0, 2.5, C.DT)
A = {'yaw': 5.0, 'pitch': 3.0}
stepres = {}
for name, kw in gsim.LADDER[:2]:
    c = gsim.config(**kw)
    ref = {ax: np.where(Ts >= 0.5, A[ax], 0.0) for ax in gsim.AX}
    r = gsim.simulate(c, Ts, {ax: np.zeros_like(Ts) for ax in gsim.AX}, theta_ref=ref,
                      plant=gsim.PLANT_REPLAY, seed=3)
    stepres[name] = {}
    for ax in gsim.AX:
        y = A[ax] - r[ax]['e']
        sm = C.step_metrics(Ts, y, A[ax], 0.5)
        sm['umax'] = float(np.abs(r[ax]['u']).max())
        sm['y'] = y.astype(np.float32)
        stepres[name][ax] = sm
    rh = gsim.simulate(c, Th, {ax: np.zeros_like(Th) for ax in gsim.AX}, plant=gsim.PLANT_REPLAY, seed=5)
    for ax in gsim.AX:
        e = rh[ax]['e'][(Th > 2)][::10]
        stepres[name][ax]['hold'] = float(np.std(e))
R['step_ladder'] = stepres; R['Ts'] = Ts

# ============================================================ 3.2.1 khao sat cascade (mo hinh danh dinh)
print('== khao sat cascade')
sweep = {'yaw': {'Kpt': [6.0, 9.5, 13.0], 'Kpw': [0.25, 0.28, 0.40], 'Kiw': [0.0, 0.5, 1.0]},
         'pitch': {'Kpt': [20.0, 38.0, 50.0], 'Kpw': [0.10, 0.15, 0.25], 'Kiw': [0.0, 0.5, 1.0]}}
base_c = gsim.config(**cfgL['cascade'])
cas = {}
Tk = np.arange(0, 5.0, C.DT)
for ax in gsim.AX:
    cas[ax] = {}
    for par, vals in sweep[ax].items():
        cas[ax][par] = []
        for v in vals:
            g = copy.deepcopy(gsim.GAINS_FINAL); g[ax][par] = v
            c = dict(base_c); c['gains'] = g
            if par != 'Kiw':
                ref = {a: np.where(Ts >= 0.5, A[a], 0.0) for a in gsim.AX}
                r = gsim.simulate(c, Ts, {a: np.zeros_like(Ts) for a in gsim.AX}, theta_ref=ref,
                                  plant=gsim.PLANT, seed=3)
                y = A[ax] - r[ax]['e']
                sm = C.step_metrics(Ts, y, A[ax], 0.5)
                sm['umax'] = float(np.abs(r[ax]['u']).max()); sm['y'] = y.astype(np.float32)
            else:
                w = np.where(Tk >= 1.0, 8.0, 0.0)
                r = gsim.simulate(c, Tk, {a: (w if a == ax else np.zeros_like(Tk)) for a in gsim.AX},
                                  plant=gsim.PLANT, seed=3)
                e = r[ax]['e']; mm = Tk >= 1.0
                sm = dict(erms=float(np.sqrt(np.mean(e[mm] ** 2))), Je=float(np.sum(np.abs(e[mm])) * C.DT),
                          elast=float(np.mean(e[Tk >= 4.0])), umax=float(np.abs(r[ax]['u']).max()),
                          y=e.astype(np.float32))
            # bai thu tham chieu voi mo hinh danh dinh (chi phan hoi)
            rr = C.run_replay(c, seeds=(1,), plant=gsim.PLANT)
            sm['bt3_erms'] = rr[ax]['erms']
            sm['v'] = v
            cas[ax][par].append(sm)
            print('  ', ax, par, v, {k: round(sm[k], 3) for k in sm if k not in ('y', 'v')})
R['cascade'] = cas; R['Tk'] = Tk

# ============================================================ 3.2.2 khao sat luat he so bu (mo hinh danh dinh)
print('== khao sat he so bu')
opts = [('Không bù', dict(ff='none')), ('k₀ = 0,80', dict(ff='fixed', k0=0.80)),
        ('k₀ = 0,88', dict(ff='fixed', k0=0.88)), ('k₀ = 0,95', dict(ff='fixed', k0=0.95)),
        ('k(v) theo vùng', dict(ff='zone'))]
ffs = []
for lab, kw in opts:
    c = cfg('bu_imu2', **kw)
    out = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT, keep=True)
    r = out.pop('_r')
    # nhieu lenh khi dung yen (BT2): do lech chuan lenh
    rh = gsim.simulate(c, Th, {ax: np.zeros_like(Th) for ax in gsim.AX}, plant=gsim.PLANT, seed=5)
    for ax in gsim.AX:
        out[ax]['u_hold'] = float(np.std(rh[ax]['u'][Th > 2]))
        out[ax]['uff_hold'] = float(np.std(rh[ax]['uff'][Th > 2]))
        seg1 = C.replay_metrics(r, ax, 8.5, 29.5) if ax == 'yaw' else C.replay_metrics(r, ax, 29.5, 47.5)
        out[ax]['slow_erms'] = seg1['erms']
        seg2 = C.replay_metrics(r, ax, 70.5, 76.0) if ax == 'yaw' else C.replay_metrics(r, ax, 60.5, 70.5)
        out[ax]['fast_erms'] = seg2['erms']
    out['series'] = keep_series(r, keys=('e',))
    ffs.append((lab, out))
    print('  ', lab, {ax: (round(out[ax]['erms'], 3), round(out[ax]['u_hold'], 3)) for ax in gsim.AX})
R['ff_survey'] = ffs

# ============================================================ 3.2.3 khao sat khoang ngoai suy
print('== khao sat ngoai suy')
tps = [0.0, 0.004, 0.008, 0.012, 0.016, 0.020]
tpr = []
for tp in tps:
    c = cfg('ngoai_suy', tp=tp)
    out = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT, keep=True)
    r = out.pop('_r')
    for ax in gsim.AX:
        u = r[ax]['u']
        # nang luong lenh tan so cao (> 20 Hz)
        U = np.fft.rfft(u - u.mean()); f = np.fft.rfftfreq(len(u), C.DT)
        out[ax]['u_hf'] = float(np.sqrt(np.sum(np.abs(U[f > 20]) ** 2) / np.sum(np.abs(U) ** 2)) * 100)
    out['series'] = keep_series(r, keys=('e', 'u'))
    tpr.append((tp, out))
    print('  ', tp, {ax: (round(out[ax]['erms'], 3), round(out[ax]['emax'], 2), round(out[ax]['u_hf'], 2)) for ax in gsim.AX})
R['tp_survey'] = tpr

# ============================================================ 3.3.1 khao sat luat gioi han
print('== khao sat gioi han')
lims = [('Cố định 135 °/s', dict(limit='fixed', umax_fixed=135.0)),
        ('Cố định 165 °/s', dict(limit='fixed', umax_fixed=165.0)),
        ('Cố định 410 °/s', dict(limit='fixed', umax_fixed=410.0)),
        ('Theo vùng', dict(limit='zone'))]
limr = []
for lab, kw in lims:
    c = cfg('gioi_han', **kw)
    out = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT, keep=True)
    r = out.pop('_r')
    out['series'] = keep_series(r, keys=('e', 'u', 'sat'))
    limr.append((lab, out))
    print('  ', lab, {ax: (round(out[ax]['erms'], 3), round(out[ax]['emax'], 2), round(out[ax]['rho'], 2)) for ax in gsim.AX})
R['lim_survey'] = limr

# ============================================================ 3.3.2 khao sat dao chieu va dung
print('== khao sat dao chieu / dung')
revs = []
for t0 in [0.010, 0.020, 0.040]:
    for aR in [300.0, 1000.0]:
        c = cfg('dao_chieu', rev_t0=t0, rev_a=aR, stop=False)
        out = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT)
        revs.append(((t0, aR), out))
        print('  rev', t0, aR, {ax: (round(out[ax]['erms'], 3), round(out[ax]['emax'], 2), out[ax]['signchg']) for ax in gsim.AX})
c = cfg('gioi_han')
out = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT)
revs.append((('none', 0), out))
print('  rev none', {ax: (round(out[ax]['erms'], 3), round(out[ax]['emax'], 2), out[ax]['signchg']) for ax in gsim.AX})
R['rev_survey'] = revs
stops = []
for wb in [1.0, 2.0, 3.0]:
    c = cfg('dao_chieu', stop_wb=wb, rev=False)
    out = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT)
    stops.append((wb, out))
    print('  stop', wb, {ax: round(out[ax]['erms'], 3) for ax in gsim.AX})
R['stop_survey'] = stops

with open('results.pkl', 'wb') as f:
    pickle.dump(R, f)
print('xong', time.time() - t_all)
