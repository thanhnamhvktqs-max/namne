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
para('Đề tài đã thiết kế, chế tạo và hiệu chỉnh hệ ổn định Gimbal hai trục Yaw – Pitch trên STM32F407VET6 và hệ điều '
     'hành thời gian thực Apache NuttX, dùng hai cảm biến ICM20948 (IMU1 trên khối camera cho phản hồi, IMU2 trên khung '
     'mang đo chuyển động cần bù) và hai động cơ MS3506 dùng chung bus RS485. Chuỗi điều khiển gồm bộ điều khiển nối '
     'tầng (cascade) góc 100 Hz – tốc độ góc 500 Hz, bù chuyển động khung mang từ IMU2, ngoại suy bù trễ, giới hạn lệnh '
     'theo trạng thái chuyển động, xử lý đảo chiều và dừng, tạo dạng lệnh và lịch truyền RS485 luân phiên, thực thi trên '
     'bảy luồng có mức ưu tiên và nhịp riêng, kèm lớp giám sát, bảo vệ và khôi phục.')

sub_head('Các kết quả chính')
para('Thứ nhất, Chương 1 đã quy năm nhóm nguyên nhân làm giảm chất lượng ổn định về sáu hướng hiệu chỉnh (Bảng 1.5); '
     'Chương 2 hiện thực các hướng đó thành một chuỗi biến đổi lệnh nhiều lớp, mỗi khâu có đầu vào, đầu ra và tham số '
     'xác định (Bảng 2.6), nhờ đó từng khâu được bổ sung và đánh giá riêng ở Chương 3.')
para('Thứ hai, mô hình mô phỏng được xây dựng từ phép thử vòng hở (τ_{d} = 12 ms; T_{m} = 13 ms cho Yaw, 4 ms cho '
     'Pitch) và dùng ở hai mức: mô phỏng khảo sát trên mô hình danh định để chọn tham số; mô phỏng tái hiện, hiệu chỉnh '
     'theo bản ghi đo log A (trễ tương đương τ_{e} = 8 / 10 ms, hệ số đường bù IMU2 1,06 / 1,02), để ước lượng các cấu '
     'hình trung gian với cùng kích thích là chuyển động khung mang đã ghi lại. Mô hình tái hiện khớp số đo về e_{rms} '
     'trong 8,4 % (Yaw) và 4,8 % (Pitch), trong khi mô hình danh định cho e_{rms} trục Yaw gần gấp đôi số đo.')
para('Thứ ba, quá trình hoàn thiện gồm bảy bước qua tám cấu hình tích lũy, mỗi bước theo cùng trình tự vấn đề – mô '
     'phỏng khảo sát – lựa chọn – áp dụng và so sánh trước, sau trên hai trục. e_{rms} tái hiện trên bài thử tham chiếu '
     'giảm từ 5,46° xuống 0,182° (96,7 %) ở Yaw và từ 2,70° xuống 0,192° (92,9 %) ở Pitch. Hiệu chỉnh nối tầng '
     '(K_{pθ} = 9,5 / 38 s⁻¹, K_{pω} = 0,28 / 0,15, K_{iω} = 1,0 / 0,5 s⁻¹) rút ngắn thời gian tăng trục Yaw 45 % nhưng '
     'e_{rms} chỉ giảm 30,4 % / 6,4 %, vì cấu trúc chỉ có phản hồi không khử được sai lệch tỉ lệ với tốc độ khung mang. '
     'Ba bước quyết định là bù từ IMU2 với hệ số k(v) theo vùng (e_{rms} giảm 89,3 % / 79,5 %), ngoại suy bù trễ '
     'τ_{p} = 12 ms (giảm tiếp 35,2 % / 40,3 %) và giới hạn lệnh theo vùng 110 / 135 / 165 °/s, vùng rất nhanh tới '
     '410 °/s (giảm tiếp 42,2 % / 35,3 %, bão hòa lệnh về gần 0).')
para('Thứ tư, các khâu hoàn thiện được chọn với đánh đổi đã lượng hóa. Xử lý đảo chiều (t_{0max} = 10 ms, '
     'α_{rev} = 1 000 °/s²), chế độ dừng (ngưỡng 1 °/s) và tạo dạng lệnh (a_{max} = 18 000 / 30 000 °/s²) không nhằm '
     'giảm e_{rms} mà xử lý trạng thái giữ và độ êm của lệnh, mỗi khâu làm e_{rms} thay đổi không quá 3,7 %; độ lệch chuẩn '
     'lệnh trục Yaw khi giữ giảm 85 %, bước lệnh lớn nhất trục Pitch giảm 38 %. Lịch truyền RS485 được chọn trong bốn '
     'phương án theo ba tiêu chí (khoảng cập nhật có cận trên xác định, sai lệch trục kém hơn nhỏ nhất, dự trữ khe ít '
     'nhất 1 ms); lịch luân phiên khe 5 ms là phương án duy nhất thỏa cả ba: khoảng cập nhật lớn nhất trục Pitch giảm từ '
     '32,3 xuống 12,5 ms, e_{rms} Pitch giảm 9,5 %, đổi lại e_{rms} Yaw tăng 19,5 % và hai trục trở nên cân bằng.')
para('Thứ năm, trên hệ thật, khi khung mang được lắc ±27° quanh trục đứng, ±23° quanh trục ngang với tốc độ góc đỉnh '
     '225 °/s, cấu hình hoàn thiện đạt e_{rms} = 0,199° (Yaw) và 0,201° (Pitch), e_{max} = 0,62° và 0,67°; sai lệch '
     'lớn nhất xuất hiện khi khung mang đổi chiều. Độ lệch chuẩn góc khi giữ tĩnh là 0,0076° / 0,0077°. Tuyến RS485 '
     'thực hiện 7 676 giao dịch mỗi trục trong 76,3 s (100,6 Hz), không có giao dịch lỗi hay quá hạn. Theo Bảng 3.16, '
     'hệ đạt các chỉ tiêu khử nhiễu, độ chính xác giữ tĩnh, vọt lố trục Yaw và tần số cập nhật.')

sub_head('Hạn chế')
para('Chỉ cấu hình hoàn thiện có bản ghi đo; số liệu bảy cấu hình trung gian là ước lượng bằng mô phỏng tái hiện, '
     'và mô hình chưa mô tả tương tác giữa hai trục qua kết cấu. Tuyến RS485 chưa tất định hoàn toàn: khoảng cập nhật '
     'lớn nhất đo được 16 / 14 ms, vượt chu kỳ danh định 10 ms tới 60 %, giao dịch dài nhất 8 ms vượt khe 5 ms khi luồng '
     'RS485 bị chen ngang, lúc đó trễ thực tế lớn hơn τ_{p}. Độ vọt lố bậc thang trục Pitch khoảng 7,8 % (mô phỏng tái hiện), chưa đạt chỉ '
     'tiêu dưới 1 %, do K_{pθ} được chọn ưu tiên khử nhiễu. Hiệu quả của xử lý đảo chiều và chế độ dừng chưa được xác '
     'nhận bằng thực nghiệm; vùng tốc độ trên 225 °/s mới được kiểm tra bằng mô phỏng. Bộ lọc chắn dải chưa đưa vào '
     'vận hành do tần số cộng hưởng chưa được xác nhận lặp lại; trục Yaw chưa có mốc phương vị tuyệt đối do không dùng '
     'từ kế.')

sub_head('Hướng phát triển')
item('Ghi đo từng cấu hình trung gian trên giá thử tạo được kích thích lặp lại và vượt 225 °/s, để kiểm chứng trực '
     'tiếp đóng góp của từng khâu và bổ sung tương tác hai trục vào mô hình.')
item('Nâng tính tất định của RS485: giảm chen ngang luồng truyền thông (DMA, ngắt kết thúc khung), khi giao dịch dài '
     'nhất dưới 3,5 ms có thể dùng khe 4 ms (124 Hz mỗi trục); về lâu dài tách bus riêng từng trục hoặc dùng CAN, kết '
     'hợp khoảng ngoại suy thích nghi theo tuổi thực của lệnh.')
item('Giảm vọt lố trục Pitch bằng lọc hoặc giới hạn tốc độ thay đổi góc đặt thay vì giảm K_{pθ}; quét tần số để xác '
     'nhận cộng hưởng và đưa bộ lọc chắn dải vào vận hành.')
item('Bổ sung tham chiếu phương vị cho trục Yaw (từ kế hoặc la bàn GNSS) và nghiên cứu điều khiển trực tiếp dòng I_{q} '
     'để rút ngắn trễ của vòng tốc độ.')

D.save(OUT)
print('saved', OUT)
