"""Dung file Word phan 3.1.3 - het Chuong 3 tu ket qua mo phong va log A."""
import sys, pickle, os
import numpy as np
from PIL import Image
sys.path.insert(0, '.')
import gsim
import common as C
from docx_util import Doc, mr, mi, sub, sup, frac, paren, sqrt, nary

R = pickle.load(open('results.pkl', 'rb'))
R2 = pickle.load(open('results2.pkl', 'rb'))
R3 = pickle.load(open('results3.pkl', 'rb'))
V = R['val']; LD = R['ladder']; SL = R['step_ladder']
FIG = 'figs'  # thu muc hinh do figs.py tao ra
TEMPLATE = 'report.docx'  # dat file bao cao goc (dung lam mau dinh dang) vao day
OUTF = 'Chuong3_3.1.3_den_het.docx'
AX = gsim.AX
AXN = {'yaw': 'Yaw', 'pitch': 'Pitch'}


def f(x, nd=2):
    s = f'{x:.{nd}f}'
    return s.replace('-', '−').replace('.', ',')


def pc(a, b, nd=1):
    """Muc thay doi tu a sang b (%)."""
    v = (b / a - 1) * 100
    s = f'{abs(v):.{nd}f}'.replace('.', ',')
    if abs(v) < 0.5 * 10 ** (-nd):
        return s + ' %'
    return ('+' if v > 0 else '−') + s + ' %'


def inc(a, b, nd=1):
    return f'{abs(b / a - 1) * 100:.{nd}f}'.replace('.', ',') + ' %'


def red(a, b, nd=1):
    """Muc giam tu a xuong b (%), so duong."""
    return f'{(1 - b / a) * 100:.{nd}f}'.replace('.', ',') + ' %'


NAME = {'ban_dau': 'cấu hình ban đầu',
        'cascade': 'cấu hình sau hiệu chỉnh bộ điều khiển nối tầng',
        'bu_imu2': 'cấu hình có bù chuyển động khung mang từ IMU2',
        'ngoai_suy': 'cấu hình có ngoại suy bù trễ',
        'gioi_han': 'cấu hình có giới hạn lệnh động',
        'dao_chieu': 'cấu hình có xử lý đảo chiều và dừng',
        'tao_dang': 'cấu hình có tạo dạng lệnh',
        'hoan_thien': 'cấu hình hoàn thiện'}
SHORT = {'ban_dau': 'Ban đầu', 'cascade': 'Sau hiệu chỉnh nối tầng', 'bu_imu2': 'Sau bù IMU2',
         'ngoai_suy': 'Sau ngoại suy bù trễ', 'gioi_han': 'Sau giới hạn lệnh động',
         'dao_chieu': 'Sau xử lý đảo chiều, dừng', 'tao_dang': 'Sau tạo dạng lệnh', 'hoan_thien': 'Hoàn thiện'}
ORDER = [n for n, _ in gsim.LADDER]

D = Doc(TEMPLATE)
# chan trang cua mau goc co mot ky tu "`" lac; bo di trong tep chuong
from docx.oxml.ns import qn as _qn
for _rel in D.d.part.rels.values():
    if _rel.reltype.endswith('/footer'):
        for _t in _rel.target_part.element.iter(_qn('w:t')):
            if _t.text and _t.text.strip() == '`':
                _t.text = ''


def fig(n, name, cap):
    """Chen hinh dung kich thuoc that (anh 600 dpi ve san theo cm), khong co gian."""
    p = os.path.join(FIG, name + '.png')
    w_cm = Image.open(p).size[0] / 600 * 2.54
    D.figure(p, f'Hình 3.{n}. {cap}', width_cm=min(w_cm, 16.0))


def ba_rows(before, after, keys):
    """Dong bang truoc / sau cho hai truc."""
    rows = []
    for lab, key, nd, src in keys:
        row = [lab]
        for ax in AX:
            if src == 'ladder':
                b = LD[before][ax][key]; a = LD[after][ax][key]
            else:
                b = src[before][ax][key]; a = src[after][ax][key]
            row += [f(b, nd), f(a, nd), pc(b, a) if b else '–']
        rows.append(row)
    return rows


BA_HEAD = [['Chỉ tiêu', 'Yaw: trước', 'Yaw: sau', 'Thay đổi', 'Pitch: trước', 'Pitch: sau', 'Thay đổi']]
BA_W = [4.2, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7]
LAD_KEYS = [('e_{rms} (°)', 'erms', 3, 'ladder'), ('Phân vị 99 % của |e| (°)', 'p99', 3, 'ladder'),
            ('e_{max} (°)', 'emax', 2, 'ladder')]
NOTE_TR = 'Ghi chú: giá trị mô phỏng tái hiện (ước lượng đáp ứng hệ thật, mục 3.1.3), trung bình 3 lượt với chuỗi nhiễu khác nhau; chỉ tiêu tính trên đoạn 8,5 – 76 s của bài thử tham chiếu tại các thời điểm lấy mẫu của log A.'

