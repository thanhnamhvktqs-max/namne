"""Ve lai toan bo hinh Chuong 3 theo mot chuan chung.

Chuan trinh bay:
- Bo cuc theo cm, hinh chen vao Word dung kich thuoc that (rong <= 15,8 cm), 600 dpi.
- Liberation Serif (cung kich thuoc chu Times New Roman): vach chia 10 pt, ten truc 11 pt, chu giai 10 pt,
  ten hinh con 11 pt, dat can giua ngay duoi tung hinh con.
- Yaw: ho mau xanh lam, Pitch: ho mau cam (nhat / chinh / dam).
- Truoc hieu chinh: net dut den; sau hieu chinh va phuong an chon: net lien mau chinh, day nhat.
  Gia tri thap hon: mau nhat, net dut; gia tri cao hon: mau dam, net cham gach; cac duong mong ve de len
  duong day de khong bi che khi trung nhau. So do (log A): cham tron rong mau den.
- Chu giai luon nam trong dai rieng phia tren hinh con, khong dat trong vung du lieu.
"""
import sys, pickle, os, io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import ticker as mt
from matplotlib import transforms as mtr
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerTuple
from PIL import Image
sys.path.insert(0, '.')
import gsim
import common as C

OUT = sys.argv[1] if len(sys.argv) > 1 else 'figs'
os.makedirs(OUT, exist_ok=True)
R = pickle.load(open('results.pkl', 'rb'))
R2 = pickle.load(open('results2.pkl', 'rb'))
E = C.exc(); T = E['T']; wd = E['wd']; L = E['log']; tu = L['tu']
AX = gsim.AX
AXN = {'yaw': 'Yaw', 'pitch': 'Pitch'}
ORDER = [n for n, _ in gsim.LADDER]

# ============================================================================ chuan chung
CM = 1 / 2.54
FW = 15.8                      # chieu rong thiet ke (cm), vua be rong trang 16 cm
LM, GC, RM = 1.75, 1.95, 0.3   # le trai, khoang giua hai cot, le phai (cm)
PW = (FW - LM - GC - RM) / 2   # be rong mot hinh con (cm)
TWO = [(LM, PW), (LM + PW + GC, PW)]
ONE = [(LM, FW - LM - RM)]
BOT = 1.22                     # dai vach chia + ten truc x
BOT2 = 1.62                    # vach chia hai dong + ten truc x
BOT0 = 0.72                    # chi co vach chia
CAPH = 0.62                    # dong ten hinh con
GAPR = 0.28                    # khoang cach giua hai hang
LEG1, LEG2 = 0.62, 1.1         # dai chu giai mot / hai dong
YLAB = 1.32                    # khoang cach ten truc y toi truc (cm)
FS_TICK, FS_LAB, FS_LEG, FS_CAP, FS_ANN = 10, 11, 10, 11, 10

PAL = {'yaw': dict(light='#4a90e2', main='#1a5bb5', dark='#0a2a5e'),
       'pitch': dict(light='#f0883a', main='#c94a10', dark='#6b2305')}
INK = '#000000'
SHADE = '#efefef'              # to nen cac doan le cua bai thu
HILITE = '#e3e3e3'             # nen cua phuong an chon tren bieu do
DASH = (0, (5.0, 2.4))
DASHDOT = (0, (8.0, 2.2, 1.8, 2.2))
DOT = (0, (1.3, 1.9))
LW_CH, LW_ALT, LW_BEF = 2.2, 1.5, 1.4
LW_SEL, LW_OPT = 2.7, 1.3   # khao sat: duong chon day, phuong an khac mong ve de len tren
SINV = 's$^{\\mathrm{-1}}$'    # don vi s^-1 (chu dung)

BEFORE = dict(color=INK, lw=LW_BEF, ls=DASH)
MEAS = dict(ls='none', marker='o', ms=3.4, mfc='white', mec=INK, mew=0.9)
REF = dict(color='#4d4d4d', lw=1.0, ls=DOT)
Z = {'chosen': 3, 'low': 4, 'high': 5}    # duong mong ve de len duong day


def after(ax):
    return dict(color=PAL[ax]['main'], lw=LW_CH, ls='-')


def opt(ax, kind):
    """Kieu duong cho phuong an khao sat: 'low', 'chosen', 'high'."""
    return {'low': dict(color=PAL[ax]['light'], lw=LW_OPT, ls=DASH),
            'chosen': dict(color=PAL[ax]['main'], lw=LW_SEL, ls='-'),
            'high': dict(color=PAL[ax]['dark'], lw=LW_OPT, ls=DASHDOT)}[kind]


plt.rcParams.update({
    'font.family': 'Liberation Serif', 'font.size': FS_LAB,
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Serif', 'mathtext.it': 'Liberation Serif:italic',
    'mathtext.bf': 'Liberation Serif:bold', 'mathtext.sf': 'Liberation Serif', 'mathtext.cal': 'Liberation Serif:italic',
    'mathtext.tt': 'Liberation Mono', 'mathtext.default': 'it',
    'axes.labelsize': FS_LAB, 'xtick.labelsize': FS_TICK, 'ytick.labelsize': FS_TICK, 'legend.fontsize': FS_LEG,
    'text.color': INK, 'axes.labelcolor': INK, 'xtick.labelcolor': INK, 'ytick.labelcolor': INK,
    'axes.edgecolor': '#333333', 'xtick.color': '#333333', 'ytick.color': '#333333',
    'axes.linewidth': 0.8, 'xtick.major.width': 0.8, 'ytick.major.width': 0.8,
    'xtick.major.size': 3.2, 'ytick.major.size': 3.2, 'xtick.major.pad': 2.6, 'ytick.major.pad': 2.6,
    'xtick.minor.visible': False, 'ytick.minor.visible': False,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.color': '#d4d4d4', 'grid.linewidth': 0.6, 'axes.axisbelow': True,
    'axes.labelpad': 3.0, 'axes.unicode_minus': True, 'axes.facecolor': 'white', 'figure.facecolor': 'white',
    'legend.frameon': False, 'legend.handlelength': 2.8, 'legend.handletextpad': 0.5,
    'legend.columnspacing': 1.6, 'legend.borderaxespad': 0.0, 'legend.borderpad': 0.1, 'legend.labelspacing': 0.35,
    'lines.linewidth': LW_ALT, 'lines.scale_dashes': False, 'lines.dash_capstyle': 'butt',
    'lines.solid_capstyle': 'round', 'lines.solid_joinstyle': 'round',
    'hatch.linewidth': 0.9, 'patch.linewidth': 0.8, 'savefig.dpi': 600,
})


def num(v, nd):
    return f'{v:.{nd}f}'.replace('-', '−').replace('.', ',')


class Comma(mt.ScalarFormatter):
    """Vach chia dung dau phay thap phan."""

    def __init__(self):
        super().__init__(useOffset=False)

    def __call__(self, x, pos=None):
        return super().__call__(x, pos).replace('.', ',')


# ---------------------------------------------------------------------------- bo cuc theo cm
def new_fig(rows, width=FW):
    """rows: moi hang {cols:[(x0,w)], h, top, bot, cap, gap} (cm). Tra ve fig va thong tin tung hang."""
    H = 0.0
    for i, r in enumerate(rows):
        H += r.get('top', 0) + r['h'] + r.get('bot', BOT) + r.get('cap', CAPH)
        if i < len(rows) - 1:
            H += r.get('gap', GAPR)
    fig = plt.figure(figsize=(width * CM, H * CM))
    y = H; geo = []
    for i, r in enumerate(rows):
        top = r.get('top', 0); h = r['h']; bot = r.get('bot', BOT); cap = r.get('cap', CAPH)
        yt = y - top; yb = yt - h
        axs = []
        for x0, w in r['cols']:
            a = fig.add_axes([x0 / width, yb / H, w / width, h / H])
            a._wcm = w; a._hcm = h
            axs.append(a)
        geo.append(dict(axes=axs, cols=r['cols'], band=(y - top / 2) / H, band_top=y / H, cap=(yb - bot) / H,
                        yt=yt / H, yb=yb / H))
        y = yb - bot - cap - r.get('gap', GAPR)
    fig._W = width; fig._H = H
    return fig, geo


def band_y(fig, g, offset_cm):
    """Tung do (phan so hinh) cach mep tren dai chu giai offset_cm."""
    return (g['band_top'] * fig._H - offset_cm) / fig._H


def subcap(fig, g, j, text, xc=None):
    """Ten hinh con can giua duoi hinh con j (hoac tai hoanh do xc, cm)."""
    if xc is None:
        x0, w = g['cols'][j]; xc = x0 + w / 2
    fig.text(xc / fig._W, g['cap'], text, ha='center', va='top', fontsize=FS_CAP)


def band_legend(fig, g, handles, labels, ncol=None, cx=None, y=None, hl=None, **kw):
    """Chu giai dat trong dai phia tren hang g, can giua tai cx (cm); tu dich vao trong khung hinh."""
    if cx is None:
        x0 = g['cols'][0][0]; x1 = g['cols'][-1][0] + g['cols'][-1][1]
        cx = (x0 + x1) / 2
    yy = g['band'] if y is None else y
    lg = fig.legend(handles, labels, loc='center', bbox_to_anchor=(cx / fig._W, yy),
                    ncol=ncol or len(labels), handler_map={tuple: HandlerTuple(ndivide=None, pad=0.3)},
                    handlelength=hl or plt.rcParams['legend.handlelength'], **kw)
    fig.canvas.draw()
    bb = lg.get_window_extent(fig.canvas.get_renderer())
    px_cm = fig.bbox.width / fig._W
    lo, hi = bb.x0 / px_cm, bb.x1 / px_cm
    shift = 0.0
    if hi > fig._W - 0.05:
        shift = fig._W - 0.05 - hi
    elif lo < 0.05:
        shift = 0.05 - lo
    if shift:
        lg.set_bbox_to_anchor(((cx + shift) / fig._W, yy), transform=fig.transFigure)
    return lg


def tup(styles):
    return tuple(Line2D([], [], **s) for s in styles)


def key_patches(chosen=True):
    h = [Patch(facecolor=PAL['yaw']['main'], edgecolor='none'), Patch(facecolor=PAL['pitch']['main'], edgecolor='none')]
    l = ['Trục Yaw', 'Trục Pitch']
    if chosen:
        h.append(Patch(facecolor=HILITE, edgecolor='#9a9a9a', lw=0.6)); l.append('Phương án chọn')
    return h, l


def hilite(a, x, horiz=False, width=0.92):
    """Danh dau nhom duoc chon: nen xam va nhan vach chia in dam."""
    if horiz:
        a.axhspan(x - width / 2, x + width / 2, color=HILITE, lw=0, zorder=0)
    else:
        a.axvspan(x - width / 2, x + width / 2, color=HILITE, lw=0, zorder=0)
    (a.get_yticklabels() if horiz else a.get_xticklabels())[x].set_fontweight('bold')


def bar_axes(a, horiz=False):
    a.grid(axis='y' if horiz else 'x', visible=False)
    a.tick_params(axis='y' if horiz else 'x', length=0)


def time_axes(a, nb=5):
    a.yaxis.set_major_locator(mt.MaxNLocator(nb, steps=[1, 2, 2.5, 5, 10]))


def seg_shade(a):
    for i, (s0, s1, _) in enumerate(C.SEG):
        if i % 2 == 0:
            a.axvspan(s0, s1, color=SHADE, lw=0, zorder=0)


def seg_header(a, dy=0.06):
    for i, (s0, s1, _) in enumerate(C.SEG):
        a.text((s0 + s1) / 2, 1.0 + dy / a._hcm, f'Đoạn {i + 1}', transform=a.get_xaxis_transform(),
               ha='center', va='bottom', fontsize=FS_ANN)


def symlim(a, *arrs, k=1.08):
    m = max(np.abs(x).max() for x in arrs) * k
    a.set_ylim(-m, m)


def best_window(ser, alts, chosen, length, segs, step=0.1):
    """Cua so dai length (s) trong cac doan segs de moi phuong an deu khac phuong an chon ro nhat."""
    best = (-1, None)
    for s0, s1 in segs:
        t = s0
        while t + length <= s1 + 1e-9:
            m = (T >= t) & (T < t + length)
            sc = min(np.sqrt(np.mean((ser[k][m] - ser[chosen][m]) ** 2)) for k in alts)
            if sc > best[0]:
                best = (sc, t)
            t += step
    return best[1], best[1] + length


SEG_AX = {'yaw': [C.SEG[i][:2] for i in (0, 2, 4)], 'pitch': [C.SEG[i][:2] for i in (1, 3)]}


# ---------------------------------------------------------------------------- kiem tra va xuat hinh
def _texts(fig, r):
    out = []
    for a in fig.axes:
        for axis in (a.xaxis, a.yaxis):
            for tk in axis._update_ticks():
                for lab in (tk.label1, tk.label2):
                    if lab.get_visible() and lab.get_text().strip():
                        out.append(('tick', lab, lab.get_window_extent(r)))
            if axis.label.get_text().strip():
                out.append(('label', axis.label, axis.label.get_window_extent(r)))
        for t in a.texts:
            if t.get_visible() and t.get_text().strip():
                out.append(('atext', t, t.get_window_extent(r)))
    for t in fig.texts:
        if t.get_text().strip():
            out.append(('ftext', t, t.get_window_extent(r)))
    for lg in fig.legends + [a.get_legend() for a in fig.axes if a.get_legend()]:
        out.append(('legend', lg, lg.get_window_extent(r)))
    return out


def _name(t):
    return t.get_text() if hasattr(t, 'get_text') else 'legend'


def check(fig, name):
    """Bao cao chu chong chu, chu giai / chu nam trong vung ve, chu ra ngoai khung hinh."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items = _texts(fig, r)
    issues = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            (ka, ta, A), (kb, tb, B) = items[i], items[j]
            ix = min(A.x1, B.x1) - max(A.x0, B.x0); iy = min(A.y1, B.y1) - max(A.y0, B.y0)
            if ix > 0.5 and iy > 0.5:
                issues.append(f'chong: [{ka}] {_name(ta)!r} / [{kb}] {_name(tb)!r}')
    for kind, t, bb in items:
        if kind in ('legend', 'ftext', 'atext'):
            for a in fig.axes:
                ab = a.get_window_extent(r)
                ix = min(ab.x1, bb.x1) - max(ab.x0, bb.x0); iy = min(ab.y1, bb.y1) - max(ab.y0, bb.y0)
                if ix > 0.5 and iy > 0.5:
                    issues.append(f'{kind} nam trong vung ve: {_name(t)!r}')
    fb = fig.bbox
    for kind, t, bb in items:
        if bb.x0 < fb.x0 - 1 or bb.x1 > fb.x1 + 1 or bb.y0 < fb.y0 - 1 or bb.y1 > fb.y1 + 1:
            issues.append(f'ra ngoai khung hinh: [{kind}] {_name(t)!r}')
    print(f'{name}: {"khong co van de" if not issues else ""}')
    for s in issues:
        print('   ', s)
    return issues


def finish(fig, name):
    for a in fig.axes:
        for axis, sc in ((a.xaxis, a.get_xscale()), (a.yaxis, a.get_yscale())):
            if sc == 'linear' and type(axis.get_major_formatter()) is mt.ScalarFormatter:
                axis.set_major_formatter(Comma())
        if a.get_ylabel() and hasattr(a, '_wcm'):
            a.yaxis.set_label_coords(-YLAB / a._wcm, 0.5)
    check(fig, name)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, bbox_inches='tight', pad_inches=0.04, facecolor='white')
    plt.close(fig)
    # bang mau 256 mau, khong khu nhieu: nhe hon ~2,5 lan, sai khac khong nhin thay (PSNR > 55 dB)
    im = Image.open(buf).convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + '.png'), optimize=True, dpi=(600, 600))


# ============================================================================ khuon hinh truoc / sau
MLAB = {'erms': '$e_{\\mathrm{rms}}$ (°)', 'p99': 'Phân vị 99 % $|e|$ (°)', 'emax': '$e_{\\mathrm{max}}$ (°)',
        'rho': '$\\rho_{\\mathrm{sat}}$ (%)', 'signchg': 'Số lần lệnh\nđổi dấu', 'dumax': 'Bước lệnh\nlớn nhất (°/s)',
        'du99': 'Phân vị 99 %\nbước lệnh (°/s)'}
MND = {'erms': 3, 'p99': 3, 'emax': 2, 'rho': 2, 'signchg': 0, 'dumax': 1, 'du99': 2}   # nhu cac bang


def _chg(vb, va):
    d = (va / vb - 1) * 100 if vb else 0.0
    if abs(d) < 0.05:
        return '0,0 %'
    return ('+' if d > 0 else '−') + num(abs(d), 1) + ' %'


def before_after(name, before, after_, windows, metrics, extra_log=False):
    nm = len(metrics)
    ax0, axw = 3.9, 6.9          # hinh con c): le trai rong cho ten chi tieu, cot gia tri ben phai
    rows = [dict(cols=TWO, h=3.0, top=LEG1), dict(cols=[(ax0, axw)], h=0.82 * nm + 0.2, top=LEG1)]
    fig, G = new_fig(rows)
    Sb = R['ladder_series'][before]; Sa = R['ladder_series'][after_]
    for j, ax in enumerate(AX):
        a = G[0]['axes'][j]
        t0, t1 = windows[ax]
        m = (T >= t0) & (T < t1)
        a.plot(T[m], Sa[ax]['e'][m], **after(ax), zorder=3)
        a.plot(T[m], Sb[ax]['e'][m], **BEFORE, zorder=4)
        arrs = [Sa[ax]['e'][m], Sb[ax]['e'][m]]
        if extra_log:
            ml = (tu >= t0) & (tu < t1)
            a.plot(tu[ml], E['elog'][ax][ml], **MEAS, zorder=5)
            arrs.append(E['elog'][ax][ml])
        symlim(a, *arrs); time_axes(a)
        a.set_xlim(t0, t1)
        a.set_xlabel('Thời gian (s)'); a.set_ylabel('Sai lệch góc (°)')
        subcap(fig, G[0], j, f'{"ab"[j]}) Trục {AXN[ax]}')
    h = [Line2D([], [], **BEFORE), tup([after('yaw'), after('pitch')])]
    lab = ['Trước hiệu chỉnh', 'Sau hiệu chỉnh']
    if extra_log:
        h.append(Line2D([], [], **MEAS)); lab.append('Đo (log A)')
    band_legend(fig, G[0], h, lab, hl=3.6, numpoints=3)
    # c) chi tieu sau / truoc (%)
    a = G[1]['axes'][0]
    Mb = R['ladder'][before]; Ma = R['ladder'][after_]
    y = np.arange(nm); vmax = 100.0
    tr = mtr.blended_transform_factory(a.transAxes, a.transData)
    for ax in AX:
        off = -0.2 if ax == 'yaw' else 0.2
        vals = []
        for i, key in enumerate(metrics):
            vb = Mb[ax][key]; va = Ma[ax][key]
            v = va / vb * 100 if vb else 100.0
            vals.append(v); vmax = max(vmax, v)
            nd = MND[key]
            a.text(1.04, i + off, f'{num(vb, nd)} → {num(va, nd)} ({_chg(vb, va)})', transform=tr,
                   ha='left', va='center', fontsize=FS_ANN, color=PAL[ax]['dark'])
        a.barh(y + off, vals, height=0.36, color=PAL[ax]['main'], zorder=3)
    a.axvline(100, color=INK, lw=1.1, zorder=4)
    a.set_yticks(y); a.set_yticklabels([MLAB[k] for k in metrics]); a.set_ylim(nm - 0.45, -0.55)
    xm = max(125.0, np.ceil((vmax + 6) / 25) * 25)
    a.set_xlim(0, xm); a.xaxis.set_major_locator(mt.MultipleLocator(25))
    a.set_xlabel('Giá trị sau hiệu chỉnh so với trước (%)')
    bar_axes(a, horiz=True)
    hk, lk = key_patches(chosen=False)
    band_legend(fig, G[1], hk, lk, cx=ax0 + axw / 2)
    fig.text((ax0 + axw * 1.04) / fig._W, G[1]['band'], 'Trước → sau (thay đổi)', ha='left', va='center',
             fontsize=FS_LEG)
    subcap(fig, G[1], 0, 'c) Chỉ tiêu sau hiệu chỉnh so với trước', xc=FW / 2)
    finish(fig, name)


# ============================================================================ Hinh 3.5
def f05():
    fig, G = new_fig([dict(cols=ONE, h=3.0, top=LEG1 + 0.5), dict(cols=ONE, h=3.0)])
    a, b = G[0]['axes'][0], G[1]['axes'][0]
    m = (tu > 4) & (tu < 77)
    a.plot(tu[m], L['by'][m], color=PAL['yaw']['main'], lw=1.5)
    a.plot(tu[m], L['bp'][m], color=PAL['pitch']['main'], lw=1.5)
    for ax in AX:
        b.plot(T, wd[ax], color=PAL[ax]['main'], lw=1.2)
    for x in (a, b):
        seg_shade(x); x.set_xlim(4, 77); x.set_xlabel('Thời gian (s)')
        x.xaxis.set_major_locator(mt.MultipleLocator(10))
    seg_header(a)
    a.set_ylabel('Góc (°)'); b.set_ylabel('Tốc độ góc (°/s)')
    a.set_ylim(-32, 32); b.set_ylim(-250, 250)
    a.yaxis.set_major_locator(mt.MultipleLocator(10)); b.yaxis.set_major_locator(mt.MultipleLocator(100))
    band_legend(fig, G[0], [Line2D([], [], color=PAL[x]['main'], lw=2.2) for x in AX], ['Yaw', 'Pitch'],
                y=band_y(fig, G[0], LEG1 / 2))
    subcap(fig, G[0], 0, 'a) Góc khung mang đo bởi IMU2')
    subcap(fig, G[1], 0, 'b) Tốc độ góc khung mang chiếu lên hai trục')
    finish(fig, 'h3_05_kich_thich')


# ============================================================================ Hinh 3.6
def f06():
    fig, G = new_fig([dict(cols=TWO, h=3.0, top=LEG1), dict(cols=ONE, h=3.0, top=LEG1, bot=BOT0)])
    S = R['series_final']
    wins = {'yaw': (50.0, 53.0), 'pitch': (64.0, 67.0)}
    for j, ax in enumerate(AX):
        a = G[0]['axes'][j]
        t0, t1 = wins[ax]
        m = (T >= t0) & (T < t1); ml = (tu >= t0) & (tu < t1)
        a.plot(T[m], S[ax]['e'][m], **after(ax), zorder=3)
        a.plot(tu[ml], E['elog'][ax][ml], **MEAS, zorder=4)
        a.set_xlim(t0, t1); symlim(a, S[ax]['e'][m], E['elog'][ax][ml]); time_axes(a)
        a.set_xlabel('Thời gian (s)'); a.set_ylabel('Sai lệch góc (°)')
        subcap(fig, G[0], j, f'{"ab"[j]}) Trục {AXN[ax]} (đoạn {3 if ax == "yaw" else 4})')
    band_legend(fig, G[0], [Line2D([], [], **MEAS), tup([after('yaw'), after('pitch')])],
                ['Đo (log A)', 'Mô phỏng tái hiện'], hl=3.6, numpoints=3)
    a = G[1]['axes'][0]
    V = R['val']
    x = np.arange(len(C.SEG) + 1); wb = 0.19
    hs, ls = [], []
    for k, ax in enumerate(AX):
        meas = [d['erms'] for d in V['log_seg'][ax]] + [V['log'][ax]['erms']]
        sim = [d['erms'] for d in V['sim_seg'][ax]] + [V['sim'][ax]['erms']]
        o = (-1.5 + 2 * k) * wb
        b1 = a.bar(x + o, meas, wb, color=PAL[ax]['main'], zorder=3)
        b2 = a.bar(x + o + wb, sim, wb, facecolor='white', edgecolor=PAL[ax]['main'], hatch='////', lw=1.0, zorder=3)
        hs += [b1, b2]; ls += [f'{AXN[ax]}, đo', f'{AXN[ax]}, mô phỏng']
    a.set_xticks(x); a.set_xticklabels([f'Đoạn {i + 1}' for i in range(len(C.SEG))] + ['Toàn bài thử'])
    a.set_ylabel('$e_{\\mathrm{rms}}$ (°)'); bar_axes(a)
    a.set_xlim(-0.6, len(x) - 0.4)
    band_legend(fig, G[1], hs, ls, hl=1.6)
    subcap(fig, G[1], 0, 'c) Sai lệch hiệu dụng theo đoạn')
    finish(fig, 'h3_06_kiem_chung')


# ============================================================================ Hinh 3.7
def _step_norm(y, Ts, A):
    return np.where(Ts < 0.5, y - A, y) / A


STEP_A = {'yaw': 5.0, 'pitch': 3.0}
STEP_XLIM = {'yaw': (-50, 700), 'pitch': (-20, 250)}


def f07():
    cas = R['cascade']; Ts = R['Ts']; Tk = R['Tk']
    fig, G = new_fig([dict(cols=TWO, h=3.0, top=LEG2), dict(cols=TWO, h=3.0, top=LEG2)])
    for j, ax in enumerate(AX):
        a = G[0]['axes'][j]
        hs = {}
        for sm, kd in zip(cas[ax]['Kpt'], ['low', 'chosen', 'high']):
            ln, = a.plot((Ts - 0.5) * 1e3, _step_norm(sm['y'], Ts, STEP_A[ax]), **opt(ax, kd), zorder=Z[kd])
            v = sm['v']
            hs[kd] = (ln, f'$K_{{p\\theta}}$ = {num(v, 1 if v % 1 else 0)} {SINV}' + (' (chọn)' if kd == 'chosen' else ''))
        a.axhline(1, **REF, zorder=2)
        a.set_xlim(*STEP_XLIM[ax]); a.set_ylim(-0.05, 1.25)
        a.set_xlabel('Thời gian sau bậc (ms)'); a.set_ylabel('$\\theta/\\theta_{\\mathrm{đặt}}$')
        order = ['low', 'high', 'chosen']
        band_legend(fig, G[0], [hs[k][0] for k in order], [hs[k][1] for k in order], ncol=2,
                    cx=G[0]['cols'][j][0] + PW / 2, columnspacing=1.2)
        subcap(fig, G[0], j, f'{"ab"[j]}) Trục {AXN[ax]}, bậc {num(STEP_A[ax], 0)}°')
    # c) khu sai lech do tac dong khong doi
    a = G[1]['axes'][0]
    for ax in AX:
        for sm in cas[ax]['Kiw']:
            ch = sm['v'] == gsim.GAINS_FINAL[ax]['Kiw']
            if sm['v'] != 0.0 and not ch:
                continue
            kd = 'chosen' if ch else 'low'
            a.plot(Tk - 1.0, sm['y'], **opt(ax, kd), zorder=Z[kd])
    a.axhline(0, **REF, zorder=2)
    a.set_xlim(-0.2, 4.0); time_axes(a)
    a.set_xlabel('Thời gian (s)'); a.set_ylabel('Sai lệch góc (°)')
    band_legend(fig, G[1], [tup([opt('yaw', 'low'), opt('pitch', 'low')]), tup([opt('yaw', 'chosen'), opt('pitch', 'chosen')])],
                ['$K_{i\\omega}$ = 0', f'$K_{{i\\omega}}$ = 1,0 / 0,5 {SINV} (chọn)'], ncol=1, cx=TWO[0][0] + PW / 2, hl=3.6)
    subcap(fig, G[1], 0, 'c) Khung mang quay đều 8 °/s')
    # d) e_rms bai thu tham chieu theo Kpt
    a = G[1]['axes'][1]
    xs = np.arange(3)
    for k, ax in enumerate(AX):
        a.bar(xs - 0.19 + 0.38 * k, [sm['bt3_erms'] for sm in cas[ax]['Kpt']], 0.36, color=PAL[ax]['main'], zorder=3)
    a.set_xticks(xs)
    a.set_xticklabels([f'{num(cas["yaw"]["Kpt"][i]["v"], 1 if cas["yaw"]["Kpt"][i]["v"] % 1 else 0)} / '
                       f'{num(cas["pitch"]["Kpt"][i]["v"], 0)}' for i in range(3)])
    hilite(a, 1)
    a.set_xlim(-0.55, 2.55)
    a.set_xlabel(f'$K_{{p\\theta}}$ Yaw / Pitch ({SINV})'); a.set_ylabel('$e_{\\mathrm{rms}}$ (°)'); bar_axes(a)
    hk, lk = key_patches()
    band_legend(fig, G[1], hk, lk, ncol=2, cx=TWO[1][0] + PW / 2, hl=1.6)
    subcap(fig, G[1], 1, 'd) Bài thử tham chiếu, chưa bù')
    finish(fig, 'h3_07_khao_sat_cascade')


# ============================================================================ Hinh 3.8
def f08():
    SL = R['step_ladder']; Ts = R['Ts']
    fig, G = new_fig([dict(cols=TWO, h=3.0, top=LEG1), dict(cols=TWO, h=3.0)])
    for j, ax in enumerate(AX):
        a = G[0]['axes'][j]
        a.plot((Ts - 0.5) * 1e3, _step_norm(SL['cascade'][ax]['y'], Ts, STEP_A[ax]), **after(ax), zorder=3)
        a.plot((Ts - 0.5) * 1e3, _step_norm(SL['ban_dau'][ax]['y'], Ts, STEP_A[ax]), **BEFORE, zorder=4)
        a.axhline(1, **REF, zorder=2)
        a.set_xlim(*STEP_XLIM[ax]); a.set_ylim(-0.05, 1.2)
        a.set_xlabel('Thời gian sau bậc (ms)'); a.set_ylabel('$\\theta/\\theta_{\\mathrm{đặt}}$')
        subcap(fig, G[0], j, f'{"ab"[j]}) Trục {AXN[ax]}, bậc {num(STEP_A[ax], 0)}°')
    for j, ax in enumerate(AX):
        a = G[1]['axes'][j]
        t0, t1 = (14.0, 20.0) if ax == 'yaw' else (36.0, 39.0)
        m = (T >= t0) & (T < t1)
        eb = R['ladder_series']['ban_dau'][ax]['e'][m]; ea = R['ladder_series']['cascade'][ax]['e'][m]
        a.plot(T[m], ea, **after(ax), zorder=3)
        a.plot(T[m], eb, **BEFORE, zorder=4)
        symlim(a, ea, eb); a.set_xlim(t0, t1); time_axes(a)
        a.set_xlabel('Thời gian (s)'); a.set_ylabel('Sai lệch góc (°)')
        subcap(fig, G[1], j, f'{"cd"[j]}) Trục {AXN[ax]}, bài thử tham chiếu')
    band_legend(fig, G[0], [Line2D([], [], **BEFORE), tup([after('yaw'), after('pitch')])],
                ['Trước hiệu chỉnh', 'Sau hiệu chỉnh'], hl=3.6)
    finish(fig, 'h3_08_cascade_truoc_sau')


# ============================================================================ Hinh 3.9
def f09():
    ffs = R['ff_survey'][1:]      # bo "Khong bu"
    fd = dict(ffs)
    fig, G = new_fig([dict(cols=TWO, h=3.0, top=LEG1), dict(cols=TWO, h=3.0, top=LEG1)])
    show = {'k₀ = 0,80': 'low', 'k₀ = 0,95': 'high', 'k(v) theo vùng': 'chosen'}
    for j, ax in enumerate(AX):
        a = G[0]['axes'][j]
        ser = {k: fd[k]['series'][ax]['e'] for k in show}
        t0, t1 = best_window(ser, ['k₀ = 0,80', 'k₀ = 0,95'], 'k(v) theo vùng', 2.5 if ax == 'yaw' else 2.0, SEG_AX[ax])
        m = (T >= t0) & (T < t1)
        for lab, kd in show.items():
            a.plot(T[m], ser[lab][m], **opt(ax, kd), zorder=Z[kd])
        symlim(a, *[ser[k][m] for k in show]); a.set_xlim(t0, t1); time_axes(a)
        a.set_xlabel('Thời gian (s)'); a.set_ylabel('Sai lệch góc (°)')
        seg_no = [i for i, s in enumerate(C.SEG) if s[0] <= t0 < s[1]][0] + 1
        subcap(fig, G[0], j, f'{"ab"[j]}) Trục {AXN[ax]}, đoạn {seg_no}')
    band_legend(fig, G[0], [tup([opt(x, k) for x in AX]) for k in ('low', 'high', 'chosen')],
                ['$k_0$ = 0,80', '$k_0$ = 0,95', '$k(v)$ theo vùng (chọn)'], hl=3.6)
    x = np.arange(len(ffs))
    ticks = ['0,80', '0,88', '0,95', '$k(v)$']
    for jj, (key, yl, cap) in enumerate([('erms', '$e_{\\mathrm{rms}}$ (°)', 'c) Sai lệch hiệu dụng'),
                                         ('uff_hold', '$\\sigma(u_{ff})$ (°/s)', 'd) Độ lệch chuẩn $u_{ff}$ khi đứng yên')]):
        a = G[1]['axes'][jj]
        for k, ax in enumerate(AX):
            a.bar(x - 0.19 + 0.38 * k, [out[ax][key] for _, out in ffs], 0.36, color=PAL[ax]['main'], zorder=3)
        a.set_xticks(x); a.set_xticklabels(ticks); hilite(a, 3)
        a.set_xlim(-0.55, len(x) - 0.45)
        a.set_xlabel('Hệ số $k_0$ cố định / luật $k(v)$'); a.set_ylabel(yl); bar_axes(a)
        subcap(fig, G[1], jj, cap)
    hk, lk = key_patches()
    band_legend(fig, G[1], hk, lk, hl=1.6)
    finish(fig, 'h3_09_khao_sat_bu')


# ============================================================================ Hinh 3.11
def f11():
    tpr = R['tp_survey']
    fig, G = new_fig([dict(cols=TWO, h=3.0, top=LEG1), dict(cols=TWO, h=3.0, top=LEG1)])
    wins = {'yaw': (50.4, 51.9), 'pitch': (64.2, 65.2)}
    show = {0.0: 'low', 0.012: 'chosen', 0.020: 'high'}
    for j, ax in enumerate(AX):
        a = G[0]['axes'][j]
        t0, t1 = wins[ax]; m = (T >= t0) & (T < t1)
        arrs = []
        for tp, out in tpr:
            kd = show.get(round(tp, 3))
            if kd is None:
                continue
            e = out['series'][ax]['e'][m]; arrs.append(e)
            a.plot(T[m], e, **opt(ax, kd), zorder=Z[kd])
        symlim(a, *arrs); a.set_xlim(t0, t1); time_axes(a)
        a.set_xlabel('Thời gian (s)'); a.set_ylabel('Sai lệch góc (°)')
        subcap(fig, G[0], j, f'{"ab"[j]}) Trục {AXN[ax]}, đoạn {3 if ax == "yaw" else 4}')
    band_legend(fig, G[0], [tup([opt(x, k) for x in AX]) for k in ('low', 'chosen', 'high')],
                ['$\\tau_p$ = 0 ms', '$\\tau_p$ = 12 ms (chọn)', '$\\tau_p$ = 20 ms'], hl=3.6)
    tp_ms = np.array([tp * 1e3 for tp, _ in tpr])
    for jj, (key, yl, cap) in enumerate([('erms', '$e_{\\mathrm{rms}}$ (°)', 'c) Sai lệch hiệu dụng'),
                                         ('u_hf', 'Năng lượng (%)', 'd) Năng lượng lệnh trên 20 Hz')]):
        a = G[1]['axes'][jj]
        a.axvspan(11.0, 13.0, color=HILITE, lw=0, zorder=0)
        for ax in AX:
            v = np.array([out[ax][key] for _, out in tpr])
            a.plot(tp_ms, v, color=PAL[ax]['main'], lw=2.0, marker='o', ms=5.5, mec='white', mew=0.8, zorder=3)
        a.set_xticks(tp_ms); a.set_xticklabels([num(v, 0) for v in tp_ms])
        a.get_xticklabels()[list(tp_ms).index(12.0)].set_fontweight('bold')
        a.set_xlim(-1, 21); a.set_ylim(bottom=0); time_axes(a)
        a.set_xlabel('Khoảng ngoại suy $\\tau_p$ (ms)'); a.set_ylabel(yl)
        subcap(fig, G[1], jj, cap)
    band_legend(fig, G[1], [Line2D([], [], color=PAL[x]['main'], lw=2.0, marker='o', ms=5.5, mec='white', mew=0.8) for x in AX]
                + [Patch(facecolor=HILITE, edgecolor='#9a9a9a', lw=0.6)], ['Trục Yaw', 'Trục Pitch', 'Phương án chọn'])
    finish(fig, 'h3_11_khao_sat_ngoai_suy')


# ============================================================================ Hinh 3.13
def f13():
    limr = R['lim_survey']; gl = R2['glitch']; Tg = R2['Tg']
    fig, G = new_fig([dict(cols=TWO, h=3.0, top=LEG2), dict(cols=TWO, h=3.0, top=LEG1, bot=BOT2)])
    wins = {'yaw': (72.6, 74.0), 'pitch': (65.0, 65.6)}
    kind = {'Cố định 135 °/s': 'low', 'Cố định 410 °/s': 'high', 'Theo vùng': 'chosen'}
    for j, ax in enumerate(AX):
        a = G[0]['axes'][j]
        t0, t1 = wins[ax]; m = (T >= t0) & (T < t1)
        for lab, out in limr:
            if lab in kind:
                a.plot(T[m], out['series'][ax]['u'][m], **opt(ax, kind[lab]), zorder=Z[kind[lab]])
        a.plot(T[m], -wd[ax][m], **REF, zorder=6)
        a.set_xlim(t0, t1); time_axes(a)
        a.set_xlabel('Thời gian (s)'); a.set_ylabel('Lệnh tốc độ (°/s)')
        subcap(fig, G[0], j, f'{"ab"[j]}) Trục {AXN[ax]}, đoạn {5 if ax == "yaw" else 4}')
    hl_ = [tup([opt(x, 'low') for x in AX]), tup([opt(x, 'chosen') for x in AX]), tup([opt(x, 'high') for x in AX]),
           Line2D([], [], **REF)]
    band_legend(fig, G[0], hl_, ['Cố định 135 °/s', 'Theo vùng (chọn)', 'Cố định 410 °/s', 'Lệnh cần để bù ($-\\omega_b$)'],
                ncol=2, hl=3.6)
    # c) e_max
    a = G[1]['axes'][0]
    x = np.arange(len(limr))
    for k, ax in enumerate(AX):
        a.bar(x - 0.19 + 0.38 * k, [out[ax]['emax'] for _, out in limr], 0.36, color=PAL[ax]['main'], zorder=3)
    a.set_xticks(x); a.set_xticklabels(['135', '165', '410', 'Theo\nvùng']); hilite(a, 3)
    a.set_xlim(-0.55, len(x) - 0.45)
    a.set_xlabel('Giới hạn lệnh (°/s)'); a.set_ylabel('$e_{\\mathrm{max}}$ (°)'); bar_axes(a)
    subcap(fig, G[1], 0, 'c) Sai lệch lớn nhất')
    # d) mau IMU2 loi
    a = G[1]['axes'][1]
    for lab in ('Cố định 135 °/s', 'Theo vùng', 'Cố định 410 °/s'):
        a.plot((Tg - 0.5) * 1e3, gl[lab]['series']['yaw']['e'], **opt('yaw', kind[lab]), zorder=Z[kind[lab]])
    a.set_xlim(-20, 250); time_axes(a)
    a.set_xlabel('Thời gian từ mẫu lỗi (ms)'); a.set_ylabel('Sai lệch góc (°)')
    subcap(fig, G[1], 1, 'd) Trục Yaw, ba mẫu IMU2 lỗi')
    hk, lk = key_patches()
    band_legend(fig, G[1], hk, lk, hl=1.6)
    finish(fig, 'h3_13_khao_sat_gioi_han')


# ============================================================================ Hinh 3.15
def f15():
    revs = R['rev_survey']; stp = R2['stop_test']
    fig, G = new_fig([dict(cols=TWO, h=3.0, top=LEG2), dict(cols=TWO, h=3.0, top=LEG1)])
    base = [o for p, o in revs if p[0] == 'none'][0]
    t0s = [0.010, 0.020, 0.040]; als = [300.0, 1000.0]
    d = {p: o for p, o in revs}
    x = np.arange(len(t0s)); wb = 0.18
    for jj, (key, axes_, cap) in enumerate([('erms', AX, 'a) Sai lệch hiệu dụng $e_{\\mathrm{rms}}$'),
                                            ('signchg', ('pitch',), 'b) Số lần lệnh Pitch đổi dấu')]):
        a = G[0]['axes'][jj]
        n = len(axes_) * 2; pos = (np.arange(n) - (n - 1) / 2) * wb
        k = 0
        for ax in axes_:
            for al in als:
                v = [(d[(t, al)][ax][key] / base[ax][key] - 1) * 100 for t in t0s]
                if al == 300.0:
                    a.bar(x + pos[k], v, wb * 0.94, facecolor='white', edgecolor=PAL[ax]['main'], hatch='////', lw=1.0, zorder=3)
                else:
                    a.bar(x + pos[k], v, wb * 0.94, color=PAL[ax]['main'], zorder=3)
                k += 1
        a.axhline(0, color=INK, lw=1.0, zorder=4)
        a.set_xticks(x); a.set_xticklabels([num(t * 1e3, 0) for t in t0s]); hilite(a, 0)
        a.set_xlim(-0.55, len(x) - 0.45); time_axes(a)
        a.set_xlabel('Tầm dự báo $t_{0\\,\\mathrm{max}}$ (ms)'); a.set_ylabel('Thay đổi (%)')
        bar_axes(a)
        subcap(fig, G[0], jj, cap)
    hs = [Patch(facecolor=PAL['yaw']['main']), Patch(facecolor=PAL['pitch']['main']),
          Patch(facecolor='white', edgecolor='#555555', hatch='////', lw=0.9), Patch(facecolor='#555555'),
          Patch(facecolor=HILITE, edgecolor='#9a9a9a', lw=0.6)]
    ls = ['Trục Yaw', 'Trục Pitch', '$\\alpha_{\\mathrm{rev}}$ = 300 °/s²', '$\\alpha_{\\mathrm{rev}}$ = 1 000 °/s² (chọn)',
          'Phương án chọn']
    band_legend(fig, G[0], hs, ls, ncol=3, hl=1.6)
    # c), d) lenh trong giai doan giu sau khi dung (tu 0,3 s, nhu Bang 3.10)
    for j, ax in enumerate(AX):
        a = G[1]['axes'][j]
        sN = stp['Không xử lý dừng'][ax]['series']; sY = stp['Có chế độ dừng'][ax]['series']
        m = (sN['T'] >= 0.3) & (sN['T'] <= 1.5)
        a.plot(sY['T'][m], sY['u'][m], **after(ax), zorder=3)
        a.plot(sN['T'][m], sN['u'][m], **BEFORE, zorder=4)
        symlim(a, sN['u'][m], sY['u'][m], k=1.1); time_axes(a)
        a.set_xlim(0.3, 1.5)
        a.set_xlabel('Thời gian từ khi khung mang dừng (s)'); a.set_ylabel('Lệnh tốc độ (°/s)')
        subcap(fig, G[1], j, f'{"cd"[j]}) Trục {AXN[ax]}, giai đoạn giữ')
    band_legend(fig, G[1], [Line2D([], [], **BEFORE), tup([after('yaw'), after('pitch')])],
                ['Không có chế độ dừng', 'Có chế độ dừng (chọn)'], hl=3.6)
    finish(fig, 'h3_15_khao_sat_dao_chieu_dung')


# ============================================================================ Hinh 3.17
def f17():
    shp = R2['shape_survey']; trj = R2['shape_traj']
    fig, G = new_fig([dict(cols=TWO, h=3.0, top=LEG2), dict(cols=TWO, h=3.0, top=LEG1, bot=BOT2)])
    a = G[0]['axes'][0]
    tms = trj['T'] * 1e3
    l3, = a.plot(tms, trj['a30'], color=INK, lw=LW_CH, zorder=3)
    l2, = a.plot(tms, trj['a18'], color='#8a8a8a', lw=LW_ALT + 0.2, ls=DASH, zorder=4)
    l1, = a.step(tms, trj['req'], where='post', color=INK, lw=1.2, ls=DOT, zorder=5)
    a.set_xlim(tms[0], tms[-1]); a.set_ylim(-340, 340)
    a.yaxis.set_major_locator(mt.MultipleLocator(150))
    a.set_xlabel('Thời gian (ms)'); a.set_ylabel('Lệnh tốc độ (°/s)')
    band_legend(fig, G[0], [l1, l3, l2], ['Lệnh yêu cầu', '$a_{\\mathrm{max}}$ = 30 000 °/s² (khi đảo chiều)',
                                          '$a_{\\mathrm{max}}$ = 18 000 °/s²'], ncol=2, cx=TWO[0][0] + PW / 2, columnspacing=1.2)
    subcap(fig, G[0], 0, 'a) Đổi chiều lệnh +300 → −300 °/s')
    a = G[0]['axes'][1]
    S0 = R['ladder_series']['dao_chieu']; S1 = R['ladder_series']['tao_dang']
    mm = (T >= C.WIN[0]) & (T < C.WIN[1])
    bins = np.linspace(0, 55, 45)
    a.hist(np.abs(S1['pitch']['du'][mm]), bins=bins, histtype='step', color=PAL['pitch']['main'], lw=LW_CH, log=True, zorder=3)
    a.hist(np.abs(S0['pitch']['du'][mm]), bins=bins, histtype='step', color=INK, lw=LW_BEF, ls=DASH, log=True, zorder=4)
    a.set_xlim(0, 55)
    a.set_xlabel('Bước lệnh trong 2 ms (°/s)'); a.set_ylabel('Số mẫu')
    band_legend(fig, G[0], [Line2D([], [], **BEFORE), Line2D([], [], **after('pitch'))], ['Không tạo dạng', 'Có tạo dạng (chọn)'],
                ncol=1, cx=TWO[1][0] + PW / 2)
    subcap(fig, G[0], 1, 'b) Phân bố bước lệnh trục Pitch')
    x = np.arange(len(shp))
    ticks = ['Không\ngiới hạn', '18 000', '30 000', '18 000 /\n30 000']
    for jj, (key, yl, cap) in enumerate([('dumax', 'Bước lệnh (°/s)', 'c) Bước lệnh lớn nhất'),
                                         ('erms', '$e_{\\mathrm{rms}}$ (°)', 'd) Sai lệch hiệu dụng')]):
        a = G[1]['axes'][jj]
        for k, ax in enumerate(AX):
            a.bar(x - 0.19 + 0.38 * k, [out[ax][key] for _, out in shp], 0.36, color=PAL[ax]['main'], zorder=3)
        a.set_xticks(x); a.set_xticklabels(ticks); hilite(a, 3)
        a.set_xlim(-0.55, len(x) - 0.45)
        a.set_xlabel('$a_{\\mathrm{max}}$ (°/s²)'); a.set_ylabel(yl); bar_axes(a)
        subcap(fig, G[1], jj, cap)
    hk, lk = key_patches()
    band_legend(fig, G[1], hk, lk, hl=1.6)
    finish(fig, 'h3_17_khao_sat_tao_dang')


# ============================================================================ Hinh 3.19
def f19():
    bus = R2['bus_sched']; bc = R2['bus_closed']
    fig, G = new_fig([dict(cols=TWO, h=3.2, top=LEG1 + LEG2)])
    g = G[0]
    y1 = band_y(fig, g, LEG1 / 2); y2 = band_y(fig, g, LEG1 + LEG2 / 2)
    hk, lk = key_patches()
    band_legend(fig, g, hk, lk, y=y1, hl=1.6)
    a = g['axes'][0]
    sty = {'yawpri': lambda ax: dict(color=PAL[ax]['light'], lw=LW_ALT, ls=DASH),
           'alt': lambda ax: dict(color=PAL[ax]['main'], lw=LW_CH if ax == 'pitch' else 1.2, ls='-')}
    for mode, ax in [('yawpri', 'yaw'), ('yawpri', 'pitch'), ('alt', 'pitch'), ('alt', 'yaw')]:
        gp = np.sort(bus[mode][ax]['gaps']); p = 1 - np.arange(len(gp)) / len(gp)
        a.semilogy(gp, p, **sty[mode](ax), zorder=3)
    a.set_xlim(0, 36); a.set_ylim(1e-4, 1.5)
    a.yaxis.set_major_locator(mt.FixedLocator([1e-4, 1e-3, 1e-2, 1e-1, 1]))
    a.yaxis.set_major_formatter(mt.FixedFormatter(['$\\mathrm{10^{-4}}$', '$\\mathrm{10^{-3}}$', '$\\mathrm{10^{-2}}$',
                                                   '$\\mathrm{10^{-1}}$', '1']))
    a.yaxis.set_minor_locator(mt.NullLocator())
    a.set_xlabel('Khoảng cập nhật lệnh $\\Delta$ (ms)'); a.set_ylabel('$P(\\Delta > x)$')
    band_legend(fig, g, [tup([sty['yawpri'](x) for x in AX]), tup([after(x) for x in AX])],
                ['Ưu tiên Yaw', 'Luân phiên (chọn)'], ncol=1, cx=TWO[0][0] + PW / 2, y=y2, hl=3.6)
    subcap(fig, g, 0, 'a) Phân bố khoảng cập nhật lệnh')
    a = g['axes'][1]
    x = np.arange(2); top = 0
    for k, ax in enumerate(AX):
        o = -0.19 + 0.38 * k
        a.bar(x + o, [bc[('yawpri', 0.012)][ax]['erms'], bc[('alt', 0.012)][ax]['erms']], 0.36, color=PAL[ax]['main'], zorder=3)
        for xi, mode in enumerate(('yawpri', 'alt')):
            for tp, mk in [(0.008, 'v'), (0.016, '^')]:
                v = bc[(mode, tp)][ax]['erms']; top = max(top, v)
                a.plot(xi + o, v, marker=mk, color=INK, ms=6.5, mec='white', mew=0.7, lw=0, zorder=6)
    a.set_xticks(x); a.set_xticklabels(['Ưu tiên Yaw', 'Luân phiên']); hilite(a, 1)
    a.set_xlim(-0.6, 1.6); a.set_ylim(0, top * 1.1); time_axes(a, 4)
    a.set_xlabel('Lịch truyền RS485'); a.set_ylabel('$e_{\\mathrm{rms}}$ (°)'); bar_axes(a)
    band_legend(fig, g, [Patch(facecolor='#8a8a8a'), Line2D([], [], marker='v', color=INK, ms=6.5, lw=0),
                         Line2D([], [], marker='^', color=INK, ms=6.5, lw=0)],
                ['$\\tau_p$ = 12 ms', '$\\tau_p$ = 8 ms', '$\\tau_p$ = 16 ms'], ncol=2, cx=TWO[1][0] + PW / 2, y=y2, hl=1.6)
    subcap(fig, g, 1, 'b) Sai lệch hiệu dụng')
    finish(fig, 'h3_19_khao_sat_rs485')


# ============================================================================ Hinh 3.21
def f21():
    V = R['val']
    fig, G = new_fig([dict(cols=ONE, h=2.6, top=LEG1 + 0.5), dict(cols=ONE, h=2.4, top=0.5), dict(cols=ONE, h=2.4, top=0.5)])
    m = (tu > 4) & (tu < 77)
    a = G[0]['axes'][0]
    a.plot(tu[m], L['by'][m], color=PAL['yaw']['main'], lw=1.5)
    a.plot(tu[m], L['bp'][m], color=PAL['pitch']['main'], lw=1.5)
    a.set_ylim(-32, 32); a.yaxis.set_major_locator(mt.MultipleLocator(15)); a.set_ylabel('Góc (°)')
    seg_header(a)
    subcap(fig, G[0], 0, 'a) Góc khung mang')
    for j, ax in enumerate(AX):
        a = G[j + 1]['axes'][0]
        a.plot(tu[m], E['elog'][ax][m], color=PAL[ax]['main'], lw=1.0, zorder=3)
        for i, (s0, s1, _) in enumerate(C.SEG):
            v = V['log_seg'][ax][i]['erms']
            a.plot([s0, s1], [v, v], color=INK, lw=1.3, ls=DASH, zorder=4)
            a.plot([s0, s1], [-v, -v], color=INK, lw=1.3, ls=DASH, zorder=4)
            a.text((s0 + s1) / 2, 1.0 + 0.06 / a._hcm, '±' + num(v, 3) + '°', transform=a.get_xaxis_transform(),
                   ha='center', va='bottom', fontsize=FS_ANN)
        a.set_ylim(-0.8, 0.8); a.yaxis.set_major_locator(mt.MultipleLocator(0.4))
        a.set_ylabel('Sai lệch góc (°)')
        subcap(fig, G[j + 1], 0, f'{"bc"[j]}) Sai lệch góc trục {AXN[ax]}')
    for g in G:
        a = g['axes'][0]
        seg_shade(a); a.set_xlim(4, 77); a.set_xlabel('Thời gian (s)')
        a.xaxis.set_major_locator(mt.MultipleLocator(10))
    band_legend(fig, G[0], [Line2D([], [], color=PAL[x]['main'], lw=2.2) for x in AX] + [Line2D([], [], color=INK, lw=1.3, ls=DASH)],
                ['Yaw', 'Pitch', '$\\pm e_{\\mathrm{rms}}$ từng đoạn'], y=band_y(fig, G[0], LEG1 / 2))
    finish(fig, 'h3_21_log_hoan_thien')


# ============================================================================ Hinh 3.22
def f22():
    V = R['val']
    fig, G = new_fig([dict(cols=ONE, h=3.3, top=LEG1, bot=0.2), dict(cols=ONE, h=3.3, bot=1.12)])
    x = np.arange(len(ORDER))
    ticks = ['Ban đầu', 'Hiệu chỉnh\nnối tầng', 'Bù IMU2', 'Ngoại suy\nbù trễ', 'Giới hạn\nlệnh động',
             'Đảo chiều,\ndừng', 'Tạo dạng\nlệnh', 'Hoàn thiện']
    tk = [0.1, 0.2, 0.5, 1, 2, 5, 10]
    mk = dict(marker='o', ms=5.5, mec='white', mew=0.8)

    def dm(ax):
        return dict(marker='D', ms=7, color=PAL[ax]['main'], mec=INK, mew=1.0, lw=0)
    for jj, (key, yl, cap) in enumerate([('erms', '$e_{\\mathrm{rms}}$ (°)', 'a) Sai lệch hiệu dụng'),
                                         ('p99', 'Phân vị 99 % $|e|$ (°)', 'b) Phân vị 99 % của $|e|$')]):
        a = G[jj]['axes'][0]
        for k, ax in enumerate(AX):
            v = [R['ladder'][n][ax][key] for n in ORDER]
            a.plot(x, v, color=PAL[ax]['main'], lw=2.0, **mk, zorder=3)
            a.plot(x[-1] + 0.2 + 0.2 * k, V['log'][ax][key], **dm(ax), zorder=5)
        a.set_yscale('log')
        a.yaxis.set_major_locator(mt.FixedLocator(tk)); a.yaxis.set_minor_locator(mt.NullLocator())
        a.yaxis.set_major_formatter(mt.FixedFormatter([num(t, 1) if t < 1 else num(t, 0) for t in tk]))
        a.set_ylim(0.12, 16); a.set_xlim(-0.4, len(x) - 0.3)
        a.set_xticks(x)
        a.set_xticklabels(ticks if jj == 1 else [])
        a.tick_params(axis='x', length=0)
        a.set_ylabel(yl)
        subcap(fig, G[jj], 0, cap)
    band_legend(fig, G[0], [Line2D([], [], color=PAL[x_]['main'], lw=2.0, **mk) for x_ in AX]
                + [tuple(Line2D([], [], **dm(x_)) for x_ in AX)],
                ['Yaw, mô phỏng tái hiện', 'Pitch, mô phỏng tái hiện', 'Đo (log A)'], hl=2.6)
    finish(fig, 'h3_22_qua_trinh_hoan_thien')


# ============================================================================ cac hinh truoc / sau
def all_before_after():
    before_after('h3_10_bu_imu2_truoc_sau', 'cascade', 'bu_imu2', {'yaw': (14.0, 20.0), 'pitch': (36.0, 39.0)},
                 ['erms', 'p99', 'emax'])
    before_after('h3_12_ngoai_suy_truoc_sau', 'bu_imu2', 'ngoai_suy', {'yaw': (50.4, 52.4), 'pitch': (64.2, 65.7)},
                 ['erms', 'p99', 'emax'])
    before_after('h3_14_gioi_han_truoc_sau', 'ngoai_suy', 'gioi_han', {'yaw': (72.4, 74.4), 'pitch': (64.6, 66.0)},
                 ['erms', 'p99', 'emax', 'rho'])
    before_after('h3_16_dao_chieu_truoc_sau', 'gioi_han', 'dao_chieu', {'yaw': (72.4, 74.4), 'pitch': (64.6, 66.0)},
                 ['erms', 'p99', 'emax', 'signchg'])
    before_after('h3_18_tao_dang_truoc_sau', 'dao_chieu', 'tao_dang', {'yaw': (72.4, 74.4), 'pitch': (64.6, 66.0)},
                 ['dumax', 'du99', 'erms', 'emax'])
    before_after('h3_20_rs485_truoc_sau', 'tao_dang', 'hoan_thien', {'yaw': (50.4, 52.4), 'pitch': (64.2, 65.7)},
                 ['erms', 'p99', 'emax'], extra_log=True)


ALL = dict(f05=f05, f06=f06, f07=f07, f08=f08, f09=f09, f11=f11, f13=f13, f15=f15, f17=f17, f19=f19, f21=f21,
           f22=f22, ba=all_before_after)

if __name__ == '__main__':
    sel = sys.argv[2:] or list(ALL)
    for k in sel:
        ALL[k]()
