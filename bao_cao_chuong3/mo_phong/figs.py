"""Ve toan bo hinh cho Chuong 3 (PNG 300 dpi, rong 16 cm)."""
import sys, pickle, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
sys.path.insert(0, '.')
import gsim
import common as C

OUT = 'figs'
os.makedirs(OUT, exist_ok=True)
R = pickle.load(open('results.pkl', 'rb'))
R2 = pickle.load(open('results2.pkl', 'rb'))
E = C.exc(); T = E['T']; wd = E['wd']; L = E['log']; tu = L['tu']

plt.rcParams.update({
    'font.family': 'Liberation Serif', 'font.size': 9, 'axes.titlesize': 9,
    'axes.labelsize': 9, 'legend.fontsize': 8, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': 0.6,
    'axes.edgecolor': '#52514e', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
    'axes.grid': True, 'grid.color': '#e4e3df', 'grid.linewidth': 0.5,
    'legend.frameon': True, 'legend.framealpha': 0.88, 'legend.edgecolor': 'none', 'legend.fancybox': False, 'lines.linewidth': 1.0, 'savefig.dpi': 300,
    'axes.titleweight': 'normal', 'axes.titlelocation': 'left'})

COL = {'yaw': '#2a78d6', 'pitch': '#eb6834'}
LIGHT = {'yaw': ['#a9c8ee', '#6fa3e3', '#2a78d6', '#1b4f8f'], 'pitch': ['#f6bda4', '#f0915f', '#eb6834', '#a8431b']}
GREY = '#8a8985'
INK = '#0b0b0b'
AXN = {'yaw': 'Yaw', 'pitch': 'Pitch'}
CM = 1 / 2.54
W = 16 * CM
NAMES = {'ban_dau': 'Ban đầu', 'cascade': 'Hiệu chỉnh nối tầng', 'bu_imu2': 'Bù IMU2',
         'ngoai_suy': 'Ngoại suy bù trễ', 'gioi_han': 'Giới hạn động', 'dao_chieu': 'Đảo chiều, dừng',
         'tao_dang': 'Tạo dạng lệnh', 'hoan_thien': 'Hoàn thiện'}
ORDER = [n for n, _ in gsim.LADDER]


def vn(x, nd=2):
    return f'{x:.{nd}f}'.replace('.', ',')


def _comma(v, p):
    t = ('%.6f' % v).rstrip('0').rstrip('.')
    return t.replace('-', '−').replace('.', ',')


def save(fig, name):
    from matplotlib.ticker import FuncFormatter, ScalarFormatter
    for a in fig.axes:
        for axis, sc in ((a.yaxis, a.get_yscale()), (a.xaxis, a.get_xscale())):
            if sc == 'linear' and isinstance(axis.get_major_formatter(), ScalarFormatter):
                axis.set_major_formatter(FuncFormatter(_comma))
    fig.savefig(os.path.join(OUT, name + '.png'), bbox_inches='tight', facecolor='white')
    plt.close(fig)


def tag(ax, s):
    ax.set_title(s, loc='left', fontsize=9)


def seg_shade(ax, labels=True, ymax=None):
    for i, (a, b, lab) in enumerate(C.SEG):
        if i % 2 == 0:
            ax.axvspan(a, b, color='#f1f0ec', zorder=0, lw=0)
        if labels:
            ax.text((a + b) / 2, 0.02, f'Đoạn {i + 1}', transform=ax.get_xaxis_transform(),
                    ha='center', va='bottom', fontsize=7, color='#52514e')


def win(r_series, ax, a, b, key='e'):
    m = (T >= a) & (T < b)
    return T[m], r_series[ax][key][m]


# -------------------------------------------------------------------------- khuon hinh "truoc / sau"
def before_after(name, before, after, windows, metrics, labels, extra_log=False, units='°'):
    """(a) Yaw, (b) Pitch: e(t) truoc (xam, net dut) / sau (mau truc); (c) chi tieu chuan hoa."""
    fig = plt.figure(figsize=(W, 8.0 * CM))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], hspace=0.7, wspace=0.28)
    Sb = R['ladder_series'][before]; Sa = R['ladder_series'][after]
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[0, j])
        a, b = windows[ax]
        t, eb = win(Sb, ax, a, b); _, ea = win(Sa, ax, a, b)
        a_.plot(t, eb, color=GREY, lw=0.8, ls='--', label='Trước: ' + NAMES[before])
        a_.plot(t, ea, color=COL[ax], lw=1.1, label='Sau: ' + NAMES[after])
        if extra_log:
            m = (tu >= a) & (tu < b)
            a_.plot(tu[m], E['elog'][ax][m], color=INK, lw=0, marker='.', ms=2.2, label='Đo (log A)')
        a_.set_xlabel('Thời gian (s)'); a_.set_ylabel('Sai lệch góc (°)')
        tag(a_, f'{"ab"[j]}) Trục {AXN[ax]}')
        a_.legend(loc='upper center', fontsize=6.8, handlelength=1.8, ncol=2 if extra_log else 1)
        lim = np.abs(np.r_[eb, ea]).max() * 1.1
        a_.set_ylim(-lim, lim * (1.9 if not extra_log else 2.1))
    a3 = fig.add_subplot(gs[1, :])
    n = len(metrics); y = np.arange(n)
    Mb = R['ladder'][before]; Ma = R['ladder'][after]
    for k, ax in enumerate(gsim.AX):
        vals = []; lab_ = []
        for mkey in metrics:
            vb = Mb[ax][mkey]; va = Ma[ax][mkey]
            vals.append(va / vb * 100 if vb else 100.0)
            nd = 0 if max(vb, va) >= 20 else (2 if max(vb, va) >= 1 else 3)
            d = (va / vb - 1) * 100 if vb else 0.0
            sg = '' if abs(d) < 0.05 else ('+' if d > 0 else '−')
            lab_.append(f'{vn(vb, nd)} → {vn(va, nd)}  ({sg}{vn(abs(d), 1)} %)')
        off = -0.19 if ax == 'yaw' else 0.19
        a3.barh(y + off, vals, height=0.36, color=COL[ax], label=f'Trục {AXN[ax]}', zorder=3)
        for yi, v, tx in zip(y, vals, lab_):
            a3.text(max(v, 100) + 3, yi + off, tx, va='center', fontsize=6.8, color='#52514e')
    a3.axvline(100, color=INK, lw=0.8)
    a3.set_yticks(y); a3.set_yticklabels(labels); a3.invert_yaxis()
    a3.set_xlabel('Giá trị sau hiệu chỉnh, % so với trước (đường đứng: trước = 100 %)')
    xm = max(200, a3.get_xlim()[1] + 85)
    a3.set_xlim(0, xm)
    a3.grid(axis='y', visible=False)
    tag(a3, 'c) Chỉ tiêu sau hiệu chỉnh so với trước (mô phỏng tái hiện)')
    a3.legend(loc='lower right', fontsize=7)
    save(fig, name)


# ========================================================================== Hinh 3.5 kich thich tham chieu
def fig_excitation():
    fig, axs = plt.subplots(2, 1, figsize=(W, 8.2 * CM), sharex=True, gridspec_kw=dict(hspace=0.38))
    a = axs[0]
    m = (tu > 4) & (tu < 77)
    a.plot(tu[m], L['by'][m], color=COL['yaw'], lw=0.8, label='Góc hướng khung mang')
    a.plot(tu[m], L['bp'][m], color=COL['pitch'], lw=0.8, label='Góc gật khung mang')
    a.plot(tu[m], L['br'][m], color='#1baf7a', lw=0.8, label='Góc liệng khung mang')
    seg_shade(a)
    a.set_ylabel('Góc (°)'); tag(a, 'a) Tư thế khung mang đo bởi IMU2 (log A)')
    a.set_ylim(-34, 40)
    a.legend(loc='upper center', ncol=3, fontsize=7, bbox_to_anchor=(0.5, 1.0))
    a = axs[1]
    for ax in gsim.AX:
        a.plot(T, wd[ax], color=COL[ax], lw=0.7, label=f'Chiếu lên trục {AXN[ax]}')
    seg_shade(a, labels=False)
    a.set_ylabel('Tốc độ góc (°/s)'); a.set_xlabel('Thời gian (s)')
    tag(a, 'b) Tốc độ góc khung mang dùng làm kích thích tái hiện')
    a.set_ylim(-260, 300)
    a.legend(loc='upper center', ncol=2, fontsize=7)
    a.set_xlim(4, 77)
    save(fig, 'h3_05_kich_thich')


# ========================================================================== Hinh 3.6 kiem chung mo hinh tai hien
def fig_validation():
    fig = plt.figure(figsize=(W, 10.0 * CM))
    gs = fig.add_gridspec(2, 2, hspace=0.55, wspace=0.28)
    S = R['series_final']
    wins = {'yaw': (50.0, 53.0), 'pitch': (64.0, 67.0)}
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[0, j])
        a, b = wins[ax]
        t, e = win(S, ax, a, b)
        m = (tu >= a) & (tu < b)
        a_.plot(t, e, color=COL[ax], lw=1.0, label='Mô phỏng tái hiện')
        a_.plot(tu[m], E['elog'][ax][m], color=INK, lw=0.6, marker='.', ms=2.5, label='Đo (log A)')
        a_.set_xlabel('Thời gian (s)'); a_.set_ylabel('Sai lệch góc (°)')
        tag(a_, f'{"ab"[j]}) Trục {AXN[ax]}, {C.SEG[2 if ax == "yaw" else 3][2].split(": ")[1]}')
        a_.legend(loc='upper right', fontsize=7)
        a_.set_ylim(-1.3, 1.3)
    a3 = fig.add_subplot(gs[1, :])
    V = R['val']
    x = np.arange(len(C.SEG) + 1); wbar = 0.2
    labs = [f'Đoạn {i + 1}' for i in range(len(C.SEG))] + ['Toàn bản ghi']
    for k, ax in enumerate(gsim.AX):
        meas = [d['erms'] for d in V['log_seg'][ax]] + [V['log'][ax]['erms']]
        sim = [d['erms'] for d in V['sim_seg'][ax]] + [V['sim'][ax]['erms']]
        o = (-1.5 + 2 * k) * wbar
        a3.bar(x + o, meas, wbar, color=COL[ax], label=f'{AXN[ax]}: đo (log A)', zorder=3)
        a3.bar(x + o + wbar, sim, wbar, color='white', edgecolor=COL[ax], hatch='////', lw=0.8,
               label=f'{AXN[ax]}: mô phỏng tái hiện', zorder=3)
    a3.set_xticks(x); a3.set_xticklabels(labs)
    a3.set_ylabel('e$_{rms}$ (°)'); a3.grid(axis='x', visible=False)
    tag(a3, 'c) Sai lệch hiệu dụng theo từng đoạn: đo và mô phỏng tái hiện')
    a3.legend(ncol=4, fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.12))
    save(fig, 'h3_06_kiem_chung')


# ========================================================================== Hinh 3.7 khao sat cascade
def fig_cascade_survey():
    cas = R['cascade']; Ts = R['Ts']; Tk = R['Tk']
    fig = plt.figure(figsize=(W, 8.6 * CM))
    gs = fig.add_gridspec(2, 2, hspace=0.66, wspace=0.3)
    A = {'yaw': 5.0, 'pitch': 3.0}
    chosen = {'yaw': 9.5, 'pitch': 38.0}
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[0, j])
        for i, sm in enumerate(cas[ax]['Kpt']):
            v = sm['v']; ch = v == chosen[ax]
            a_.plot((Ts - 0.5) * 1e3, np.where(Ts < 0.5, sm['y'] - A[ax], sm['y']) / A[ax], color=LIGHT[ax][[0, 2, 3][i]] if not ch else COL[ax],
                    lw=1.6 if ch else 0.9, label=f'K$_{{pθ}}$ = {vn(v, 1)} 1/s' + (' (chọn)' if ch else ''))
        a_.axhline(1, color=GREY, lw=0.6, ls=':')
        a_.set_xlim(-50, 700); a_.set_xlabel('Thời gian sau bậc (ms)'); a_.set_ylabel('θ / biên độ bậc')
        tag(a_, f'{"ab"[j]}) Bậc thang trục {AXN[ax]} ({vn(A[ax], 0)}°)')
        a_.legend(loc='lower right', fontsize=7)
    a3 = fig.add_subplot(gs[1, 0])
    for ax in gsim.AX:
        for i, sm in enumerate(cas[ax]['Kiw']):
            if sm['v'] not in (0.0, 1.0 if ax == 'yaw' else 0.5):
                continue
            ch = sm['v'] == gsim.GAINS_FINAL[ax]['Kiw']
            a3.plot(Tk - 1.0, sm['y'], color=COL[ax] if ch else LIGHT[ax][0], lw=1.4 if ch else 0.9,
                    ls='-' if ch else '--',
                    label=f'{AXN[ax]}: K$_{{iω}}$ = {vn(sm["v"], 1)}' + (' (chọn)' if ch else ''))
    a3.set_xlim(-0.2, 4.0); a3.set_xlabel('Thời gian từ khi khung quay đều 8 °/s (s)')
    a3.set_ylabel('Sai lệch góc (°)'); tag(a3, 'c) Khử sai lệch do tác động không đổi')
    a3.legend(fontsize=7, loc='lower right')
    a4 = fig.add_subplot(gs[1, 1])
    xs = np.arange(3)
    for k, ax in enumerate(gsim.AX):
        vals = [sm['bt3_erms'] for sm in cas[ax]['Kpt']]
        oss = [sm['OS'] for sm in cas[ax]['Kpt']]
        o = -0.2 + 0.4 * k
        cols = [COL[ax] if sm['v'] == chosen[ax] else LIGHT[ax][0] for sm in cas[ax]['Kpt']]
        a4.bar(xs + o, vals, 0.38, color=cols, zorder=3)
        for xi, v, os_, sm in zip(xs, vals, oss, cas[ax]['Kpt']):
            a4.text(xi + o, v + 0.1, f'{vn(os_, 1)}%', ha='center', fontsize=6.3, color='#52514e')
    a4.set_xticks(xs); a4.set_xticklabels(['6 / 20 1/s', '9,5 / 38 1/s\n(chọn)', '13 / 50 1/s'], fontsize=7)
    a4.set_ylim(0, 6.9); a4.set_ylabel('e$_{rms}$ bài thử tham chiếu (°)')
    a4.grid(axis='x', visible=False)
    a4.legend(handles=[Patch(color=COL['yaw'], label='Yaw'), Patch(color=COL['pitch'], label='Pitch')],
              fontsize=7, loc='upper right')
    tag(a4, 'd) Chọn K$_{pθ}$ Yaw / Pitch (nhãn: độ vọt lố)')
    save(fig, 'h3_07_khao_sat_cascade')


# ========================================================================== Hinh 3.8 truoc/sau cascade
def fig_cascade_real():
    fig = plt.figure(figsize=(W, 10.0 * CM))
    gs = fig.add_gridspec(2, 2, hspace=0.58, wspace=0.28)
    SL = R['step_ladder']; Ts = R['Ts']
    A = {'yaw': 5.0, 'pitch': 3.0}
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[0, j])
        a_.plot((Ts - 0.5) * 1e3, np.where(Ts < 0.5, SL['ban_dau'][ax]['y'] - A[ax], SL['ban_dau'][ax]['y']) / A[ax], color=GREY, ls='--', lw=0.9, label='Trước: Ban đầu')
        a_.plot((Ts - 0.5) * 1e3, np.where(Ts < 0.5, SL['cascade'][ax]['y'] - A[ax], SL['cascade'][ax]['y']) / A[ax], color=COL[ax], lw=1.2, label='Sau: Hiệu chỉnh nối tầng')
        a_.axhline(1, color=GREY, lw=0.6, ls=':')
        a_.set_xlim(-50, 800); a_.set_xlabel('Thời gian sau bậc (ms)'); a_.set_ylabel('θ / biên độ bậc')
        tag(a_, f'{"ab"[j]}) Bậc thang trục {AXN[ax]}')
        a_.legend(loc='lower right', fontsize=7)
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[1, j])
        a, b = (14.0, 20.0) if ax == 'yaw' else (36.0, 39.0)
        t, eb = win(R['ladder_series']['ban_dau'], ax, a, b); _, ea = win(R['ladder_series']['cascade'], ax, a, b)
        a_.plot(t, eb, color=GREY, ls='--', lw=0.8, label='Trước')
        a_.plot(t, ea, color=COL[ax], lw=1.0, label='Sau')
        a_.set_xlabel('Thời gian (s)'); a_.set_ylabel('Sai lệch góc (°)')
        tag(a_, f'{"cd"[j]}) Bài thử tham chiếu, trục {AXN[ax]}')
        a_.legend(loc='upper right', fontsize=7)
    save(fig, 'h3_08_cascade_truoc_sau')


# ========================================================================== Hinh 3.9 khao sat he so bu
def fig_ff_survey():
    ffs = R['ff_survey']
    fig = plt.figure(figsize=(W, 8.6 * CM))
    gs = fig.add_gridspec(2, 2, hspace=0.66, wspace=0.3)
    wins = {'yaw': (72.0, 74.5), 'pitch': (64.0, 66.0)}
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[0, j])
        a, b = wins[ax]
        for i, (lab, out) in enumerate(ffs[1:]):
            t, e = win(out['series'], ax, a, b)
            ch = lab.startswith('k(v)')
            a_.plot(t, e, color=COL[ax] if ch else LIGHT[ax][i if i < 3 else 0], lw=1.3 if ch else 0.8,
                    ls='-' if ch else '--', label=lab + (' (chọn)' if ch else ''))
        a_.set_xlabel('Thời gian (s)'); a_.set_ylabel('Sai lệch góc (°)')
        tag(a_, f'{"ab"[j]}) Trục {AXN[ax]}')
        a_.legend(fontsize=6.5, loc='upper right', ncol=2)
    a3 = fig.add_subplot(gs[1, 0]); a4 = fig.add_subplot(gs[1, 1])
    labs = [l for l, _ in ffs[1:]]
    x = np.arange(len(labs))
    for k, ax in enumerate(gsim.AX):
        o = -0.2 + 0.4 * k
        a3.bar(x + o, [out[ax]['erms'] for _, out in ffs[1:]], 0.38,
               color=[COL[ax] if l.startswith('k(v)') else LIGHT[ax][0] for l in labs], zorder=3)
        a4.bar(x + o, [out[ax]['uff_hold'] for _, out in ffs[1:]], 0.38,
               color=[COL[ax] if l.startswith('k(v)') else LIGHT[ax][0] for l in labs], zorder=3)
    for a_, yl, tt in [(a3, 'e$_{rms}$ (°)', 'c) Chỉ tiêu chính: sai lệch hiệu dụng'),
                       (a4, 'Độ lệch chuẩn u$_{ff}$ khi đứng yên (°/s)', 'd) Ràng buộc: nhiễu IMU2 đưa vào lệnh')]:
        a_.set_xticks(x); a_.set_xticklabels([l.replace(' theo vùng', '\ntheo vùng') for l in labs], fontsize=7)
        a_.set_ylabel(yl); tag(a_, tt); a_.grid(axis='x', visible=False)
        a_.legend(handles=[Patch(color=COL['yaw'], label='Yaw'), Patch(color=COL['pitch'], label='Pitch')], fontsize=7)
    a4.set_ylim(0, max(out[ax]['uff_hold'] for _, out in ffs[1:] for ax in gsim.AX) * 1.3)
    save(fig, 'h3_09_khao_sat_bu')


# ========================================================================== Hinh 3.11 khao sat ngoai suy
def fig_tp_survey():
    tpr = R['tp_survey']
    fig = plt.figure(figsize=(W, 8.6 * CM))
    gs = fig.add_gridspec(2, 2, hspace=0.66, wspace=0.3)
    wins = {'yaw': (50.4, 51.9), 'pitch': (64.2, 65.2)}
    show = [0.0, 0.008, 0.012, 0.020]
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[0, j])
        a, b = wins[ax]
        i = 0
        for tp, out in tpr:
            if tp not in show:
                continue
            t, e = win(out['series'], ax, a, b)
            ch = abs(tp - 0.012) < 1e-9
            a_.plot(t, e, color=COL[ax] if ch else [LIGHT[ax][0], LIGHT[ax][1], None, LIGHT[ax][3]][i],
                    lw=1.3 if ch else 0.8, ls='-' if ch else '--',
                    label=f'τ$_p$ = {tp * 1e3:.0f} ms' + (' (chọn)' if ch else ''))
            i += 1
        a_.set_xlabel('Thời gian (s)'); a_.set_ylabel('Sai lệch góc (°)')
        tag(a_, f'{"ab"[j]}) Trục {AXN[ax]}')
        a_.legend(fontsize=6.5, loc='upper right', ncol=2)
    a3 = fig.add_subplot(gs[1, 0]); a4 = fig.add_subplot(gs[1, 1])
    tp_ms = [tp * 1e3 for tp, _ in tpr]
    for ax in gsim.AX:
        a3.plot(tp_ms, [out[ax]['erms'] for _, out in tpr], color=COL[ax], marker='o', ms=4, label=f'{AXN[ax]}')
        a4.plot(tp_ms, [out[ax]['u_hf'] for _, out in tpr], color=COL[ax], marker='o', ms=4, label=f'{AXN[ax]}')
    for a_ in (a3, a4):
        a_.axvline(12, color=INK, lw=0.7, ls=':')
        a_.text(12.3, a_.get_ylim()[1] * 0.97, 'chọn 12 ms', fontsize=7, va='top')
        a_.set_xlabel('Khoảng ngoại suy τ$_p$ (ms)'); a_.legend(fontsize=7)
    a3.axvspan(8, 15, color='#f1f0ec', zorder=0, lw=0)
    a3.set_ylabel('e$_{rms}$ (°)'); tag(a3, 'c) Chỉ tiêu chính theo τ$_p$')
    a4.set_ylabel('Tỉ lệ năng lượng lệnh trên 20 Hz (%)'); tag(a4, 'd) Ràng buộc: nhiễu tần số cao trong lệnh')
    save(fig, 'h3_11_khao_sat_ngoai_suy')


# ========================================================================== Hinh 3.13 khao sat gioi han
def fig_lim_survey():
    limr = R['lim_survey']; gl = R2['glitch']; Tg = R2['Tg']
    fig = plt.figure(figsize=(W, 8.6 * CM))
    gs = fig.add_gridspec(2, 2, hspace=0.66, wspace=0.3)
    wins = {'yaw': (72.6, 74.0), 'pitch': (65.0, 65.6)}
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[0, j])
        a, b = wins[ax]
        for i, (lab, out) in enumerate(limr):
            if lab.startswith('Cố định 165'):
                continue
            t, u = win(out['series'], ax, a, b, key='u')
            ch = lab == 'Theo vùng'
            a_.plot(t, u, color=COL[ax] if ch else LIGHT[ax][[0, 1, 3][min(i, 2)]], lw=1.3 if ch else 0.8,
                    ls='-' if ch else '--', label=lab + (' (chọn)' if ch else ''))
        m = (T >= a) & (T < b)
        a_.plot(T[m], -wd[ax][m], color=INK, lw=0.6, ls=':', label='Lệnh cần để bù (−ω$_b$)')
        a_.set_xlabel('Thời gian (s)'); a_.set_ylabel('Lệnh tốc độ (°/s)')
        tag(a_, f'{"ab"[j]}) Lệnh trục {AXN[ax]} ở đoạn nhanh nhất')
        a_.legend(fontsize=6.3, loc='lower left')
    a3 = fig.add_subplot(gs[1, 0])
    labs = [l for l, _ in limr]; x = np.arange(len(labs))
    for k, ax in enumerate(gsim.AX):
        o = -0.2 + 0.4 * k
        a3.bar(x + o, [out[ax]['emax'] for _, out in limr], 0.38,
               color=[COL[ax] if l == 'Theo vùng' else LIGHT[ax][0] for l in labs], zorder=3)
        for xi, (_, out) in zip(x, limr):
            a3.text(xi + o, out[ax]['emax'] + 0.1, f'ρ {vn(out[ax]["rho"], 1)}%', ha='center', fontsize=6, rotation=90, va='bottom', color='#52514e')
    a3.set_xticks(x); a3.set_xticklabels([l.replace(' °/s', '').replace('Cố định', 'Cố định\n') for l in labs], fontsize=7)
    a3.set_ylabel('e$_{max}$ (°)'); a3.grid(axis='x', visible=False); a3.set_ylim(0, 8.5)
    tag(a3, 'c) Sai lệch lớn nhất và tỉ lệ bão hòa ρ')
    a3.legend(handles=[Patch(color=COL['yaw'], label='Yaw'), Patch(color=COL['pitch'], label='Pitch')], fontsize=7)
    a4 = fig.add_subplot(gs[1, 1])
    for lab, ls, col in [('Cố định 410 °/s', '--', LIGHT['yaw'][1]), ('Theo vùng', '-', COL['yaw'])]:
        s = gl[lab]['series']['yaw']
        a4.plot((Tg - 0.5) * 1e3, s['e'], color=col, ls=ls, lw=1.1 if ls == '-' else 0.9, label=lab)
    a4.set_xlim(-20, 250); a4.set_xlabel('Thời gian từ mẫu IMU2 lỗi (ms)'); a4.set_ylabel('Sai lệch góc Yaw (°)')
    tag(a4, 'd) Ràng buộc an toàn: 3 mẫu IMU2 lỗi khi đứng yên'); a4.legend(fontsize=7)
    save(fig, 'h3_13_khao_sat_gioi_han')


# ========================================================================== Hinh 3.15 khao sat dao chieu / dung
def fig_rev_survey():
    revs = R['rev_survey']; stp = R2['stop_test']
    fig = plt.figure(figsize=(W, 10.0 * CM))
    gs = fig.add_gridspec(2, 2, hspace=0.62, wspace=0.3)
    a1 = fig.add_subplot(gs[0, 0]); a2 = fig.add_subplot(gs[0, 1])
    base = [o for p, o in revs if p[0] == 'none'][0]
    items = [(p, o) for p, o in revs if p[0] != 'none']
    labs = [f'{p[0] * 1e3:.0f} ms\n{p[1]:.0f}' for p, _ in items]
    x = np.arange(len(items))
    for k, ax in enumerate(gsim.AX):
        o = -0.2 + 0.4 * k
        ch = [(p[0] == 0.010 and p[1] == 1000.0) for p, _ in items]
        a1.bar(x + o, [(oo[ax]['erms'] / base[ax]['erms'] - 1) * 100 for _, oo in items], 0.38,
               color=[COL[ax] if c else LIGHT[ax][0] for c in ch], zorder=3)
        a2.bar(x + o, [(oo[ax]['signchg'] / base[ax]['signchg'] - 1) * 100 for _, oo in items], 0.38,
               color=[COL[ax] if c else LIGHT[ax][0] for c in ch], zorder=3)
    for a_, yl, tt in [(a1, 'Thay đổi e$_{rms}$ (%)', 'a) Ảnh hưởng tới sai lệch hiệu dụng'),
                       (a2, 'Thay đổi số lần lệnh đổi dấu (%)', 'b) Ảnh hưởng tới số lần lệnh đổi dấu')]:
        a_.axhline(0, color=INK, lw=0.7)
        a_.set_xticks(x); a_.set_xticklabels(labs, fontsize=6.5)
        a_.set_xlabel('t$_{0max}$ / α$_{rev}$ (°/s²)'); a_.set_ylabel(yl); tag(a_, tt)
        a_.grid(axis='x', visible=False)
        a_.legend(handles=[Patch(color=COL['yaw'], label='Yaw'), Patch(color=COL['pitch'], label='Pitch')], fontsize=7)
    for j, ax in enumerate(gsim.AX):
        a_ = fig.add_subplot(gs[1, j])
        for lab, ls, col in [('Không xử lý dừng', '--', GREY), ('Có chế độ dừng', '-', COL[ax])]:
            s = stp[lab][ax]['series']
            a_.plot(s['T'], s['e'], color=col, ls=ls, lw=1.1 if ls == '-' else 0.9, label=lab)
        a_.axvline(0, color=INK, lw=0.6, ls=':')
        a_.set_xlim(-0.3, 1.0); a_.set_xlabel('Thời gian từ khi khung mang dừng (s)'); a_.set_ylabel('Sai lệch góc (°)')
        tag(a_, f'{"cd"[j]}) Bài thử dừng đột ngột, trục {AXN[ax]}'); a_.legend(fontsize=7)
    save(fig, 'h3_15_khao_sat_dao_chieu_dung')


# ========================================================================== Hinh 3.17 khao sat tao dang
def fig_shape_survey():
    shp = R2['shape_survey']; tr = R2['shape_traj']
    fig = plt.figure(figsize=(W, 8.6 * CM))
    gs = fig.add_gridspec(2, 2, hspace=0.66, wspace=0.3)
    a1 = fig.add_subplot(gs[0, 0])
    a1.step(tr['T'] * 1e3, tr['req'], where='post', color=GREY, ls='--', lw=0.9, label='Lệnh yêu cầu')
    a1.plot(tr['T'] * 1e3, tr['a18'], color=LIGHT['yaw'][1], lw=0.9, ls='--', label='a$_{max}$ = 18 000 °/s²')
    a1.plot(tr['T'] * 1e3, tr['a30'], color=COL['yaw'], lw=1.3, label='a$_{max}$ = 30 000 °/s² (khi đảo chiều)')
    a1.set_xlabel('Thời gian (ms)'); a1.set_ylabel('Lệnh tốc độ (°/s)'); a1.legend(fontsize=6.5, loc='upper right')
    tag(a1, 'a) Đổi lệnh +300 → −300 °/s')
    a2 = fig.add_subplot(gs[0, 1])
    base = shp[0][1]; ch = shp[3][1]
    for ax in gsim.AX:
        pass
    S0 = R['ladder_series']['dao_chieu']; S1 = R['ladder_series']['tao_dang']
    mm = (T >= C.WIN[0]) & (T < C.WIN[1])
    bins = np.linspace(0, 55, 45)
    a2.hist(np.abs(S0['pitch']['du'][mm]), bins=bins, color=GREY, alpha=0.6, label='Không tạo dạng', log=True)
    a2.hist(np.abs(S1['pitch']['du'][mm]), bins=bins, histtype='step', color=COL['pitch'], lw=1.2, label='Có tạo dạng', log=True)
    a2.set_xlabel('Bước lệnh trong một chu kỳ 2 ms (°/s)'); a2.set_ylabel('Số mẫu'); a2.legend(fontsize=7)
    tag(a2, 'b) Phân bố bước lệnh trục Pitch')
    a3 = fig.add_subplot(gs[1, 0]); a4 = fig.add_subplot(gs[1, 1])
    labs = ['Không\ngiới hạn', '18 000\ncố định', '30 000\ncố định', '18 000 /\n30 000']
    x = np.arange(4)
    for k, ax in enumerate(gsim.AX):
        o = -0.2 + 0.4 * k
        cols = [LIGHT[ax][0]] * 3 + [COL[ax]]
        a3.bar(x + o, [out[ax]['dumax'] for _, out in shp], 0.38, color=cols, zorder=3)
        a4.bar(x + o, [out[ax]['erms'] for _, out in shp], 0.38, color=cols, zorder=3)
    for a_, yl, tt in [(a3, 'Bước lệnh lớn nhất (°/s)', 'c) Chỉ tiêu chính: bước lệnh lớn nhất'),
                       (a4, 'e$_{rms}$ (°)', 'd) Ràng buộc: sai lệch hiệu dụng')]:
        a_.set_xticks(x); a_.set_xticklabels(labs, fontsize=7); a_.set_ylabel(yl); tag(a_, tt)
        a_.grid(axis='x', visible=False)
        a_.legend(handles=[Patch(color=COL['yaw'], label='Yaw'), Patch(color=COL['pitch'], label='Pitch')], fontsize=7)
    save(fig, 'h3_17_khao_sat_tao_dang')


# ========================================================================== Hinh 3.19 khao sat lich RS485
def fig_bus_survey():
    bus = R2['bus_sched']; bc = R2['bus_closed']
    fig = plt.figure(figsize=(W, 5.8 * CM))
    gs = fig.add_gridspec(1, 2, wspace=0.3)
    a1 = fig.add_subplot(gs[0, 0])
    for mode, ls, lab in [('yawpri', '--', 'Ưu tiên Yaw'), ('alt', '-', 'Luân phiên')]:
        for ax in gsim.AX:
            g = np.sort(bus[mode][ax]['gaps']); p = 1 - np.arange(len(g)) / len(g)
            a1.semilogy(g, p, color=COL[ax], ls=ls, lw=1.1, label=f'{lab}, {AXN[ax]}')
    a1.set_xlim(0, 36); a1.set_ylim(1e-4, 1.1)
    a1.set_xlabel('Khoảng cập nhật lệnh Δ (ms)'); a1.set_ylabel('Xác suất vượt P(Δ > x)')
    a1.legend(fontsize=6.5); tag(a1, 'a) Phân bố khoảng cập nhật')
    a2 = fig.add_subplot(gs[0, 1])
    x = np.arange(2)
    for k, ax in enumerate(gsim.AX):
        o = -0.2 + 0.4 * k
        a2.bar(x + o, [bc[('yawpri', 0.012)][ax]['erms'], bc[('alt', 0.012)][ax]['erms']], 0.38,
               color=[LIGHT[ax][0], COL[ax]], zorder=3)
        for xi, mode in enumerate(('yawpri', 'alt')):
            for tp, mk in [(0.008, 'v'), (0.016, '^')]:
                a2.plot(xi + o, bc[(mode, tp)][ax]['erms'], marker=mk, color=INK, ms=3.5, lw=0, zorder=6)
    a2.set_xticks(x); a2.set_xticklabels(['Ưu tiên Yaw', 'Luân phiên']); a2.grid(axis='x', visible=False)
    a2.set_ylabel('e$_{rms}$ (°)')
    a2.legend(handles=[Patch(color=COL['yaw'], label='Yaw'), Patch(color=COL['pitch'], label='Pitch'),
                       Line2D([], [], marker='v', lw=0, color=INK, label='τ$_p$ = 8 ms'),
                       Line2D([], [], marker='^', lw=0, color=INK, label='τ$_p$ = 16 ms')], fontsize=6.5, ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.12))
    tag(a2, 'b) Sai lệch với hai lịch (cột: τ$_p$ = 12 ms)')
    save(fig, 'h3_19_khao_sat_rs485')


# ========================================================================== Hinh 3.21 log A toan ban ghi
def fig_final_log():
    fig, axs = plt.subplots(3, 1, figsize=(W, 10.0 * CM), sharex=True, gridspec_kw=dict(hspace=0.35, height_ratios=[1, 1, 1]))
    m = (tu > 4) & (tu < 77)
    a = axs[0]
    a.plot(tu[m], L['by'][m], color=COL['yaw'], lw=0.7, label='Góc hướng khung mang')
    a.plot(tu[m], L['bp'][m], color=COL['pitch'], lw=0.7, label='Góc gật khung mang')
    seg_shade(a); a.set_ylabel('Góc (°)'); a.set_ylim(-34, 52); a.legend(fontsize=7, ncol=2, loc='upper center')
    tag(a, 'a) Chuyển động khung mang')
    V = R['val']
    for j, ax in enumerate(gsim.AX):
        a = axs[j + 1]
        a.plot(tu[m], E['elog'][ax][m], color=COL[ax], lw=0.6)
        seg_shade(a, labels=False)
        for i, (s0, s1, _) in enumerate(C.SEG):
            a.text((s0 + s1) / 2, 0.93, vn(V['log_seg'][ax][i]['erms'], 3) + '°', transform=a.get_xaxis_transform(),
                   ha='center', fontsize=7, color='#52514e')
        a.set_ylim(-1.0, 1.0); a.set_ylabel('Sai lệch (°)')
        a.axhline(0, color=GREY, lw=0.5)
        tag(a, f'{"bc"[j]}) Sai lệch góc trục {AXN[ax]} (nhãn: e$_{{rms}}$ từng đoạn)')
    axs[-1].set_xlabel('Thời gian (s)'); axs[-1].set_xlim(4, 77)
    save(fig, 'h3_21_log_hoan_thien')


# ========================================================================== Hinh 3.22 qua trinh hoan thien
def fig_progress():
    fig, axs = plt.subplots(1, 2, figsize=(W, 6.6 * CM), gridspec_kw=dict(wspace=0.3))
    x = np.arange(len(ORDER))
    V = R['val']
    for a_, key, tt in [(axs[0], 'erms', 'a) Sai lệch hiệu dụng e$_{rms}$'), (axs[1], 'p99', 'b) Phân vị 99 % của |e|')]:
        for ax in gsim.AX:
            vals = [R['ladder'][n][ax][key] for n in ORDER]
            a_.semilogy(x, vals, color=COL[ax], marker='o', ms=4, lw=1.2, label=f'{AXN[ax]}: mô phỏng tái hiện')
            a_.plot(x[-1] + 0.12, V['log'][ax][key], marker='D', ms=5, color=COL[ax], mec=INK, mew=0.8, lw=0,
                    label=f'{AXN[ax]}: đo (log A)')
        a_.set_xticks(x); a_.set_xticklabels([NAMES[n] for n in ORDER], rotation=40, ha='right', fontsize=7)
        a_.set_ylabel('Độ (°), thang log'); tag(a_, tt)
        from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
        tk = [0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20]
        a_.yaxis.set_major_locator(FixedLocator(tk)); a_.yaxis.set_minor_locator(NullLocator())
        a_.yaxis.set_major_formatter(FuncFormatter(lambda v, p: _comma(v, p)))
        a_.set_ylim(0.12, 16)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=4, fontsize=7, loc='lower center', bbox_to_anchor=(0.5, -0.24))
    save(fig, 'h3_22_qua_trinh_hoan_thien')


def all_before_after():
    W3 = {'yaw': (72.0, 75.0), 'pitch': (64.0, 66.5)}
    before_after('h3_10_bu_imu2_truoc_sau', 'cascade', 'bu_imu2', {'yaw': (14.0, 20.0), 'pitch': (36.0, 39.0)},
                 ['erms', 'p99', 'emax'], ['e$_{rms}$', 'Phân vị 99 % |e|', 'e$_{max}$'])
    before_after('h3_12_ngoai_suy_truoc_sau', 'bu_imu2', 'ngoai_suy', {'yaw': (50.4, 52.4), 'pitch': (64.2, 65.7)},
                 ['erms', 'p99', 'emax'], ['e$_{rms}$', 'Phân vị 99 % |e|', 'e$_{max}$'])
    before_after('h3_14_gioi_han_truoc_sau', 'ngoai_suy', 'gioi_han', {'yaw': (72.4, 74.4), 'pitch': (64.6, 66.0)},
                 ['erms', 'p99', 'emax', 'rho'], ['e$_{rms}$', 'Phân vị 99 % |e|', 'e$_{max}$', 'Tỉ lệ bão hòa ρ'])
    before_after('h3_16_dao_chieu_truoc_sau', 'gioi_han', 'dao_chieu', {'yaw': (72.4, 74.4), 'pitch': (64.6, 66.0)},
                 ['erms', 'p99', 'emax', 'signchg'], ['e$_{rms}$', 'Phân vị 99 % |e|', 'e$_{max}$', 'Số lần lệnh đổi dấu'])
    before_after('h3_18_tao_dang_truoc_sau', 'dao_chieu', 'tao_dang', {'yaw': (72.4, 74.4), 'pitch': (64.6, 66.0)},
                 ['dumax', 'du99', 'erms', 'emax'], ['Bước lệnh lớn nhất', 'Phân vị 99 % bước lệnh', 'e$_{rms}$', 'e$_{max}$'])
    before_after('h3_20_rs485_truoc_sau', 'tao_dang', 'hoan_thien', {'yaw': (50.4, 52.4), 'pitch': (64.2, 65.7)},
                 ['erms', 'p99', 'emax'], ['e$_{rms}$', 'Phân vị 99 % |e|', 'e$_{max}$'], extra_log=True)


if __name__ == '__main__':
    fig_excitation(); fig_validation(); fig_cascade_survey(); fig_cascade_real()
    fig_ff_survey(); fig_tp_survey(); fig_lim_survey(); fig_rev_survey(); fig_shape_survey()
    fig_bus_survey(); fig_final_log(); fig_progress(); all_before_after()
    print('ok', sorted(os.listdir(OUT)))
