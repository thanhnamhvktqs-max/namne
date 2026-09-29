"""Mo phong hai truc Yaw - Pitch theo dung chuoi lenh Chuong 2.

Doi tuong: moi truc la dong co MS3506 co vong toc do tich hop (tre thuan tau_d,
hang so thoi gian Tm, bang 3.1). Toc do tuong doi w_m = w_c - w_d duoc vong toc do
tich hop dieu chinh, nen chuyen dong khung mang w_d tac dong len camera qua cung
khau quan tinh. Ma sat Coulomb/tinh o khop va mot dang dao dong rieng 16,5 Hz cua
ket cau duoc bo sung (hai yeu to mo hinh (3.4) chua mo ta).
"""
import numpy as np

DT = 0.002

AX = ('yaw', 'pitch')

# ----------------------------------------------------------------------------- tham so
PLANT = {          # mo hinh danh dinh (Bang 3.1) - dung cho mo phong khao sat
    'yaw':   dict(Tm=0.013, taud=0.012),
    'pitch': dict(Tm=0.004, taud=0.012),
}
PLANT_REPLAY = {   # mo hinh tai hien: tre tuong duong khi chuyen dong lien tuc (hieu chinh theo log A)
    'yaw':   dict(Tm=0.013, taud=0.008),
    'pitch': dict(Tm=0.004, taud=0.010),
}
# yeu to hieu chinh (khong co trong mo hinh danh dinh) - duoc chinh o muc 3.1.3
CAL = {
    'yaw':   dict(Ti=0.15, Fc=2.0, Fs=3.5, g_mode=0.02, dscale=0.06),
    'pitch': dict(Ti=0.15, Fc=1.5, Fs=3.0, g_mode=0.02, dscale=0.02),
    'f_mode': 16.5, 'z_mode': 0.06,
    'gyro_noise': 0.13, 'ang_noise': 0.0075, 'imu2_noise': 0.13,
}

GAINS_FINAL = {
    'yaw':   dict(Kpt=9.5, Kpw=0.28, Kiw=1.0, Kff=1.0, wmax=110.0, abr=500.0, Ilim=35.0),
    'pitch': dict(Kpt=38.0, Kpw=0.15, Kiw=0.5, Kff=1.0, wmax=100.0, abr=500.0, Ilim=30.0),
}
GAINS_INIT = {
    'yaw':   dict(Kpt=6.0, Kpw=0.25, Kiw=0.0, Kff=1.0, wmax=110.0, abr=500.0, Ilim=35.0),
    'pitch': dict(Kpt=20.0, Kpw=0.12, Kiw=0.0, Kff=1.0, wmax=100.0, abr=500.0, Ilim=30.0),
}

# Bang 2.5 (Yaw / Pitch). Vung "rat nhanh": k theo (2.15), u_ffmax va u_max tang theo v
ZONES = {
    'yaw':   dict(ven=[0, 50, 140, 220], vex=[0, 36, 100, 160],
                  aen=[0, 300, 800, 1400], aex=[0, 200, 500, 900],
                  k=[0.85, 0.90, 0.95, 0.97], uffmax=[180, 190, 210, 380],
                  umax=[110, 135, 165, 410]),
    'pitch': dict(ven=[0, 30, 90, 170], vex=[0, 22, 65, 125],
                  aen=[0, 300, 800, 1400], aex=[0, 200, 500, 900],
                  k=[0.80, 0.86, 0.92, 0.95], uffmax=[120, 150, 185, 380],
                  umax=[110, 135, 165, 410]),
}
V_TOP = {'yaw': 300.0, 'pitch': 250.0}   # toc do ung voi muc tran cua vung rat nhanh


def zone_params(ax, z, v):
    Z = ZONES[ax]
    if z < 3:
        return Z['k'][z], Z['uffmax'][z], Z['umax'][z]
    # vung rat nhanh: noi suy tu moc vung nhanh toi muc tran (2.15)
    s = np.clip((v - Z['ven'][3]) / (V_TOP[ax] - Z['ven'][3]), 0, 1)
    s0 = np.clip((v - Z['ven'][2]) / (Z['ven'][3] - Z['ven'][2]), 0, 1)
    k = Z['k'][2] + (Z['k'][3] - Z['k'][2]) * max(s, s0)
    uff = Z['uffmax'][2] + (Z['uffmax'][3] - Z['uffmax'][2]) * max(s, 0.5 * s0)
    um = Z['umax'][2] + (Z['umax'][3] - Z['umax'][2]) * max(s, 0.5 * s0)
    return k, uff, um


# ----------------------------------------------------------------------------- bus
def txn_time(rng):
    r = rng.random()
    if r < 0.86:
        return 2.25e-3
    if r < 0.975:
        return rng.uniform(2.5e-3, 3.25e-3)
    return rng.uniform(4.0e-3, 7.5e-3)


def schedule(mode, T_end, rng, slot=5e-3):
    """Tra ve danh sach (thoi diem bat dau phat, truc) theo lich truyen."""
    ev = {'yaw': [], 'pitch': []}
    t = 0.0; n = 0
    if mode == 'alt':
        while t < T_end:
            ax = AX[n % 2]
            d = txn_time(rng)
            ev[ax].append((t, t + d))
            end = t + d
            nxt = t + slot
            t = nxt if end <= nxt else end      # dat lai lich tu thoi diem hoan tat
            n += 1
    else:  # uu tien Yaw: moi khe mot giao dich Yaw, Pitch ghep vao khe le neu du thoi gian
        while t < T_end:
            d = txn_time(rng)
            ev['yaw'].append((t, t + d))
            end = t + d
            if n % 2 == 1:
                dp = txn_time(rng)
                if (t + slot) - end >= 2.75e-3 - 1e-9:
                    ev['pitch'].append((end, end + dp)); end += dp
                else:
                    n -= 1                        # hoan sang khe sau
            nxt = t + slot
            t = nxt if end <= nxt else end
            n += 1
    return ev


# ----------------------------------------------------------------------------- mo phong
DEFAULT = dict(gains=GAINS_FINAL, ff='zone', k0=0.88, tp=0.012, dwmax=90.0,
               limit='zone', umax_fixed=135.0, rev=True, stop=True,
               shape=True, amax=18000.0, amax_rev=30000.0, jmax=2.5e6,
               bus='alt', rev_prio=True,
               rev_t0=0.010, rev_a=1000.0, rev_wxn=3.0,
               stop_wb=1.0, stop_al=60.0, stop_wm=2.0)


def config(**kw):
    c = dict(DEFAULT); c.update(kw); return c


def simulate(cfg, T, wd, theta_ref=None, seed=1, cal=CAL, plant=PLANT, record=False,
             t_metric=None):
    """Mo phong dong thoi hai truc tren luoi thoi gian T (buoc 2 ms)."""
    rng = np.random.default_rng(seed)
    N = len(T)
    ev = schedule(cfg['bus'], T[-1] - T[0] + 0.1, rng)
    res = {}
    # chuan bi lich phat/nhan theo buoc tinh cho moi truc
    tx_step = {}
    for ax in AX:
        tx = np.zeros(N, dtype=np.int8)
        ks = [int(round(s / DT)) for s, e in ev[ax]]
        for k in ks:
            if k < N:
                tx[k] = 1
        tx_step[ax] = tx
    gaps = {ax: np.diff([s for s, e in ev[ax]]) for ax in AX}

    for ax in AX:
        G = cfg['gains'][ax]; P = plant[ax]; C = cal[ax]
        d = int(round(P['taud'] / DT))
        w = wd[ax]
        ref = np.zeros(N) if theta_ref is None else theta_ref[ax]
        th = 0.0 if theta_ref is None else 0.0
        wc = 0.0; wm = 0.0; Iint = 0.0
        x = 0.0; xd = 0.0
        w0 = 2 * np.pi * cal['f_mode']; zt = cal['z_mode']
        ubuf = np.zeros(N + d + 2)
        I = 0.0; wsp = 0.0; us = 0.0; us1 = 0.0; utx = 0.0
        wbf = 0.0; wbprev = 0.0; alf = 0.0; uff_prev = 0.0
        a60 = 2 * np.pi * (60 if ax == 'yaw' else 55) * DT
        a60 = a60 / (1 + a60)
        a18 = 2 * np.pi * 18 * DT; a18 = a18 / (1 + a18)
        z = 0; lam = 1.0; zprev = 0; up_t = 0.0; dn_t = 0.0
        rev_on = False; sc = 0.0; sgn_hist = [0, 0, 0]; rev_age = 0.0; bad_t = 0.0
        stop_t = 0.0; stop_mode = False; stop_age = 0.0; kph = 1.0; hold_t = 0.0
        wm_q = 0.0
        e = np.zeros(N); u_log = np.zeros(N); sat = np.zeros(N, bool)
        du = np.zeros(N); uff_log = np.zeros(N); zone_log = np.zeros(N, np.int8)
        wc_log = np.zeros(N); rev_log = np.zeros(N, bool); wm_log = np.zeros(N)
        iq_log = np.zeros(N)
        prev_wm_rel = 0.0
        umax_cur = cfg['umax_fixed']
        for k in range(N):
            # ---------------- doi tuong: vong toc do tich hop cua dong co + ma sat
            u_in = ubuf[k]
            wrel = wc - w[k]
            drive = (u_in - wrel) + Iint
            if abs(wrel) < 0.05 and abs(drive) < C['Fs']:
                acc_rel = 0.0
                wc = w[k]                         # dinh: camera quay theo khung mang
            else:
                sgn = np.sign(wrel) if abs(wrel) >= 0.05 else np.sign(drive)
                acc = (drive - C['Fc'] * sgn) / P['Tm']
                wc = wc + acc * DT
            Iint += (u_in - wrel) * DT / C['Ti']
            iq_log[k] = drive                     # dai luong ti le voi dong Iq
            wrel_new = wc - w[k]
            acc_rel = (wrel_new - prev_wm_rel) / DT
            prev_wm_rel = wrel_new
            # dang dao dong rieng ket cau, kich thich boi gia toc tuong doi
            xdd = -2 * zt * w0 * xd - w0 * w0 * x + C['g_mode'] * acc_rel
            xd += xdd * DT; x += xd * DT
            th += wc * DT
            los = th + x
            e_true = ref[k] - los
            wc_log[k] = wc + xd
            wm_q = np.round(wrel_new)             # phan hoi toc do dong co 1 deg/s
            wm_log[k] = wrel_new
            # ---------------- cam bien
            wmeas = wc + xd + rng.normal(0, cal['gyro_noise'])
            thm = los + rng.normal(0, cal['ang_noise'])
            e[k] = ref[k] - thm                   # sai lech do boi IMU1 (nhu kenh giam sat)
            # ---------------- IMU2 va uoc luong chuyen dong khung mang
            wb_m = w[k] * (1 + C['dscale']) + rng.normal(0, cal['imu2_noise'])
            if cfg.get('glitch') and cfg['glitch'][0] <= k < cfg['glitch'][1]:
                wb_m += cfg['glitch'][2]          # mau IMU2 sai nhung van huu han
            wbf += a60 * (wb_m - wbf)
            al = (wbf - wbprev) / DT; wbprev = wbf
            alf += a18 * (al - alf)
            alpha = alf if abs(alf) > 30.0 else 0.0
            if cfg['ff'] == 'zone' or cfg['ff'] == 'fixed':
                what = wbf + np.clip(cfg['tp'] * alpha, -cfg['dwmax'], cfg['dwmax'])
            else:
                what = wbf
            v = abs(what)
            # ---------------- vung chuyen dong (2.18)-(2.20)
            Z = ZONES[ax]
            if cfg['limit'] == 'zone' or cfg['ff'] == 'zone':
                if z < 3 and (v > Z['ven'][z + 1] or abs(alpha) > Z['aen'][z + 1]):
                    up_t += DT
                else:
                    up_t = 0.0
                if z > 0 and v < Z['vex'][z] and abs(alpha) < Z['aex'][z]:
                    dn_t += DT
                else:
                    dn_t = 0.0
                if up_t >= 0.006:
                    zprev = z; z += 1; lam = 0.0; up_t = 0.0
                elif dn_t >= 0.15:
                    zprev = z; z -= 1; lam = 0.0; dn_t = 0.0
                lam += (1.0 - lam) * DT / 0.02
            k_a, uffm_a, umax_a = zone_params(ax, z, v)
            k_b, uffm_b, umax_b = zone_params(ax, zprev, v)
            kz = lam * k_a + (1 - lam) * k_b
            uffm = lam * uffm_a + (1 - lam) * uffm_b
            umz = lam * umax_a + (1 - lam) * umax_b
            zone_log[k] = z
            # ---------------- thanh phan bu
            if cfg['ff'] == 'zone':
                uff = np.clip(kz * what, -uffm, uffm)
            elif cfg['ff'] == 'fixed':
                uff = np.clip(cfg['k0'] * what, -380, 380)
            else:
                uff = 0.0
            # ---------------- phat hien dung (2.25)
            if cfg['stop']:
                still = abs(wbf) < cfg['stop_wb'] and abs(alf) < cfg['stop_al'] and abs(wm_q) < cfg['stop_wm']
                stop_t = stop_t + DT if still else 0.0
                if not stop_mode and stop_t >= 0.22 and uff_prev != 0.0:
                    stop_mode = True; stop_age = 0.0; I *= 0.30
                if stop_mode:
                    stop_age += DT
                    if stop_age > 0.15 and not still:
                        stop_mode = False
                kph = 1.0 if not stop_mode else max(0.0, 1 - stop_age / 0.05)
                uff *= kph
            uff_prev = uff if uff != 0 else uff_prev
            uff_log[k] = uff
            # ---------------- vong goc 100 Hz (2.11)-(2.12)
            if k % 5 == 0:
                eth = ref[k] - thm
                L = min(G['wmax'], np.sqrt(2 * G['abr'] * abs(eth)))
                wsp = float(np.clip(G['Kpt'] * eth, -L, L))
            ew = wsp - wmeas
            ufb = G['Kff'] * wsp + G['Kpw'] * ew + I
            ut = ufb - uff
            # ---------------- gioi han lenh (2.21)
            umax_cur = umz if cfg['limit'] == 'zone' else cfg['umax_fixed']
            u = float(np.clip(ut, -umax_cur, umax_cur))
            s = abs(ut) > umax_cur
            sat[k] = s
            if (not s) or ew * ut < 0:
                I = float(np.clip(I + G['Kiw'] * ew * DT, -G['Ilim'], G['Ilim']))
            # ---------------- che do dung (2.26)
            if cfg['stop'] and stop_mode:
                eth = ref[k] - thm
                u = float(np.clip(G['Kpt'] * eth, -1.0, 1.0) - np.clip(0.05 * wm_q, -2.0, 2.0)) - uff
            # ---------------- xu ly dao chieu (2.22)-(2.24)
            sg = -np.sign(what) if abs(what) >= cfg['rev_wxn'] else 0
            sgn_hist = [sg] + sgn_hist[:2]
            if cfg['rev']:
                if not rev_on and alpha != 0 and abs(alpha) >= cfg['rev_a']:
                    t0 = -what / alpha
                    if 0 < t0 <= cfg['rev_t0'] and abs(us) > 0:
                        rev_on = True; sc = np.sign(us); rev_age = 0.0; bad_t = 0.0
                if rev_on:
                    rev_age += DT
                    newside = sgn_hist[0] == -sc and sgn_hist[1] == -sc  # dau moi cua lenh
                    t0n = (-what / alpha) if alpha != 0 else -1.0
                    valid = (0 < t0n <= cfg['rev_t0']) or abs(what) < cfg['rev_wxn']
                    bad_t = bad_t + DT if not valid else 0.0
                    if newside or bad_t >= 0.004 or rev_age > 0.12:
                        rev_on = False
                    else:
                        uk = sc * u; up = sc * us
                        u = sc * min(max(uk, 0.0), max(up, 0.0))
            rev_log[k] = rev_on
            # ---------------- tao dang lenh (2.27)
            if cfg['shape']:
                am = cfg['amax_rev'] if rev_on else cfg['amax']
                a_prev = (us - us1) / DT
                a_req = (u - us) / DT
                a_req = np.clip(a_req, a_prev - cfg['jmax'] * DT, a_prev + cfg['jmax'] * DT)
                a_req = np.clip(a_req, -am, am)
                step = a_req * DT
                if (u - us) * step > 0 and abs(step) > abs(u - us):
                    step = u - us                 # khong vuot qua gia tri dich
                usn = us + step
            else:
                usn = u
            du[k] = usn - us
            us1 = us; us = usn
            u_log[k] = us
            # ---------------- truyen lenh RS485, tre thuan tau_d
            if tx_step[ax][k]:
                utx = round(us, 2)
            ubuf[k + d] = utx
            if k + d + 1 < len(ubuf):
                ubuf[k + d + 1] = utx
        out = dict(e=e, u=u_log, sat=sat, du=du, uff=uff_log, zone=zone_log,
                   wc=wc_log, rev=rev_log, wm=wm_log, gaps=gaps[ax], iq=iq_log)
        res[ax] = out
    return res


def metrics(T, r, ax, mask=None, ds=None):
    """Chi tieu tren cua so mask; ds: buoc lay mau lai (mo phong nhu kenh giam sat)."""
    e = r[ax]['e']; u = r[ax]['u']
    if mask is None:
        mask = np.ones(len(T), bool)
    idx = np.where(mask)[0]
    if ds:
        step = max(1, int(round(ds / DT)))
        idx_s = idx[::step]
    else:
        idx_s = idx
    es = e[idx_s]
    return dict(erms=float(np.sqrt(np.mean(es ** 2))), emax=float(np.abs(es).max()),
                p99=float(np.percentile(np.abs(es), 99)),
                rho=float(r[ax]['sat'][idx].mean() * 100),
                umax=float(np.abs(u[idx]).max()),
                dumax=float(np.abs(r[ax]['du'][idx]).max()),
                du99=float(np.percentile(np.abs(r[ax]['du'][idx]), 99)))


LADDER = [
    ('ban_dau', dict(gains=GAINS_INIT, ff='none', tp=0.0, limit='fixed', rev=False, stop=False, shape=False, bus='yawpri')),
    ('cascade', dict(ff='none', tp=0.0, limit='fixed', rev=False, stop=False, shape=False, bus='yawpri')),
    ('bu_imu2', dict(ff='zone', tp=0.0, limit='fixed', rev=False, stop=False, shape=False, bus='yawpri')),
    ('ngoai_suy', dict(ff='zone', tp=0.012, limit='fixed', rev=False, stop=False, shape=False, bus='yawpri')),
    ('gioi_han', dict(ff='zone', tp=0.012, limit='zone', rev=False, stop=False, shape=False, bus='yawpri')),
    ('dao_chieu', dict(ff='zone', tp=0.012, limit='zone', rev=True, stop=True, shape=False, bus='yawpri')),
    ('tao_dang', dict(ff='zone', tp=0.012, limit='zone', rev=True, stop=True, shape=True, bus='yawpri')),
    ('hoan_thien', dict(ff='zone', tp=0.012, limit='zone', rev=True, stop=True, shape=True, bus='alt')),
]
