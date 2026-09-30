"""Phan 2: tao dang lenh, lich RS485, bai thu dung, xung nhieu IMU2, su kien dao chieu."""
import sys, copy, pickle, time
import numpy as np
sys.path.insert(0, '.')
import gsim
import common as C

R = {}
E = C.exc(); T = E['T']; wd = E['wd']; L = E['log']; tu = L['tu']
cfgL = dict(gsim.LADDER)
t_all = time.time()


def cfg(name, **kw):
    c = gsim.config(**cfgL[name]); c.update(kw); return c


def band_energy(e, f1=10.0, f2=30.0):
    x = e - e.mean()
    X = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), C.DT)
    return float(np.sum(X[(f >= f1) & (f <= f2)]))


# ------------------------------------------------------------ tao dang lenh: khao sat
print('== tao dang')
shp = []
mm = (T >= C.WIN[0]) & (T < C.WIN[1])
for lab, kw in [('Không giới hạn', dict(shape=False)),
                ('18 000 °/s² cố định', dict(shape=True, amax=18000.0, amax_rev=18000.0)),
                ('30 000 °/s² cố định', dict(shape=True, amax=30000.0, amax_rev=30000.0)),
                ('18 000 / 30 000 °/s² khi đảo chiều', dict(shape=True, amax=18000.0, amax_rev=30000.0))]:
    c = cfg('tao_dang', **kw)
    out = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT, keep=True)
    r = out.pop('_r')
    for ax in gsim.AX:
        out[ax]['e_band'] = band_energy(r[ax]['e'][mm])
    shp.append((lab, out))
    print('  ', lab, {ax: (round(out[ax]['erms'], 3), round(out[ax]['dumax'], 1), round(out[ax]['iqrms'], 2)) for ax in gsim.AX})
b0 = {ax: shp[0][1][ax]['e_band'] for ax in gsim.AX}
for lab, out in shp:
    for ax in gsim.AX:
        out[ax]['e_band_pct'] = out[ax]['e_band'] / b0[ax] * 100
R['shape_survey'] = shp

# quy dao lenh khi doi +300 -> -300 deg/s qua khau tao dang (chi khau tao dang)
def shaper(u_req, amax, jmax=2.5e6):
    us = u_req[0]; us1 = us; out = []
    for u in u_req:
        a_prev = (us - us1) / C.DT
        a = np.clip((u - us) / C.DT, a_prev - jmax * C.DT, a_prev + jmax * C.DT)
        a = np.clip(a, -amax, amax)
        st = a * C.DT
        if (u - us) * st > 0 and abs(st) > abs(u - us):
            st = u - us
        us1 = us; us = us + st; out.append(us)
    return np.array(out)


Tc = np.arange(0, 0.12, C.DT)
ureq = np.where(Tc < 0.02, 300.0, -300.0)
R['shape_traj'] = dict(T=Tc, req=ureq, a18=shaper(ureq, 18000.0), a30=shaper(ureq, 30000.0))

# ------------------------------------------------------------ lich RS485: khao sat
print('== RS485')
rng = np.random.default_rng(11)
bus = {}
for mode in ('yawpri', 'alt'):
    ev = gsim.schedule(mode, 100.0, rng)
    bus[mode] = {}
    for ax in gsim.AX:
        s = np.array([a for a, b in ev[ax]]); d = np.array([b - a for a, b in ev[ax]])
        g = np.diff(s) * 1e3
        bus[mode][ax] = dict(med=float(np.median(g)), p99=float(np.percentile(g, 99)), mx=float(g.max()),
                             std=float(g.std()), rate=float(len(s) / 100.0), gaps=g.astype(np.float32),
                             txn_p99=float(np.percentile(d, 99) * 1e3), txn_max=float(d.max() * 1e3))
    print('  ', mode, {ax: (round(bus[mode][ax]['med'], 2), round(bus[mode][ax]['p99'], 2), round(bus[mode][ax]['mx'], 2), round(bus[mode][ax]['std'], 2)) for ax in gsim.AX})
busr = {}
for mode in ('yawpri', 'alt'):
    for tp in (0.008, 0.012, 0.016):
        c = cfg('tao_dang', bus=mode, tp=tp)
        busr[(mode, tp)] = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT)
        print('  ', mode, tp, {ax: round(busr[(mode, tp)][ax]['erms'], 3) for ax in gsim.AX})
R['bus_sched'] = bus; R['bus_closed'] = busr

# ------------------------------------------------------------ xung nhieu IMU2 (bao ve cua gioi han theo vung)
print('== xung nhieu IMU2')
Tg = np.arange(0, 1.2, C.DT)
gl = {}
for lab, kw in [('Cố định 135 °/s', dict(limit='fixed', umax_fixed=135.0)),
                ('Cố định 410 °/s', dict(limit='fixed', umax_fixed=410.0)),
                ('Theo vùng', dict(limit='zone'))]:
    acc = {ax: [] for ax in gsim.AX}
    for s in range(1, 7):
        c = cfg('gioi_han', **kw); c['glitch'] = (250, 253, 600.0)
        r = gsim.simulate(c, Tg, {a: np.zeros_like(Tg) for a in gsim.AX}, plant=gsim.PLANT_REPLAY, seed=s)
        for ax in gsim.AX:
            acc[ax].append((np.abs(r[ax]['e'][240:]).max(), np.abs(r[ax]['u']).max()))
        if s == 1:
            ser = {ax: dict(e=r[ax]['e'].astype(np.float32), u=r[ax]['u'].astype(np.float32)) for ax in gsim.AX}
    gl[lab] = {ax: dict(epk=float(np.mean([a[0] for a in acc[ax]])), upk=float(np.mean([a[1] for a in acc[ax]]))) for ax in gsim.AX}
    gl[lab]['series'] = ser
    print('  ', lab, {ax: (round(gl[lab][ax]['epk'], 3), round(gl[lab][ax]['upk'], 1)) for ax in gsim.AX})
R['glitch'] = gl; R['Tg'] = Tg

# ------------------------------------------------------------ bai thu dung dot ngot
print('== dung dot ngot')


def stop_profile(ax):
    v0 = {'yaw': 110.0, 'pitch': 85.0}[ax]
    Tq = np.arange(0, 2.6, C.DT); w = np.zeros_like(Tq)
    t1 = 0.2; t2 = t1 + v0 / 1500.0; t3 = t2 + 0.75; t4 = t3 + v0 / 2300.0
    w = np.where(Tq < t1, 0, np.where(Tq < t2, 1500 * (Tq - t1), np.where(Tq < t3, v0,
                 np.where(Tq < t4, v0 - 2300 * (Tq - t3), 0.0))))
    return Tq, w, t4


stp = {}
for lab, stop in [('Không xử lý dừng', False), ('Có chế độ dừng', True)]:
    stp[lab] = {}
    for ax in gsim.AX:
        Tq, w, t4 = stop_profile(ax)
        vals = []
        for s in range(1, 13):
            c = cfg('dao_chieu', stop=stop, rev=True, rev_t0=0.010, rev_a=1000.0, stop_wb=1.0)
            r = gsim.simulate(c, Tq, {a: (w if a == ax else np.zeros_like(Tq)) for a in gsim.AX},
                              plant=gsim.PLANT_REPLAY, seed=s)
            e = r[ax]['e']; aft = Tq >= t4
            ea = np.abs(e[aft]); ta = Tq[aft] - t4
            pk = ea[:int(0.3 / C.DT)].max()
            idx = np.where(ea > 0.1)[0]; trec = ta[idx[-1]] if len(idx) else 0.0
            res = float(np.mean(np.abs(e[(Tq > t4 + 0.6) & (Tq < t4 + 0.8)])))
            ua = np.abs(r[ax]['u'][Tq > t4 + 0.3])
            vals.append((pk, trec, res, ua.max(), float(np.std(r[ax]['u'][Tq > t4 + 0.3]))))
            if s == 1:
                ser = dict(T=Tq - t4, e=e.astype(np.float32), u=r[ax]['u'].astype(np.float32), w=w)
        v = np.array(vals).mean(0)
        stp[lab][ax] = dict(pk=v[0], trec=v[1], res=v[2], uhold=v[3], ustd=v[4], series=ser)
        print('  ', lab, ax, np.round(v, 3))
R['stop_test'] = stp

# ------------------------------------------------------------ su kien dao chieu tren cac cau hinh (mo phong tai hien) va log A
print('== su kien dao chieu')
ev = {}
mlog = C.log_mask(*C.WIN)
t_l = tu[mlog]
for ax in gsim.AX:
    w_l = np.interp(t_l, T, wd[ax])
    pk, idx = C.reversal_events(t_l, w_l, E['elog'][ax][mlog])
    ev[('log', ax)] = dict(mean=float(pk.mean()), max=float(pk.max()), n=len(pk))
    print('  log', ax, len(pk), round(pk.mean(), 3), round(pk.max(), 3))
R['rev_events'] = ev

with open('results2.pkl', 'wb') as f:
    pickle.dump(R, f)
print('xong', time.time() - t_all)
