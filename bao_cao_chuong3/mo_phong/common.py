"""Tien ich chung: kich thich, cua so danh gia, chi tieu."""
import numpy as np
import excite
import gsim

DT = gsim.DT
SEG = [(8.5, 29.5, 'Đoạn 1: Yaw dao động chậm'),
       (29.5, 47.5, 'Đoạn 2: Pitch dao động'),
       (47.5, 60.5, 'Đoạn 3: Yaw dao động nhanh'),
       (60.5, 70.5, 'Đoạn 4: Pitch dao động nhanh'),
       (70.5, 76.0, 'Đoạn 5: Yaw đảo chiều gắt')]
WIN = (8.5, 76.0)
HOLD = (4.5, 8.0)

_E = None


def exc():
    global _E
    if _E is None:
        _E = excite.build(t0=4.0, t1=77.0, fc=10)
        L = _E['log']
        tu = L['tu']
        yref = np.median(L['y'][(tu > HOLD[0]) & (tu < HOLD[1])])
        _E['elog'] = {'yaw': -(L['y'] - yref), 'pitch': -(L['p'] - 0.0)}
        _E['yref'] = yref
    return _E


def log_mask(a, b):
    E = exc(); tu = E['log']['tu']
    return (tu >= a) & (tu < b)


def emet(e):
    return dict(erms=float(np.sqrt(np.mean(e ** 2))), emax=float(np.abs(e).max()),
                p99=float(np.percentile(np.abs(e), 99)))


def replay_metrics(r, ax, a=WIN[0], b=WIN[1]):
    """Chi tieu tai dung cac thoi diem lay mau cua kenh giam sat (nhu log A)."""
    E = exc(); T = E['T']; tu = E['log']['tu']
    m = log_mask(a, b)
    e = np.interp(tu[m], T, r[ax]['e'])
    out = emet(e)
    mm = (T >= a) & (T < b)
    out['rho'] = float(r[ax]['sat'][mm].mean() * 100)
    out['umax'] = float(np.abs(r[ax]['u'][mm]).max())
    du = np.abs(r[ax]['du'][mm])
    out['dumax'] = float(du.max()); out['du99'] = float(np.percentile(du, 99))
    out['durms'] = float(np.sqrt(np.mean(du ** 2)))
    out['iqrms'] = float(np.sqrt(np.mean(r[ax]['iq'][mm] ** 2)))
    u = r[ax]['u'][mm]
    nz = np.abs(u) > 0.5
    out['signchg'] = int(np.sum(np.diff(np.sign(u[nz])) != 0))
    return out


def avg(dicts):
    keys = dicts[0].keys()
    return {k: float(np.mean([d[k] for d in dicts])) for k in keys}


def run_replay(cfg, seeds=(1, 2, 3), plant=None, cal=None, keep=False):
    E = exc()
    plant = plant or gsim.PLANT_REPLAY
    cal = cal or gsim.CAL
    res = {ax: [] for ax in gsim.AX}
    first = None
    for s in seeds:
        r = gsim.simulate(cfg, E['T'], E['wd'], plant=plant, cal=cal, seed=s)
        if first is None:
            first = r
        for ax in gsim.AX:
            res[ax].append(replay_metrics(r, ax))
    out = {ax: avg(res[ax]) for ax in gsim.AX}
    if keep:
        out['_r'] = first
    return out


def step_metrics(T, y, A, t0):
    """tr (10-90 %), ts (+-2 %), OS (%) cua dap ung chuan hoa y/A sau t0."""
    m = T >= t0
    ys = np.convolve(np.pad(y, 2, mode='edge'), np.ones(5) / 5, mode='valid')  # loc trung binh 10 ms
    t = T[m] - t0; x = ys[m] / A
    x[:3] = y[m][:3] / A
    try:
        t10 = t[np.argmax(x >= 0.1)]; t90 = t[np.argmax(x >= 0.9)]
    except Exception:
        t10 = t90 = np.nan
    out = np.where(np.abs(x - 1) > 0.02)[0]
    ts = t[out[-1] + 1] if len(out) and out[-1] + 1 < len(t) else np.nan
    os_ = max(0.0, (x.max() - 1) * 100)
    return dict(tr=(t90 - t10) * 1e3, ts=ts * 1e3, OS=os_)


def reversal_events(t, w, e, pre=60.0):
    """Cac lan khung mang doi chieu: w doi dau, truoc do |w| > pre trong 0,3 s."""
    idx = np.where(np.sign(w[1:]) != np.sign(w[:-1]))[0]
    dt = np.median(np.diff(t))
    n_pre = int(0.3 / dt); n_a = int(0.1 / dt); n_b = int(0.3 / dt)
    pk = []; ev = []
    for i in idx:
        if i < n_pre or i + n_b >= len(t):
            continue
        if np.abs(w[i - n_pre:i]).max() < pre:
            continue
        seg = e[i - n_a:i + n_b]
        pk.append(np.abs(seg).max()); ev.append(i)
    return np.array(pk), ev
