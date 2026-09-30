"""Tep Word rieng cho muc 3.4.1 - Hoan thien lich truyen RS485 (Hinh 3.19 - 3.21, Bang 3.12 - 3.13, cong thuc 3.7).

Chay sau run_part5.py va figs341.py:  python build341.py
"""
exec(open('build_head.py', encoding='utf8').read())   # D, f, pc, inc, red, fig, LD, V, R2, AX, AXN ...
import pickle
R5 = pickle.load(open('results5.pkl', 'rb'))
OUT341 = OUTF.replace('Chuong3_3.1.3_den_het', 'Muc_3.4.1_lich_RS485')

E = C.exc(); T = E['T']
L6 = LD['tao_dang']; L7 = LD['hoan_thien']
SV = R5['survey']; YP = SV[('yawpri', 5e-3)]; A4 = SV[('alt', 4e-3)]; A5 = SV[('alt', 5e-3)]; A6 = SV[('alt', 6e-3)]
P = R5['pair']; BG = P['by_gap']
bc = R2['bus_closed']
rows_bus = R5['log_bus']; last = rows_bus[-1]
T_CTRL = 76.306                               # 21:49:12,037 -> 21:50:28,343 (log A)
n_tx = int(last[1]); rate_meas = n_tx / T_CTRL; n_tx_s = f'{n_tx:,}'.replace(',', '\u00a0')
gmaxY, gmaxP, exec_max = last[3] / 1e3, last[4] / 1e3, last[6] / 1e3
dmax_tx = int(np.abs(rows_bus[:, 1] - rows_bus[:, 2]).max())
gp = np.asarray(YP['sched']['pitch']['gaps'], float)
frac13 = float(np.mean(gp >= 13.0) * 100)
m4 = (T >= C.SEG[3][0]) & (T < C.SEG[3][1])
a95 = float(np.percentile(np.abs(np.gradient(E['wd']['pitch'], gsim.DT))[m4], 95))
a95_s = f'{a95:,.0f}'.replace(',', '\u00a0')
worse = lambda o: max(o['yaw']['erms'], o['pitch']['erms'])
ntot = sum(v['n'] for v in BG.values())

D.heading('3.4.1. Hoàn thiện lịch truyền RS485', 3)

# ---------------------------------------------------------------------------- a)
D.lead('a) Vấn đề của cấu hình đầu vào.',
       f'Sau khâu tạo dạng, e_{{rms}} tái hiện của trục Pitch ({f(L6["pitch"]["erms"], 3)}°) lớn hơn trục Yaw '
       f'({f(L6["yaw"]["erms"], 3)}°) dù Pitch có quán tính nhỏ hơn và hệ số vòng góc lớn hơn. Nguyên nhân nằm ở cách hai '
       'trục chia nhau bus: hai động cơ dùng chung bus RS485 bán song công nên mỗi thời điểm chỉ có một giao dịch. Với lịch '
       'ưu tiên Yaw, mỗi khe 5 ms luôn dành cho Yaw; giao dịch Pitch chỉ được ghép vào khe xen kẽ khi phần còn lại của khe '
       'đủ cho một giao dịch, tức giao dịch Yaw phải kết thúc trong 2,25 ms. Hình 3.19a minh họa điều này: giao dịch Yaw '
       '4,3 ms rồi 2,9 ms làm lượt Pitch bị hoãn hai lần liên tiếp, khoảng cập nhật Pitch tăng từ 10 lên 20 ms; giao dịch '
       'Yaw 6,2 ms tràn khe còn đẩy lùi mốc của cả lịch. Độ đều của lịch được đánh giá bằng khoảng cập nhật và độ tản mát '
       'của nó:')
D.equation(sub(mi('Δ'), mi('i,k')) + mr('=') + sub(mi('t'), mi('i,k')) + mr('−') + sub(mi('t'), mi('i,k') + mr('−1')) + mr(',   ') +
           sub(mi('σ'), mi('Δ,i')) + mr('=') + sqrt(frac(mr('1'), mi('N') + mr('−1')) + nary('∑', mi('k') + mr('=1'), mi('N'),
                                                                                          sup(paren(sub(mi('Δ'), mi('i,k')) + mr('−') + sub(mi('Δ̄'), mi('i'))), mr('2')))), '3.7')
D.para('với t_{i,k} là thời điểm phát lệnh thứ k của trục i, Δ_{i,k} là khoảng cập nhật và σ_{Δ,i} là độ tản mát. '
       f'Trên 100 s mô phỏng theo sự kiện, lịch ưu tiên Yaw cập nhật Pitch trung bình mỗi {f(YP["sched"]["pitch"]["mean"], 1)} ms '
       f'nhưng {f(frac13, 1)} % số lần có Δ ≥ 13 ms, phân vị 99 % là {f(YP["sched"]["pitch"]["p99"], 0)} ms, lớn nhất '
       f'{f(YP["sched"]["pitch"]["mx"], 1)} ms, σ_{{Δ}} = {f(YP["sched"]["pitch"]["std"], 2)} ms; trục Yaw gần như đều '
       f'(σ_{{Δ}} = {f(YP["sched"]["yaw"]["std"], 2)} ms) (Hình 3.19c).')
D.para('Khoảng cập nhật không đều tác động trực tiếp vào khâu bù. Ngoại suy (2.14) bù một độ trễ cố định τ_{p} = 12 ms; '
       'trong suốt khoảng chờ, động cơ giữ lệnh cũ, nên khi khung mang đang tăng tốc, lệnh thiếu xấp xỉ α_{b}(Δ − 10 ms) '
       f'so với lệnh cần có. Ở đoạn 4, gia tốc khung mang trên trục Pitch đạt {a95_s} °/s² (phân vị 95 %), nên mỗi lần '
       f'Δ = 20 ms lệnh thiếu khoảng {f(a95 * 0.010, 0)} °/s trong 10 ms – phần mà ngoại suy không biết để bù. Để tách riêng '
       'ảnh hưởng này, mô phỏng tái hiện được chạy theo cặp: cùng chuỗi nhiễu, cùng lịch của Yaw, chỉ thay thời điểm cập '
       'nhật Pitch bằng lưới đều 10 ms. Sai lệch lớn nhất trong một khoảng cập nhật Pitch tăng theo độ dài khoảng: cao hơn '
       f'{inc(BG[0]["eR"], BG[0]["eY"], 0)} khi Δ ≈ 10 ms, {inc(BG[1]["eR"], BG[1]["eY"], 0)} khi Δ ≈ 15 ms và '
       f'{inc(BG[2]["eR"], BG[2]["eY"], 0)} khi Δ ≥ 20 ms so với khi cập nhật đều (Hình 3.19d). Trên toàn bài thử, chỉ '
       f'riêng việc làm đều khoảng cập nhật đã giảm e_{{rms}} Pitch từ {f(P["yawpri"]["pitch"]["erms"], 3)}° xuống '
       f'{f(P["reg"]["pitch"]["erms"], 3)}° ({red(P["yawpri"]["pitch"]["erms"], P["reg"]["pitch"]["erms"])}) và phân vị 99 % '
       f'từ {f(P["yawpri"]["pitch"]["p99"], 3)}° xuống {f(P["reg"]["pitch"]["p99"], 3)}° '
       f'({red(P["yawpri"]["pitch"]["p99"], P["reg"]["pitch"]["p99"])}), trong khi Yaw không đổi. Như vậy yêu cầu đối với '
       'lịch truyền không phải là tần số cao nhất cho một trục, mà là khoảng cập nhật của cả hai trục có cận trên xác '
       'định (mục 1.4.1).')
fig(19, 'h3_19_lich_rs485_co_che', 'Ảnh hưởng của lịch truy cập bus tới khoảng cập nhật và sai lệch trục Pitch')

# ---------------------------------------------------------------------------- b)
D.lead('b) Mô phỏng khảo sát và lựa chọn phương án.',
       'Lịch truyền được chọn theo ba tiêu chí, xếp theo thứ tự ưu tiên: (1) tính tất định – khoảng cập nhật của mỗi '
       'trục có cận trên xác định và σ_{Δ} nhỏ, là điều kiện để khâu ngoại suy làm việc đúng; (2) sai lệch của trục kém '
       'hơn trong hai trục nhỏ nhất, vì yêu cầu kỹ thuật áp dụng cho cả hai trục; (3) mỗi khe còn ít nhất 1 ms dự trữ sau '
       'cửa sổ giao dịch lớn nhất, để hấp thụ trễ của luồng RS485 (mức ưu tiên 110 – 116, thấp hơn luồng IMU 120 và luồng '
       'an toàn 118).')
D.para('Bốn phương án được so sánh: lịch ưu tiên Yaw đang dùng và lịch luân phiên (2.33) với độ dài khe 4, 5 và 6 ms. '
       'Mỗi phương án được mô phỏng theo sự kiện trong 100 s với thời gian giao dịch lấy ngẫu nhiên theo ba nhóm: ngắn '
       '2,25 ms (86 %), thông thường 2,5 – 3,25 ms (11,5 %) và kéo dài 4 – 7,5 ms (2,5 %) khi luồng RS485 bị chen ngang '
       f'(log A ghi giao dịch dài nhất {f(exec_max, 0)} ms); khi một giao dịch tràn khe, mốc khe kế tiếp được đặt lại từ lúc '
       'hoàn tất như nguyên tắc thứ hai ở mục 2.4.2. Sau đó mỗi lịch được đưa vào vòng kín trên mô hình danh định với bài '
       'thử tham chiếu và τ_{p} = 12 ms (Hình 3.20, Bảng 3.12).')
D.para('So với lịch ưu tiên Yaw, lịch luân phiên khe 5 ms loại bỏ việc hoãn lượt: mỗi trục có khe riêng, giao dịch dài '
       'của trục này chỉ ảnh hưởng tới trục kia khi tràn khe và khi đó chỉ kéo dài Δ thêm đúng phần tràn (Hình 3.19b). '
       f'σ_{{Δ}} của Pitch giảm từ {f(YP["sched"]["pitch"]["std"], 2)} xuống {f(A5["sched"]["pitch"]["std"], 2)} ms, '
       f'Δ lớn nhất từ {f(YP["sched"]["pitch"]["mx"], 1)} xuống {f(A5["sched"]["pitch"]["mx"], 1)} ms, tần số cập nhật '
       f'Pitch tăng từ {f(YP["sched"]["pitch"]["rate"], 1)} lên {f(A5["sched"]["pitch"]["rate"], 1)} Hz. Cái giá là Yaw chỉ '
       f'còn {f(A5["sched"]["yaw"]["rate"], 1)} Hz thay vì {f(YP["sched"]["yaw"]["rate"], 0)} Hz: lệnh Yaw được giữ trung bình '
       'lâu hơn khoảng 2,5 ms mà ngoại suy 12 ms không bù, nên e_{rms} Yaw tăng từ '
       f'{f(YP["closed"]["yaw"]["erms"], 3)} lên {f(A5["closed"]["yaw"]["erms"], 3)}° ({inc(YP["closed"]["yaw"]["erms"], A5["closed"]["yaw"]["erms"])}), '
       f'còn Pitch giảm từ {f(YP["closed"]["pitch"]["erms"], 3)} xuống {f(A5["closed"]["pitch"]["erms"], 3)}° '
       f'({red(YP["closed"]["pitch"]["erms"], A5["closed"]["pitch"]["erms"])}). Theo tiêu chí (2), sai lệch của trục kém hơn '
       f'giảm từ {f(worse(YP["closed"]), 3)}° (Pitch) xuống {f(worse(A5["closed"]), 3)}° (Yaw).')
D.para('Độ dài khe quyết định đánh đổi giữa tần số và độ đều. Khe 6 ms đều nhất '
       f'(σ_{{Δ}} = {f(A6["sched"]["pitch"]["std"], 2)} ms) nhưng chỉ còn {f(A6["sched"]["pitch"]["rate"], 0)} Hz mỗi trục, '
       f'e_{{rms}} tăng lên {f(A6["closed"]["yaw"]["erms"], 3)} / {f(A6["closed"]["pitch"]["erms"], 3)}° (Yaw / Pitch). Khe 4 ms '
       f'cho {f(A4["sched"]["pitch"]["rate"], 0)} Hz và e_{{rms}} thấp nhất trong mô hình '
       f'({f(A4["closed"]["yaw"]["erms"], 3)} / {f(A4["closed"]["pitch"]["erms"], 3)}°, trục kém hơn thấp hơn khe 5 ms '
       f'{red(worse(A5["closed"]), worse(A4["closed"]))}), nhưng σ_{{Δ}} tăng lên {f(A4["sched"]["pitch"]["std"], 2)} ms và '
       f'Δ lớn nhất ({f(A4["sched"]["pitch"]["mx"], 1)} ms) bằng {f(A4["sched"]["pitch"]["mx"] / 8.0, 2)} lần chu kỳ danh '
       f'định, so với {f(A5["sched"]["pitch"]["mx"] / 10.0, 2)} lần ở khe 5 ms. Quyết định hơn là ngân sách thời gian: cửa '
       'sổ giao dịch lớn nhất gồm phát khung lệnh 10 byte (0,43 ms) và chờ phản hồi tối đa 3 ms, tức 3,5 ms như nguyên tắc '
       'thứ nhất ở mục 2.4.2; khe 4 ms chỉ còn 0,5 ms dự trữ, khe 5 ms còn 1,5 ms (Hình 3.20d). Giao dịch dài nhất đo '
       f'được trên hệ thật ({f(exec_max, 0)} ms) cho thấy trễ luồng là có thật, trong khi mô hình chỉ mô tả nó bằng nhóm '
       'giao dịch kéo dài, nên ưu thế của khe 4 ms là cận lạc quan.')
D.para('Lịch luân phiên với khe 5 ms được chọn vì là phương án duy nhất thỏa cả ba tiêu chí: lịch ưu tiên Yaw không có '
       'cận trên cho khoảng cập nhật Pitch, khe 4 ms không đủ dự trữ thời gian, khe 6 ms làm cả hai trục kém hơn. Khe '
       '4 ms chỉ nên dùng khi đã đo được trễ luồng với độ phân giải dưới 1 ms và xác nhận dự trữ 0,5 ms là đủ, đúng như '
       'Chương 2 đã dự kiến cho trường hợp tải truyền thông thấp. Khoảng ngoại suy cũng được kiểm tra lại với lịch mới: '
       'với τ_{p} = 8, 12 và 16 ms, lịch luân phiên luôn làm Yaw kém đi và Pitch tốt lên (e_{rms} Yaw '
       + ', '.join(f'{f(bc[("yawpri", tp)]["yaw"]["erms"], 3)} → {f(bc[("alt", tp)]["yaw"]["erms"], 3)}°' for tp in (0.008, 0.012, 0.016))
       + '; Pitch ' + ', '.join(f'{f(bc[("yawpri", tp)]["pitch"]["erms"], 3)} → {f(bc[("alt", tp)]["pitch"]["erms"], 3)}°' for tp in (0.008, 0.012, 0.016))
       + '), nên thứ tự giữa hai lịch không đổi. Sai lệch của cả hai lịch còn giảm khi tăng τ_{p} tới 16 ms; giới hạn trên '
       'của τ_{p} vẫn là năng lượng lệnh trên 20 Hz đã xét ở mục 3.2.3 và không phụ thuộc lịch truyền, nên giữ τ_{p} = 12 ms.')
fig(20, 'h3_20_khao_sat_rs485', 'Mô phỏng khảo sát phương án lập lịch và độ dài khe RS485')
rows = []
for (mode, slot), lab in zip([('yawpri', 5e-3), ('alt', 4e-3), ('alt', 5e-3), ('alt', 6e-3)],
                             ['Ưu tiên Yaw, khe 5 ms', 'Luân phiên, khe 4 ms', 'Luân phiên, khe 5 ms', 'Luân phiên, khe 6 ms']):
    o = SV[(mode, slot)]
    for ax in AX:
        s = o['sched'][ax]
        rows.append([lab, AXN[ax], f(s['rate'], 1), f(s['mean'], 2), f(s['p99'], 2), f(s['mx'], 2), f(s['std'], 2),
                     f(o['closed'][ax]['erms'], 3)])
D.table('Bảng 3.12. Kết quả khảo sát phương án lập lịch và độ dài khe RS485',
        [['Phương án', 'Trục', 'Tần số (Hz)', 'Δ trung bình (ms)', 'Δ p99 (ms)', 'Δ lớn nhất (ms)', 'σ_{Δ} (ms)', 'e_{rms} (°)']],
        rows, [3.6, 1.3, 1.5, 1.8, 1.5, 1.7, 1.4, 1.5], size=10, bold_rows=[4, 5], align=['left'] + ['center'] * 7,
        note='Ghi chú: mô phỏng khảo sát; Δ, σ_{Δ} từ mô phỏng theo sự kiện 100 s; e_{rms} trên bài thử tham chiếu với '
             'τ_{p} = 12 ms, trung bình 2 lượt.')

# ---------------------------------------------------------------------------- c)
D.lead('c) Áp dụng và đánh giá.',
       'Lịch luân phiên khe 5 ms được áp dụng cho cấu hình có tạo dạng lệnh, cho ra cấu hình hoàn thiện; bước này có cả '
       'số đo log A (Hình 3.21, Bảng 3.13). ' +
       f'Trên mô phỏng tái hiện, e_{{rms}} Pitch giảm {red(L6["pitch"]["erms"], L7["pitch"]["erms"])} và phân vị 99 % giảm '
       f'{red(L6["pitch"]["p99"], L7["pitch"]["p99"])}, còn e_{{rms}} Yaw tăng {inc(L6["yaw"]["erms"], L7["yaw"]["erms"])} '
       'đúng như khảo sát dự báo. Hai trục trở nên cân bằng '
       f'({f(L7["yaw"]["erms"], 3)}° / {f(L7["pitch"]["erms"], 3)}°) và sai lệch của trục kém hơn giảm từ '
       f'{f(max(L6["yaw"]["erms"], L6["pitch"]["erms"]), 3)}° xuống {f(max(L7["yaw"]["erms"], L7["pitch"]["erms"]), 3)}°. '
       f'Số đo log A xác nhận: e_{{rms}} = {f(V["log"]["yaw"]["erms"], 3)}° (Yaw), {f(V["log"]["pitch"]["erms"], 3)}° (Pitch).')
D.para('Bộ đếm RS485 trong log A cho phép kiểm tra trực tiếp tính tất định của lịch trên hệ thật (Hình 3.21d, e). '
       f'Trong {f(T_CTRL, 1)} s điều khiển, mỗi trục thực hiện {n_tx_s} giao dịch ({f(rate_meas, 1)} Hz), số giao dịch của ' +
       f'hai trục chênh nhau không quá {dmax_tx} ở mọi lần ghi và không có giao dịch lỗi hay quá hạn. Khoảng cập nhật lớn '
       f'nhất là {f(gmaxY, 0)} ms (Yaw) và {f(gmaxP, 0)} ms (Pitch), giao dịch dài nhất {f(exec_max, 0)} ms; bộ đếm có độ '
       'phân giải 1 ms nên đây là cận trên. Khoảng lớn nhất đo được dài hơn mô phỏng khe 5 ms '
       f'({f(A5["sched"]["yaw"]["mx"], 1)} ms) vì giao dịch dài nhất trên hệ thật ({f(exec_max, 0)} ms) vượt nhóm kéo dài '
       'của mô hình (7,5 ms), nhưng chỉ bằng khoảng một nửa khoảng lớn nhất của Pitch với lịch ưu tiên Yaw '
       f'({f(YP["sched"]["pitch"]["mx"], 0)} ms, mô phỏng). Log A không có bản ghi với lịch ưu tiên Yaw, nên trạng thái '
       'trước hiệu chỉnh chỉ có số liệu mô phỏng tái hiện.')
D.para('Tính tất định cải thiện rõ nhưng chưa tuyệt đối: một giao dịch 8 ms vẫn kéo dài khoảng cập nhật thêm khoảng '
       '3 ms. Giao dịch này dài hơn cửa sổ 3,5 ms của giao thức, nên nguyên nhân nằm ở trễ của luồng chứ không ở lịch; '
       'muốn thu hẹp tiếp cần đo thời gian giao dịch với độ phân giải nhỏ hơn 1 ms để xác định luồng nào chen ngang.')
fig(21, 'h3_21_rs485_truoc_sau', 'Trước và sau hoàn thiện lịch truyền RS485: mô phỏng tái hiện và số đo log A')
rows = []
for lab, getb, geta, getm, nd in [
        ('Tần số cập nhật (Hz)', lambda ax: YP['sched'][ax]['rate'], lambda ax: A5['sched'][ax]['rate'], lambda ax: rate_meas, 1),
        ('Khoảng cập nhật lớn nhất (ms)', lambda ax: YP['sched'][ax]['mx'], lambda ax: A5['sched'][ax]['mx'],
         lambda ax: gmaxY if ax == 'yaw' else gmaxP, 1),
        ('e_{rms} (°)', lambda ax: L6[ax]['erms'], lambda ax: L7[ax]['erms'], lambda ax: V['log'][ax]['erms'], 3),
        ('Phân vị 99 % |e| (°)', lambda ax: L6[ax]['p99'], lambda ax: L7[ax]['p99'], lambda ax: V['log'][ax]['p99'], 3),
        ('e_{max} (°)', lambda ax: L6[ax]['emax'], lambda ax: L7[ax]['emax'], lambda ax: V['log'][ax]['emax'], 2)]:
    row = [lab]
    for ax in AX:
        b_, a_ = getb(ax), geta(ax)
        row += [f(b_, nd), f(a_, nd), pc(b_, a_), f(getm(ax), nd)]
    rows.append(row)
D.table('Bảng 3.13. Chỉ tiêu trước và sau hoàn thiện lịch truyền RS485',
        [['Chỉ tiêu', 'Yaw: trước', 'Yaw: sau', 'Thay đổi', 'Yaw: đo', 'Pitch: trước', 'Pitch: sau', 'Thay đổi', 'Pitch: đo']],
        rows, [3.2, 1.35, 1.35, 1.45, 1.35, 1.35, 1.35, 1.45, 1.35], size=10, align=['left'] + ['center'] * 8,
        note='Ghi chú: "trước", "sau" là mô phỏng tái hiện, riêng hai dòng đầu là mô phỏng theo sự kiện 100 s; cột "đo" là '
             'số đo trực tiếp log A, khoảng cập nhật đo với độ phân giải 1 ms.')
D.save(OUT341)
print('saved', OUT341)
