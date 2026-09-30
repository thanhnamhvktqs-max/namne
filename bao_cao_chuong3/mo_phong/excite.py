"""Dung tin hieu kich thich tai hien tu log A (IMU2 tren khung mang)."""
import re
import numpy as np
from scipy.interpolate import CubicSpline

import os as _os
LOG = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'log_A.txt')
PAT = re.compile(r'\[(\d+):(\d+):([\d.]+)\] goc roll=\s*([-\d.]+) pitch=\s*([-\d.]+) '
                 r'yaw=\s*([-\d.]+) zaru=(\w+) base=([-\d.]+)/([-\d.]+)/([-\d.]+)')
DT = 0.002


def hms(s):
    h, m, x = s.split(':')
    return int(h) * 3600 + int(m) * 60 + float(x)


def load_log():
    t, r, p, y, br, bp, by = [], [], [], [], [], [], []
    for line in open(LOG):
        m = PAT.search(line)
        if not m:
            continue
        t.append(int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]))
        r.append(float(m[4])); p.append(float(m[5])); y.append(float(m[6]))
        br.append(float(m[8])); bp.append(float(m[9])); by.append(float(m[10]))
    t = np.array(t)
    t_start = hms('21:49:12.037'); t_stop = hms('21:50:28.343')
    import os
    tu = np.load(os.path.join(os.path.dirname(__file__), 't_true.npy'))  # thoi diem that (retime.py)
    lat = np.median((t - t[0]) - tu)
    return dict(tu=tu, dts=0.02, lat=lat, r=np.array(r), p=np.array(p), y=np.array(y),
                br=np.array(br), bp=np.array(bp), by=np.array(by),
                t_start=t_start - t[0] - lat, t_stop=t_stop - t[0] - lat)


def lpf(x, fc, dt=DT):
    a = 2 * np.pi * fc * dt / (1 + 2 * np.pi * fc * dt)
    y = np.empty_like(x); acc = x[0]
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y


def build(t0=7.0, t1=76.5, fc=12.0):
    L = load_log()
    tu = L['tu']
    T = np.arange(t0, t1, DT)
    out = {}
    for key in ('by', 'bp', 'br'):
        cs = CubicSpline(tu, L[key])
        ang = cs(T)
        rate = cs(T, 1)
        # loc hai chieu (khong lech pha) de bo gai do luong tu 0,01 deg
        rate = lpf(rate, fc); rate = lpf(rate[::-1], fc)[::-1]
        out[key] = ang; out['w' + key[1]] = rate
    # truc Yaw: toc do quay khung mang quanh truc thang dung
    wd_yaw = out['wy']
    # truc Pitch: phep chieu (2.9), q_y = goc khop Yaw ~ -(psi_b - psi_b0)
    qy = np.deg2rad(-(out['by'] - out['by'][0]))
    wd_pitch = -out['wr'] * np.sin(qy) + out['wp'] * np.cos(qy)
    return dict(T=T, wd={'yaw': wd_yaw, 'pitch': wd_pitch}, qy=qy, log=L)


if __name__ == '__main__':
    E = build()
    for ax in ('yaw', 'pitch'):
        w = E['wd'][ax]
        print(ax, 'rms %.1f peak %.1f' % (np.sqrt(np.mean(w ** 2)), np.abs(w).max()))
