"""Phan KET LUAN cua toan bao cao, viet lai cho khop Chuong 3 da chinh sua (8 cau hinh tich luy, log A, muc 3.4.1).

Chay:  python build_ketluan.py   ->  ../Ket_luan.docx
So lieu lay tu Chuong3_3.1.3_den_het.docx (Bang 3.2, 3.4, 3.5, 3.10, 3.14 - 3.16) va muc 3.4.1 ban 4 trang.
"""
import copy, re
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx_util import Doc

TEMPLATE = '../report.docx'
OUT = '../Ket_luan.docx'
NB = ' '

# lay dung doan tieu de "KET LUAN" cua ban goc (can giua, dam 16 pt, muc de cuong 0 de vao muc luc)
_src = Document(TEMPLATE)
_title = next(p for p in _src.paragraphs if p.text.strip() == 'KẾT LUẬN')

D = Doc(TEMPLATE)
for _rel in D.d.part.rels.values():                       # ky tu "`" lac o chan trang mau goc
    if _rel.reltype.endswith('/footer'):
        for _t in _rel.target_part.element.iter(qn('w:t')):
            if _t.text and _t.text.strip() == '`':
                _t.text = ''

UNITS = r'(%|ms|Hz|°/s|s\^\{−1\}|lần|giao dịch)'


def nb(s):
    """Khong ngat dong giua so va don vi, trong so co dau cach hang nghin, quanh dau '/' giua hai so."""
    s = s.replace('⁻¹', '^{−1}')
    s = re.sub(r'(\d) ' + UNITS, lambda m: m.group(1) + NB + m.group(2), s)
    s = re.sub(r'(\d) (\d{3})\b', r'\1' + NB + r'\2', s)
    s = re.sub(r'(\d[°%]?) / (\d)', r'\1' + NB + '/' + NB + r'\2', s)
    return s


def title():
    p = copy.deepcopy(_title._p)
    for el in list(p.iter()):
        if el.tag in (qn('w:bookmarkStart'), qn('w:bookmarkEnd'), qn('w:lastRenderedPageBreak')):
            el.getparent().remove(el)
    D.body.insert(D.body.index(D.sect), p)
    D._bookmark(D.d.paragraphs[-1])


def sub_head(text):
    """Tieu muc dam trong phan ket luan, giu dinh dang ban goc (lui dau dong 1 cm, dinh voi doan sau)."""
    p = D._p(); pf = p.paragraph_format
    pf.first_line_indent = Cm(1.0); pf.keep_with_next = True
    pf.space_before = Pt(6); pf.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run(text).bold = True


def para(text, lead=None):
    if lead:
        D.lead(lead, nb(text))
    else:
        D.para(nb(text))


def item(text):
    p = D.para(nb('– ' + text))
    return p


title()
para('Đề tài đã thiết kế, chế tạo và hiệu chỉnh hệ ổn định Gimbal hai trục Yaw – Pitch trên STM32F407VET6 và Apache '
     'NuttX, dùng hai cảm biến ICM20948 (IMU1 trên camera cho phản hồi, IMU2 trên khung mang đo chuyển động cần bù) và '
     'hai động cơ MS3506 dùng chung bus RS485. Chuỗi điều khiển gồm bộ điều khiển nối tầng góc 100 Hz – tốc độ góc '
     '500 Hz, bù chuyển động khung mang, ngoại suy bù trễ, giới hạn lệnh theo trạng thái, xử lý đảo chiều và dừng, tạo '
     'dạng lệnh và lịch RS485 luân phiên, thực thi trên bảy luồng thời gian thực kèm lớp giám sát, bảo vệ.')

sub_head('Các kết quả chính')
para('Thứ nhất, mô hình mô phỏng được xây dựng từ phép thử vòng hở (τ_{d} = 12 ms; T_{m} = 13 / 4 ms) và dùng ở hai '
     'mức: mô phỏng khảo sát để chọn tham số; mô phỏng tái hiện, hiệu chỉnh theo log A, để ước lượng các cấu hình trung '
     'gian với cùng kích thích. Mô hình tái hiện khớp số đo về e_{rms} trong 8,4 % (Yaw) và 4,8 % (Pitch).')
para('Thứ hai, qua tám cấu hình tích lũy, e_{rms} tái hiện giảm từ 5,46° xuống 0,182° (96,7 %) ở Yaw và từ 2,70° '
     'xuống 0,192° (92,9 %) ở Pitch. Ba bước quyết định là bù từ IMU2 (giảm 89,3 % / 79,5 %), ngoại suy bù trễ '
     'τ_{p} = 12 ms (giảm tiếp 35,2 % / 40,3 %) và giới hạn lệnh theo vùng, tới 410 °/s ở vùng rất nhanh (giảm tiếp '
     '42,2 % / 35,3 %, bão hòa lệnh về gần 0). Xử lý đảo chiều, dừng và tạo dạng lệnh cải thiện trạng thái giữ và độ '
     'êm của lệnh với chi phí mỗi khâu không quá 3,7 % e_{rms}. Lịch luân phiên khe 5 ms được chọn trong bốn phương án '
     'vì là phương án duy nhất vừa cho khoảng cập nhật có cận trên xác định, vừa còn dự trữ khe 1,5 ms: e_{rms} Pitch '
     'giảm 9,5 %, đổi lại e_{rms} Yaw tăng 19,5 %.')
para('Thứ ba, trên hệ thật, khi khung mang lắc ±27° / ±23° với tốc độ góc đỉnh 225 °/s, cấu hình hoàn thiện đạt '
     'e_{rms} = 0,199° (Yaw) và 0,201° (Pitch), e_{max} = 0,62° và 0,67°; độ lệch chuẩn khi giữ tĩnh 0,0076° / 0,0077°; '
     'tuyến RS485 cập nhật 100,6 Hz mỗi trục, không có giao dịch lỗi. Hệ đạt các chỉ tiêu khử nhiễu, độ chính xác giữ '
     'tĩnh và tần số cập nhật (Bảng 3.16).')

sub_head('Hạn chế')
para('Số liệu bảy cấu hình trung gian là ước lượng bằng mô phỏng tái hiện. Khoảng cập nhật RS485 lớn nhất đo được '
     '16 / 14 ms và giao dịch dài nhất 8 ms, vượt khe 5 ms khi luồng truyền thông bị chen ngang. Trục Pitch vọt lố '
     'khoảng 7,8 % do K_{pθ} được chọn ưu tiên khử nhiễu. Hiệu quả của xử lý đảo chiều, dừng và vùng tốc độ trên '
     '225 °/s chưa được xác nhận bằng thực nghiệm; bộ lọc chắn dải chưa đưa vào vận hành; trục Yaw chưa có mốc phương '
     'vị tuyệt đối.')

sub_head('Hướng phát triển')
para('Ghi đo từng cấu hình trên giá thử tạo được kích thích lặp lại; giảm chen ngang luồng RS485 (DMA, ngắt kết thúc '
     'khung) để có thể dùng khe 4 ms, về lâu dài tách bus từng trục hoặc dùng CAN kết hợp ngoại suy thích nghi; giảm '
     'vọt lố trục Pitch bằng lọc góc đặt; quét tần số để đưa bộ lọc chắn dải vào vận hành; bổ sung tham chiếu phương '
     'vị (từ kế hoặc GNSS) cho trục Yaw.')

D.save(OUT)
print('saved', OUT)
