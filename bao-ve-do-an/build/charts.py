# -*- coding: utf-8 -*-
"""Ve lai cac bieu do chi tieu cho trinh chieu.

Moi bieu do duoc xuat thanh PNG nen trong suot, 300 dpi, kich thuoc dung bang
kich thuoc dat tren slide (1 pt trong hinh = 1 pt tren slide). Bieu do truoc/sau
duoc tach thanh cac lop (base, after, seg1..) co cung khung hinh de xep chong va
cho xuat hien lan luot bang hieu ung. Toa do cac diem neo (inch, tinh tu goc
tren-trai cua anh) duoc ghi ra anchors.json de dat nhan ban dia (native) len tren.

Chay:  python charts.py <thu_muc_ra>
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.container import BarContainer  # noqa: E402
from matplotlib.legend_handler import HandlerTuple  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from data import (  # noqa: E402
    ACCENT, BEFORE, BEFORE_DARK, CHAIN, GRID, INK, MUTED, PITCH, YAW,
    RS_REAL, SIM_COMP_240, SIM_LIMIT_600, TAUP_SWEEP, TRADE, pct, vn,
)

DPI = 300
C = lambda h: "#" + h  # noqa: E731

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "font.size": 14,
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic",
    "mathtext.bf": "Liberation Sans:bold",
    "axes.edgecolor": "#9AA7B4",
    "axes.linewidth": 1.0,
    "axes.labelcolor": C(INK),
    "axes.labelsize": 14,
    "xtick.color": C(INK),
    "ytick.color": C(INK),
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.transparent": True,
    "legend.frameon": False,
})

AX_COL = {"Yaw": YAW, "Pitch": PITCH}
AX_MARK = {"Yaw": "o", "Pitch": "s"}
ANCH = {}


def _flat(arts):
    out = []
    for a in arts:
        if isinstance(a, BarContainer):
            out.extend(a.patches)
        elif isinstance(a, (list, tuple)):
            out.extend(_flat(a))
        else:
            out.append(a)
    return out


def _save_layers(fig, name, outdir, layers):
    """layers: ten_lop -> list artist. Lop 'base' = moi artist khong thuoc lop khac
    (ke ca truc, luoi, nhan); cac lop con lai chi chua dung artist cua lop do."""
    layers = {k: _flat(v) for k, v in layers.items()}
    other = {id(a) for ln, arts in layers.items() if ln != "base" for a in arts}
    everything = []
    for ax in fig.axes:
        everything += ax.get_children()
    everything += list(fig.legends) + list(fig.texts) + list(fig.lines) + list(fig.patches)
    orig = {id(a): a.get_visible() for a in everything}
    files = {}
    for lname, arts in layers.items():
        ids = {id(a) for a in arts}
        for a in everything:
            if lname == "base":
                a.set_visible(orig[id(a)] and id(a) not in other)
            else:
                a.set_visible(orig[id(a)] and id(a) in ids)
        fn = os.path.join(outdir, f"{name}_{lname}.png" if len(layers) > 1 else f"{name}.png")
        fig.savefig(fn, dpi=DPI, transparent=True)
        files[lname] = os.path.basename(fn)
    for a in everything:
        a.set_visible(orig[id(a)])
    return files


def _to_in(fig, ax, x, y):
    """Toa do du lieu -> inch tu goc tren-trai cua hinh."""
    px, py = ax.transData.transform((x, y))
    w, h = fig.get_size_inches()
    return round(px / DPI, 3), round(h - py / DPI, 3)


def _style_ax(ax, ygrid=True):
    ax.set_axisbelow(True)
    if ygrid:
        ax.yaxis.grid(True, color=C(GRID), linewidth=1.0)
    ax.tick_params(length=0, pad=6)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#9AA7B4")


def _axis_label(ax, x, y, axname, fontsize=15):
    """Nhan truc 'o Yaw' / '# Pitch' voi ky hieu mang mau truc, chu mau muc."""
    tr = ax.get_xaxis_transform()
    ax.plot([x - 0.24], [y], marker=AX_MARK[axname], color=C(AX_COL[axname]),
            markersize=10, transform=tr, clip_on=False, linestyle="none")
    ax.text(x - 0.14, y, axname, transform=tr, ha="left", va="center",
            fontsize=fontsize, color=C(INK), fontweight="bold", clip_on=False)


# ---------------------------------------------------------------------------
# 1. Cot truoc/sau nhieu panel (Yaw, Pitch)
# ---------------------------------------------------------------------------
def before_after(name, outdir, panels, size, widths=None):
    """panels: [{'key':..,'title':..,'groups':[('Yaw', truoc, sau), ...],'nd': 2}]
    Lop 'base': truc + cot truoc; lop 'after': cot sau + gia tri + % thay doi."""
    fig = plt.figure(figsize=size, dpi=DPI)
    n = len(panels)
    widths = widths or [len(p["groups"]) for p in panels]
    tot = float(sum(widths))
    left, right, bottom, top, gap = 0.01, 0.995, 0.15, 0.80, 0.06
    avail = right - left - gap * (n - 1)
    x0 = left
    after_arts, base_arts = [], []
    anchors = {}
    for i, p in enumerate(panels):
        w = avail * widths[i] / tot
        px0 = x0
        ax = fig.add_axes([x0 + 0.055, bottom, w - 0.055, top - bottom])
        x0 += w + gap
        _style_ax(ax)
        vals = [v for g in p["groups"] for v in g[1:]]
        ymax = max(vals) * 1.42
        ax.set_ylim(0, ymax)
        ng = len(p["groups"])
        ax.set_xlim(-0.62, ng - 0.38)
        ax.set_xticks([])
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4, steps=[1, 2, 2.5, 5, 10]))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: vn(v, 0) if abs(v - round(v)) < 1e-9 else vn(v, 1)))
        nd = p.get("nd", 2)
        bw, off = 0.33, 0.215
        for gi, (axname, b, a) in enumerate(p["groups"]):
            xb, xa = gi - off, gi + off
            rb = ax.bar([xb], [b], width=bw, color=C(BEFORE), zorder=2)
            ra = ax.bar([xa], [a], width=bw, color=C(AX_COL[axname]), zorder=2)
            tb = ax.text(xb, b + ymax * 0.02, vn(b, nd), ha="center", va="bottom",
                         fontsize=14, color=C(MUTED))
            ta = ax.text(xa, a + ymax * 0.02, vn(a, nd), ha="center", va="bottom",
                         fontsize=15, color=C(INK), fontweight="bold")
            d = pct(b, a)
            arrow = "▼" if d < 0 else "▲"
            td = ax.text(gi, max(a, b) + ymax * 0.135, f"{arrow} {vn(abs(d), 1)} %", ha="center",
                         va="bottom", fontsize=15, color=C(INK), fontweight="bold")
            _axis_label(ax, gi, -0.085, axname)
            base_arts += [rb, tb]
            after_arts += [ra, ta, td]
            anchors.setdefault(p["key"], {})[axname] = {
                "center": _to_in(fig, ax, gi, 0)[0], "pct": round(d, 1)}
        ttl = fig.text(px0 + 0.008, 0.935, p["title"], ha="left", va="center",
                       fontsize=16, color=C(INK), fontweight="bold")
        base_arts.append(ttl)
    files = _save_layers(fig, name, outdir, {"base": base_arts, "after": after_arts})
    plt.close(fig)
    ANCH[name] = {"files": files, "size": list(size), "anchors": anchors}


# ---------------------------------------------------------------------------
# 2. Cot phuong an mo phong (phuong an chon = cam)
# ---------------------------------------------------------------------------
def options_bars(name, outdir, items, chosen, size, ylabel, nd=2, ymax=None, horizontal=False,
                 ghost=None):
    fig = plt.figure(figsize=size, dpi=DPI)
    if horizontal:
        ax = fig.add_axes([0.40, 0.08, 0.50, 0.86])
    else:
        ax = fig.add_axes([0.12, 0.25, 0.86, 0.70])
    _style_ax(ax, ygrid=not horizontal)
    labels = [i[0] for i in items]
    vals = [i[1] for i in items]
    cols = [C(ACCENT) if k == chosen else (C("D5DBE1") if ghost is not None and k in ghost else C(BEFORE_DARK))
            for k in range(len(items))]
    anchors = {}
    if horizontal:
        y = list(range(len(items)))[::-1]
        ax.barh(y, vals, height=0.56, color=cols, zorder=2)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=14)
        ax.xaxis.set_visible(False)
        ax.spines["bottom"].set_visible(False)
        mx = ymax or max(vals) * 1.25
        ax.set_xlim(0, mx)
        for k, (yy, v) in enumerate(zip(y, vals)):
            ax.text(v + mx * 0.02, yy, vn(v, nd) + " °", va="center", ha="left",
                    fontsize=15, color=C(INK), fontweight="bold" if k == chosen else "normal")
            anchors[k] = _to_in(fig, ax, v, yy)
        for t in ax.get_yticklabels():
            t.set_color(C(INK))
    else:
        x = list(range(len(items)))
        ax.bar(x, vals, width=0.56, color=cols, zorder=2)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=14)
        mx = ymax or max(vals) * 1.25
        ax.set_ylim(0, mx)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: vn(v, 0)))
        ax.set_ylabel(ylabel, fontsize=14)
        for k, (xx, v) in enumerate(zip(x, vals)):
            ax.text(xx, v + mx * 0.025, vn(v, nd), ha="center", va="bottom", fontsize=15,
                    color=C(INK), fontweight="bold" if k == chosen else "normal")
            anchors[k] = _to_in(fig, ax, xx, v)
    fig.savefig(os.path.join(outdir, f"{name}.png"), dpi=DPI, transparent=True)
    plt.close(fig)
    ANCH[name] = {"files": {"base": f"{name}.png"}, "size": list(size), "anchors": anchors}


# ---------------------------------------------------------------------------
# 3. Khao sat tau_p (mo phong)
# ---------------------------------------------------------------------------
def taup_line(name, outdir, size):
    fig = plt.figure(figsize=size, dpi=DPI)
    ax = fig.add_axes([0.14, 0.24, 0.83, 0.70])
    _style_ax(ax)
    xs = [r[0] for r in TAUP_SWEEP]
    ys = [r[1] for r in TAUP_SWEEP]
    ax.plot(xs, ys, color=C(BEFORE_DARK), linewidth=2.2, zorder=2)
    for x, y in zip(xs, ys):
        chosen = x == 12
        ax.plot([x], [y], marker="o", markersize=13 if chosen else 9,
                color=C(ACCENT) if chosen else C(BEFORE_DARK), markeredgecolor="white",
                markeredgewidth=2, zorder=3)
        ax.text(x, y + 0.28, vn(y, 2), ha="center", va="bottom", fontsize=15,
                color=C(INK), fontweight="bold" if chosen else "normal")
    ax.set_xlim(-1.5, 16.5)
    ax.set_ylim(0, 5.0)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{x}" for x in xs], fontsize=14)
    ax.set_xlabel(r"Khoảng ngoại suy $\tau_p$ (ms)", fontsize=14)
    ax.set_ylabel(r"$e_{\mathrm{rms}}$ (°)", fontsize=14)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: vn(v, 0)))
    fig.savefig(os.path.join(outdir, f"{name}.png"), dpi=DPI, transparent=True)
    anchors = {str(x): _to_in(fig, ax, x, y) for x, y in zip(xs, ys)}
    plt.close(fig)
    ANCH[name] = {"files": {"base": f"{name}.png"}, "size": list(size), "anchors": anchors}


# ---------------------------------------------------------------------------
# 4. Khoang cap nhat RS485 tren he that (cot = p99, rau = lon nhat)
# ---------------------------------------------------------------------------
def rs485_real(name, outdir, size):
    fig = plt.figure(figsize=size, dpi=DPI)
    base, after = [], []
    anchors = {}
    for i, axname in enumerate(["Yaw", "Pitch"]):
        axx = 0.085 + i * 0.49
        ax = fig.add_axes([axx, 0.15, 0.40, 0.65])
        _style_ax(ax)
        ax.set_ylim(0, 72)
        ax.set_xlim(-0.62, 1.62)
        ax.set_xticks([])
        ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(20))
        ref = ax.axhline(10, color=C("C62828"), linewidth=1.4, linestyle=(0, (5, 3)), zorder=1)
        base.append(ref)
        d = RS_REAL[axname]
        for k, (scheme, col, lab) in enumerate([("prio", BEFORE, "Ưu tiên Yaw"),
                                                ("rr", AX_COL[axname], "Luân phiên")]):
            p99, mx = d[scheme]
            bar = ax.bar([k], [p99], width=0.46, color=C(col), zorder=2)
            wcol = C(BEFORE_DARK) if scheme == "prio" else C(AX_COL[axname])
            wl = ax.plot([k, k], [p99, mx], color=wcol, linewidth=2.2, zorder=3)[0]
            cap = ax.plot([k - 0.12, k + 0.12], [mx, mx], color=wcol, linewidth=3.0, zorder=3,
                          solid_capstyle="butt")[0]
            tv = ax.text(k, p99 / 2, vn(p99, 1), ha="center", va="center", fontsize=14,
                         color=C(INK) if scheme == "prio" else "white", fontweight="bold")
            tm = ax.text(k + 0.16, mx, vn(mx, 1), ha="left", va="center", fontsize=14,
                         color=C(INK), fontweight="bold")
            lb = ax.text(k, -3.0, lab, ha="center", va="top", fontsize=14, color=C(INK))
            arts = [bar, wl, cap, tv, tm, lb]
            (base if scheme == "prio" else after).extend(arts)
            anchors.setdefault(axname, {})[scheme] = {"x": _to_in(fig, ax, k, mx)[0],
                                                      "max_y": _to_in(fig, ax, k, mx)[1]}
        base.append(fig.text(axx - 0.07, 0.9, "●" if axname == "Yaw" else "■", ha="left",
                             va="center", fontsize=17, color=C(AX_COL[axname])))
        base.append(fig.text(axx - 0.04, 0.9, f"Trục {axname}", ha="left", va="center",
                             fontsize=16, fontweight="bold", color=C(INK)))
        if i == 0:
            ax.set_ylabel("Khoảng cập nhật (ms)", fontsize=14)
    base.append(fig.text(0.995, 0.9, "cột: p99  ·  râu: lớn nhất", ha="right", va="center",
                         fontsize=13, color=C(MUTED)))
    base.append(fig.text(0.995, 0.81, "– – 10 ms danh định", ha="right", va="center",
                         fontsize=13, color=C("C62828")))
    files = _save_layers(fig, name, outdir, {"base": base, "after": after})
    plt.close(fig)
    ANCH[name] = {"files": files, "size": list(size), "anchors": anchors}


# ---------------------------------------------------------------------------
# 5. Tong hop e_max qua cac buoc (dung dan tung doan)
# ---------------------------------------------------------------------------
def chain_emax(name, outdir, size):
    fig = plt.figure(figsize=size, dpi=DPI)
    ax = fig.add_axes([0.085, 0.215, 0.895, 0.665])
    _style_ax(ax)
    n = len(CHAIN)
    xs = list(range(n))
    yaw = [r[2] for r in CHAIN]
    pit = [r[4] for r in CHAIN]
    ax.set_xlim(-0.45, n - 0.55)
    ax.set_ylim(0, 24)
    ax.set_xticks(xs)
    ax.set_xticklabels([r[0] for r in CHAIN], fontsize=13, linespacing=1.05)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    ax.set_ylabel(r"$e_{\max}$ (°) · bài thử đảo chiều nhanh 10,1 s", fontsize=14)
    # dai nhan manh: ngoai suy (lon nhat) va tao dang (danh doi)
    hl1 = ax.axvspan(1.08, 1.92, color=C(ACCENT), alpha=0.10, zorder=0, linewidth=0)
    hl2 = ax.axvspan(4.08, 4.92, color=C(TRADE), alpha=0.13, zorder=0, linewidth=0)
    layers = {"base": [], }
    # diem dau
    p0y = ax.plot([0], [yaw[0]], marker="o", markersize=11, color=C(YAW), markeredgecolor="white", markeredgewidth=2, zorder=4)[0]
    p0p = ax.plot([0], [pit[0]], marker="s", markersize=10, color=C(PITCH), markeredgecolor="white", markeredgewidth=2, zorder=4)[0]
    t0y = ax.text(-0.12, yaw[0] + 1.0, vn(yaw[0], 2) + "°", ha="center", va="bottom", fontsize=15, fontweight="bold", color=C(INK))
    t0p = ax.text(-0.12, pit[0] - 1.1, vn(pit[0], 2) + "°", ha="center", va="top", fontsize=15, fontweight="bold", color=C(INK))
    layers["base"] += [p0y, p0p, t0y, t0p]
    anchors = {}
    for k in range(1, n):
        arts = []
        arts += ax.plot(xs[k - 1:k + 1], yaw[k - 1:k + 1], color=C(YAW), linewidth=2.6, zorder=3)
        arts += ax.plot(xs[k - 1:k + 1], pit[k - 1:k + 1], color=C(PITCH), linewidth=2.6, zorder=3)
        arts += ax.plot([k], [yaw[k]], marker="o", markersize=11, color=C(YAW), markeredgecolor="white", markeredgewidth=2, zorder=4)
        arts += ax.plot([k], [pit[k]], marker="s", markersize=10, color=C(PITCH), markeredgecolor="white", markeredgewidth=2, zorder=4)
        dy, dp = pct(yaw[k - 1], yaw[k]), pct(pit[k - 1], pit[k])
        xm = k - 0.5
        ym_y = (yaw[k - 1] + yaw[k]) / 2
        ym_p = (pit[k - 1] + pit[k]) / 2
        if abs(dy) >= 0.05:
            arts.append(ax.text(xm, ym_y + 1.15, vn(dy, 1, sign=True) + " %", ha="center", va="bottom",
                                fontsize=13, color=C(INK), fontweight="bold" if abs(dy) > 10 else "normal"))
        else:
            arts.append(ax.text(xm, ym_y + 1.15, "0 %", ha="center", va="bottom", fontsize=13, color=C(MUTED)))
        if abs(dp) >= 0.05:
            arts.append(ax.text(xm, ym_p - 1.2, vn(dp, 1, sign=True) + " %", ha="center", va="top",
                                fontsize=13, color=C(INK), fontweight="bold" if abs(dp) > 10 else "normal"))
        else:
            arts.append(ax.text(xm, ym_p - 1.2, "0 %", ha="center", va="top", fontsize=13, color=C(MUTED)))
        if k == n - 1:
            arts.append(ax.text(k + 0.13, yaw[k] + 1.0, vn(yaw[k], 2) + "°", ha="center", va="bottom", fontsize=15, fontweight="bold", color=C(INK)))
            arts.append(ax.text(k + 0.13, pit[k] - 1.1, vn(pit[k], 2) + "°", ha="center", va="top", fontsize=15, fontweight="bold", color=C(INK)))
        if k == 2:
            arts.append(hl1)
        if k == 5:
            arts.append(hl2)
        layers[f"seg{k}"] = arts
        anchors[k] = {"x": _to_in(fig, ax, k, 0)[0], "yaw_y": _to_in(fig, ax, k, yaw[k])[1],
                      "pitch_y": _to_in(fig, ax, k, pit[k])[1]}
    anchors[0] = {"x": _to_in(fig, ax, 0, 0)[0], "yaw_y": _to_in(fig, ax, 0, yaw[0])[1],
                  "pitch_y": _to_in(fig, ax, 0, pit[0])[1]}
    leg = ax.legend([Line2D([], [], color=C(YAW), marker="o", linewidth=2.6, markersize=10),
                     Line2D([], [], color=C(PITCH), marker="s", linewidth=2.6, markersize=9)],
                    ["Trục Yaw", "Trục Pitch"], loc="lower left", bbox_to_anchor=(0.0, 1.0),
                    ncol=2, fontsize=14, handlelength=2.4, columnspacing=1.4, borderaxespad=0.3)
    layers["base"].append(leg)
    files = _save_layers(fig, name, outdir, layers)
    plt.close(fig)
    ANCH[name] = {"files": files, "size": list(size), "anchors": anchors}


# ---------------------------------------------------------------------------
# 6. Minh hoa nguyen ly ngoai suy (so do nguyen ly, khong phai so lieu do)
# ---------------------------------------------------------------------------
def extrap_concept(name, outdir, size):
    import numpy as np
    fig = plt.figure(figsize=size, dpi=DPI)
    ax = fig.add_axes([0.02, 0.10, 0.96, 0.86])
    f = lambda t: np.cos(np.pi * t * 1.25)  # noqa: E731
    df = lambda t: -np.pi * 1.25 * np.sin(np.pi * t * 1.25)  # noqa: E731
    t = np.linspace(0.07, 0.92, 400)
    ax.plot(t, f(t), color=C(YAW), linewidth=3.0, zorder=2)
    t0, tp = 0.30, 0.17
    w0, a0 = f(t0), df(t0)
    ax.plot([t0 - 0.08, t0 + tp + 0.04], [w0 - a0 * 0.08, w0 + a0 * (tp + 0.04)], color=C(ACCENT),
            linewidth=2.4, linestyle=(0, (6, 3)), zorder=3)
    ax.plot([t0, t0 + tp], [w0, w0], color=C(BEFORE_DARK), linewidth=2.2, zorder=2)
    for x in (t0, t0 + tp):
        ax.plot([x, x], [-1.2, 1.08], color="#C5CED8", linewidth=1.0, zorder=1)
    ax.plot([t0], [w0], marker="o", markersize=12, color=C(YAW), markeredgecolor="white", markeredgewidth=2, zorder=5)
    ax.plot([t0 + tp], [w0], marker="s", markersize=11, color=C(BEFORE_DARK), markeredgecolor="white", markeredgewidth=2, zorder=5)
    ax.plot([t0 + tp], [w0 + a0 * tp], marker="o", markersize=13, color=C(ACCENT), markeredgecolor="white", markeredgewidth=2, zorder=6)
    ax.annotate("", xy=(t0 + tp, -1.08), xytext=(t0, -1.08),
                arrowprops=dict(arrowstyle="<->", color=C(INK), lw=1.5))
    ax.text(t0 + tp / 2, -1.02, r"$\tau_p$ = 12 ms", ha="center", va="bottom", fontsize=15, color=C(INK))
    ax.text(t0 - 0.02, w0 + 0.07, r"$\omega_b(t)$", ha="right", va="bottom", fontsize=16, color=C(INK))
    ax.text(0.0, 0.99, r"$\omega_b$", ha="left", va="top", fontsize=15, color=C(MUTED), transform=ax.transAxes)
    ax.text(0.99, 0.47, "t", ha="right", va="bottom", fontsize=15, color=C(MUTED), transform=ax.transAxes)
    ax.axhline(0, color="#9AA7B4", linewidth=1.0, zorder=1)
    lx, ly = 0.53, 0.93
    ax.plot([lx], [ly], marker="o", markersize=12, color=C(ACCENT), markeredgecolor="white", transform=ax.transAxes, clip_on=False)
    ax.text(lx + 0.03, ly, "có ngoại suy: đúng lúc", ha="left", va="center", fontsize=14, color=C(INK), transform=ax.transAxes)
    ax.plot([lx], [ly - 0.13], marker="s", markersize=11, color=C(BEFORE_DARK), markeredgecolor="white", transform=ax.transAxes, clip_on=False)
    ax.text(lx + 0.03, ly - 0.13, "không ngoại suy: trễ 12 ms", ha="left", va="center", fontsize=14, color=C(INK), transform=ax.transAxes)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(-1.25, 1.12)
    ax.axis("off")
    fig.savefig(os.path.join(outdir, f"{name}.png"), dpi=DPI, transparent=True)
    plt.close(fig)
    ANCH[name] = {"files": {"base": f"{name}.png"}, "size": list(size), "anchors": {}}


def build_all(outdir):
    os.makedirs(outdir, exist_ok=True)
    RIGHT = (7.40, 3.40)
    LEFT = (4.06, 2.30)
    # Buoc 2 - bu IMU2
    before_after("s20_real", outdir, [
        {"key": "emax", "title": r"$e_{\max}$ (°)", "nd": 2,
         "groups": [("Yaw", 20.24, 18.15), ("Pitch", 13.24, 11.89)]},
        {"key": "erms", "title": r"$e_{\mathrm{rms}}$ (°)", "nd": 3,
         "groups": [("Yaw", 5.462, 5.153), ("Pitch", 2.931, 2.753)]},
    ], RIGHT)
    options_bars("s20_sim", outdir, SIM_COMP_240[:3], 2, LEFT, r"$e_{\mathrm{rms}}$ (°)",
                 nd=2, horizontal=True, ymax=27)
    # Buoc 3 - ngoai suy
    before_after("s21_real", outdir, [
        {"key": "emax", "title": r"$e_{\max}$ (°)", "nd": 2,
         "groups": [("Yaw", 18.15, 14.20), ("Pitch", 11.89, 9.10)]},
        {"key": "erms", "title": r"$e_{\mathrm{rms}}$ (°)", "nd": 3,
         "groups": [("Yaw", 5.153, 4.268), ("Pitch", 2.753, 2.271)]},
    ], RIGHT)
    taup_line("s21_sim", outdir, LEFT)
    # Buoc 4 - gioi han dong
    before_after("s22_real", outdir, [
        {"key": "rho", "title": r"Tỉ lệ bão hòa $\rho_{\mathrm{sat}}$ (%)", "nd": 1,
         "groups": [("Yaw", 2.6, 0.8)]},
        {"key": "emax", "title": r"$e_{\max}$ (°)", "nd": 2,
         "groups": [("Yaw", 14.20, 13.52), ("Pitch", 9.10, 9.08)]},
    ], RIGHT, widths=[1.3, 2])
    options_bars("s22_sim", outdir, SIM_LIMIT_600, 2, LEFT, r"$e_{\mathrm{rms}}$ (°)", nd=2, ymax=12.5)
    # Buoc 7 - RS485
    rs485_real("s25_real", outdir, RIGHT)
    # Tong hop
    chain_emax("s26_chain", outdir, (8.25, 4.95))
    # Minh hoa ngoai suy
    extrap_concept("s13_extrap", outdir, (5.75, 2.75))
    with open(os.path.join(outdir, "anchors.json"), "w", encoding="utf-8") as f:
        json.dump(ANCH, f, ensure_ascii=False, indent=1)
    return ANCH


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "charts_out"
    a = build_all(out)
    print(json.dumps({k: v["files"] for k, v in a.items()}, ensure_ascii=False, indent=1))
