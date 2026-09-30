"""Muc 3.4.1 - Hoan thien lich truyen RS485, ban khoang 4 trang A4.

Hinh 3.19 (co che), 3.20 (khao sat va lua chon), 3.21 (truoc / sau); Bang 3.12, 3.13; cong thuc (3.7).
Tren hinh chi co so lieu mo phong; so do log A chi nam trong loi van va cot "do" cua Bang 3.13.
Ky hieu: bien in nghieng (*e*, *Δ*, *σ*, *τ*, *α*, *t*, *k*, *N*), chi so mo ta in dung (rms, p, b).

Chay sau run_part5.py va figs341.py (phan '4tr'):  python build341_4tr.py
"""
exec(open('build_head.py', encoding='utf8').read())   # D, f, pc, inc, red, fig, LD, V, R2, AX, AXN ...
import pickle
NB = ' '
_pc, _inc, _red = pc, inc, red
pc = lambda a, b, nd=1: _pc(a, b, nd).replace(' %', NB + '%')      # khong ngat dong truoc dau %
inc = lambda a, b, nd=1: _inc(a, b, nd).replace(' %', NB + '%')
red = lambda a, b, nd=1: _red(a, b, nd).replace(' %', NB + '%')
R5 = pickle.load(open('results5.pkl', 'rb'))
OUT = OUTF.replace('Chuong3_3.1.3_den_het', 'Muc_3.4.1_lich_RS485_4_trang')


def bar(x):
    """Dau gach tren (gia tri trung binh) trong OMML."""
    return '<m:acc><m:accPr><m:chr m:val="̅"/></m:accPr><m:e>%s</m:e></m:acc>' % x


E = C.exc(); T = E['T']
L6 = LD['tao_dang']; L7 = LD['hoan_thien']
SV = R5['survey']; YP = SV[('yawpri', 5e-3)]; A4 = SV[('alt', 4e-3)]; A5 = SV[('alt', 5e-3)]; A6 = SV[('alt', 6e-3)]
P = R5['pair']; BG = P['by_gap']
bc = R2['bus_closed']
last = R5['log_bus'][-1]
T_CTRL = 76.306                               # 21:49:12,037 -> 21:50:28,343 (log A)
n_tx = int(last[1]); rate_meas = n_tx / T_CTRL; n_tx_s = f'{n_tx:,}'.replace(',', NB)
gmaxY, gmaxP, exec_max = last[3] / 1e3, last[4] / 1e3, last[6] / 1e3
dmax_tx = int(np.abs(R5['log_bus'][:, 1] - R5['log_bus'][:, 2]).max())
gp = np.asarray(YP['sched']['pitch']['gaps'], float)
m4 = (T >= C.SEG[3][0]) & (T < C.SEG[3][1])
a95 = float(np.percentile(np.abs(np.gradient(E['wd']['pitch'], gsim.DT))[m4], 95))
a95_s = f'{a95:,.0f}'.replace(',', NB)
worse = lambda o: max(o['yaw']['erms'], o['pitch']['erms'])
yp_, a5_ = YP['sched']['pitch'], A5['sched']['pitch']
ER = '*e*_{rms}'; DL = '*Δ*'; SD = '*σ*_{Δ}'; TP = '*τ*_{p}'; AB = '*α*_{b}'

D.heading('3.4.1. Hoàn thiện lịch truyền RS485', 3)

# ============================================================================ a)
D.lead('a) Vấn đề của cấu hình đầu vào.',
       f'Sau khâu tạo dạng, {ER} tái hiện của trục Pitch ({f(L6["pitch"]["erms"], 3)}°) lớn hơn trục Yaw '
       f'({f(L6["yaw"]["erms"], 3)}°) dù Pitch có quán tính nhỏ hơn. Hai động cơ dùng chung bus RS485 bán song công nên '
       'mỗi thời điểm chỉ có một giao dịch. Với lịch ưu tiên Yaw, mỗi khe 5 ms luôn dành cho Yaw; giao dịch Pitch chỉ được '
       'ghép vào khe xen kẽ khi giao dịch Yaw kết thúc trong 2,25 ms, nếu không lượt Pitch bị hoãn sang khe sau. Trên '
       'Hình 3.19a, hai giao dịch Yaw 4,3 ms và 2,9 ms làm lượt Pitch bị hoãn hai lần, khoảng cập nhật tăng từ 10 lên '
       '20 ms. Độ đều của lịch được đánh giá bằng khoảng cập nhật và độ lệch chuẩn của nó:')
fig(19, 'h3_19_lich_rs485', 'Ảnh hưởng của lịch truyền RS485 tới khoảng cập nhật và sai lệch trục Pitch')
D.equation(sub(mi('Δ'), mi('i,k')) + mr('=') + sub(mi('t'), mi('i,k')) + mr('−') + sub(mi('t'), mi('i,k') + mr('−1')) + mr(',     ') +
           sub(mi('σ'), mr('Δ,') + mi('i')) + mr('=') +
           sqrt(frac(mr('1'), mi('N') + mr('−1')) + nary('∑', mi('k') + mr('=1'), mi('N'),
                                                         sup(paren(sub(mi('Δ'), mi('i,k')) + mr('−') + sub(bar(mi('Δ')), mi('i'))), mr('2')))),
           '3.7')
D.para(f'trong đó *t*_{{i,k}} là thời điểm phát lệnh thứ *k* của trục *i*, *N* là số lần phát lệnh, *Δ̄*_{{i}} '
       f'là khoảng cập nhật trung bình. Trên 100 s mô phỏng theo sự kiện, trục Pitch có {DL} trung bình {f(yp_["mean"], 1)} ms '
       f'nhưng {f(np.mean(gp >= 13.0) * 100, 1)} % số lần từ 13 ms trở lên, lớn nhất {f(yp_["mx"], 1)} ms, '
       f'{SD} = {f(yp_["std"], 2)} ms; trục Yaw gần như đều ({SD} = {f(YP["sched"]["yaw"]["std"], 2)} ms) (Hình 3.19c).')
D.para(f'Khoảng cập nhật không đều làm sai khâu bù trễ: ngoại suy (2.14) giả thiết độ trễ không đổi {TP} = 12 ms, còn '
       f'khi {DL} kéo dài, động cơ giữ lệnh cũ thêm ({DL}{NB}−{NB}10{NB}ms) nên lệnh thiếu xấp xỉ '
       f'{AB}({DL}{NB}−{NB}10{NB}ms) khi khung mang tăng tốc. Mô phỏng tái hiện chạy theo cặp – cùng chuỗi nhiễu, chỉ thay '
       'thời điểm cập nhật Pitch bằng lưới đều 10 ms – cho thấy sai lệch lớn nhất trong một khoảng cập nhật cao hơn '
       f'{inc(BG[0]["eR"], BG[0]["eY"], 0)}, {inc(BG[1]["eR"], BG[1]["eY"], 0)} và {inc(BG[2]["eR"], BG[2]["eY"], 0)} khi '
       f'{DL} ≈ 10 ms, ≈ 15 ms và ≥ 20 ms (Hình 3.19d); riêng việc làm đều {DL} giảm {ER} Pitch '
       f'{red(P["yawpri"]["pitch"]["erms"], P["reg"]["pitch"]["erms"])}, trục Yaw không đổi. Vì vậy yêu cầu đối với lịch '
       'truyền là khoảng cập nhật của cả hai trục có cận trên xác định.')

# ============================================================================ b)
D.lead('b) Mô phỏng khảo sát và lựa chọn phương án.',
       f'Ba tiêu chí xếp theo thứ tự ưu tiên: (1) {DL} của mỗi trục có cận trên xác định và {SD} nhỏ; (2) {ER} của trục '
       'kém hơn trong hai trục nhỏ nhất; (3) mỗi khe còn ít nhất 1 ms dự trữ sau cửa sổ giao dịch lớn nhất để hấp thụ trễ '
       'của luồng RS485. Bốn phương án được so sánh: lịch ưu tiên Yaw và lịch luân phiên (2.33) với khe 4, 5, 6 ms. Mỗi '
       'phương án được mô phỏng theo sự kiện 100 s, thời gian giao dịch 2,25 ms (86 %), 2,5 – 3,25 ms (11,5 %) hoặc '
       '4 – 7,5 ms (2,5 %, khi luồng bị chen ngang), giao dịch tràn khe thì mốc khe sau đặt lại từ lúc hoàn tất; sau đó '
       f'đưa vào vòng kín trên mô hình danh định với {TP} = 12 ms (Hình 3.20, Bảng 3.12).')
D.para('Lịch luân phiên loại bỏ việc hoãn lượt vì mỗi trục có khe riêng; giao dịch dài chỉ kéo dài '
       f'{DL} thêm đúng phần tràn khe (Hình 3.19b). Với khe 5 ms, {SD} của Pitch giảm từ {f(yp_["std"], 2)} xuống '
       f'{f(a5_["std"], 2)} ms, {DL} lớn nhất từ {f(yp_["mx"], 1)} xuống {f(a5_["mx"], 1)} ms (Hình 3.20b). Cái giá là Yaw '
       f'chỉ còn {f(A5["sched"]["yaw"]["rate"], 0)} Hz thay vì {f(YP["sched"]["yaw"]["rate"], 0)} Hz (Hình 3.20a), lệnh Yaw '
       f'bị giữ lâu hơn trung bình 2,5 ms nên {ER} Yaw tăng {inc(YP["closed"]["yaw"]["erms"], A5["closed"]["yaw"]["erms"])}, '
       f'Pitch giảm {red(YP["closed"]["pitch"]["erms"], A5["closed"]["pitch"]["erms"])}; sai lệch của trục kém hơn giảm từ '
       f'{f(worse(YP["closed"]), 3)}° xuống {f(worse(A5["closed"]), 3)}° (Hình 3.20c).')
fig(20, 'h3_20_khao_sat_rs485', 'Mô phỏng khảo sát phương án lập lịch và độ dài khe RS485')
rows = []
verdict = {('yawpri', 5e-3): 'Loại (1)', ('alt', 4e-3): 'Loại (3)', ('alt', 5e-3): 'Chọn', ('alt', 6e-3): 'Loại (2)'}
for (mode, slot), lab in zip([('yawpri', 5e-3), ('alt', 4e-3), ('alt', 5e-3), ('alt', 6e-3)],
                             ['Ưu tiên Yaw, khe 5 ms', 'Luân phiên, khe 4 ms', 'Luân phiên, khe 5 ms', 'Luân phiên, khe 6 ms']):
    o = SV[(mode, slot)]; s = o['sched']
    rows.append([lab, f(s['yaw']['rate'], 0) + ' / ' + f(s['pitch']['rate'], 0),
                 f(s['yaw']['std'], 2) + ' / ' + f(s['pitch']['std'], 2),
                 f(s['yaw']['mx'], 1) + ' / ' + f(s['pitch']['mx'], 1), f(slot * 1e3 - 3.5, 1),
                 f(o['closed']['yaw']['erms'], 3) + ' / ' + f(o['closed']['pitch']['erms'], 3), verdict[(mode, slot)]])
D.table('Bảng 3.12. Kết quả khảo sát phương án lập lịch RS485 (giá trị Yaw / Pitch)',
        [['Phương án', 'Tần số cập nhật (Hz)', f'{SD} (ms)', f'{DL} lớn nhất (ms)', 'Dự trữ khe (ms)', f'{ER} (°)', 'Đánh giá']],
        rows, [3.9, 1.8, 1.9, 2.0, 1.5, 2.3, 1.5], size=10, bold_rows=[2], align=['left'] + ['center'] * 6,
        note='Ghi chú: mô phỏng khảo sát; (1), (2), (3) là các tiêu chí nêu trên.')
D.para(f'Khe dài thì đều hơn nhưng chậm hơn: khe 6 ms có {SD} = {f(A6["sched"]["pitch"]["std"], 2)} ms nhưng mỗi trục '
       f'chỉ {f(A6["sched"]["pitch"]["rate"], 0)} Hz, {ER} tăng lên {f(A6["closed"]["yaw"]["erms"], 3)} / '
       f'{f(A6["closed"]["pitch"]["erms"], 3)}°. Khe 4 ms cho {ER} thấp nhất trong mô hình '
       f'({f(A4["closed"]["yaw"]["erms"], 3)} / {f(A4["closed"]["pitch"]["erms"], 3)}°) nhưng bị giới hạn bởi ngân sách thời '
       'gian: cửa sổ giao dịch lớn nhất gồm phát khung lệnh 0,43 ms và chờ phản hồi tối đa 3 ms, tức 3,5 ms (mục 2.4.2), '
       'nên khe 4 ms chỉ còn 0,5 ms dự trữ, khe 5 ms còn 1,5 ms (Hình 3.20d); mô hình chưa có trễ luồng nên ưu thế của '
       'khe 4 ms là cận lạc quan. Lịch luân phiên khe 5 ms là phương án duy nhất thỏa cả ba tiêu chí nên được chọn. '
       f'Với {TP} = 8 và 16 ms, thứ tự giữa hai lịch không đổi; giới hạn trên của {TP} vẫn là năng lượng lệnh trên 20 Hz '
       f'(mục 3.2.3), nên giữ {TP} = 12 ms.')

# ============================================================================ c)
D.lead('c) Áp dụng và đánh giá.',
       'Lịch luân phiên khe 5 ms được áp dụng cho cấu hình có tạo dạng lệnh (Hình 3.21, Bảng 3.13). Trên mô phỏng tái '
       f'hiện, {ER} Pitch giảm {red(L6["pitch"]["erms"], L7["pitch"]["erms"])}, {ER} Yaw tăng '
       f'{inc(L6["yaw"]["erms"], L7["yaw"]["erms"])} như khảo sát dự báo; hai trục cân bằng '
       f'({f(L7["yaw"]["erms"], 3)}° / {f(L7["pitch"]["erms"], 3)}°), số đo log A là {f(V["log"]["yaw"]["erms"], 3)}° / '
       f'{f(V["log"]["pitch"]["erms"], 3)}°. Bộ đếm bus trong log A ghi mỗi trục {n_tx_s} giao dịch trong {f(T_CTRL, 1)} s '
       f'({f(rate_meas, 1)} Hz), hai trục chênh nhau không quá {dmax_tx} giao dịch, không có giao dịch lỗi; {DL} lớn nhất '
       f'{f(gmaxY, 0)} / {f(gmaxP, 0)} ms (độ phân giải 1 ms), bằng khoảng một nửa so với Pitch dùng lịch ưu tiên Yaw.')
fig(21, 'h3_21_rs485_truoc_sau_mp', 'Trước và sau hoàn thiện lịch truyền RS485 (mô phỏng tái hiện)')
rows = []
for lab, getb, geta, getm, nd in [
        ('Tần số cập nhật (Hz)', lambda ax: YP['sched'][ax]['rate'], lambda ax: A5['sched'][ax]['rate'], lambda ax: rate_meas, 1),
        (f'{DL} lớn nhất (ms)', lambda ax: YP['sched'][ax]['mx'], lambda ax: A5['sched'][ax]['mx'],
         lambda ax: gmaxY if ax == 'yaw' else gmaxP, 1),
        (f'{ER} (°)', lambda ax: L6[ax]['erms'], lambda ax: L7[ax]['erms'], lambda ax: V['log'][ax]['erms'], 3),
        ('Phân vị 99 % của |*e*| (°)', lambda ax: L6[ax]['p99'], lambda ax: L7[ax]['p99'], lambda ax: V['log'][ax]['p99'], 3)]:
    row = [lab]
    for ax in AX:
        b_, a_ = getb(ax), geta(ax)
        row += [f(b_, nd), f(a_, nd), pc(b_, a_), f(getm(ax), nd)]
    rows.append(row)
D.table('Bảng 3.13. Chỉ tiêu trước và sau hoàn thiện lịch truyền RS485',
        [['Chỉ tiêu', 'Yaw: trước', 'Yaw: sau', 'Thay đổi', 'Yaw: đo', 'Pitch: trước', 'Pitch: sau', 'Thay đổi', 'Pitch: đo']],
        rows, [3.9, 1.2, 1.2, 1.6, 1.2, 1.2, 1.2, 1.6, 1.2], size=10, align=['left'] + ['center'] * 8,
        note='Ghi chú: "trước", "sau": mô phỏng tái hiện (hai dòng đầu: mô phỏng theo sự kiện); "đo": log A.')
D.save(OUT)
print('saved', OUT)
