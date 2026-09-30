"""Ban rut gon (khoang 2 trang A4) cua muc 3.4.1 - Hoan thien lich truyen RS485.

Chay sau run_part5.py va figs341.py (phan 'short'):  python build341_ngan.py
"""
exec(open('build_head.py', encoding='utf8').read())   # D, f, pc, inc, red, fig, LD, V, R2, AX, AXN ...
import pickle
NB = '\u00a0'
_pc, _inc, _red = pc, inc, red
pc = lambda a, b, nd=1: _pc(a, b, nd).replace(' %', NB + '%')      # khong ngat dong truoc dau %
inc = lambda a, b, nd=1: _inc(a, b, nd).replace(' %', NB + '%')
red = lambda a, b, nd=1: _red(a, b, nd).replace(' %', NB + '%')
R5 = pickle.load(open('results5.pkl', 'rb'))
OUT = OUTF.replace('Chuong3_3.1.3_den_het', 'Muc_3.4.1_lich_RS485_rut_gon')

E = C.exc(); T = E['T']
L6 = LD['tao_dang']; L7 = LD['hoan_thien']
SV = R5['survey']; YP = SV[('yawpri', 5e-3)]; A4 = SV[('alt', 4e-3)]; A5 = SV[('alt', 5e-3)]
P = R5['pair']; BG = P['by_gap']
last = R5['log_bus'][-1]
T_CTRL = 76.306                               # 21:49:12,037 -> 21:50:28,343 (log A)
n_tx = int(last[1]); rate_meas = n_tx / T_CTRL; n_tx_s = f'{n_tx:,}'.replace(',', ' ')
gmaxY, gmaxP, exec_max = last[3] / 1e3, last[4] / 1e3, last[6] / 1e3
dmax_tx = int(np.abs(R5['log_bus'][:, 1] - R5['log_bus'][:, 2]).max())
gp = np.asarray(YP['sched']['pitch']['gaps'], float)
m4 = (T >= C.SEG[3][0]) & (T < C.SEG[3][1])
a95 = float(np.percentile(np.abs(np.gradient(E['wd']['pitch'], gsim.DT))[m4], 95))
worse = lambda o: max(o['yaw']['erms'], o['pitch']['erms'])
yp_, a5_ = YP['sched']['pitch'], A5['sched']['pitch']

D.heading('3.4.1. Hoàn thiện lịch truyền RS485', 3)
D.lead('a) Vấn đề của cấu hình đầu vào.',
       f'Sau khâu tạo dạng, e_{{rms}} tái hiện trục Pitch ({f(L6["pitch"]["erms"], 3)}°) lớn hơn trục Yaw '
       f'({f(L6["yaw"]["erms"], 3)}°). Với lịch ưu tiên Yaw, giao dịch Pitch chỉ được ghép '
       'vào khe 5 ms khi giao dịch Yaw kết thúc trong 2,25 ms, nếu không sẽ bị hoãn sang khe sau (Hình 3.19a). Khoảng cập '
       f'nhật Δ của Pitch vì thế không đều: lớn nhất {f(yp_["mx"], 1)} ms, độ lệch chuẩn σ_{{Δ}} = {f(yp_["std"], 2)} ms '
       '(Hình 3.19c). Lệnh cũ bị giữ lâu hơn trễ cố định τ_{p} = 12 ms mà ngoại suy (2.14) bù, nên lệnh thiếu xấp xỉ '
       'α_{b}(Δ\u00a0−\u00a010\u00a0ms). Thử cặp trên mô phỏng tái hiện, chỉ làm đều Δ của Pitch: '
       f'sai lệch lớn nhất trong một khoảng cập nhật cao hơn {inc(BG[1]["eR"], BG[1]["eY"], 0)} khi '
       f'Δ ≈ 15 ms và {inc(BG[2]["eR"], BG[2]["eY"], 0)} khi Δ ≥ 20 ms (Hình 3.19d); riêng việc làm đều Δ đã giảm e_{{rms}} '
       f'Pitch {red(P["yawpri"]["pitch"]["erms"], P["reg"]["pitch"]["erms"])}.')
fig(19, 'h3_19_lich_rs485', 'Lịch truyền RS485 và khoảng cập nhật trục Pitch')

D.lead('b) Mô phỏng khảo sát và lựa chọn phương án.',
       'Lịch được chọn theo ba tiêu chí xếp theo thứ tự ưu tiên: (1) Δ của mỗi trục có cận trên xác định và σ_{Δ} nhỏ – '
       'điều kiện để ngoại suy làm việc đúng; (2) e_{rms} của trục kém hơn nhỏ nhất; (3) mỗi khe còn ít nhất 1 ms dự trữ '
       'sau cửa sổ giao dịch lớn nhất 3,5 ms (khung lệnh 0,43 ms và chờ phản hồi tối đa 3 ms). Kết quả mô phỏng theo sự '
       'kiện 100 s và vòng kín trên mô hình danh định ở Bảng 3.12.')
rows = []
verdict = {('yawpri', 5e-3): 'Loại (1)', ('alt', 4e-3): 'Loại (3)', ('alt', 5e-3): 'Chọn',
           ('alt', 6e-3): 'Loại (2)'}
for (mode, slot), lab in zip([('yawpri', 5e-3), ('alt', 4e-3), ('alt', 5e-3), ('alt', 6e-3)],
                             ['Ưu tiên Yaw, khe 5 ms', 'Luân phiên, khe 4 ms', 'Luân phiên, khe 5 ms', 'Luân phiên, khe 6 ms']):
    o = SV[(mode, slot)]; s = o['sched']
    rows.append([lab, f(s['yaw']['rate'], 0) + ' / ' + f(s['pitch']['rate'], 0),
                 f(s['yaw']['std'], 2) + ' / ' + f(s['pitch']['std'], 2),
                 f(s['yaw']['mx'], 1) + ' / ' + f(s['pitch']['mx'], 1), f(slot * 1e3 - 3.5, 1),
                 f(o['closed']['yaw']['erms'], 3) + ' / ' + f(o['closed']['pitch']['erms'], 3), verdict[(mode, slot)]])
D.table('Bảng 3.12. Khảo sát phương án lập lịch RS485 (giá trị Yaw / Pitch)',
        [['Phương án', 'Tần số (Hz)', 'σ_{Δ} (ms)', 'Δ lớn nhất (ms)', 'Dự trữ khe (ms)', 'e_{rms} (°)', 'Đánh giá']],
        rows, [3.9, 1.7, 2.0, 2.1, 1.5, 2.3, 1.5], size=10, bold_rows=[2], align=['left'] + ['center'] * 6,
        note='Ghi chú: mô phỏng khảo sát, τ_{p} = 12 ms; (1), (2), (3) là các tiêu chí nêu trên.')
D.para('Lịch luân phiên cho mỗi trục khe riêng nên không còn hoãn lượt; giao dịch dài chỉ kéo dài Δ thêm phần tràn khe '
       f'(Hình 3.19b). Với khe 5 ms, σ_{{Δ}} của Pitch giảm từ {f(yp_["std"], 2)} xuống {f(a5_["std"], 2)} ms; đổi lại Yaw chỉ '
       f'còn {f(A5["sched"]["yaw"]["rate"], 0)} Hz nên e_{{rms}} Yaw tăng {inc(YP["closed"]["yaw"]["erms"], A5["closed"]["yaw"]["erms"])}, '
       f'Pitch giảm {red(YP["closed"]["pitch"]["erms"], A5["closed"]["pitch"]["erms"])} và sai lệch của trục kém hơn giảm từ '
       f'{f(worse(YP["closed"]), 3)}° xuống {f(worse(A5["closed"]), 3)}°. Khe 4 ms tốt hơn trong mô hình nhưng chỉ dư 0,5 ms, '
       f'trong khi thực tế có giao dịch kéo dài tới {f(exec_max, 0)} ms do luồng RS485 bị chen ngang; khe 6 ms làm cả hai '
       'trục kém đi. Vì vậy chọn lịch luân phiên khe 5 ms và giữ τ_{p} = 12 ms (kiểm tra với 8 và 16 ms cho cùng kết luận).')

D.lead('c) Áp dụng và đánh giá.',
       f'Trên mô phỏng tái hiện, lịch luân phiên giảm e_{{rms}} Pitch {red(L6["pitch"]["erms"], L7["pitch"]["erms"])}, tăng '
       f'e_{{rms}} Yaw {inc(L6["yaw"]["erms"], L7["yaw"]["erms"])} và làm hai trục cân bằng '
       f'({f(L7["yaw"]["erms"], 3)}° / {f(L7["pitch"]["erms"], 3)}°); số đo log A là {f(V["log"]["yaw"]["erms"], 3)}° / '
       f'{f(V["log"]["pitch"]["erms"], 3)}°. Bộ đếm bus trong log A cho thấy mỗi trục thực hiện {n_tx_s} giao '
       f'dịch trong {f(T_CTRL, 1)} s ({f(rate_meas, 1)} Hz), hai trục chênh nhau không quá {dmax_tx} giao dịch, không có '
       f'giao dịch lỗi; khoảng cập nhật lớn nhất {f(gmaxY, 0)} / {f(gmaxP, 0)} ms, bằng khoảng một nửa so với lịch ưu tiên '
       'Yaw.')
D.save(OUT)
print('saved', OUT)
