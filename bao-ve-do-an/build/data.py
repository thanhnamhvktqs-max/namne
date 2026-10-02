# -*- coding: utf-8 -*-
"""So lieu dung chung cho bieu do, slide va ghi chu thuyet trinh.

Tat ca gia tri lay tu bo slide bao cao goc (cac Bang 1.4, 2.4, 2.5, 3.9, 3.13,
3.18, 3.19, 3.20, 3.21 va ghi chu cac slide). Moi bieu do trong bo slide moi
deu ve lai tu cac so lieu nay - khong co so lieu nao duoc noi suy hay tu tao.
"""

# ---------------------------------------------------------------------------
# Mau sac va ky hieu thong nhat cho toan bo slide
# ---------------------------------------------------------------------------
NAVY = "0B2545"      # tieu de, khoi toi
BLUE = "0A5FA8"      # mau chu dao (nhan phan, khung)
INK = "1E2B3A"       # chu than
MUTED = "5B6B7B"     # chu phu
YAW = "1F5FAF"       # truc Yaw  - ky hieu tron (o)
PITCH = "2E8B57"     # truc Pitch - ky hieu vuong (#)
BEFORE = "B8C2CC"    # cau hinh truoc / doi chung
BEFORE_DARK = "7F8B98"
ACCENT = "E8710A"    # gia tri quan trong, phuong an duoc chon
TRADE = "B7791F"     # danh doi co chu dich
BAD = "C62828"       # van de / chua dat
GOOD = "1E7B34"      # dat (luon kem bieu tuong)
CARD = "FFFFFF"
TINT = "EAF3FB"      # nen nhat cho the
GRID = "E3E8EE"

# ---------------------------------------------------------------------------
# Lo trinh hieu chinh (Bang 3.20 - bai thu dao chieu nhanh 10,1 s)
# ---------------------------------------------------------------------------
STEPS = [
    # nhan ngan (tracker), ten day du
    ("Ban đầu", "Cấu hình ban đầu"),
    ("Cascade", "Hiệu chỉnh cascade"),
    ("Bù IMU2", "Bù IMU2"),
    ("Ngoại suy", "Ngoại suy bù trễ"),
    ("Giới hạn động", "Giới hạn lệnh động"),
    ("Đảo chiều/dừng", "Xử lý đảo chiều và dừng"),
    ("Tạo dạng lệnh", "Tạo dạng lệnh"),
    ("Lịch RS485", "Hoàn thiện lịch RS485"),
    ("Hoàn thiện", "Cấu hình hoàn thiện"),
]

# Cau hinh -> (e_rms Yaw, e_max Yaw, e_rms Pitch, e_max Pitch, rho_sat Yaw %, t_ph dao chieu s)
CHAIN = [
    ("Ban đầu\n(cascade)", 5.462, 20.24, 2.931, 13.24, 6.1, 0.392),
    ("Bù IMU2", 5.153, 18.15, 2.753, 11.89, 4.3, 0.347),
    ("Ngoại suy\n12 ms", 4.268, 14.20, 2.271, 9.10, 2.6, 0.318),
    ("Giới hạn\nđộng", 4.192, 13.52, 2.266, 9.08, 0.8, 0.309),
    ("Đảo chiều,\ndừng", 4.131, 12.96, 2.238, 8.83, 0.7, 0.291),
    ("Tạo dạng\nlệnh", 4.189, 13.17, 2.262, 8.93, 0.7, 0.299),
    ("Lịch RS485\n(hoàn thiện)", 4.189, 13.17, 2.262, 8.93, 0.7, 0.299),
]


def pct(before, after):
    """Phan tram thay doi (after - before) / before * 100."""
    return (after - before) / before * 100.0


def vn(x, nd=1, sign=False):
    """So kieu Viet Nam: dau phay thap phan, dau tru dai."""
    s = f"{abs(x):.{nd}f}".replace(".", ",")
    if x < 0:
        return "−" + s
    if sign and x > 0:
        return "+" + s
    return s


# ---------------------------------------------------------------------------
# Buoc 1 - noi tang (Bang 2.4, Hinh 3.4, 3.7)
# ---------------------------------------------------------------------------
KP_SWEEP = [  # Kp_theta, t_r ms, t_s ms, u_max deg/s, % gioi han 110 deg/s
    (6.0, 299.6, 566, 38.8),
    (9.5, 162.7, 318, 61.5),
    (13.0, 97.1, 196, 84.1),
]
OMEGA_MAX_YAW = 110.0
JE_KI = -85.7
GAINS = {  # Yaw, Pitch
    "Kp_theta": (9.5, 38.0), "Kp_omega": (0.28, 0.15), "Ki_omega": (1.0, 0.5),
    "omega_max": (110, 100),
}
STEP_REAL = {  # Bang 3.21 - 7 lan thu Yaw, 6 lan thu Pitch
    "tr": (224.5, 108.6), "ts": (520.0, 265.0), "os": (0.398, 0.716),
    "sigma": (0.0205, 0.0068),
}

# ---------------------------------------------------------------------------
# Buoc 2, 3 - bu IMU2 va ngoai suy (Hinh 3.x, Bang 3.9)
# ---------------------------------------------------------------------------
SIM_COMP_240 = [  # e_rms (deg), khung mang nhanh 240 deg/s
    ("Chỉ phản hồi", 20.925),
    ("Bù hệ số cố định", 2.293),
    ("Bù theo tốc độ", 1.886),
    ("+ Ngoại suy 12 ms", 1.318),
]
TAUP_SWEEP = [  # tau_p ms, e_rms, e_max, omega_c_rms, t_ph ms, u_max
    (0, 4.061, 5.936, 31.36, 302, 364.4),
    (8, 3.134, 4.640, 24.43, 274, 355.6),
    (12, 2.672, 3.988, 21.01, 260, 351.3),
    (15, 2.326, 3.499, 18.48, 250, 348.0),
]
IMU2_SLOW_FAST = {"before": (3.778, 6.114), "after": (3.435, 5.698)}  # e_rms cham/nhanh
TS_FAST = (2.305, 2.433)  # t_s khi khung nhanh, s (+5,6 %)

# ---------------------------------------------------------------------------
# Buoc 4 - gioi han lenh dong (Bang 2.5, mo phong xung 600 deg/s)
# ---------------------------------------------------------------------------
SIM_LIMIT_600 = [("Cố định\n135 °/s", 9.91), ("Hai mốc", 8.17), ("Bốn mốc", 8.05)]
ZONES = [  # ten, nguong vao Yaw/Pitch, k Yaw/Pitch, gioi han
    ("Chậm", "–", "0,85 / 0,80", 110),
    ("Thường", "50 / 30", "0,90 / 0,86", 135),
    ("Nhanh", "140 / 90", "0,95 / 0,92", 165),
    ("Rất nhanh", "220 / 170", "k(v)", 165),
]

# ---------------------------------------------------------------------------
# Buoc 5 - dao chieu va dung (12 lan thu, ham 2 300 deg/s^2)
# ---------------------------------------------------------------------------
RECOVERY = {"Yaw": (0.572, 0.272), "Pitch": (0.443, 0.183)}  # s
STOP_CONFIRM = {"Yaw": ("7/12", "12/12"), "Pitch": ("8/12", "12/12")}

# ---------------------------------------------------------------------------
# Buoc 6 - tao dang lenh (Bang 3.13, Hinh 3.18)
# ---------------------------------------------------------------------------
SHAPING_SIM = [  # phuong an, buoc lenh deg/s, doi dau ms, e_max deg, t_ph ms, nang luong 10-30 Hz %
    ("Không giới hạn", 600, 2, 19.87, 238, 100),
    ("18 000 °/s²", 36, 42, 21.40, 258, 21),
    ("30 000 °/s²", 60, 32, 20.30, 243, 38),
    ("18 000 / 30 000", 60, 32, 20.33, 244, 23),
]
CMD_STEP = (109.0, 59.9)  # buoc lenh lon nhat tren chu ky 2 ms, deg/s (truc Yaw)
IQ_CHANGE = -22.3        # % dong Iq hieu dung

# ---------------------------------------------------------------------------
# Buoc 7 - lich RS485 (Bang 3.18, 3.19, Hinh 3.19, 3.20)
# ---------------------------------------------------------------------------
RS_SIM = {  # p99, max (ms); Yaw lay tu nhan Hinh 3.19, Pitch tu Bang 3.18
    "Yaw": {"prio": (7.06, 15.05), "rr": (11.74, 30.13)},
    "Pitch": {"prio": (30.23, 70.02), "rr": (11.82, 22.18)},
}
RS_SIM_NOSTART = (7.2, 0.8)  # % giao dich khong khoi dong duoc
RS_REAL = {  # tai day du: p99, max (ms) - Bang 3.19
    "Yaw": {"prio": (8.1, 16.1), "rr": (12.0, 14.1)},
    "Pitch": {"prio": (23.8, 62.1), "rr": (12.1, 14.1)},
}
RS_SIGMA_PITCH = (13.3, 2.0)  # ms
RS_TRANS = {"low_rr": (2.25, 2.25, 3.25), "full_rr": (2.25, 4.25, 6.00), "full_prio": (2.25, 5.75, 7.50)}
RS_ERR = {"rr": (4.189, 13.17, 2.262, 8.93), "prio": (3.825, 12.14, 2.391, 10.96)}
