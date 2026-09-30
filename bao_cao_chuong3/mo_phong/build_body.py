# ============================================================================ 3.1.3
ex = V['exc_all']; ln = V['sim_nom']; lg = V['log']; sm = V['sim']
L0 = LD['ban_dau']; L1 = LD['cascade']; L2 = LD['bu_imu2']; L3 = LD['ngoai_suy']
L4 = LD['gioi_han']; L5 = LD['dao_chieu']; L6 = LD['tao_dang']; L7 = LD['hoan_thien']
b0 = SL['ban_dau']; b1 = SL['cascade']
cas = R['cascade']; kp = R3['kpw']
R4 = pickle.load(open('results4.pkl', 'rb')); CF = R4['cascade_full']

D.heading('3.1.3. Mô hình mô phỏng, bài thử chuẩn và kiểm chứng mô hình', 3)
D.para('Các bước hiệu chỉnh ở mục 3.2 – 3.4 dùng một chương trình mô phỏng Python cài đặt đúng chuỗi lệnh của Chương 2 (Bảng 2.6) ở hai mức. **Mô phỏng khảo sát** dùng mô hình danh định của mục 3.1.2 (τ_{d} = 12 ms; T_{m} = 13 ms cho Yaw, 4 ms cho Pitch) để so sánh các phương án và chọn tham số. **Mô phỏng tái hiện** dùng mô hình được hiệu chỉnh để tái hiện bản ghi đo của cấu hình hoàn thiện (log A), và được dùng để ước lượng đáp ứng hệ thật ở các cấu hình trung gian không còn bản ghi đo. Trong chương, giá trị ghi "mô phỏng tái hiện" là giá trị ước lượng theo cách này; chỉ các giá trị ghi "đo (log A)" và Bảng 3.1 là số đo trực tiếp.')

D.lead('a) Mô hình hai trục.', 'Bộ điều khiển tích hợp của MS3506 điều khiển tốc độ tương đối giữa rô-to và stato, tức ω_{c} − ω_{b}, nên chuyển động khung mang tác động lên camera qua chính khâu quán tính của cơ cấu; với mỗi trục, mô hình (3.4) được viết lại thành:')
D.equation(sub(mi('T'), mr('m')) + frac(mr('d') + sub(mi('ω'), mr('c')), mr('d') + mi('t')) + mr('+') +
           sub(mi('ω'), mr('c')) + mr('=') + mi('u') + paren(mi('t') + mr('−') + sub(mi('τ'), mr('e'))) + mr('+') +
           sub(mi('ω'), mr('b')) + mr('+') + sub(mi('I'), mr('m')) + mr('−') +
           sub(mi('F'), mr('ms')) + paren(sub(mi('ω'), mr('c')) + mr('−') + sub(mi('ω'), mr('b'))), '3.5')
D.para('trong đó τ_{e} là trễ tương đương của đường lệnh, I_{m} là thành phần tích phân của vòng tốc độ tích hợp và F_{ms} là ma sát Coulomb – ma sát tĩnh tại khớp. Mô hình bổ sung dạng dao động riêng 16,5 Hz của kết cấu, nhiễu con quay 0,13 °/s trên hai IMU (đo bởi lệnh imu2 trong log A), lượng tử lệnh 0,01 °/s và phản hồi tốc độ 1 °/s, ma sát Coulomb / tĩnh giả thiết 2,0 / 3,5 °/s (Yaw) và 1,5 / 3,0 °/s (Pitch), lịch RS485 theo sự kiện và phép chiếu (2.9); bước tính 2 ms, vòng góc 100 Hz, vòng tốc độ 500 Hz, tham số điều khiển theo Bảng 2.4 – 2.6.')


D.lead('b) Bài thử tham chiếu.', f'Log A ghi góc camera (IMU1) và tư thế khung mang (IMU2) ở 50 Hz trong 76 s điều khiển, khi khung mang được lắc bằng tay theo năm đoạn (Hình 3.5; đặc trưng từng đoạn ở Bảng 3.14). Khoảng 10 % mẫu bị mất khi chương trình in dòng trạng thái, nên thời điểm thật của từng mẫu được dựng lại bằng quy hoạch động (gán mỗi mẫu vào khe 20 ms nguyên sao cho gia tốc các góc đo nhỏ nhất, xác định được 376 lần mất một mẫu và 16 lần mất hai mẫu). Tư thế khung mang được nội suy spline, lấy đạo hàm và lọc hai chiều 10 Hz để có tốc độ góc khung mang chiếu lên hai trục, hiệu dụng {f(ex["yaw"]["rms"], 0)} / {f(ex["pitch"]["rms"], 0)} °/s, đỉnh {f(ex["yaw"]["peak"], 0)} / {f(ex["pitch"]["peak"], 0)} °/s (Yaw / Pitch). Mọi cấu hình được mô phỏng tái hiện với đúng kích thích này, nên chênh lệch giữa các cấu hình chỉ do chuỗi điều khiển.')
fig(5, 'h3_05_kich_thich', 'Bài thử tham chiếu: chuyển động khung mang ghi trong log A')

D.para('Các bước còn dùng bậc thang góc 5° (Yaw), 3° (Pitch) khi khung mang đứng yên, giữ tĩnh, các lần khung mang đổi chiều trong bài thử tham chiếu, dừng đột ngột từ 110 °/s (Yaw) hoặc 85 °/s (Pitch) với gia tốc hãm 2 300 °/s², và đặc tính thời gian bus. Sai lệch góc được tính trên đoạn 8,5 – 76 s tại đúng các thời điểm lấy mẫu của log A, nên số tái hiện và số đo so sánh trực tiếp được; ngoài e_{rms}, e_{max}, t_{r}, t_{s}, OS, ρ_{sat} của Bảng 1.1, phân vị 99 % của |e| được dùng vì ít nhạy với một mẫu đơn lẻ.')

D.lead('c) Hiệu chỉnh và kiểm chứng mô hình tái hiện.', f'Với mô hình danh định, cấu hình hoàn thiện cho e_{{rms}} = {f(ln["yaw"]["erms"], 3)}° (Yaw), {f(ln["pitch"]["erms"], 3)}° (Pitch), lớn hơn số đo {f(lg["yaw"]["erms"], 3)}° và {f(lg["pitch"]["erms"], 3)}°; hồi quy cho thấy phần chênh tương quan chủ yếu với gia tốc khung mang, tức trễ tương đương của mô hình lớn hơn hệ thật khi chuyển động liên tục. Lý do là τ_{{d}} = 12 ms đo từ bậc lệnh khi động cơ đứng yên, gồm cả thời gian vượt ma sát tĩnh. Hai tham số tương đương được hiệu chỉnh bằng quét lưới theo e_{{rms}} và phân vị 99 % của log A: τ_{{e}} = 8 ms (Yaw), 10 ms (Pitch) và hệ số đường bù IMU2 1,06 / 1,02 (gộp sai số tỉ lệ, lệch trục IMU2 và biến dạng giá đỡ). Kết quả ở Hình 3.6 và Bảng 3.2.')
fig(6, 'h3_06_kiem_chung', 'Kiểm chứng mô hình tái hiện với log A của cấu hình hoàn thiện')
vrows = []
for lab, key, nd in [('e_{rms} (°)', 'erms', 3), ('Phân vị 99 % |e| (°)', 'p99', 3), ('e_{max} (°)', 'emax', 3)]:
    row = [lab]
    for ax in AX:
        row += [f(ln[ax][key], nd), f(sm[ax][key], nd), f(lg[ax][key], nd), pc(lg[ax][key], sm[ax][key])]
    vrows.append(row)
vrows.append(['Độ lệch chuẩn giữ tĩnh (°)', f(R4['nom_hold']['yaw'], 4), f(V['sim_hold']['yaw']['erms'], 4), f(V['log_hold']['yaw']['erms'], 4),
              pc(V['log_hold']['yaw']['erms'], V['sim_hold']['yaw']['erms']), f(R4['nom_hold']['pitch'], 4), f(V['sim_hold']['pitch']['erms'], 4),
              f(V['log_hold']['pitch']['erms'], 4), pc(V['log_hold']['pitch']['erms'], V['sim_hold']['pitch']['erms'])])
D.table('Bảng 3.2. Kiểm chứng mô hình tái hiện trên cấu hình hoàn thiện',
        [['Chỉ tiêu', 'Yaw: danh định', 'Yaw: tái hiện', 'Yaw: đo', 'Sai khác', 'Pitch: danh định', 'Pitch: tái hiện', 'Pitch: đo', 'Sai khác']],
        vrows, [3.3, 1.4, 1.4, 1.4, 1.35, 1.4, 1.4, 1.4, 1.35], size=10, align=['left'] + ['center'] * 8,
        note='Ghi chú: "sai khác" giữa mô phỏng tái hiện và số đo log A.')
DIRECT = {'yaw': [0, 2, 4], 'pitch': [1, 3]}
dir_err = [abs(V['sim_seg'][ax][i]['erms'] / V['log_seg'][ax][i]['erms'] - 1) * 100 for ax in AX for i in DIRECT[ax]]
off_err = [(V['sim_seg'][ax][i]['erms'] / V['log_seg'][ax][i]['erms'] - 1) * 100 for ax in AX for i in range(5) if i not in DIRECT[ax]]
D.para(f'Mô hình tái hiện sai khác {pc(lg["yaw"]["erms"], sm["yaw"]["erms"])} (Yaw) và {pc(lg["pitch"]["erms"], sm["pitch"]["erms"])} (Pitch) về e_{{rms}}, dạng sóng trùng tần số và pha với số đo. Ở các đoạn trục chịu kích thích trực tiếp, sai khác không vượt {f(max(dir_err), 0)} %; ở các đoạn còn lại mô hình thấp hơn đo {f(-max(off_err), 0)} – {f(-min(off_err), 0)} % vì chưa mô tả tương tác giữa hai trục qua kết cấu. e_{{max}} tái hiện lớn hơn đo {f(sm["yaw"]["emax"] / lg["yaw"]["emax"], 1)} – {f(sm["pitch"]["emax"] / lg["pitch"]["emax"], 1)} lần do vài lần đổi chiều gắt nhất (gia tốc trên 4 000 °/s²), nên e_{{max}} tái hiện chỉ dùng để so sánh tương đối; e_{{rms}} và phân vị 99 % được dùng làm ước lượng định lượng.')

D.lead('d) Chuỗi cấu hình tích lũy.', 'Quá trình hoàn thiện gồm tám cấu hình nối tiếp (Bảng 3.3), mỗi bước bổ sung một khâu và cấu hình sau bước là đầu vào của bước kế tiếp. Mỗi bước gồm: a) vấn đề của cấu hình đầu vào; b) mô phỏng khảo sát và lựa chọn tham số; c) áp dụng, so sánh trước – sau trên hai trục bằng mô phỏng tái hiện và đánh giá – hạn chế còn lại là vấn đề của bước sau.')
D.table('Bảng 3.3. Chuỗi cấu hình tích lũy',
        [['Cấu hình', 'Nội dung bổ sung', 'Tham số chính', 'Mục']],
        [['Ban đầu', 'Hệ số khởi tạo; không bù; giới hạn 135 °/s; lịch ưu tiên Yaw', 'K_{pθ} = 6 / 20 s⁻¹; K_{pω} = 0,25 / 0,12; K_{iω} = 0', '3.2.1'],
         ['Sau hiệu chỉnh nối tầng', 'Bộ hệ số nối tầng được chọn', 'Bảng 2.4', '3.2.1'],
         ['Sau bù IMU2', 'Thành phần bù u_{ff} với hệ số k(v) theo vùng', 'Bảng 2.5', '3.2.2'],
         ['Sau ngoại suy bù trễ', 'Ngoại suy bậc nhất (2.14)', 'τ_{p} = 12 ms; Δω_{max} = 90 °/s', '3.2.3'],
         ['Sau giới hạn lệnh động', 'u_{max} theo vùng (2.18) – (2.21)', '110 / 135 / 165 °/s, vùng rất nhanh tới 410 °/s', '3.3.1'],
         ['Sau xử lý đảo chiều, dừng', '(2.22) – (2.26)', 't_{0max} = 10 ms; α_{rev} = 1 000 °/s²; ngưỡng dừng 1 °/s', '3.3.2'],
         ['Sau tạo dạng lệnh', '(2.27)', 'a_{max} = 18 000 / 30 000 °/s²; j_{max} = 2,5·10⁶ °/s³', '3.3.3'],
         ['Hoàn thiện', 'Lịch RS485 luân phiên (2.33)', 'Khe 5 ms; 100 Hz mỗi trục', '3.4.1']],
        [3.8, 5.2, 5.8, 1.0], size=10, align=['left', 'left', 'left', 'center'])

# ============================================================================ 3.2
D.heading('3.2. Hiệu chỉnh vòng phản hồi và bù chuyển động khung mang', 2)

# ---------------------------------------------------------------------------- 3.2.1
D.heading('3.2.1. Hiệu chỉnh bộ điều khiển nối tầng', 3)
D.lead('a) Vấn đề của cấu hình ban đầu.', f'Cấu hình ban đầu dùng hệ số khởi tạo K_{{pθ}} = 6 / 20 s⁻¹, K_{{pω}} = 0,25 / 0,12, chưa có tích phân vòng tốc độ, giới hạn lệnh 135 °/s và lịch ưu tiên Yaw. Trên mô phỏng tái hiện, bậc thang trục Yaw có t_{{r}} = {f(b0["yaw"]["tr"], 0)} ms, t_{{s}} = {f(b0["yaw"]["ts"], 0)} ms; trên bài thử tham chiếu e_{{rms}} = {f(L0["yaw"]["erms"], 2)}° (Yaw), {f(L0["pitch"]["erms"], 2)}° (Pitch). Hai hạn chế là bám chậm trên trục Yaw và không khử được sai lệch do tác động kéo dài, vì khi K_{{iω}} = 0 vòng góc phải duy trì một sai lệch để sinh lệnh bù (1.28).')


def cget(ax, par, v):
    return [s for s in cas[ax][par] if abs(s['v'] - v) < 1e-9][0]


y = {k: cget('yaw', 'Kpt', k) for k in (6.0, 9.5, 13.0)}
p = {k: cget('pitch', 'Kpt', k) for k in (20.0, 38.0, 50.0)}
iw = {ax: {s['v']: s for s in cas[ax]['Kiw']} for ax in AX}
kpy = {x['v']: x for x in kp['yaw']}; kpp = {x['v']: x for x in kp['pitch']}
D.lead('b) Mô phỏng khảo sát và lựa chọn tham số.', 'Mỗi hệ số được thay đổi quanh giá trị dự kiến, hai hệ số còn lại giữ nguyên: K_{pθ}, K_{pω} đánh giá bằng bậc thang và bài thử tham chiếu khi chưa bù; K_{iω} đánh giá bằng tích phân sai lệch J_{e} khi khung mang quay đều 8 °/s (Hình 3.7, Bảng 3.4).')
fig(7, 'h3_07_khao_sat_cascade', 'Mô phỏng khảo sát bộ hệ số nối tầng trên hai trục')
rows = []; bold = []
for par, lab in [('Kpt', 'K_{pθ} (s⁻¹)'), ('Kpw', 'K_{pω}'), ('Kiw', 'K_{iω} (s⁻¹)')]:
    for lvl in range(3):
        cells = {}
        for ax in AX:
            s_ = cas[ax][par][lvl]
            ch = abs(s_['v'] - gsim.GAINS_FINAL[ax][par]) < 1e-9
            vv = (f(s_['v'], 2) if s_['v'] < 1 else f(s_['v'], 1)) + ('*' if ch else '')
            q = CF[ax][par][lvl]
            cells[ax] = [vv, f(q['tr'], 0), f(q['ts'], 0), f(q['OS'], 1), f(s_['bt3_erms'], 2), f(q['Je'], 3), f(q['band'], 1)]
        rows.append([lab] + [cells['yaw'][c] + ' / ' + cells['pitch'][c] for c in range(7)])
        if par != 'Kiw' and lvl == 1:
            bold.append(len(rows) - 1)
D.table('Bảng 3.4. Kết quả khảo sát bộ hệ số nối tầng (giá trị Yaw / Pitch)',
        [['Hệ số', 'Giá trị', 't_{r} (ms)', 't_{s} (ms)', 'OS (%)', 'e_{rms} tham chiếu (°)', 'J_{e} (°·s)', 'Dải 10 – 30 Hz (%)']],
        rows, [1.7, 1.9, 1.6, 1.8, 1.5, 2.0, 2.5, 1.8], size=10, bold_rows=bold,
        note='Ghi chú: mô phỏng khảo sát, mỗi giá trị được chạy đủ ba bài thử (bậc thang; khung mang quay đều 8 °/s trong 4 s cho J_{e}; bài thử tham chiếu); * là giá trị được chọn; e_{rms} tham chiếu khi chưa bù; dải 10 – 30 Hz là tỉ lệ năng lượng sai lệch trong dải chứa dạng dao động 16,5 Hz, tính trên cấu hình hoàn thiện.')
D.para(f'Trục Yaw: tăng K_{{pθ}} từ 6 lên 9,5 s⁻¹ rút ngắn t_{{r}} từ {f(y[6.0]["tr"], 0)} xuống {f(y[9.5]["tr"], 0)} ms và t_{{s}} từ {f(y[6.0]["ts"], 0)} xuống {f(y[9.5]["ts"], 0)} ms; giá trị 13 s⁻¹ nhanh hơn nhưng lệnh khi bám bậc 5° đạt {f(y[13.0]["umax"], 0)} °/s ({f(y[13.0]["umax"] / 110 * 100, 0)} % ω_{{max}}), không còn dự trữ cho khâu bù. Trục Pitch: cả ba giá trị đều chạm giới hạn theo quãng dừng (2.12) nên t_{{r}} gần như không đổi; 38 s⁻¹ rút ngắn t_{{s}} từ {f(p[20.0]["ts"], 0)} xuống {f(p[38.0]["ts"], 0)} ms nhưng OS tăng lên {f(p[38.0]["OS"], 1)} %. Giá trị này vẫn được chọn vì ưu tiên khử nhiễu (trên cấu hình hoàn thiện, e_{{rms}} Pitch khoảng 0,19° so với 0,26° khi dùng 20 s⁻¹); vọt lố chỉ xuất hiện khi đổi góc đặt, đổi lại năng lượng sai lệch trong dải 10 – 30 Hz tăng từ {f(CF["pitch"]["Kpt"][0]["band"], 1)} lên {f(CF["pitch"]["Kpt"][1]["band"], 1)} %. K_{{pω}} lớn hơn giảm sai lệch nhưng đẩy năng lượng vào dải cộng hưởng (tăng 0,28 → 0,40 ở Yaw: {f(kpy[0.28]["band"], 1)} → {f(kpy[0.40]["band"], 1)} %; 0,15 → 0,25 ở Pitch: {f(kpp[0.15]["band"], 1)} → {f(kpp[0.25]["band"], 1)} %), nên giữ 0,28 / 0,15. Tích phân K_{{iω}} = 1,0 s⁻¹ giảm J_{{e}} trục Yaw {red(iw["yaw"][0.0]["Je"], iw["yaw"][1.0]["Je"], 0)}; với Pitch, 0,5 s⁻¹ đã giảm J_{{e}} {red(iw["pitch"][0.0]["Je"], iw["pitch"][0.5]["Je"], 0)} và tăng lên 1,0 không cải thiện e_{{rms}} tham chiếu, nên giữ 0,5 s⁻¹.')
rows = []
for lab, key, nd in [('t_{r} bậc thang (ms)', 'tr', 0), ('t_{s} bậc thang (ms)', 'ts', 0), ('OS bậc thang (%)', 'OS', 2)]:
    row = [lab]
    for ax in AX:
        bv = SL['ban_dau'][ax][key]; av = SL['cascade'][ax][key]
        row += [f(bv, nd), f(av, nd), pc(bv, av) if bv > 0.05 else ('+' if av >= bv else '−') + f(abs(av - bv), 2) + ' điểm %']
    rows.append(row)
rows += ba_rows('ban_dau', 'cascade', LAD_KEYS)
D.lead('c) Áp dụng và đánh giá.', 'Bộ hệ số đã chọn (Bảng 2.4) được áp dụng cho mô hình tái hiện (Hình 3.8, Bảng 3.5).' + ' ' + f'Trục Yaw bám nhanh hơn rõ (t_{{r}} giảm {red(b0["yaw"]["tr"], b1["yaw"]["tr"], 0)}, t_{{s}} giảm {red(b0["yaw"]["ts"], b1["yaw"]["ts"], 0)}), e_{{rms}} tham chiếu giảm {red(L0["yaw"]["erms"], L1["yaw"]["erms"], 1)} (Yaw) và {red(L0["pitch"]["erms"], L1["pitch"]["erms"], 1)} (Pitch). Tuy nhiên sai lệch vẫn cỡ vài độ và tỉ lệ với tốc độ khung mang (Hình 3.8c, d): đây là giới hạn (1.28) của cấu trúc chỉ có phản hồi, không khắc phục được bằng tăng hệ số, dẫn tới bước bù từ IMU2.')
fig(8, 'h3_08_cascade_truoc_sau', 'Trước và sau hiệu chỉnh bộ điều khiển nối tầng (mô phỏng tái hiện)')
D.table('Bảng 3.5. Chỉ tiêu trước và sau hiệu chỉnh bộ điều khiển nối tầng', BA_HEAD, rows, BA_W, size=10,
        align=['left'] + ['center'] * 6, note=NOTE_TR)

# ---------------------------------------------------------------------------- 3.2.2
D.heading('3.2.2. Bù chuyển động khung mang từ IMU2', 3)
ffs = R['ff_survey']
kv = [o for l_, o in ffs if l_.startswith('k(v)')][0]; k88 = [o for l_, o in ffs if '0,88' in l_][0]
k95 = [o for l_, o in ffs if '0,95' in l_][0]; k80 = [o for l_, o in ffs if '0,80' in l_][0]; nb = ffs[0][1]
D.lead('a) Vấn đề của cấu hình đầu vào.', 'Sai lệch cùng pha với tốc độ khung mang: vòng phản hồi chỉ tác động sau khi đường ngắm đã lệch. IMU2 đo trực tiếp chuyển động này, cho phép tạo thành phần bù u_{ff} = k·ω_{b} trừ vào lệnh trước khâu giới hạn (2.17); cần xác định luật hệ số k.')
D.lead('b) Mô phỏng khảo sát và lựa chọn tham số.', 'So sánh ba hệ số cố định k_{0} = 0,80; 0,88; 0,95 và luật k(v) theo vùng (2.15) với các mốc của Bảng 2.5. Chỉ tiêu chính là e_{rms}; ràng buộc là độ lệch chuẩn của u_{ff} khi khung mang đứng yên, tức lượng nhiễu IMU2 đi vào lệnh (Hình 3.9, Bảng 3.6).')
fig(9, 'h3_09_khao_sat_bu', 'Mô phỏng khảo sát luật hệ số bù chuyển động khung mang')
rows = []
for lab, o in ffs:
    rows.append([lab] + [f(o[ax]['erms'], 3) for ax in AX] + [f(o[ax]['fast_erms'], 3) for ax in AX] +
                [f(o['yaw']['uff_hold'], 4) + ' / ' + f(o['pitch']['uff_hold'], 4)])
D.table('Bảng 3.6. Kết quả khảo sát luật hệ số bù',
        [['Phương án', 'e_{rms} Yaw (°)', 'e_{rms} Pitch (°)', 'Đoạn nhanh Yaw (°)', 'Đoạn nhanh Pitch (°)', 'σ(u_{ff}) đứng yên Yaw / Pitch (°/s)']],
        rows, [3.0, 2.0, 2.0, 2.2, 2.2, 3.6], size=10, bold_rows=[4],
        note='Ghi chú: mô phỏng khảo sát; đoạn nhanh là đoạn 5 (Yaw) và đoạn 4 (Pitch).')
D.para(f'Mọi phương án bù đều giảm sai lệch mạnh so với khi chưa bù (với k_{{0}} = 0,88: {f(nb["yaw"]["erms"], 2)} → {f(k88["yaw"]["erms"], 3)}° ở Yaw, {f(nb["pitch"]["erms"], 2)} → {f(k88["pitch"]["erms"], 3)}° ở Pitch), phù hợp với (1.33). k_{{0}} càng lớn sai lệch càng nhỏ nhưng nhiễu vào lệnh càng tăng (σ(u_{{ff}}) {f(k80["yaw"]["uff_hold"], 4)} → {f(k95["yaw"]["uff_hold"], 4)} °/s khi k_{{0}} tăng 0,80 → 0,95). Luật k(v) cho e_{{rms}} gần bằng k_{{0}} = 0,95 ({f(kv["yaw"]["erms"], 3)}° so với {f(k95["yaw"]["erms"], 3)}° ở Yaw; {f(kv["pitch"]["erms"], 3)}° so với {f(k95["pitch"]["erms"], 3)}° ở Pitch) với mức nhiễu chỉ tương đương k_{{0}} = 0,80 – 0,88, vì hệ số nhỏ dùng ở vùng chậm, hệ số lớn chỉ dùng khi quay nhanh; luật này được chọn và dùng chung bộ nhận dạng vùng với mục 3.3.1. Mức nhiễu tuyệt đối nhỏ do mô hình chỉ giả thiết nhiễu trắng 0,13 °/s; khi khung mang rung, lợi ích của hệ số nhỏ ở vùng chậm sẽ lớn hơn.')
D.lead('c) Áp dụng và đánh giá.', 'Khâu bù với k(v) được bổ sung vào cấu hình sau hiệu chỉnh nối tầng; giá trị trước – sau ghi trực tiếp trên Hình 3.10c, giá trị của mọi cấu hình tổng hợp ở Bảng 3.15.' + ' ' + f'Bù từ IMU2 là bước tác động lớn nhất: e_{{rms}} giảm từ {f(L1["yaw"]["erms"], 2)}° xuống {f(L2["yaw"]["erms"], 3)}° ({red(L1["yaw"]["erms"], L2["yaw"]["erms"], 1)}) ở Yaw và từ {f(L1["pitch"]["erms"], 2)}° xuống {f(L2["pitch"]["erms"], 3)}° ({red(L1["pitch"]["erms"], L2["pitch"]["erms"], 1)}) ở Pitch mà không đổi hệ số nào của vòng kín – khâu bù giảm nhiễu hiệu dụng chứ không lấn vào dự trữ ổn định (mục 1.3.2). Hai hạn chế còn lại: sai lệch dư tập trung ở các pha tăng tốc, giảm tốc (lệnh bù đến muộn), và lệnh bắt đầu chạm giới hạn 135 °/s ở các đoạn nhanh (ρ_{{sat}} = {f(L2["yaw"]["rho"], 2)} / {f(L2["pitch"]["rho"], 2)} %) vì phần bù nay lớn gần bằng tốc độ khung mang.')
fig(10, 'h3_10_bu_imu2_truoc_sau', 'Trước và sau bổ sung bù chuyển động khung mang từ IMU2 (mô phỏng tái hiện)')

# ---------------------------------------------------------------------------- 3.2.3
D.heading('3.2.3. Ngoại suy bù trễ', 3)
tpr = R['tp_survey']; tpd = {round(tp * 1e3): o for tp, o in tpr}
D.lead('a) Vấn đề của cấu hình đầu vào.', 'Lệnh bù tính từ ω_{b} tại thời điểm lấy mẫu nhưng chỉ có hiệu lực ở đầu trục sau trễ tổng τ của đường lệnh. Bỏ qua ma sát, phần tốc độ khung mang còn lại sau khâu bù ở tần số ω là:')
D.equation(frac(mr('Δ') + sub(mi('ω'), mr('b')) + paren(mi('jω')), sub(mi('ω'), mr('b')) + paren(mi('jω'))) + mr('≈') +
           mr('1') + mr('−') + mi('k') + sup(mi('e'), mr('−') + mi('jω') + paren(mi('τ') + mr('−') + sub(mi('τ'), mr('p')))), '3.6')
D.para('với τ_{p} là khoảng ngoại suy (2.14). Khi τ_{p} = 0, thành phần pha của (3.6) tăng theo tần số, nên phần dư lớn nhất ở đoạn dao động nhanh và ở trục Pitch (2 – 3 Hz). Ngoại suy làm giảm τ − τ_{p} nhưng dùng gia tốc α_{b} tính bằng vi phân số, nên τ_{p} càng lớn thì nhiễu tần số cao vào lệnh càng nhiều.')
D.lead('b) Mô phỏng khảo sát và lựa chọn tham số.', 'Trên cấu hình có bù IMU2, τ_{p} được thay đổi 0 – 20 ms; chỉ tiêu chính là e_{rms}, ràng buộc là tỉ lệ năng lượng lệnh trên 20 Hz (Hình 3.11, Bảng 3.7).')
fig(11, 'h3_11_khao_sat_ngoai_suy', 'Mô phỏng khảo sát khoảng ngoại suy bù trễ')
rows = []
for tp, o in tpr:
    rows.append([f'{tp * 1e3:.0f}'] + [x for ax in AX for x in (f(o[ax]['erms'], 3), f(o[ax]['emax'], 2), f(o[ax]['u_hf'], 2))])
D.table('Bảng 3.7. Kết quả khảo sát khoảng ngoại suy τ_{p}',
        [['τ_{p} (ms)', 'Yaw: e_{rms} (°)', 'Yaw: e_{max} (°)', 'Yaw: lệnh > 20 Hz (%)', 'Pitch: e_{rms} (°)', 'Pitch: e_{max} (°)', 'Pitch: lệnh > 20 Hz (%)']],
        rows, [1.6, 1.9, 1.9, 2.1, 1.9, 1.9, 2.1], size=10, bold_rows=[3],
        note='Ghi chú: mô phỏng khảo sát (τ_{d} = 12 ms); e_{max} ở bước này bị chi phối bởi bão hòa lệnh 135 °/s.')
D.para(f'Tăng τ_{{p}} từ 0 lên 12 ms giảm e_{{rms}} {red(tpd[0]["yaw"]["erms"], tpd[12]["yaw"]["erms"])} (Yaw) và {red(tpd[0]["pitch"]["erms"], tpd[12]["pitch"]["erms"])} (Pitch) – Pitch được lợi nhiều hơn đúng như (3.6). Tăng tiếp lên 20 ms vẫn giảm e_{{rms}} trên mô hình danh định nhưng năng lượng lệnh trên 20 Hz tăng từ {f(tpd[12]["yaw"]["u_hf"], 2)} lên {f(tpd[20]["yaw"]["u_hf"], 2)} % (Yaw), từ {f(tpd[12]["pitch"]["u_hf"], 2)} lên {f(tpd[20]["pitch"]["u_hf"], 2)} % (Pitch); hơn nữa trễ tương đương của hệ thật khi chuyển động liên tục chỉ 8 – 10 ms (mục 3.1.3), nên τ_{{p}} lớn dễ bù thừa khi đổi chiều. τ_{{p}} = 12 ms, bằng τ_{{d}} đã nhận dạng, được chọn; dải 8 – 15 ms giữ làm dải hiệu chỉnh.')
D.lead('c) Áp dụng và đánh giá.', 'Ngoại suy τ_{p} = 12 ms, Δω_{max} = 90 °/s được bổ sung vào cấu hình có bù IMU2 (Hình 3.12).' + ' ' + f'e_{{rms}} giảm từ {f(L2["yaw"]["erms"], 3)}° xuống {f(L3["yaw"]["erms"], 3)}° ({red(L2["yaw"]["erms"], L3["yaw"]["erms"], 1)}) ở Yaw và từ {f(L2["pitch"]["erms"], 3)}° xuống {f(L3["pitch"]["erms"], 3)}° ({red(L2["pitch"]["erms"], L3["pitch"]["erms"], 1)}) ở Pitch; sai lệch ở các pha tăng tốc – giảm tốc bị triệt gần hết (Hình 3.12a, b). Ý nghĩa của bước này là đưa lệnh bù về đúng thời điểm có hiệu lực mà không cần giảm trễ vật lý. Tuy nhiên e_{{max}} gần như không đổi ({f(L2["yaw"]["emax"], 2)} → {f(L3["yaw"]["emax"], 2)}° ở Yaw) vì đỉnh sai lệch lớn nhất nằm ở đoạn 4 – 5, nơi lệnh bị cắt ở 135 °/s (ρ_{{sat}} = {f(L3["yaw"]["rho"], 2)} / {f(L3["pitch"]["rho"], 2)} %).')
fig(12, 'h3_12_ngoai_suy_truoc_sau', 'Trước và sau bổ sung ngoại suy bù trễ (mô phỏng tái hiện)')

# ============================================================================ 3.3
D.heading('3.3. Hiệu chỉnh đáp ứng ở vùng biên', 2)
D.para('Sau ba bước đầu, các hiện tượng còn lại xuất hiện ở biên: lệnh chạm giới hạn, khung mang đổi chiều hoặc dừng, và lệnh thay đổi nhanh. Mỗi bước dưới đây được đánh giá bằng chỉ tiêu gắn với cơ chế của nó, đồng thời kiểm tra ảnh hưởng tới sai lệch trên bài thử tham chiếu.')

# ---------------------------------------------------------------------------- 3.3.1
D.heading('3.3.1. Giới hạn lệnh theo trạng thái chuyển động', 3)
limr = dict(R['lim_survey']); gl = R2['glitch']
D.lead('a) Vấn đề của cấu hình đầu vào.', f'Lệnh cần để bù tỉ lệ với tốc độ khung mang và vượt 135 °/s ở các đoạn nhanh (đỉnh {f(ex["yaw"]["peak"], 0)} °/s ở Yaw); phần bị cắt tích lũy thành sai lệch lớn. Nâng giới hạn cố định khắc phục được nhưng khi hệ gần đứng yên, một mẫu đo sai cũng được phép sinh lệnh lớn (mục 1.4.1 e).')
D.lead('b) Mô phỏng khảo sát và lựa chọn tham số.', 'So sánh giới hạn cố định 135, 165, 410 °/s và giới hạn theo vùng (2.18) – (2.21) với các mức 110 / 135 / 165 °/s của Bảng 2.5, vùng rất nhanh tăng theo tốc độ khung mang tới 410 °/s; ngưỡng gia tốc vào vùng a_{en} = 300 / 800 / 1 400 °/s², ra a_{ex} = 200 / 500 / 900 °/s². Ràng buộc an toàn được kiểm tra bằng ba mẫu IMU2 liên tiếp (6 ms) sai +600 °/s khi khung mang đứng yên (Hình 3.13, Bảng 3.8).')
fig(13, 'h3_13_khao_sat_gioi_han', 'Mô phỏng khảo sát luật giới hạn lệnh')
rows = []
for lab, o in R['lim_survey']:
    g = gl.get(lab) or (R4['glitch165'] if '165' in lab else None)
    rows.append([lab] + [f(o['yaw']['erms'], 3), f(o['yaw']['emax'], 2), f(o['yaw']['rho'], 2),
                         f(o['pitch']['erms'], 3), f(o['pitch']['emax'], 2), f(o['pitch']['rho'], 2),
                         (f(g['yaw']['epk'], 2) + ' / ' + f(g['yaw']['upk'], 0)) if g else '–'])
D.table('Bảng 3.8. Kết quả khảo sát luật giới hạn lệnh',
        [['Luật giới hạn', 'Yaw: e_{rms} (°)', 'Yaw: e_{max} (°)', 'Yaw: ρ_{sat} (%)', 'Pitch: e_{rms} (°)', 'Pitch: e_{max} (°)', 'Pitch: ρ_{sat} (%)', 'Mẫu IMU2 lỗi: |e| Yaw (°) / lệnh (°/s)']],
        rows, [2.6, 1.6, 1.6, 1.5, 1.6, 1.6, 1.5, 3.0], size=10, bold_rows=[3],
        note='Ghi chú: mô phỏng khảo sát; bài thử mẫu IMU2 lỗi dùng mô hình tái hiện, trung bình 6 lượt.')
D.para(f'Giới hạn 135 °/s cắt lệnh ở {f(limr["Cố định 135 °/s"]["yaw"]["rho"], 2)} % (Yaw) và {f(limr["Cố định 135 °/s"]["pitch"]["rho"], 2)} % (Pitch) số mẫu, e_{{max}} tới {f(limr["Cố định 135 °/s"]["yaw"]["emax"], 2)}° và {f(limr["Cố định 135 °/s"]["pitch"]["emax"], 2)}°; 165 °/s giảm bão hòa nhưng chưa đủ cho đoạn 5. Giới hạn 410 °/s cố định và giới hạn theo vùng cho cùng chất lượng trên bài thử tham chiếu; khác biệt nằm ở bài thử an toàn: với 410 °/s, ba mẫu IMU2 lỗi sinh lệnh {f(gl["Cố định 410 °/s"]["yaw"]["upk"], 0)} °/s và sai lệch {f(gl["Cố định 410 °/s"]["yaw"]["epk"], 2)}°, còn với giới hạn theo vùng hệ vẫn ở vùng chậm nên lệnh bị chặn ở {f(gl["Theo vùng"]["yaw"]["upk"], 0)} °/s và sai lệch chỉ {f(gl["Theo vùng"]["yaw"]["epk"], 2)}° (giảm {red(gl["Cố định 410 °/s"]["yaw"]["epk"], gl["Theo vùng"]["yaw"]["epk"], 0)}). Giới hạn theo vùng được chọn: rộng khi khung mang quay nhanh, hẹp khi chậm hoặc đứng yên.')
D.lead('c) Áp dụng và đánh giá.', 'Giới hạn theo vùng được bổ sung vào cấu hình có ngoại suy bù trễ (Hình 3.14).' + ' ' + f'ρ_{{sat}} giảm từ {f(L3["yaw"]["rho"], 2)} % xuống {f(L4["yaw"]["rho"], 2)} % (Yaw) và từ {f(L3["pitch"]["rho"], 2)} % xuống {f(L4["pitch"]["rho"], 2)} % (Pitch); nhờ phần lệnh không còn bị cắt, e_{{max}} tái hiện giảm {red(L3["yaw"]["emax"], L4["yaw"]["emax"], 0)} (Yaw) và {red(L3["pitch"]["emax"], L4["pitch"]["emax"], 0)} (Pitch), e_{{rms}} giảm {red(L3["yaw"]["erms"], L4["yaw"]["erms"], 1)} và {red(L3["pitch"]["erms"], L4["pitch"]["erms"], 1)}. Đây là bước giảm sai lệch lớn thứ hai vì bài thử tham chiếu có tốc độ khung mang vượt xa giới hạn cố định. Sau bước này e_{{rms}} tái hiện còn {f(L4["yaw"]["erms"], 3)}° (Yaw), {f(L4["pitch"]["erms"], 3)}° (Pitch); phần còn lại tập trung quanh các lần khung mang đổi chiều.')
fig(14, 'h3_14_gioi_han_truoc_sau', 'Trước và sau bổ sung giới hạn lệnh theo trạng thái động (mô phỏng tái hiện)')

# ---------------------------------------------------------------------------- 3.3.2
D.heading('3.3.2. Xử lý đảo chiều và dừng', 3)
revs = R['rev_survey']; stp = R2['stop_test']; RL = R3['rev_ladder']
base = [o for p_, o in revs if p_[0] == 'none'][0]
revd = {k: o for k, o in revs}
o3 = revd[(0.040, 300.0)]; oc = revd[(0.010, 1000.0)]
D.lead('a) Vấn đề của cấu hình đầu vào.', f'Đỉnh sai lệch trung bình quanh các lần khung mang đổi chiều là {f(RL["gioi_han"]["yaw"]["mean"], 3)}° (Yaw) và {f(RL["gioi_han"]["pitch"]["mean"], 3)}° (Pitch), gấp 2 – 3 lần e_{{rms}}. Gần điểm đổi chiều, ω̂_{{b}} nhỏ nên dấu lệnh dễ đổi theo nhiễu trong khi động cơ còn quay theo chiều cũ; khi khung mang dừng, lượng bù và tích phân tồn dư vẫn tác động vào lệnh.')
D.lead('b) Mô phỏng khảo sát và lựa chọn tham số.', 'Khảo sát tầm dự báo t_{0max} và ngưỡng α_{rev} của (2.22), và ngưỡng tốc độ của bộ phát hiện dừng; các tham số khác theo Bảng 2.6 (Hình 3.15, Bảng 3.9).')
fig(15, 'h3_15_khao_sat_dao_chieu_dung', 'Mô phỏng khảo sát tham số xử lý đảo chiều và chế độ dừng')
rows = [['Không xử lý đảo chiều', f(base['yaw']['erms'], 3), f(base['pitch']['erms'], 3), f(base['pitch']['signchg'], 0)]]
bold = []
for (t0, aR), o in revs:
    if t0 == 'none' or (t0, aR) not in [(0.010, 1000.0), (0.010, 300.0), (0.040, 300.0), (0.040, 1000.0)]:
        continue
    rows.append([f't_{{0max}} = {t0 * 1e3:.0f} ms; α_{{rev}} = {aR:,.0f} °/s²'.replace(',', ' '), f(o['yaw']['erms'], 3), f(o['pitch']['erms'], 3), f(o['pitch']['signchg'], 0)])
    if t0 == 0.010 and aR == 1000.0:
        bold.append(len(rows) - 1)
for wb, o in R['stop_survey']:
    if wb == 2.0:
        continue
    rows.append([f'Ngưỡng dừng |ω_{{b}}| < {f(wb, 0)} °/s', f(o['yaw']['erms'], 3), f(o['pitch']['erms'], 3), f(o['pitch']['signchg'], 0)])
    if wb == 1.0:
        bold.append(len(rows) - 1)
D.table('Bảng 3.9. Kết quả khảo sát tham số xử lý đảo chiều và phát hiện dừng',
        [['Phương án', 'e_{rms} Yaw (°)', 'e_{rms} Pitch (°)', 'Số lần lệnh Pitch đổi dấu']],
        rows, [7.0, 2.4, 2.4, 2.8], size=10, bold_rows=bold, align=['left', 'center', 'center', 'center'],
        note='Ghi chú: mô phỏng khảo sát trên bài thử tham chiếu, trung bình 2 lượt; số lần lệnh Yaw đổi dấu không thay đổi.')
D.para(f'Xử lý đảo chiều có hai tác dụng ngược nhau. Với t_{{0max}} = 40 ms, α_{{rev}} = 300 °/s², số lần lệnh Pitch đổi dấu giảm {red(base["pitch"]["signchg"], o3["pitch"]["signchg"], 0)}, nhưng ràng buộc (2.24) cũng kích hoạt ở những lần dự báo sai và giữ lệnh ở phía cũ, làm e_{{rms}} Pitch tăng {inc(base["pitch"]["erms"], o3["pitch"]["erms"])}. Rút tầm dự báo còn 10 ms và nâng ngưỡng lên 1 000 °/s² để cơ chế chỉ tác động ở lần đổi chiều gắt giảm mức tăng e_{{rms}} còn {inc(base["pitch"]["erms"], oc["pitch"]["erms"])} (Pitch) và {inc(base["yaw"]["erms"], oc["yaw"]["erms"])} (Yaw); cặp giá trị này được chọn. Ngưỡng dừng 1 °/s tránh nhận nhầm pha quay chậm là dừng (với 3 °/s, e_{{rms}} Yaw tăng {inc(base["yaw"]["erms"], R["stop_survey"][2][1]["yaw"]["erms"])}). Như vậy trên mô hình, xử lý đảo chiều không giảm sai lệch tham chiếu; tham số được chọn để giữ tác dụng bảo vệ với chi phí nhỏ nhất.')
rows = ba_rows('gioi_han', 'dao_chieu', [('e_{rms} tham chiếu (°)', 'erms', 3, 'ladder'), ('Số lần lệnh đổi dấu', 'signchg', 0, 'ladder')])
rows.append(['Đỉnh |e| trung bình khi đổi chiều (°)'] + [x for ax in AX for x in (f(RL['gioi_han'][ax]['mean'], 3), f(RL['dao_chieu'][ax]['mean'], 3), pc(RL['gioi_han'][ax]['mean'], RL['dao_chieu'][ax]['mean']))])
sN = stp['Không xử lý dừng']; sY = stp['Có chế độ dừng']
for lab, key, nd in [('Dừng đột ngột: sai lệch đỉnh (°)', 'pk', 3), ('Dừng đột ngột: lệnh lớn nhất khi giữ (°/s)', 'uhold', 2), ('Dừng đột ngột: σ lệnh khi giữ (°/s)', 'ustd', 3)]:
    rows.append([lab] + [x for ax in AX for x in (f(sN[ax][key], nd), f(sY[ax][key], nd), pc(sN[ax][key], sY[ax][key]))])
D.lead('c) Áp dụng và đánh giá.', 'Hai cơ chế được bổ sung vào cấu hình có giới hạn lệnh động và đánh giá trên bài thử tham chiếu, các lần đổi chiều và bài thử dừng đột ngột 12 lượt mỗi trục (Hình 3.16, Bảng 3.10).' + ' ' + f'Bước này gần như trung tính với sai lệch: e_{{rms}} thay đổi {pc(L4["yaw"]["erms"], L5["yaw"]["erms"])} (Yaw), {pc(L4["pitch"]["erms"], L5["pitch"]["erms"])} (Pitch); đỉnh sai lệch khi dừng ({f(sY["yaw"]["pk"], 2)}° / {f(sY["pitch"]["pk"], 2)}°) không đổi vì với bù, ngoại suy và giới hạn động, hệ đã phục hồi trước khi trạng thái dừng được xác nhận (220 ms). Tác dụng đo được của chế độ dừng là ở giai đoạn giữ (Hình 3.15c, d): trên trục Yaw lệnh lớn nhất giảm từ {f(sN["yaw"]["uhold"], 2)} xuống {f(sY["yaw"]["uhold"], 2)} °/s, độ lệch chuẩn lệnh giảm {red(sN["yaw"]["ustd"], sY["yaw"]["ustd"], 0)}, động cơ không còn bị kích liên tục quanh ma sát tĩnh; trục Pitch cải thiện ít hơn. Các hiện tượng mà hai cơ chế hướng tới – rung của IMU2, trôi điểm không khi dừng lâu, lượng tử của vòng tốc độ tích hợp gần tốc độ không – chưa có trong mô hình, nên hiệu quả của chúng cần xác nhận bằng thực nghiệm. Lệnh vẫn còn các bước nhảy lớn ở lần chuyển vùng, đổi chiều và thoát chế độ dừng.')
fig(16, 'h3_16_dao_chieu_truoc_sau', 'Trước và sau bổ sung xử lý đảo chiều và dừng (mô phỏng tái hiện)')
D.table('Bảng 3.10. Chỉ tiêu trước và sau bổ sung xử lý đảo chiều và dừng', BA_HEAD, rows, BA_W, size=10,
        align=['left'] + ['center'] * 6, note='Ghi chú: mô phỏng tái hiện; "giữ" là giai đoạn từ 0,3 s sau khi khung mang dừng, trung bình 12 lượt.')

# ---------------------------------------------------------------------------- 3.3.3
D.heading('3.3.3. Tạo dạng lệnh', 3)
shp = R2['shape_survey']; tr_ = R2['shape_traj']
t18 = tr_['T'][np.argmax(tr_['a18'] <= -285)] - 0.02
t30 = tr_['T'][np.argmax(tr_['a30'] <= -285)] - 0.02
D.lead('a) Vấn đề của cấu hình đầu vào.', f'Bước thay đổi lệnh lớn nhất trong một chu kỳ 2 ms là {f(L5["yaw"]["dumax"], 1)} °/s (Yaw) và {f(L5["pitch"]["dumax"], 1)} °/s (Pitch); các bước này kích thích dạng dao động 16,5 Hz và làm tăng dòng động cơ.')
D.lead('b) Mô phỏng khảo sát và lựa chọn tham số.', f'Khảo sát bốn phương án a_{{max}} của (2.27) với j_{{max}} = 2,5·10⁶ °/s³. Với bước đổi lệnh +300 → −300 °/s, lệnh đạt 95 % giá trị mới sau {f(t18 * 1e3, 0)} ms khi a_{{max}} = 18 000 °/s² và {f(t30 * 1e3, 0)} ms khi 30 000 °/s² (Hình 3.17a); kết quả trên bài thử tham chiếu ở Bảng 3.11.')
fig(17, 'h3_17_khao_sat_tao_dang', 'Mô phỏng khảo sát khâu tạo dạng lệnh')
rows = []
for lab, o in shp:
    rows.append([lab] + [x for ax in AX for x in (f(o[ax]['dumax'], 1), f(o[ax]['du99'], 2), f(o[ax]['erms'], 3))])
D.table('Bảng 3.11. Kết quả khảo sát khâu tạo dạng lệnh',
        [['Phương án a_{max}', 'Yaw: bước lệnh lớn nhất (°/s)', 'Yaw: p99 bước lệnh (°/s)', 'Yaw: e_{rms} (°)', 'Pitch: bước lệnh lớn nhất (°/s)', 'Pitch: p99 bước lệnh (°/s)', 'Pitch: e_{rms} (°)']],
        rows, [3.4, 1.9, 1.8, 1.6, 1.9, 1.8, 1.6], size=10, bold_rows=[3],
        note='Ghi chú: mô phỏng khảo sát, trung bình 2 lượt; bước lệnh tính trên chu kỳ 2 ms.')
s0 = shp[0][1]; s3 = shp[3][1]
D.para(f'Trên bài thử tham chiếu ba phương án có giới hạn cho cùng kết quả vì các bước lệnh thực tế bị giới hạn độ giật chặn trước khi chạm a_{{max}}: bước lệnh lớn nhất giảm từ {f(s0["yaw"]["dumax"], 1)} xuống {f(s3["yaw"]["dumax"], 1)} °/s (Yaw), từ {f(s0["pitch"]["dumax"], 1)} xuống {f(s3["pitch"]["dumax"], 1)} °/s (Pitch), với e_{{rms}} thay đổi {pc(s0["yaw"]["erms"], s3["yaw"]["erms"])} và {pc(s0["pitch"]["erms"], s3["pitch"]["erms"])}. a_{{max}} chỉ tác dụng với bước lệnh lớn (Hình 3.17a); phương án 18 000 °/s², nới lên 30 000 °/s² khi đảo chiều được chọn để lệnh êm ở chế độ thường mà không chậm thêm khi đổi chiều.')

D.lead('c) Áp dụng và đánh giá.', 'Khâu tạo dạng được bổ sung vào cấu hình có xử lý đảo chiều và dừng (Hình 3.18, giá trị trước – sau ghi trên hình).' + ' ' + f'Khâu tạo dạng tác động chủ yếu lên lệnh: bước lệnh lớn nhất giảm {red(L5["yaw"]["dumax"], L6["yaw"]["dumax"], 0)} (Yaw) và {red(L5["pitch"]["dumax"], L6["pitch"]["dumax"], 0)} (Pitch), nên dạng dao động 16,5 Hz ít bị kích thích khi lệnh chuyển trạng thái. Cái giá là trễ nhỏ khi lệnh đổi nhanh: e_{{rms}} thay đổi {pc(L5["yaw"]["erms"], L6["yaw"]["erms"])} (Yaw), {pc(L5["pitch"]["erms"], L6["pitch"]["erms"])} (Pitch) – một đánh đổi có chủ đích với chi phí vài phần trăm. Sau bước này e_{{rms}} tái hiện trục Pitch ({f(L6["pitch"]["erms"], 3)}°) lớn hơn Yaw ({f(L6["yaw"]["erms"], 3)}°) dù Pitch có quán tính nhỏ hơn; các đỉnh sai lệch Pitch trùng với những lần khoảng cập nhật lệnh Pitch bị kéo dài do lịch ưu tiên Yaw.')
fig(18, 'h3_18_tao_dang_truoc_sau', 'Trước và sau bổ sung khâu tạo dạng lệnh (mô phỏng tái hiện)')

# ============================================================================ 3.4
D.heading('3.4. Hoàn thiện lịch truyền RS485 và đánh giá cấu hình hoàn thiện', 2)
D.heading('3.4.1. Hoàn thiện lịch truyền RS485', 3)
bus = R2['bus_sched']; bc = R2['bus_closed']; yp = bus['yawpri']; al = bus['alt']
D.lead('a) Vấn đề của cấu hình đầu vào.', 'Với lịch ưu tiên Yaw, giao dịch Pitch chỉ được ghép vào khe xen kẽ khi còn đủ thời gian; khi giao dịch Yaw kéo dài, Pitch bị hoãn. Khoảng cập nhật Pitch vì vậy không đều, trong khi khâu ngoại suy (2.14) giả thiết trễ là hằng số. Độ đều được đánh giá bằng:')
D.equation(sub(mi('Δ'), mi('i,k')) + mr('=') + sub(mi('t'), mi('i,k')) + mr('−') + sub(mi('t'), mi('i,k') + mr('−1')) + mr(',   ') +
           sub(mi('σ'), mi('Δ,i')) + mr('=') + sqrt(frac(mr('1'), mi('N') + mr('−1')) + nary('∑', mi('k') + mr('=1'), mi('N'),
                                                                                          sup(paren(sub(mi('Δ'), mi('i,k')) + mr('−') + sub(mi('Δ̄'), mi('i'))), mr('2')))), '3.7')
D.para('với t_{i,k} là thời điểm phát lệnh thứ k của trục i, Δ_{i,k} là khoảng cập nhật và σ_{Δ,i} là độ tản mát.')
D.lead('b) Mô phỏng khảo sát và lựa chọn phương án.', 'Hai lịch được so sánh bằng mô phỏng theo sự kiện trên 20 000 khe, sau đó đưa vào vòng kín với τ_{p} = 8, 12, 16 ms để kiểm tra lại lựa chọn ở mục 3.2.3 (Hình 3.19, Bảng 3.12).')
fig(19, 'h3_19_khao_sat_rs485', 'Mô phỏng khảo sát hai phương án lập lịch RS485')
rows = []
for mode, lab in [('yawpri', 'Ưu tiên Yaw'), ('alt', 'Luân phiên')]:
    for ax in AX:
        b_ = bus[mode][ax]
        rows.append([lab, AXN[ax], f(b_['rate'], 0), f(b_['med'], 2), f(b_['p99'], 2), f(b_['mx'], 2), f(b_['std'], 2),
                     f(bc[(mode, 0.012)][ax]['erms'], 3)])
D.table('Bảng 3.12. Kết quả khảo sát phương án lập lịch RS485',
        [['Lịch truyền', 'Trục', 'Tần số (Hz)', 'Δ trung vị (ms)', 'Δ p99 (ms)', 'Δ lớn nhất (ms)', 'σ_{Δ} (ms)', 'e_{rms} (°)']],
        rows, [2.9, 1.3, 1.6, 1.8, 1.6, 1.8, 1.4, 1.6], size=10, bold_rows=[2, 3],
        note='Ghi chú: mô phỏng khảo sát; e_{rms} với τ_{p} = 12 ms.')
D.para(f'Lịch ưu tiên Yaw cho Yaw 200 Hz nhưng khoảng cập nhật Pitch có p99 {f(yp["pitch"]["p99"], 1)} ms, lớn nhất {f(yp["pitch"]["mx"], 1)} ms, σ_{{Δ}} = {f(yp["pitch"]["std"], 2)} ms. Lịch luân phiên cập nhật mỗi trục 100 Hz, p99 hai trục {f(al["yaw"]["p99"], 1)} – {f(al["pitch"]["p99"], 1)} ms, σ_{{Δ}} trục Pitch giảm {red(yp["pitch"]["std"], al["pitch"]["std"], 0)}. Trong vòng kín, lịch luân phiên giảm e_{{rms}} Pitch ({f(bc[("yawpri", 0.012)]["pitch"]["erms"], 3)} → {f(bc[("alt", 0.012)]["pitch"]["erms"], 3)}°) nhưng tăng e_{{rms}} Yaw ({f(bc[("yawpri", 0.012)]["yaw"]["erms"], 3)} → {f(bc[("alt", 0.012)]["yaw"]["erms"], 3)}°) do tần số cập nhật giảm một nửa; xu hướng giữ nguyên với τ_{{p}} = 8 và 16 ms, nên không cần chọn lại τ_{{p}}. Lịch luân phiên được chọn vì bảo đảm tính tất định cho cả hai trục – điều kiện để khâu ngoại suy làm việc đúng – và cân bằng sai lệch hai trục.')
rows = []
for lab, key, nd in [('e_{rms} (°)', 'erms', 3), ('Phân vị 99 % |e| (°)', 'p99', 3), ('e_{max} (°)', 'emax', 2)]:
    row = [lab]
    for ax in AX:
        b_ = LD['tao_dang'][ax][key]; a_ = LD['hoan_thien'][ax][key]
        row += [f(b_, nd), f(a_, nd), pc(b_, a_), f(V['log'][ax][key], nd)]
    rows.append(row)
D.lead('c) Áp dụng và đánh giá.', 'Áp dụng lịch luân phiên cho cấu hình có tạo dạng lệnh cho ra cấu hình hoàn thiện; bước này có cả số đo log A (Hình 3.20, Bảng 3.13).' + ' ' + f'Lịch luân phiên giảm e_{{rms}} Pitch {red(L6["pitch"]["erms"], L7["pitch"]["erms"], 1)} và phân vị 99 % {red(L6["pitch"]["p99"], L7["pitch"]["p99"], 1)}, đổi lại e_{{rms}} Yaw tăng {inc(L6["yaw"]["erms"], L7["yaw"]["erms"])}; hai trục trở nên cân bằng ({f(L7["yaw"]["erms"], 3)}° / {f(L7["pitch"]["erms"], 3)}°) và sai lệch lớn hơn trong hai trục giảm từ {f(max(L6["yaw"]["erms"], L6["pitch"]["erms"]), 3)}° xuống {f(max(L7["yaw"]["erms"], L7["pitch"]["erms"]), 3)}°. Số đo log A xác nhận: e_{{rms}} = {f(V["log"]["yaw"]["erms"], 3)}° (Yaw), {f(V["log"]["pitch"]["erms"], 3)}° (Pitch). Bộ đếm RS485 trong log A ghi mỗi trục 7 676 giao dịch trong 76,3 s (100,6 Hz), không có giao dịch lỗi hay quá hạn; khoảng cập nhật lớn nhất 16 ms (Yaw), 14 ms (Pitch), giao dịch dài nhất 8 ms – tính tất định cải thiện rõ nhưng chưa tuyệt đối.')
fig(20, 'h3_20_rs485_truoc_sau', 'Trước và sau hoàn thiện lịch truyền RS485: mô phỏng tái hiện và số đo log A')
D.table('Bảng 3.13. Chỉ tiêu trước và sau hoàn thiện lịch truyền RS485',
        [['Chỉ tiêu', 'Yaw: trước', 'Yaw: sau', 'Thay đổi', 'Yaw: đo', 'Pitch: trước', 'Pitch: sau', 'Thay đổi', 'Pitch: đo']],
        rows, [3.0, 1.4, 1.4, 1.4, 1.4, 1.4, 1.4, 1.4, 1.4], size=10, align=['left'] + ['center'] * 8,
        note='Ghi chú: "trước", "sau" là mô phỏng tái hiện; cột "đo" là số đo trực tiếp log A.')

# ---------------------------------------------------------------------------- 3.4.2
D.heading('3.4.2. Đánh giá cấu hình hoàn thiện', 3)
lgs = V['log_seg']; ev = R2['rev_events']
D.lead('a) Kết quả đo trên hệ thật.', f'Hình 3.21 và Bảng 3.14 trình bày log A của cấu hình hoàn thiện trên bài thử tham chiếu. Trong toàn bài thử, sai lệch hai trục nằm trong ±{f(max(V["log"]["yaw"]["emax"], V["log"]["pitch"]["emax"]) + 0.005, 2)}° khi khung mang quay ±27° quanh trục đứng, ±23° quanh trục ngang với tốc độ góc tới {f(ex["yaw"]["peak"], 0)} °/s.')
fig(21, 'h3_21_log_hoan_thien', 'Kết quả đo cấu hình hoàn thiện trên bài thử tham chiếu (log A)')
rows = []
for i, (a, b, lab) in enumerate(C.SEG):
    rows.append([f'Đoạn {i + 1} ({f(a, 1)} – {f(b, 1)} s)'] + [x for ax in AX for x in (f(V['exc_seg'][ax][i]['rms'], 0) + ' / ' + f(V['exc_seg'][ax][i]['peak'], 0), f(lgs[ax][i]['erms'], 3), f(lgs[ax][i]['emax'], 3))])
rows.append(['Toàn bài thử'] + [x for ax in AX for x in (f(ex[ax]['rms'], 0) + ' / ' + f(ex[ax]['peak'], 0), f(V['log'][ax]['erms'], 3), f(V['log'][ax]['emax'], 3))])
rows.append(['Giữ tĩnh (4,5 – 8 s)', '0', f(V['log_hold']['yaw']['erms'], 4), f(V['log_hold']['yaw']['emax'], 3), '0', f(V['log_hold']['pitch']['erms'], 4), f(V['log_hold']['pitch']['emax'], 3)])
rows.append(['Các lần đổi chiều*', f(R4['rev_w']['yaw']['rms'], 0) + ' / ' + f(R4['rev_w']['yaw']['peak'], 0), f(ev[('log', 'yaw')]['mean'], 3), f(ev[('log', 'yaw')]['max'], 3), f(R4['rev_w']['pitch']['rms'], 0) + ' / ' + f(R4['rev_w']['pitch']['peak'], 0), f(ev[('log', 'pitch')]['mean'], 3), f(ev[('log', 'pitch')]['max'], 3)])
D.table('Bảng 3.14. Bài thử tham chiếu và kết quả đo cấu hình hoàn thiện theo từng đoạn (log A)',
        [['Đoạn', 'Yaw: ω_{b} hiệu dụng / đỉnh (°/s)', 'Yaw: e_{rms} (°)', 'Yaw: e_{max} (°)', 'Pitch: ω_{b} hiệu dụng / đỉnh (°/s)', 'Pitch: e_{rms} (°)', 'Pitch: e_{max} (°)']],
        rows, [3.6, 2.4, 1.6, 1.6, 2.4, 1.6, 1.6], size=10, bold_rows=[5], align=['left'] + ['center'] * 6,
        note=f'Ghi chú: số đo trực tiếp; giữ tĩnh: độ lệch chuẩn sau khi trừ giá trị trung bình; (*) đỉnh |e| trung bình / lớn nhất của {ev[("log", "yaw")]["n"]} (Yaw) và {ev[("log", "pitch")]["n"]} (Pitch) lần đổi chiều; ω_{b} của dòng này là giá trị hiệu dụng trong ±0,3 s quanh điểm đổi chiều / đỉnh trung bình trước khi đổi chiều. Nội dung đoạn: 1 – Yaw dao động chậm; 2 – Pitch dao động; 3 – Yaw dao động nhanh; 4 – Pitch dao động nhanh; 5 – Yaw đảo chiều gắt.')
D.para(f'Cấu hình hoàn thiện đạt e_{{rms}} = {f(V["log"]["yaw"]["erms"], 3)}° (Yaw), {f(V["log"]["pitch"]["erms"], 3)}° (Pitch), e_{{max}} = {f(V["log"]["yaw"]["emax"], 2)}° và {f(V["log"]["pitch"]["emax"], 2)}°, phân vị 99 % {f(V["log"]["yaw"]["p99"], 2)}° và {f(V["log"]["pitch"]["p99"], 2)}°. Sai lệch lớn nhất xuất hiện ở các lần đổi chiều (đỉnh trung bình {f(ev[("log", "yaw")]["mean"], 2)}° / {f(ev[("log", "pitch")]["mean"], 2)}°); đoạn khó nhất với Pitch là đoạn 4 (3 Hz), với Yaw là đoạn 3 và 5. Khi đứng yên, độ lệch chuẩn góc chỉ {f(V["log_hold"]["yaw"]["erms"], 4)}° / {f(V["log_hold"]["pitch"]["erms"], 4)}°, nên nhiễu đo và độ phân giải không phải yếu tố giới hạn.')
D.lead('b) Quá trình hoàn thiện.', 'Hình 3.22 và Bảng 3.15 tổng hợp các chỉ tiêu qua tám cấu hình (bảy cấu hình đầu là mô phỏng tái hiện; cấu hình hoàn thiện có cả số đo).')
fig(22, 'h3_22_qua_trinh_hoan_thien', 'Chỉ tiêu sai lệch qua các bước hiệu chỉnh trên bài thử tham chiếu')
rows = []
prev = None
for n in ORDER:
    o = LD[n]
    rows.append([SHORT[n], f(o['yaw']['erms'], 3), (pc(LD[prev]['yaw']['erms'], o['yaw']['erms']) if prev else 'mốc'),
                 f(o['pitch']['erms'], 3), (pc(LD[prev]['pitch']['erms'], o['pitch']['erms']) if prev else 'mốc'),
                 f(o['yaw']['p99'], 2) + ' / ' + f(o['pitch']['p99'], 2), f(o['yaw']['rho'], 2) + ' / ' + f(o['pitch']['rho'], 2)])
    prev = n
rows.append(['Hoàn thiện – đo (log A)', f(V['log']['yaw']['erms'], 3), pc(L7['yaw']['erms'], V['log']['yaw']['erms']) + ' (a)', f(V['log']['pitch']['erms'], 3), pc(L7['pitch']['erms'], V['log']['pitch']['erms']) + ' (a)',
             f(V['log']['yaw']['p99'], 2) + ' / ' + f(V['log']['pitch']['p99'], 2), f(L7['yaw']['rho'], 2) + ' / ' + f(L7['pitch']['rho'], 2) + ' (b)'])
D.table('Bảng 3.15. Chỉ tiêu trên bài thử tham chiếu qua các cấu hình',
        [['Cấu hình', 'e_{rms} Yaw (°)', 'So với bước trước', 'e_{rms} Pitch (°)', 'So với bước trước', 'p99 |e| Yaw / Pitch (°)', 'ρ_{sat} Yaw / Pitch (%)']],
        rows, [4.6, 1.5, 1.6, 1.5, 1.6, 2.3, 2.1], size=10, bold_rows=[8], align=['left'] + ['center'] * 6,
        note='Ghi chú: tám dòng đầu là mô phỏng tái hiện; dòng cuối là số đo trực tiếp. (a) so với cấu hình hoàn thiện mô phỏng tái hiện; (b) log A không ghi cờ bão hòa lệnh, giá trị lấy từ mô phỏng tái hiện.')
D.para(f'Từ cấu hình ban đầu đến hoàn thiện, e_{{rms}} tái hiện giảm từ {f(L0["yaw"]["erms"], 2)}° xuống {f(L7["yaw"]["erms"], 3)}° ({red(L0["yaw"]["erms"], L7["yaw"]["erms"], 1)}) ở Yaw và từ {f(L0["pitch"]["erms"], 2)}° xuống {f(L7["pitch"]["erms"], 3)}° ({red(L0["pitch"]["erms"], L7["pitch"]["erms"], 1)}) ở Pitch. Ba bước giảm sai lệch theo bậc độ lớn là bù IMU2 ({red(L1["yaw"]["erms"], L2["yaw"]["erms"], 0)} / {red(L1["pitch"]["erms"], L2["pitch"]["erms"], 0)} e_{{rms}} Yaw / Pitch), ngoại suy bù trễ ({red(L2["yaw"]["erms"], L3["yaw"]["erms"], 0)} / {red(L2["pitch"]["erms"], L3["pitch"]["erms"], 0)}) và giới hạn lệnh động ({red(L3["yaw"]["erms"], L4["yaw"]["erms"], 0)} / {red(L3["pitch"]["erms"], L4["pitch"]["erms"], 0)}); hiệu chỉnh nối tầng chủ yếu cải thiện đặc tính bám. Ba bước sau không nhằm giảm e_{{rms}} mà xử lý trạng thái giữ sau khi dừng, độ êm của lệnh và tính tất định của truyền thông; chi phí của chúng lên e_{{rms}} nằm trong vài phần trăm, riêng lịch luân phiên đổi một phần độ chính xác trục Yaw lấy độ chính xác và tính đều đặn của trục Pitch.')
D.lead('c) Đánh giá tổng hợp theo yêu cầu kỹ thuật.', 'Bảng 3.16 đánh giá cấu hình hoàn thiện theo các nhóm chỉ tiêu của Bảng 1.1: nhóm khử nhiễu và độ chính xác theo số đo log A so với mục tiêu của đề tài, nhóm thời gian thực theo ngưỡng thiết kế ở Chương 2.')
D.table('Bảng 3.16. Đánh giá tổng hợp cấu hình hoàn thiện theo chỉ tiêu kỹ thuật',
        [['Nhóm', 'Chỉ tiêu', 'Mục tiêu / ngưỡng', 'Kết quả', 'Nguồn', 'Đánh giá']],
        [['Khử nhiễu', 'e_{rms} Yaw / Pitch, bài thử tham chiếu', '≈ 0,2°', f(V['log']['yaw']['erms'], 3) + '° / ' + f(V['log']['pitch']['erms'], 3) + '°', 'Đo', 'Đạt'],
         ['Khử nhiễu', 'e_{max} Yaw / Pitch', '0,5 – 1,0°', f(V['log']['yaw']['emax'], 2) + '° / ' + f(V['log']['pitch']['emax'], 2) + '°', 'Đo', 'Đạt'],
         ['Khử nhiễu', 'Giảm e_{rms} so với cấu hình ban đầu', 'Không đặt ngưỡng', red(L0['yaw']['erms'], L7['yaw']['erms'], 1) + ' / ' + red(L0['pitch']['erms'], L7['pitch']['erms'], 1), 'Tái hiện', 'Cải thiện'],
         ['Khử nhiễu', 'Tỉ lệ bão hòa lệnh ρ_{sat}', '≈ 0', f(L7['yaw']['rho'], 2) + ' % / ' + f(L7['pitch']['rho'], 2) + ' %', 'Tái hiện', 'Đạt'],
         ['Độ chính xác', 'Độ lệch chuẩn góc khi giữ tĩnh', '< 0,03°', f(V['log_hold']['yaw']['erms'], 4) + '° / ' + f(V['log_hold']['pitch']['erms'], 4) + '°', 'Đo', 'Đạt'],
         ['Đáp ứng', 't_{r} / OS bậc thang Yaw', 'OS < 1 %', f(SL['cascade']['yaw']['tr'], 0) + ' ms / ' + f(SL['cascade']['yaw']['OS'], 2) + ' %', 'Tái hiện', 'Đạt'],
         ['Đáp ứng', 't_{r} / OS bậc thang Pitch', 'OS < 1 %', f(SL['cascade']['pitch']['tr'], 0) + ' ms / ' + f(SL['cascade']['pitch']['OS'], 1) + ' %', 'Tái hiện', 'Chưa đạt'],
         ['Thời gian thực', 'Tần số cập nhật mỗi trục; giao dịch lỗi', '100 Hz; 0', '100,6 Hz; 0', 'Đo', 'Đạt'],
         ['Thời gian thực', 'Khoảng cập nhật lớn nhất Yaw / Pitch', '10 ms', '16 / 14 ms', 'Đo', 'Chưa đạt'],
         ['Thời gian thực', 'Thời gian giao dịch lớn nhất', '≤ 5 ms', '8 ms', 'Đo', 'Chưa đạt']],
        [2.2, 4.6, 2.2, 3.2, 1.6, 1.8], size=10, align=['left', 'left', 'center', 'center', 'center', 'center'])
D.para('Cấu hình hoàn thiện đạt mục tiêu khử nhiễu: e_{rms} khoảng 0,2° và e_{max} 0,62 – 0,67° trên cả hai trục khi khung mang quay tới khoảng 230 °/s. Các điểm chưa đạt gồm: khoảng cập nhật lớn nhất vượt chu kỳ danh định 10 ms tới 60 % và có giao dịch vượt khe 5 ms, làm trễ thực tế lúc đó lớn hơn τ_{p}; độ vọt lố bậc thang trục Pitch do K_{pθ} được chọn ưu tiên khử nhiễu.')

# ============================================================================ 3.5
D.heading('3.5. Kết luận chương 3', 2)
D.para(f'Chương 3 đã xây dựng mô hình hai trục từ phép thử vòng hở và hiệu chỉnh theo bản ghi đo của cấu hình hoàn thiện, với kích thích là chuyển động khung mang do IMU2 ghi lại; mô hình tái hiện khớp số đo về e_{{rms}} trong {f(abs(sm["yaw"]["erms"] / lg["yaw"]["erms"] - 1) * 100, 1)} % (Yaw) và {f(abs(sm["pitch"]["erms"] / lg["pitch"]["erms"] - 1) * 100, 1)} % (Pitch).')
D.para(f'Quá trình hoàn thiện gồm bảy bước theo cấu hình tích lũy, mỗi bước cùng trình tự vấn đề – mô phỏng khảo sát – áp dụng và so sánh trước, sau trên hai trục – đánh giá. Hiệu chỉnh nối tầng rút ngắn t_{{r}} trục Yaw {red(b0["yaw"]["tr"], b1["yaw"]["tr"], 0)}; bù từ IMU2 là bước quyết định, giảm e_{{rms}} khoảng {f((1 - L2["yaw"]["erms"] / L1["yaw"]["erms"]) * 100, 0)} % (Yaw) và {f((1 - L2["pitch"]["erms"] / L1["pitch"]["erms"]) * 100, 0)} % (Pitch); ngoại suy 12 ms và giới hạn lệnh theo vùng giảm tiếp sai lệch và loại bỏ gần hết bão hòa lệnh; xử lý đảo chiều, dừng, tạo dạng lệnh và lịch luân phiên hoàn thiện trạng thái giữ, độ êm của lệnh và tính tất định truyền thông với chi phí nhỏ đã được lượng hóa.')
D.para(f'Cấu hình hoàn thiện đo trên hệ thật đạt e_{{rms}} = {f(V["log"]["yaw"]["erms"], 3)}° (Yaw), {f(V["log"]["pitch"]["erms"], 3)}° (Pitch), e_{{max}} = {f(V["log"]["yaw"]["emax"], 2)}° và {f(V["log"]["pitch"]["emax"], 2)}°, giữ tĩnh dưới 0,01°, cập nhật 100,6 Hz mỗi trục, không có giao dịch lỗi. Hạn chế còn lại: khoảng cập nhật lớn nhất tới 16 ms và giao dịch dài nhất 8 ms trên bus RS485; độ vọt lố bậc thang trục Pitch; hiệu quả xử lý đảo chiều và dừng chưa được xác nhận thực nghiệm; số liệu cấu hình trung gian là ước lượng, cần kiểm chứng bằng bản ghi đo.')

D.save(OUTF)
print('saved', OUTF)
