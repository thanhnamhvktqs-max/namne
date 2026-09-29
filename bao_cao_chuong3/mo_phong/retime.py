"""Dung lai thoi diem that cua tung mau stream 50 Hz trong log A.

Kenh giam sat phat moi 20 ms nhung may tinh nhan theo cum va bi mat mau (khoang 10 %)
khi chuong trinh in cac dong trang thai. Moi mau i duoc gan chi so khe n_i nguyen
(20 ms), rang buoc: mau khong the den may tinh truoc khi duoc phat, do tre nhan khong
qua L_MAX. Trong mien kha thi, chon day n_i lam cuc tieu tong binh phuong gia toc
(sai phan bac hai) cua cac goc do - quy hoach dong tren trang thai (n_i, g_i).
"""
import numpy as np
import excite

TS = 0.020
L_MAX = 0.30
C0 = 0.06
GMAX = 10


def retime():
    t = []
    sig = {k: [] for k in ('r', 'p', 'y', 'br', 'bp', 'by')}
    for line in open(excite.LOG):
        m = excite.PAT.search(line)
        if not m:
            continue
        t.append(int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]))
        for k, gi in zip(('r', 'p', 'y', 'br', 'bp', 'by'), (4, 5, 6, 8, 9, 10)):
            sig[k].append(float(m[gi]))
    h = np.array(t); h0 = h[0]; h = h - h0
    S = np.vstack([np.array(sig[k]) for k in ('by', 'bp', 'br', 'y', 'p')])
    scale = np.array([1.0, 1.0, 1.0, 0.05, 0.05])[:, None]   # can bang theo bien do
    S = S / scale
    N = len(h)
    hi = np.floor((h + C0) / TS).astype(int)          # n_i <= hi
    lo = np.ceil((h - L_MAX) / TS).astype(int)
    lo = np.maximum(lo, 0); lo[0] = 0; hi[0] = 0
    # dam bao kha thi theo thu tu
    for i in range(1, N):
        lo[i] = max(lo[i], lo[i - 1] + 1)
    for i in range(N - 2, -1, -1):
        hi[i] = min(hi[i], hi[i + 1] - 1)
    INF = 1e30
    # trang thai (n_i, g_i): cost
    W = [hi[i] - lo[i] + 1 for i in range(N)]
    cost = {}
    back = [None] * N
    # i = 1: n_1 = g_1
    prev = np.full((W[1], GMAX + 1), INF)
    for g in range(1, GMAX + 1):
        n1 = g
        if lo[1] <= n1 <= hi[1]:
            prev[n1 - lo[1], g] = 0.0
    back[1] = None
    backs = [None, None]
    for i in range(1, N - 1):
        cur = np.full((W[i + 1], GMAX + 1), INF)
        bk = np.full((W[i + 1], GMAX + 1, 2), -1, dtype=np.int32)
        s_prev = (S[:, i] - S[:, i - 1])
        s_next = (S[:, i + 1] - S[:, i])
        for oi in range(W[i]):
            n = lo[i] + oi
            row = prev[oi]
            gs = np.where(row < INF / 2)[0]
            if len(gs) == 0:
                continue
            for g2 in range(1, GMAX + 1):
                n2 = n + g2
                if n2 < lo[i + 1] or n2 > hi[i + 1]:
                    continue
                # gia toc voi moi g (vector hoa theo g)
                g = gs
                v1 = s_prev[:, None] / g[None, :]
                v2 = s_next[:, None] / g2
                acc = 2 * (v2 - v1) / (g[None, :] + g2)
                c = row[g] + np.sum(acc ** 2, axis=0) + 1e-4 * (g2 - 1)
                j = np.argmin(c)
                if c[j] < cur[n2 - lo[i + 1], g2]:
                    cur[n2 - lo[i + 1], g2] = c[j]
                    bk[n2 - lo[i + 1], g2] = (oi, g[j])
        backs.append(bk)
        prev = cur
    # truy vet
    oi, g = np.unravel_index(np.argmin(prev), prev.shape)
    n = np.zeros(N, int)
    n[N - 1] = lo[N - 1] + oi
    gcur = g
    for i in range(N - 1, 1, -1):
        o_prev, g_prev = backs[i][n[i] - lo[i], gcur]
        n[i - 1] = lo[i - 1] + o_prev
        gcur = g_prev
    n[0] = 0
    return n * TS, h


if __name__ == '__main__':
    tt, h = retime()
    import os
    np.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 't_true.npy'), tt)
    g = np.diff(np.round(tt / TS)).astype(int)
    print('N', len(tt), 'span', tt[-1], 'host span', h[-1])
    print('gap histogram', {k: int((g == k).sum()) for k in range(1, 8)})
    print('latency (h - t) ms: min %.0f med %.0f max %.0f' % ((h - tt).min() * 1e3, np.median(h - tt) * 1e3, (h - tt).max() * 1e3))
