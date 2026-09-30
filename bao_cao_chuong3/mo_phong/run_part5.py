"""Phan 5: muc 3.4.1 - lich truyen RS485.

1. Thu cap: cung chuoi nhieu, chi doi thoi diem cap nhat Pitch (uu tien Yaw -> deu 10 ms).
2. Khao sat phuong an lich va do dai khe (mo hinh danh dinh).
3. Bo dem bus trong log A.
"""
import sys, re, pickle
import numpy as np
sys.path.insert(0, '.')
import gsim
import common as C

E = C.exc(); T = E['T']; wd = E['wd']
cfgL = dict(gsim.LADDER)
Tend = T[-1] - T[0] + 0.1
DT = gsim.DT
LOG = sys.argv[1] if len(sys.argv) > 1 else 'log_A.txt'
R5 = {}


def sched_stats(ev, slot):
    out = {}
    for ax in gsim.AX:
        s = np.array([a for a, b in ev[ax]]); d = np.array([b - a for a, b in ev[ax]])
        g = np.diff(s) * 1e3
        out[ax] = dict(rate=len(s) / (s[-1] - s[0]), mean=float(g.mean()), std=float(g.std()),
                       p99=float(np.percentile(g, 99)), mx=float(g.max()),
                       over=float(np.mean(d > slot) * 100), gaps=g.astype(np.float32))
    return out


# ---------------------------------------------------------------- 1. thu cap
print('== thu cap')
pair = {'yawpri': [], 'reg': []}
keep = None
for seed in (1, 2, 3):
    rng = np.random.default_rng(seed); ev_y = gsim.schedule('yawpri', Tend, rng)
    sp = np.array([a for a, b in ev_y['pitch']])
    ev_r = {'yaw': ev_y['yaw'], 'pitch': [(t, t + 0.00225) for t in np.arange(sp[0], Tend, 0.010)]}
    c = gsim.config(**cfgL['tao_dang'])
    rY = gsim.simulate(c, T, wd, plant=gsim.PLANT_REPLAY, seed=seed)
    cR = dict(c); cR['ev'] = ev_r
    rR = gsim.simulate(cR, T, wd, plant=gsim.PLANT_REPLAY, seed=seed)
    pair['yawpri'].append({ax: C.replay_metrics(rY, ax) for ax in gsim.AX})
    pair['reg'].append({ax: C.replay_metrics(rR, ax) for ax in gsim.AX})
    if keep is None:
        keep = dict(eY=rY['pitch']['e'], eR=rR['pitch']['e'], sp=sp, sr=np.array([a for a, b in ev_r['pitch']]),
                    uY=rY['pitch']['u'], uR=rR['pitch']['u'])
    # thong ke theo tung khoang cap nhat Pitch
    g = np.diff(sp); dd = int(round(0.010 / DT))
    for k in range(len(g)):
        if T[0] + sp[k] < C.WIN[0] or T[0] + sp[k + 1] > C.WIN[1]:
            continue
        i0 = int(round(sp[k] / DT)); i1 = int(round(sp[k + 1] / DT)) + dd
        cls = 0 if g[k] < 0.0115 else (1 if g[k] < 0.0165 else 2)
        pair.setdefault('int', []).append((cls, np.abs(rY['pitch']['e'][i0:i1]).max(), np.abs(rR['pitch']['e'][i0:i1]).max()))
avg = lambda L: {ax: C.avg([d[ax] for d in L]) for ax in gsim.AX}
R5['pair'] = dict(yawpri=avg(pair['yawpri']), reg=avg(pair['reg']), series=keep)
iv = np.array(pair['int'])
R5['pair']['by_gap'] = {int(c): dict(n=int((iv[:, 0] == c).sum()), eY=float(iv[iv[:, 0] == c, 1].mean()),
                                     eR=float(iv[iv[:, 0] == c, 2].mean())) for c in (0, 1, 2)}
print(' yawpri', {ax: round(R5['pair']['yawpri'][ax]['erms'], 4) for ax in gsim.AX},
      ' deu', {ax: round(R5['pair']['reg'][ax]['erms'], 4) for ax in gsim.AX})
print(' theo khoang', R5['pair']['by_gap'])

# ---------------------------------------------------------------- 2. phuong an lich va do dai khe
print('== khao sat lich / khe')
cands = [('yawpri', 5e-3), ('alt', 4e-3), ('alt', 5e-3), ('alt', 6e-3)]
sv = {}
for mode, slot in cands:
    rng = np.random.default_rng(11)
    st = sched_stats(gsim.schedule(mode, 100.0, rng, slot=slot), slot)
    c = gsim.config(**cfgL['tao_dang']); c.update(bus=mode, slot=slot)
    cl = C.run_replay(c, seeds=(1, 2), plant=gsim.PLANT)
    sv[(mode, slot)] = dict(sched=st, closed=cl)
    print(' ', mode, slot, {ax: (round(st[ax]['rate'], 1), round(st[ax]['std'], 2), round(st[ax]['p99'], 2),
                                 round(st[ax]['mx'], 2), round(st[ax]['over'], 2), round(cl[ax]['erms'], 4)) for ax in gsim.AX})
R5['survey'] = sv

# ---------------------------------------------------------------- 3. bo dem bus log A (gian do bus minh hoa ve trong figs341.py)
lines = open(LOG, encoding='utf8').read().splitlines()
pat = re.compile(r'\[(\d+):(\d+):([\d.]+)\] bus txY=(\d+) txP=(\d+) gapY/P=(\d+)/(\d+)us exec=(\d+)/(\d+)us fail=(\d+) timeout=(\d+)')
rows = []
for ln in lines:
    m = pat.search(ln)
    if m:
        h, mi, s = int(m[1]), int(m[2]), float(m[3])
        rows.append([h * 3600 + mi * 60 + s] + [int(m[i]) for i in range(4, 12)])
rows = np.array(rows, float)
R5['log_bus'] = rows
print(' log bus', rows.shape, rows[-1])
pickle.dump(R5, open('results5.pkl', 'wb'))
print('xong')
