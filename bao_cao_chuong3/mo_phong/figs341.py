"""Hinh cho muc 3.4.1 - Hoan thien lich truyen RS485 (Hinh 3.19 - 3.21), cung chuan voi figs2.py.

Chay: python figs341.py figs log_A.txt [full] [short]
"""
import sys, re, pickle
import numpy as np
from matplotlib import ticker as mt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import figs as F

LOG = sys.argv[2] if len(sys.argv) > 2 else 'log_A.txt'
R5 = pickle.load(open('results5.pkl', 'rb'))
AX = F.AX; PAL = F.PAL; INK = F.INK; num = F.num
CANDS = [('yawpri', 5e-3), ('alt', 4e-3), ('alt', 5e-3), ('alt', 6e-3)]
CAND_LAB = ['Ưu tiên Yaw, khe 5 ms', 'Luân phiên, khe 4 ms', 'Luân phiên, khe 5 ms', 'Luân phiên, khe 6 ms']
CHOSEN = 2
BEF_BAR = '#5f5f5f'              # cot "truoc" (lich uu tien Yaw) tren bieu do cot
T_TX = 0.43                      # phat khung lenh 10 byte o 230,4 kbit/s (ms)
T_WIN = 3.5                      # cua so giao dich lon nhat: phat khung + cho phan hoi toi da 3 ms (ms)


def ann(t):
    t._ann = True                # chu chu thich co chu dich trong vung ve (bo qua khi kiem tra)
    return t


# ---------------------------------------------------------------------------- gian do bus minh hoa
def timeline(mode, dur, t_end=0.072, slot=5e-3):
    """Cung logic gsim.schedule, voi thoi gian giao dich cho truoc dur(truc, thoi diem bat dau)."""
    ev = {'yaw': [], 'pitch': []}; slots = []; miss = []
    t = 0.0; n = 0
    while t < t_end:
        slots.append(t)
        if mode == 'alt':
            ax = AX[n % 2]; d = dur(ax, t)
            ev[ax].append((t, t + d)); end = t + d
        else:
            d = dur('yaw', t); ev['yaw'].append((t, t + d)); end = t + d
            if n % 2 == 1:
                if (t + slot) - end >= 2.75e-3 - 1e-9:
                    dp = dur('pitch', end); ev['pitch'].append((end, end + dp)); end += dp
                else:
                    miss.append(t); n -= 1           # Pitch bi hoan sang khe sau
        nxt = t + slot
        t = nxt if end <= nxt else end
        n += 1
    return ev, slots, miss


LONG_YAW = [(19.9, 25.1, 4.3), (29.9, 30.1, 2.9), (49.9, 50.1, 6.2)]


def dur(ax, t):
    ms = t * 1e3
    if ax == 'yaw':
        for a, b, d in LONG_YAW:
            if a < ms < b:
                return d * 1e-3
        return 2.25e-3
    return 2.4e-3


def draw_timeline(a, mode):
    a._hcm_ref = 2.3
    ev, slots, miss = timeline(mode, dur)
    for s in slots:
        a.axvline(s * 1e3, color='#8c8c8c', lw=0.9, ls=F.DOT, zorder=1)
    labs = []
    for yy, ax in ((1, 'yaw'), (0, 'pitch')):
        for s, e in ev[ax]:
            d = (e - s) * 1e3
            lg = ax == 'yaw' and d > 2.3
            a.broken_barh([(s * 1e3, d)], (yy - 0.3, 0.6), facecolor=PAL[ax]['main'],
                          edgecolor=INK if lg else 'none', lw=0.9, hatch='////' if lg else None, zorder=3)
            if lg:
                xc = s * 1e3 + d / 2
                lift = 0.62 * a._hcm_ref / a._hcm if labs and xc - labs[-1][0] < 6.5 and labs[-1][1] == 0 else 0.0
                labs.append((xc, lift))
                ann(a.text(xc, yy + 0.36 + lift, num(d, 1) + ' ms', ha='center', va='bottom', fontsize=9))
    for tm in miss:
        a.plot(tm * 1e3 + 3.6, 0, marker='x', ms=7, mew=1.6, color=INK, zorder=4)
    sp = [s * 1e3 for s, e in ev['pitch']]
    for x0, x1 in zip(sp[:-1], sp[1:]):
        dd = x1 - x0; bad = dd > 10.5
        c = INK if bad else '#5a5a5a'
        a.annotate('', xy=(x1, -0.62), xytext=(x0, -0.62),
                   arrowprops=dict(arrowstyle='<->', lw=1.2 if bad else 0.8, color=c, shrinkA=0, shrinkB=0), zorder=4)
        nd = 0 if abs(dd - round(dd)) < 0.05 else 1
        ann(a.text((x0 + x1) / 2, -0.74, num(dd, nd) + ' ms', ha='center', va='top', fontsize=9.5, color=c,
                   fontweight='bold' if bad else 'normal', bbox=dict(fc='white', ec='none', pad=0.6), zorder=5))
    a.set_xlim(-0.5, 72); a.set_ylim(-1.75, 2.45 + (0.62 * 2.3 / a._hcm - 0.62))
    a.set_yticks([0, 1]); a.set_yticklabels(['Pitch', 'Yaw'])
    a.xaxis.set_major_locator(mt.MultipleLocator(10))
    a.grid(False); a.tick_params(axis='y', length=0)
    a.set_xlabel('Thời gian (ms)')
    return sp


def fig319():
    fig, G = F.new_fig([dict(cols=F.ONE, h=2.3, top=F.LEG2), dict(cols=F.ONE, h=2.3),
                        dict(cols=F.TWO, h=2.9, top=F.LEG2, bot=F.BOT2)])
    draw_timeline(G[0]['axes'][0], 'yawpri')
    F.subcap(fig, G[0], 0, 'a) Lịch ưu tiên Yaw: khoảng cập nhật trục Pitch')
    draw_timeline(G[1]['axes'][0], 'alt')
    F.subcap(fig, G[1], 0, 'b) Lịch luân phiên: khoảng cập nhật trục Pitch')
    F.band_legend(fig, G[0], [Patch(facecolor=PAL['yaw']['main']), Patch(facecolor=PAL['pitch']['main']),
                              Patch(facecolor='white', edgecolor=INK, hatch='////', lw=0.9),
                              Line2D([], [], marker='x', ms=7, mew=1.6, color=INK, lw=0),
                              Line2D([], [], color='#8c8c8c', lw=0.9, ls=F.DOT)],
                  ['Giao dịch Yaw', 'Giao dịch Pitch', 'Giao dịch Yaw > 2,25 ms', 'Lượt Pitch bị hoãn', 'Đầu khe'],
                  ncol=3, hl=1.6)
    # c) khoang cap nhat Pitch theo thoi gian
    a = G[2]['axes'][0]
    gy = np.asarray(R5['survey'][('yawpri', 5e-3)]['sched']['pitch']['gaps'], float)
    ga = np.asarray(R5['survey'][('alt', 5e-3)]['sched']['pitch']['gaps'], float)
    ty = np.cumsum(gy) / 1e3; ta = np.cumsum(ga) / 1e3
    i = int(np.argmax(gy >= 25)); t0 = max(0.0, ty[i] - 0.45); t1 = t0 + 1.0
    for t_, g_, sty, z in ((ty, gy, dict(color=INK, lw=1.1, ls=F.DASH, marker='o', ms=3.4, mfc='white', mew=0.8), 3),
                           (ta, ga, dict(color=PAL['pitch']['main'], lw=2.2, ls='-'), 5)):
        m = (t_ >= t0) & (t_ < t1)
        a.plot(t_[m] - t0, g_[m], zorder=z, **sty)
    a.axhline(10, **F.REF, zorder=2)
    a.set_xlim(0, 1.0); a.set_ylim(0, 36); a.yaxis.set_major_locator(mt.MultipleLocator(10))
    a.set_xlabel('Thời gian (s)'); a.set_ylabel('$\\Delta$ (ms)')
    F.band_legend(fig, G[2], [Line2D([], [], color=INK, lw=1.1, ls=F.DASH, marker='o', ms=3.4, mfc='white', mew=0.8),
                              Line2D([], [], color=PAL['pitch']['main'], lw=2.2)],
                  ['Ưu tiên Yaw', 'Luân phiên'], ncol=1, cx=F.TWO[0][0] + F.PW / 2)
    F.subcap(fig, G[2], 0, 'c) Khoảng cập nhật của trục Pitch')
    # d) sai lech lon nhat trong moi khoang cap nhat, theo do dai khoang (thu cap)
    a = G[2]['axes'][1]
    bg = R5['pair']['by_gap']; ntot = sum(v['n'] for v in bg.values())
    x = np.arange(3)
    vy = [bg[c]['eY'] for c in range(3)]; vr = [bg[c]['eR'] for c in range(3)]
    a.bar(x - 0.19, vy, 0.36, color=BEF_BAR, zorder=3)
    a.bar(x + 0.19, vr, 0.36, color=PAL['pitch']['main'], zorder=3)
    for xi, y1, y2 in zip(x, vy, vr):
        ann(a.text(xi - 0.19, y1 + 0.004, '+' + num((y1 / y2 - 1) * 100, 0) + ' %', ha='center', va='bottom', fontsize=9.5))
    a.set_xticks(x)
    a.set_xticklabels([f'{lab}\n({num(bg[c]["n"] / ntot * 100, 0)} %)' for c, lab in enumerate(['≈ 10 ms', '≈ 15 ms', '≥ 20 ms'])])
    a.set_ylim(0, max(vy) * 1.18); a.set_xlim(-0.55, 2.55)
    a.set_xlabel('Khoảng cập nhật $\\Delta$ của trục Pitch'); a.set_ylabel('max $|e|$ (°)'); F.bar_axes(a)
    F.band_legend(fig, G[2], [Patch(facecolor=BEF_BAR), Patch(facecolor=PAL['pitch']['main'])],
                  ['Cập nhật theo lịch ưu tiên Yaw', 'Cập nhật đều 10 ms'], ncol=1, cx=F.TWO[1][0] + F.PW / 2, hl=1.6)
    F.subcap(fig, G[2], 1, 'd) Sai lệch Pitch theo khoảng cập nhật')
    F.finish(fig, 'h3_19_lich_rs485_co_che')


# ---------------------------------------------------------------------------- khao sat phuong an
def fig320():
    lab0, w3 = 3.55, 3.6
    cols3 = [(lab0, w3), (lab0 + w3 + 0.45, w3), (lab0 + 2 * (w3 + 0.45), w3)]
    fig, G = F.new_fig([dict(cols=cols3, h=3.3, top=F.LEG1), dict(cols=[(lab0, 3 * w3 + 0.9)], h=2.3, top=F.LEG2)])
    SV = R5['survey']
    y = np.arange(len(CANDS))
    specs = [('rate', 'Tần số (Hz)', 'a) Tần số cập nhật', lambda s, ax: s['sched'][ax]['rate']),
             ('std', '$\\sigma_{\\Delta}$ (ms)', 'b) Độ tản mát của $\\Delta$', lambda s, ax: s['sched'][ax]['std']),
             ('erms', '$e_{\\mathrm{rms}}$ (°)', 'c) Sai lệch hiệu dụng', lambda s, ax: s['closed'][ax]['erms'])]
    for j, (key, xl, cap, getv) in enumerate(specs):
        a = G[0]['axes'][j]
        for k, ax in enumerate(AX):
            a.barh(y - 0.19 + 0.38 * k, [getv(SV[c], ax) for c in CANDS], 0.36, color=PAL[ax]['main'], zorder=3)
        a.set_yticks(y); a.set_yticklabels(CAND_LAB if j == 0 else [''] * len(y))
        F.hilite(a, CHOSEN, horiz=True)
        a.set_ylim(len(y) - 0.45, -0.55)
        a.xaxis.set_major_locator(mt.MaxNLocator(4, steps=[1, 2, 2.5, 5, 10]))
        a.set_xlabel(xl); F.bar_axes(a, horiz=True)
        F.subcap(fig, G[0], j, cap)
    hk, lk = F.key_patches()
    F.band_legend(fig, G[0], hk, lk, hl=1.6)
    # d) ngan sach thoi gian mot khe
    a = G[1]['axes'][0]
    slots = [4.0, 5.0, 6.0]; yy = np.arange(3)
    a.axvspan(2.3, 2.9, color='#cfe3d4', lw=0, zorder=1)
    for i, T in enumerate(slots):
        a.barh(i, T_TX, 0.5, left=0, color='#3d3d3d', zorder=3)
        a.barh(i, T_WIN - T_TX, 0.5, left=T_TX, color='#9e9e9e', zorder=3)
        a.barh(i, T - T_WIN, 0.5, left=T_WIN, facecolor='white', edgecolor='#3d3d3d', hatch='\\\\\\\\', lw=0.9, zorder=3)
        ann(a.text(T + 0.1, i, 'dự trữ ' + num(T - T_WIN, 1) + ' ms', ha='left', va='center', fontsize=9.5))
    a.axvline(8.0, color=INK, lw=1.3, ls=F.DASH, zorder=4)
    a.set_yticks(yy); a.set_yticklabels([f'Khe {num(T, 0)} ms' for T in slots])
    F.hilite(a, 1, horiz=True)
    a.set_ylim(2.5, -0.5); a.set_xlim(0, 8.6)
    a.xaxis.set_major_locator(mt.MultipleLocator(1))
    a.set_xlabel('Thời gian tính từ đầu khe (ms)'); F.bar_axes(a, horiz=True)
    F.band_legend(fig, G[1], [Patch(facecolor='#3d3d3d'), Patch(facecolor='#9e9e9e'),
                              Patch(facecolor='white', edgecolor='#3d3d3d', hatch='\\\\\\\\', lw=0.9),
                              Patch(facecolor='#cfe3d4'), Line2D([], [], color=INK, lw=1.3, ls=F.DASH)],
                  ['Phát khung lệnh (0,43 ms)', 'Chờ phản hồi (tối đa 3 ms)', 'Dự trữ',
                   'Giao dịch thông thường', 'Giao dịch dài nhất (log A)'], ncol=3, hl=1.6)
    F.subcap(fig, G[1], 0, 'd) Ngân sách thời gian của một khe')
    F.finish(fig, 'h3_20_khao_sat_rs485')


# ---------------------------------------------------------------------------- truoc / sau + bo dem bus log A
def log_bus_series():
    rows = R5['log_bus']
    lines = open(LOG, encoding='utf8').read().splitlines()
    first = next(l for l in lines if '] goc ' in l)
    h, m, s = re.match(r'\[(\d+):(\d+):([\d.]+)\]', first).groups()
    t0 = int(h) * 3600 + int(m) * 60 + float(s)
    tu_rows = rows[:, 0] - t0 - F.E['log']['lat']
    act = rows[:, 1] > 0
    cnt = {'yaw': rows[:, 1], 'pitch': rows[:, 2]}
    gmax = {'yaw': rows[act, 3] / 1e3, 'pitch': rows[act, 4] / 1e3}
    return tu_rows, cnt, tu_rows[act], gmax


def draw_bus(fig, g):
    tr, cnt, tg, gmax = log_bus_series()
    t_on, t_off = F.E['log']['t_start'], F.E['log']['t_stop']
    sty = {'yaw': dict(color=PAL['yaw']['main'], lw=2.2, marker='o', ms=5, mec='white', mew=0.8),
           'pitch': dict(color=PAL['pitch']['main'], lw=1.4, ls=F.DASH, marker='s', ms=4, mec='white', mew=0.6)}
    a = g['axes'][0]
    tt = np.array([0, t_on, t_off, 80.0])
    a.plot(tt, np.clip(tt - t_on, 0, t_off - t_on) * 100.0, **F.REF, zorder=2)
    for ax in AX:
        a.plot(tr, cnt[ax], zorder=3 if ax == 'yaw' else 4, **sty[ax])
    a.set_ylim(0, 8500); a.set_xlim(0, 80); a.yaxis.set_major_locator(mt.MultipleLocator(2000))
    a.set_xlabel('Thời gian (s)'); a.set_ylabel('Số giao dịch')
    F.subcap(fig, g, 0, 'd) Số giao dịch tích lũy mỗi trục')
    a = g['axes'][1]
    for ax in AX:
        a.step(tg, gmax[ax], where='post', zorder=3 if ax == 'yaw' else 4,
               **{k: v for k, v in sty[ax].items() if k not in ('marker', 'ms', 'mec', 'mew')})
    ymx = R5['survey'][('yawpri', 5e-3)]['sched']['pitch']['mx']
    a.axhline(ymx, color='#6e6e6e', lw=1.3, ls=F.DASHDOT, zorder=2)
    a.axhline(10, **F.REF, zorder=2)
    a.set_ylim(0, 36); a.set_xlim(0, 80); a.yaxis.set_major_locator(mt.MultipleLocator(10))
    a.set_xlabel('Thời gian (s)'); a.set_ylabel('$\\Delta_{\\max}$ (ms)')
    F.subcap(fig, g, 1, 'e) Khoảng cập nhật lớn nhất đo được')
    F.band_legend(fig, g, [Line2D([], [], **sty['yaw']), Line2D([], [], **sty['pitch']), Line2D([], [], **F.REF),
                           Line2D([], [], color='#6e6e6e', lw=1.3, ls=F.DASHDOT)],
                  ['Yaw (log A)', 'Pitch (log A)', 'Danh định 100 Hz / 10 ms', 'Pitch, ưu tiên Yaw (mô phỏng)'],
                  ncol=2, hl=2.8)


def fig321():
    F.before_after('h3_21_rs485_truoc_sau', 'tao_dang', 'hoan_thien', {'yaw': (50.4, 52.4), 'pitch': (64.2, 65.7)},
                   ['erms', 'p99', 'emax'], extra_log=True,
                   extra=dict(row=dict(cols=F.TWO, h=2.6, top=F.LEG2), draw=draw_bus))


# ---------------------------------------------------------------------------- ban rut gon (mot hinh, chi mo phong)
def fig319_short():
    """Ban rut gon cua muc 3.4.1: gian do bus (a, b), khoang cap nhat Pitch (c), sai lech theo khoang cap nhat (d)."""
    fig, G = F.new_fig([dict(cols=F.ONE, h=1.7, top=F.LEG2, bot=F.BOT0), dict(cols=F.ONE, h=1.7),
                        dict(cols=F.TWO, h=2.0, top=F.LEG2, bot=F.BOT2)])
    draw_timeline(G[0]['axes'][0], 'yawpri')
    G[0]['axes'][0].set_xlabel('')
    F.subcap(fig, G[0], 0, 'a) Lịch ưu tiên Yaw')
    draw_timeline(G[1]['axes'][0], 'alt')
    F.subcap(fig, G[1], 0, 'b) Lịch luân phiên, khe 5 ms (chọn)')
    F.band_legend(fig, G[0], [Patch(facecolor=PAL['yaw']['main']), Patch(facecolor=PAL['pitch']['main']),
                              Patch(facecolor='white', edgecolor=INK, hatch='////', lw=0.9),
                              Line2D([], [], marker='x', ms=7, mew=1.6, color=INK, lw=0),
                              Line2D([], [], color='#8c8c8c', lw=0.9, ls=F.DOT)],
                  ['Giao dịch Yaw', 'Giao dịch Pitch', 'Giao dịch Yaw > 2,25 ms', 'Lượt Pitch bị hoãn', 'Đầu khe'],
                  ncol=3, hl=1.6)
    # c) khoang cap nhat Pitch theo thoi gian (mo phong theo su kien)
    a = G[2]['axes'][0]
    gy = np.asarray(R5['survey'][('yawpri', 5e-3)]['sched']['pitch']['gaps'], float)
    ga = np.asarray(R5['survey'][('alt', 5e-3)]['sched']['pitch']['gaps'], float)
    ty = np.cumsum(gy) / 1e3; ta = np.cumsum(ga) / 1e3
    i = int(np.argmax(gy >= 25)); t0 = max(0.0, ty[i] - 0.45); t1 = t0 + 1.0
    sy = dict(color=INK, lw=1.1, ls=F.DASH, marker='o', ms=3.4, mfc='white', mew=0.8)
    sa = dict(color=PAL['pitch']['main'], lw=2.2, ls='-')
    for t_, g_, sty, z in ((ty, gy, sy, 3), (ta, ga, sa, 5)):
        m = (t_ >= t0) & (t_ < t1)
        a.plot(t_[m] - t0, g_[m], zorder=z, **sty)
    a.axhline(10, **F.REF, zorder=2)
    a.set_xlim(0, 1.0); a.set_ylim(0, 36); a.yaxis.set_major_locator(mt.MultipleLocator(10))
    a.set_xlabel('Thời gian (s)'); a.set_ylabel('$\\Delta$ (ms)')
    F.band_legend(fig, G[2], [Line2D([], [], **sy), Line2D([], [], **sa)], ['Ưu tiên Yaw', 'Luân phiên, khe 5 ms'],
                  ncol=1, cx=F.TWO[0][0] + F.PW / 2)
    F.subcap(fig, G[2], 0, 'c) Khoảng cập nhật của trục Pitch')
    # d) sai lech lon nhat trong moi khoang cap nhat Pitch (thu cap tren mo phong tai hien)
    a = G[2]['axes'][1]
    bg = R5['pair']['by_gap']; ntot = sum(v['n'] for v in bg.values())
    x = np.arange(3)
    vy = [bg[c]['eY'] for c in range(3)]; vr = [bg[c]['eR'] for c in range(3)]
    a.bar(x - 0.19, vy, 0.36, color=BEF_BAR, zorder=3)
    a.bar(x + 0.19, vr, 0.36, color=PAL['pitch']['main'], zorder=3)
    for xi, y1, y2 in zip(x, vy, vr):
        ann(a.text(xi - 0.19, y1 + 0.004, '+' + num((y1 / y2 - 1) * 100, 0) + ' %', ha='center', va='bottom', fontsize=9.5))
    a.set_xticks(x)
    a.set_xticklabels([f'{lab}\n({num(bg[c]["n"] / ntot * 100, 0)} %)' for c, lab in enumerate(['≈ 10 ms', '≈ 15 ms', '≥ 20 ms'])])
    a.set_ylim(0, max(vy) * 1.2); a.set_xlim(-0.55, 2.55)
    a.set_xlabel('Khoảng cập nhật $\\Delta$ của Pitch'); a.set_ylabel('max $|e|$ (°)'); F.bar_axes(a)
    F.band_legend(fig, G[2], [Patch(facecolor=BEF_BAR), Patch(facecolor=PAL['pitch']['main'])],
                  ['Theo lịch ưu tiên Yaw', 'Cập nhật đều 10 ms'], ncol=1, cx=F.TWO[1][0] + F.PW / 2, hl=1.6)
    F.subcap(fig, G[2], 1, 'd) Sai lệch Pitch theo khoảng cập nhật')
    F.finish(fig, 'h3_19_lich_rs485')


if __name__ == '__main__':
    sel = sys.argv[3:] or ['full', 'short']
    if 'full' in sel:
        fig319(); fig320(); fig321()
    if 'short' in sel:
        fig319_short()
