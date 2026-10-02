# KỊCH BẢN THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN TỐT NGHIỆP (≈ 20 phút · 30 slide)

**Đề tài:** Thiết kế bộ điều khiển Gimbal trên cơ sở hệ điều hành thời gian thực NuttX
**Học viên:** Huỳnh Thanh Nam – Lớp Tên lửa phòng không 2
**File slide:** `Slide_Bao_ve_DATN_Gimbal_NuttX.pptx` (16:9, giữ nền xanh lục giác của bộ slide cũ)

> Ký hiệu trong kịch bản: **(Nhấp)** = bấm chuột/phím để chạy lớp hiệu ứng tiếp theo.
> Toàn bộ lời thoại dưới đây đã được chép vào phần *Notes* của từng slide (mở *Presenter View* để đọc khi trình bày).

---

## 1. Phân bổ thời gian

| Phần | Slide | Thời lượng | Ghi chú |
|---|---|---|---|
| Mở đầu: lý do chọn đề tài, ứng dụng UAV cánh bằng, mục tiêu, kết cấu | 1 – 4 | ≈ 2 phút | |
| Phần 1 · Bài toán và nguyên nhân sai lệch | 5 – 6 | ≈ 2 phút | |
| Phần 2 · Thiết kế phần cứng, sản phẩm, NuttX, hai IMU | 7 – 11 | ≈ 3,5 phút | |
| Phần 3 · Thuật toán điều khiển, RS485, giám sát, phần mềm máy tính | 12 – 17 | ≈ 4 phút | |
| **Phần 4 · Mô phỏng – hiệu chỉnh – thực nghiệm (trọng tâm)** | **18 – 26** | **≈ 6,5 phút** | 7 bước hiệu chỉnh + slide tổng hợp |
| Phần 5 · Đánh giá, tổng hợp, kết luận | 27 – 30 | ≈ 2 phút | |
| **Tổng** | **30** | **≈ 19,5 – 20 phút** | |

## 2. Mạch logic của bài trình bày

```
Lý do (UAV cánh bằng) → Bài toán gimbal Yaw–Pitch → Nguyên nhân sai lệch (5 nhóm)
   → 6 hướng giải pháp → Phần cứng + NuttX + 2 IMU → 6 khâu điều khiển
   → Mô phỏng thu hẹp tham số → 7 bước hiệu chỉnh trên hệ thật (trước/sau, Yaw & Pitch)
   → Tổng hợp mức cải thiện → Đánh giá theo chỉ tiêu → Kết luận, hạn chế, hướng phát triển
```

Lộ trình hiệu chỉnh (xuất hiện ở đầu mỗi slide 19–26, chuyển cảnh **Morph** làm ô sáng “trượt” sang bước kế tiếp):

**Cấu hình ban đầu → Hiệu chỉnh cascade → Bù IMU2 → Ngoại suy bù trễ → Giới hạn lệnh động → Xử lý đảo chiều và dừng → Tạo dạng lệnh → Hoàn thiện lịch RS485 → Cấu hình hoàn thiện**

Mỗi slide hiệu chỉnh dùng cùng một khuôn: **Vấn đề → Mô phỏng khảo sát → Phương án/tham số → Lựa chọn → Áp dụng hệ thật → So sánh trước/sau → Mức cải thiện**, luôn có số liệu **cả Yaw và Pitch**.

## 3. Quy ước hình thức

- Font thống nhất **Arial** (công thức: Cambria nghiêng). Tiêu đề 28 pt, nội dung 16–20 pt, số liệu chính 28–36 pt, chữ nhỏ nhất 11–12 pt (chỉ dùng cho nhãn phụ).
- Màu: **Yaw = xanh dương, ký hiệu ●**; **Pitch = xanh lá, ký hiệu ■**; *trước/đối chứng = xám*; **phương án được chọn / giá trị quan trọng = cam**; đánh đổi = vàng đậm; vấn đề/chưa đạt = đỏ (luôn kèm biểu tượng).
- Biểu đồ chỉ tiêu được **vẽ lại** từ các bảng số liệu của báo cáo (Bảng 3.9, 3.13, 3.18–3.21), chữ ≥ 13 pt, giá trị ghi trực tiếp trên cột; các lớp “trước” và “sau” xuất hiện lần lượt.
- Đồ thị theo thời gian (Hình 3.3, 3.7, 3.17, 3.18) giữ nguyên từ báo cáo vì không có số liệu thô, được phóng lớn và chú thích bổ sung bằng hộp chữ lớn.

## 4. Kế hoạch chi tiết từng slide

| # | Nội dung chính | Hình ảnh / đồ thị | Chuyển cảnh | Lớp hiệu ứng (theo thứ tự nhấp) | Thời gian |
|---|---|---|---|---|---|
| 1 | Trang bìa | Logo HVKTQS, ảnh CAD gimbal | Fade | Tự động: ảnh Zoom → tiêu đề Wipe → thông tin Fade | 0:20 |
| 2 | Lý do chọn đề tài, ứng dụng trên **UAV cánh bằng** | Hình UAV cánh bằng vẽ lại + đường ngắm, 4 ô ứng dụng | Fade | ① UAV + nhiễu (rung, lượn vòng, đảo hướng) → đường ngắm lệch ② đặc điểm UAV cánh bằng ③ 4 ứng dụng ④ đường ngắm ổn định + tên đề tài (Pulse) | 0:55 |
| 3 | Mục tiêu và yêu cầu | Khối mục tiêu, 4 nhóm chỉ tiêu, 3 ngưỡng thời gian thực | Push | ① Mục tiêu ② 4 nhóm yêu cầu (lần lượt) ③ ngưỡng 2 / 5 / 10 ms + phạm vi | 0:35 |
| 4 | Kết cấu đồ án | Timeline 5 phần, phần 4 “trọng tâm” | Fade | Tự động: trục Wipe → 5 nút lần lượt → nhấn mạnh phần 4 | 0:15 |
| 5 | Bài toán ổn định Gimbal hai trục | Hình gimbal có chú thích, chuỗi động học | Push | ① Chuỗi Khung mang → Yaw → Pitch → Camera ② nguyên lý bù ③ vai trò IMU1/IMU2 ④ tình huống khó | 0:50 |
| 6 | Nguyên nhân sai lệch và ảnh hưởng | Công thức (1.28), thanh trễ 4 nguồn, 5 nguyên nhân → 6 giải pháp | Fade | ① sai lệch ∝ ω_b ② 4 nguồn trễ (Wipe từng thanh) ③ mất pha ④ 5 nguyên nhân ⑤ 6 hướng giải pháp ①–⑥ | 1:05 |
| 7 | Kiến trúc phần cứng | Sơ đồ khối vẽ lại + ảnh linh kiện | Push | ① miền cảm biến ② vi điều khiển ③ bus RS485 + 2 động cơ ④ nguồn, kênh giám sát | 0:40 |
| 8 | Thiết kế mạch và khung cơ khí | Sơ đồ nguyên lý → PCB → 3D → mạch thật; bản vẽ → tách rời → lắp ráp | Fade | ① hàng mạch (Wipe trái→phải) ② hàng cơ khí | 0:30 |
| 9 | **Sản phẩm đã chế tạo** | Ảnh gimbal thật + chú thích; mạch, 2×MS3506, 2×ICM20948 | Zoom | ① ảnh sản phẩm Zoom ② chú thích từng bộ phận ③ 3 thẻ linh kiện | 0:30 |
| 10 | Tổ chức phần mềm trên **Apache NuttX** | 5 tầng NuttX, giản đồ thời gian 0–10 ms của 7 luồng | Fade | ① 5 tầng (dưới→trên) ② luồng IMU → điều khiển (semaphore) + **Motion Path** con trỏ thời gian ③ RS485 và các luồng khác ④ 3 quyết định thiết kế | 0:45 |
| 11 | Hai IMU: xử lý, lọc, ước lượng tư thế | Chuỗi xử lý 2 ms, thẻ IMU1/IMU2, công thức chiếu (2.9) | Fade | ① chuỗi xử lý (từng khối) ② IMU1 ③ IMU2 + công thức ④ bảo vệ điểm kỳ dị, khôi phục | 0:40 |
| 12 | Bộ điều khiển cascade góc – tốc độ góc | Sơ đồ khối toàn hệ, bảng hệ số Yaw/Pitch | Push | ① vòng góc + vòng tốc độ + phản hồi (theo luồng tín hiệu) ② nhánh bù IMU2 và chuỗi giới hạn – tạo dạng – RS485 ③ luật (2.11)(2.12), hệ số | 0:40 |
| 13 | Bù IMU2 và ngoại suy bù trễ | Sơ đồ bù truyền thẳng; minh họa ngoại suy Taylor | Fade | ① nhánh bù ② (1.30) k = 0,9 → sai lệch ÷10 (Pulse) ③ minh họa ngoại suy ④ công thức (2.14) + cổng tin cậy | 0:45 |
| 14 | Giới hạn lệnh theo trạng thái động | Bậc thang 4 vùng 110/135/165 °/s | Fade | ① vấn đề ② 4 cột vùng mọc lần lượt ③ trễ chuyển vùng + bảng ngưỡng | 0:30 |
| 15 | Xử lý đảo chiều, dừng và tạo dạng lệnh | 3 thẻ: dự báo đảo chiều, máy trạng thái dừng, giới hạn tốc độ biến thiên | Fade | ① đảo chiều ② dừng ③ tạo dạng | 0:40 |
| 16 | Truyền thông RS485, giám sát – bảo vệ – khôi phục | Giản đồ khe 5 ms Yaw/Pitch, máy 4 chế độ | Fade | ① vấn đề bus chung ② khe luân phiên + **Motion Path** “token” ③ quy tắc ④ 4 chế độ ⑤ nhóm lỗi | 0:40 |
| 17 | **Phần mềm giám sát và điều khiển** | Ảnh giao diện lớn, khung highlight 5 vùng | Fade | 5 lần nhấp: khung sáng chuyển lần lượt: kết nối + START/STOP → điều khiển góc/tốc độ → Yaw/Pitch + IMU → động cơ, RS485, thời gian thực → đồ thị, log | 0:40 |
| 18 | Mô hình mô phỏng và quy trình hiệu chỉnh | Lộ trình 9 nút, quy trình 7 bước, G_m(s), Hình 3.3 | Push | ① lộ trình ② quy trình ③ mô hình ④ kiểm chứng mô hình 2,4 % / 2,2 % | 0:45 |
| 19 | B1 · Hiệu chỉnh cascade | Bảng khảo sát K_p^θ, Hình 3.7, ô chỉ tiêu t_r, t_s, độ vọt lố, σ | **Morph** | vấn đề → mô phỏng → chọn → hệ thật → cấu hình đối chứng | 0:50 |
| 20 | B2 · Bù IMU2 | Cột e_rms mô phỏng; cột trước/sau e_max, e_rms Yaw–Pitch | **Morph** | vấn đề → mô phỏng → chọn → cột “trước” → cột “sau” (Wipe) → % cải thiện (Zoom) | 0:40 |
| 21 | B3 · Ngoại suy bù trễ | Đường τ_p = 0/8/12/15 ms; cột trước/sau | **Morph** | như trên | 0:50 |
| 22 | B4 · Giới hạn lệnh động | Cột mô phỏng 3 luật; ρ_sat và e_max trước/sau | **Morph** | như trên | 0:40 |
| 23 | B5 · Xử lý đảo chiều và dừng | Hình 3.17 phóng lớn + chú thích; ô thời gian phục hồi | **Morph** | vấn đề → phương án → hệ thật → nhấn mạnh phục hồi −52,4 % / −58,7 % | 0:45 |
| 24 | B6 · Tạo dạng lệnh | Bảng 4 phương án a_max; Hình 3.18 phóng lớn | **Morph** | vấn đề → mô phỏng → hệ thật → bước lệnh −45 %, I_q −22,3 %, đánh đổi | 0:35 |
| 25 | B7 · Hoàn thiện lịch RS485 | Khoảng cập nhật p99/lớn nhất (mô phỏng, hệ thật) | **Morph** | vấn đề → mô phỏng → “ưu tiên Yaw” → “luân phiên” → tản mát −85 % | 0:40 |
| 26 | **Tổng hợp mức cải thiện qua từng bước** | Đường e_max Yaw/Pitch dựng dần từng đoạn | **Morph** | mỗi nhấp vẽ thêm một bước (Wipe) → ô tổng −34,9 % / −32,6 % | 0:50 |
| 27 | Đánh giá kết quả theo chỉ tiêu | 4 cột Đạt / Cải thiện / Đánh đổi / Chưa đạt | Push | 4 cột lần lượt | 0:35 |
| 28 | **Tổng hợp: các thành phần → Hệ Gimbal hoàn thiện** | 10 ô có biểu tượng + ảnh sản phẩm | Zoom | ① 10 ô lần lượt kèm dấu “+” ② mũi tên → sản phẩm hoàn thiện (Zoom + Pulse) | 0:30 |
| 29 | Kết luận, hạn chế, hướng phát triển | 3 cột | Fade | 3 cột lần lượt | 0:50 |
| 30 | Cảm ơn | | Fade | Tự động | 0:10 |

## 5. Lời thoại chi tiết

Lời thoại đầy đủ (kèm mốc **(Nhấp)**) nằm trong phần Notes của từng slide và được trích ra dưới đây.

<!-- NOTES-START -->

### Slide 1 · Trang bìa  _(≈ 0:20)_

Kính thưa đồng chí Trưởng tiểu ban, các thầy trong Hội đồng chấm đồ án tốt nghiệp cùng toàn thể các đồng chí. Dưới sự hướng dẫn khoa học của Trung tá, TS. Nguyễn Ngọc Hưng và Trung tá, ThS. Lê Văn Huy, em đã hoàn thành đồ án với đề tài: “Thiết kế bộ điều khiển Gimbal trên cơ sở hệ điều hành thời gian thực NuttX”. Sau đây em xin trình bày tóm tắt kết quả nghiên cứu trong khoảng 20 phút.

### Slide 2 · Camera trên UAV cánh bằng cần được ổn định đường ngắm  _(≈ 0:55)_

Về lý do chọn đề tài. Camera trên máy bay không người lái là phương tiện quan sát chủ yếu trong cả lĩnh vực quân sự và dân sự, đặc biệt trên UAV cánh bằng. **(Nhấp)** UAV cánh bằng bay nhanh, không thể treo tại chỗ, liên tục lượn vòng và đổi hướng, lại chịu rung động cơ và nhiễu động khí quyển. Nếu camera gắn cứng, đường ngắm bị kéo lệch, ảnh rung, nhòe và dễ mất mục tiêu. **(Nhấp)** Vì vậy hệ ổn định camera là thành phần không thể thiếu trong các nhiệm vụ trinh sát – giám sát, bám và chỉ thị mục tiêu, tuần tra – tìm kiếm cứu nạn và khảo sát. **(Nhấp)** Gimbal giữ cho đường ngắm luôn hướng vào mục tiêu. Từ đó em chọn đề tài thiết kế bộ điều khiển Gimbal chạy trên Apache NuttX – hệ điều hành thời gian thực mã nguồn mở, chuẩn POSIX, cũng là nền của bộ điều khiển bay PX4 – để bảo đảm tính tất định thời gian và dễ tích hợp trên UAV.

### Slide 3 · Mục tiêu và yêu cầu của đồ án  _(≈ 0:35)_

**(Nhấp)** Mục tiêu của đồ án là thiết kế, chế tạo bộ điều khiển Gimbal hai trục Yaw – Pitch trên NuttX, giữ ổn định đường ngắm khi khung mang chuyển động nhanh, đảo chiều và dừng đột ngột. **(Nhấp)** Chất lượng được đánh giá theo bốn nhóm yêu cầu: độ chính xác giữ hướng; đáp ứng động; khả năng khử nhiễu và bảo vệ cơ cấu chấp hành; và tính tất định thời gian. **(Nhấp)** Ba ngưỡng thời gian thực là vòng tốc độ góc 2 ms, khe RS485 5 ms và cập nhật mỗi trục 10 ms. Phạm vi: điều khiển Yaw và Pitch, Roll chỉ ước lượng; phương pháp kết hợp lý thuyết, mô phỏng và thực nghiệm.

### Slide 4 · Kết cấu đồ án tốt nghiệp  _(≈ 0:15)_

Đồ án gồm năm nội dung: bài toán và nguyên nhân sai lệch; thiết kế phần cứng và phần mềm thời gian thực; thuật toán điều khiển; mô phỏng, hiệu chỉnh và thực nghiệm – là phần trọng tâm; cuối cùng là đánh giá và kết luận.

### Slide 5 · Bài toán: Gimbal tạo chuyển động bù để đường ngắm đứng yên  _(≈ 0:50)_

Đối tượng nghiên cứu là Gimbal hai trục. **(Nhấp)** Các khâu nối tiếp nhau: khung mang, trục Yaw, trục Pitch rồi tới camera; động cơ Pitch nằm trên khung Yaw. **(Nhấp)** Góc đường ngắm bằng góc khung mang cộng góc quay các khớp, nên Gimbal phải quay bù ngược chuyển động khung mang để đường ngắm đứng yên trong không gian. **(Nhấp)** Hệ dùng hai cảm biến: IMU1 gắn trên camera đo tư thế đường ngắm làm tín hiệu phản hồi; IMU2 gắn trên đế đo trực tiếp chuyển động khung mang để bù trước. **(Nhấp)** Bài toán là giữ sai lệch nhỏ trên cả hai trục trong các tình huống khó: khung quay nhanh, đảo chiều, dừng đột ngột, với trễ khoảng 12 ms trên đường tín hiệu.

### Slide 6 · Nguyên nhân sai lệch: phản hồi đến muộn, trễ chặn việc tăng hệ số  _(≈ 1:05)_

Vì sao chỉ dùng phản hồi thì chưa đủ? **(Nhấp)** Theo (1.28), sai lệch xác lập tỉ lệ thuận với tốc độ khung mang và tỉ lệ nghịch với hệ số vòng góc: khung quay 8 °/s với K_p^θ = 9,5 cho sai lệch khoảng 0,84°; muốn giảm 10 lần phải tăng hệ số 10 lần. **(Nhấp)** Nhưng trên đường tín hiệu có bốn nguồn trễ: lấy mẫu và lọc, tính toán, chờ khe RS485 và đáp ứng động cơ; trễ hiệu dụng cần bù khoảng 12 ms. **(Nhấp)** Trễ làm mất 43° pha ở 10 Hz và 86° ở 20 Hz, nên không thể tăng hệ số tùy ý. **(Nhấp)** Từ đó em xác định năm nhóm nguyên nhân và ảnh hưởng: nhiễu đo; trễ và biên ổn định; truyền thông không tất định; chuyển động nhanh, đảo chiều, dừng; và giới hạn lệnh cố định. **(Nhấp)** Mỗi nhóm tương ứng một hướng giải pháp, đánh số từ ① đến ⑥, được thiết kế ở Phần 3 và kiểm chứng ở Phần 4.

### Slide 7 · Phần cứng: 2 IMU trên 2 bus SPI, 2 động cơ chung bus RS485  _(≈ 0:40)_

Phần cứng được tổ chức thành ba miền. **(Nhấp)** Miền cảm biến: hai IMU ICM20948 – IMU1 trên camera, IMU2 trên khung mang – lấy mẫu 500 Hz. **(Nhấp)** Hai IMU đi trên hai bus SPI riêng tới miền xử lý: vi điều khiển STM32F407VET6 168 MHz có FPU, chạy Apache NuttX. **(Nhấp)** Miền truyền động: qua UART5 và MAX485, hai động cơ MS3506 dùng chung một bus RS485 bán song công – đây là gốc của bài toán lập lịch. **(Nhấp)** Nguồn 12 V hạ xuống 5 V và 3,3 V; kênh USART qua USB–TTL nối máy tính giám sát, tách khỏi kênh điều khiển.

### Slide 8 · Thiết kế mạch điều khiển 5 khối và khung cơ khí hai trục  _(≈ 0:30)_

**(Nhấp)** Mạch điều khiển được thiết kế trên Altium gồm năm khối: vi điều khiển, giao tiếp cảm biến kép, RS485, chuyển mức logic và nguồn – từ sơ đồ nguyên lý, mạch in hai lớp, mô hình 3D đến mạch đã chế tạo. **(Nhấp)** Khung cơ khí hai trục gồm 12 chi tiết: đế sợi carbon trên bốn đệm cao su mang IMU2; trục Yaw mang toàn bộ khung Pitch; trục Pitch đỡ giá chữ L mang camera và IMU1.

### Slide 9 · Sản phẩm: Gimbal, mạch điều khiển, 2 × MS3506, 2 × ICM20948  _(≈ 0:30)_

**(Nhấp)** Đây là cơ cấu Gimbal hai trục đã chế tạo hoàn chỉnh: động cơ Pitch ở trên, động cơ Yaw ở dưới tấm quay, giá camera cùng IMU1 trên trục Pitch, IMU2 gắn trên đế carbon có đệm cao su. **(Nhấp)** Các thành phần chính: mạch điều khiển STM32F407 tự thiết kế, hai động cơ MS3506 giao tiếp RS485 và hai cảm biến ICM20948.

### Slide 10 · Apache NuttX: 7 luồng ưu tiên chiếm quyền giữ nhịp 2 ms  _(≈ 0:45)_

**(Nhấp)** Phần mềm chạy trên Apache NuttX, tổ chức năm tầng: phần cứng, driver truy cập qua /dev, nhân với bộ lập lịch SCHED_FIFO, tầng đồng bộ bằng semaphore, mutex và tầng ứng dụng gồm bảy luồng. **(Nhấp)** Trong mỗi chu kỳ 2 ms, luồng IMU ưu tiên 120 đọc hai cảm biến rồi phát semaphore đánh thức luồng điều khiển ưu tiên 115; vòng góc chạy mỗi 10 ms, vòng tốc độ góc mỗi 2 ms trong cùng một luồng. **(Nhấp)** Luồng RS485 làm việc theo khe 5 ms, luân phiên Yaw và Pitch; các luồng giám sát, khôi phục IMU2, báo cáo và LED có ưu tiên thấp hơn. **(Nhấp)** Ba quyết định thiết kế: chờ semaphore có hạn 6 ms, chỉ dùng mẫu mới nhất để trễ không tích lũy, và nâng ưu tiên RS485 lên 116 khi phát khung.

### Slide 11 · Hai IMU: IMU1 cho phản hồi, IMU2 đo khung mang để bù trước  _(≈ 0:40)_

**(Nhấp)** Mỗi chu kỳ 2 ms: đọc hai IMU, kiểm tra hợp lệ và tuổi mẫu, kiểm tra độ lệch thời gian hai mẫu không quá 1,5 ms, hiệu chuẩn tỉ lệ, lệch trục, điểm không, lọc rồi ước lượng tư thế bằng Mahony kết hợp Kalman. **(Nhấp)** IMU1 cho góc và tốc độ góc đường ngắm – tín hiệu phản hồi; mất IMU1 thì dừng an toàn. **(Nhấp)** IMU2 cho tốc độ góc khung mang và gia tốc góc; vì động cơ Pitch nằm trên khung Yaw nên tốc độ khung được chiếu lên từng trục theo góc q_y. Mất IMU2 thì chỉ mất khâu bù, vòng kín vẫn làm việc. **(Nhấp)** Điểm kỳ dị tại q_p = ±90° được chặn; IMU2 chỉ được dùng sau khi chờ yên, hiệu chuẩn và kiểm chứng.

### Slide 12 · Bộ điều khiển nối tầng góc – tốc độ góc và vị trí các khâu bù  _(≈ 0:40)_

**(Nhấp)** Cấu trúc điều khiển là nối tầng: vòng góc 100 Hz thuần tỉ lệ tạo tốc độ đặt, có giới hạn theo quãng đường dừng; vòng tốc độ góc 500 Hz là PI có truyền thẳng, khử nhiễu nhanh; cả hai lấy phản hồi từ IMU1. **(Nhấp)** Các khâu bổ sung gắn vào vòng trong: lệnh bù từ IMU2 có ngoại suy được cộng vào đầu ra vòng tốc độ, sau đó qua giới hạn động, xử lý đảo chiều – dừng – tạo dạng, rồi lịch RS485 tới động cơ. **(Nhấp)** Hệ số Pitch lớn hơn vì quán tính nhỏ hơn; vòng ngoài giữ thuần P để tránh hai tích phân lồng nhau; lệnh bù cộng trước khâu giới hạn nên không phá giới hạn an toàn.

### Slide 13 · ② Bù trước bằng IMU2 và ③ ngoại suy bù trễ 12 ms  _(≈ 0:45)_

**(Nhấp)** Khâu ② – bù IMU2: thay vì chờ sai lệch xuất hiện, tốc độ góc khung mang đo bởi IMU2 nhân hệ số k được cộng thẳng vào lệnh tốc độ. **(Nhấp)** Theo (1.30), với k = 0,9 sai lệch xác lập giảm 10 lần mà không phải tăng hệ số vòng kín, nên không lấn vào dự trữ ổn định; k tăng theo vùng tốc độ từ 0,85 đến 0,98. **(Nhấp)** Khâu ③ – lệnh bù đến động cơ trễ khoảng 12 ms. Ngoại suy dùng khai triển Taylor bậc nhất: dùng tiếp tuyến tại thời điểm hiện tại để dự báo tốc độ khung sau τ_p. **(Nhấp)** Lượng ngoại suy bị chặn 90 °/s, gia tốc góc lọc 18 Hz có vùng chết; IMU2 quá 12 ms thì giảm bù về 0 trong 30 ms.

### Slide 14 · ④ Giới hạn lệnh động: nới khi khung quay nhanh, chặt khi tĩnh  _(≈ 0:30)_

**(Nhấp)** Giới hạn lệnh cố định thấp thì bão hòa khi khung quay nhanh, cao thì lệnh lớn ngay cả khi tĩnh. **(Nhấp)** Giải pháp là bốn vùng theo tốc độ khung mang: chậm, thường, nhanh, rất nhanh với giới hạn 110, 135, 165 °/s và hệ số bù tăng dần. **(Nhấp)** Ngưỡng ra thấp hơn ngưỡng vào 25–30 % để không chuyển vùng qua lại; giới hạn được nội suy nên lệnh không nhảy bậc. **(Nhấp)** Bảng ngưỡng cho cả hai trục.

### Slide 15 · ⑤ Xử lý đảo chiều, dừng đột ngột và tạo dạng lệnh  _(≈ 0:40)_

**(Nhấp)** Khi đảo chiều, chương trình dự báo thời điểm tốc độ khung qua không t_0 = −ω_b/α_b; khi t_0 ≤ 20 ms thì mở cửa sổ, giảm biên độ phía cũ, chỉ đổi phía khi dấu mới được xác nhận hai chu kỳ. **(Nhấp)** Khi khung dừng đột ngột, hệ đi qua các trạng thái phanh, ổn định, đã dừng; dừng được xác nhận bằng ba điều kiện trong 220 ms, sau đó bù giảm dần về 0 để camera không vượt ngược. **(Nhấp)** Tạo dạng lệnh giới hạn tốc độ biến thiên 18 000 °/s², nới 30 000 °/s² khi đảo chiều, và giới hạn độ giật để lệnh không nhảy bậc.

### Slide 16 · ⑥ Lịch RS485 tất định và cơ chế giám sát – bảo vệ – khôi phục  _(≈ 0:40)_

**(Nhấp)** Hai động cơ chung bus bán song công; nếu lập lịch ưu tiên động, trễ truyền thông trở thành ngẫu nhiên, trái với giả thiết trễ hằng của khâu ngoại suy. **(Nhấp)** Vì vậy em dùng lịch luân phiên: khe cố định 5 ms, khe chẵn Yaw, khe lẻ Pitch. **(Nhấp)** Mỗi trục được cập nhật đều 10 ms; phản hồi quá 3 ms ghi lỗi, không thử lại trong khe, 5 lỗi liên tiếp báo sự cố. **(Nhấp)** Hệ có bốn chế độ: khởi tạo, sẵn sàng, điều khiển và dừng an toàn. **(Nhấp)** Luồng giám sát ưu tiên 118 theo dõi mất IMU1, tuổi mẫu và lỗi RS485: có sự cố thì dừng động cơ, ghi mã lỗi; mất IMU2 thì tắt bù và khôi phục nền.

### Slide 17 · Phần mềm giám sát và điều khiển trên máy tính  _(≈ 0:40)_

Để vận hành và thu thập số liệu, em xây dựng phần mềm giám sát trên máy tính bằng Python – PySide6. **(Nhấp)** Khu vực kết nối cổng nối tiếp và nút bắt đầu – dừng điều khiển. **(Nhấp)** Đặt góc, tốc độ và điều chỉnh nhanh cho từng trục. **(Nhấp)** Theo dõi sai số Yaw, Pitch, mô hình 3D và tư thế từ IMU. **(Nhấp)** Trạng thái cảm biến, nguồn, nhiệt độ động cơ, bus RS485 và nhịp thời gian thực; tab Động cơ hiển thị dòng điện và tốc độ. **(Nhấp)** Đồ thị thời gian thực, chỉ tiêu chất lượng và nhật ký sự kiện, lỗi. **(Nhấp)** Dữ liệu được ghi với chu kỳ 10 ms, là nguồn số liệu thực nghiệm của Phần 4.

### Slide 18 · Mô phỏng thu hẹp miền tham số, hệ thật quyết định lựa chọn  _(≈ 0:45)_

Phần trọng tâm là quá trình hoàn thiện hệ thống. **(Nhấp)** Lộ trình đi từ cấu hình ban đầu, qua bảy bước hiệu chỉnh, tới cấu hình hoàn thiện. **(Nhấp)** Mỗi bước theo cùng một quy trình: nêu vấn đề, mô phỏng khảo sát các phương án, chọn tham số, áp dụng lên hệ thật, so sánh trước – sau và lượng hóa mức cải thiện trên cả Yaw và Pitch; cấu hình sau mỗi bước là đối chứng của bước tiếp theo. **(Nhấp)** Mô hình cơ cấu chấp hành là khâu quán tính bậc nhất nối tiếp trễ thuần 12 ms, hằng số thời gian 13 ms với Yaw, 4 ms với Pitch. **(Nhấp)** Mô hình tái tạo đáp ứng bậc thang hệ thật với sai lệch dạng sóng 2,4 % và 2,2 %, đủ tin cậy để khảo sát xu hướng; quyết định cuối cùng dựa trên số đo hệ thật.

### Slide 19 · B1 · Hiệu chỉnh cascade: Kpθ = 9,5 s−1 bám nhanh, còn dự trữ lệnh  _(≈ 0:50)_

Bước 1 – hiệu chỉnh cascade. Vấn đề: cần bộ hệ số vừa bám nhanh vừa còn dự trữ lệnh cho các khâu bù. **(Nhấp)** Mô phỏng khảo sát K_p^θ = 6; 9,5; 13: tăng lên 9,5 thời gian lên giảm từ 299,6 xuống 162,7 ms; lên 13 nhanh hơn nhưng lệnh chiếm 76 % giới hạn, không còn dự trữ. **(Nhấp)** Chọn K_p^θ = 9,5 cho Yaw, 38 cho Pitch; tích phân vòng tốc độ giảm J_e 85,7 % trong mô phỏng. **(Nhấp)** Trên hệ thật, 13 lần thử bậc thang của cả hai trục bám sát nhau. **(Nhấp)** Thời gian lên 224,5 và 108,6 ms, độ vọt lố 0,398 và 0,716 %, độ lệch chuẩn khi giữ tĩnh 0,0205° và 0,0068°. **(Nhấp)** Đây là cấu hình đối chứng: ở bài thử đảo chiều nhanh 10,1 s, e_max là 20,24° với Yaw và 13,24° với Pitch.

### Slide 20 · B2 · Bù IMU2: emax giảm khoảng 10 % trên cả hai trục  _(≈ 0:40)_

Bước 2 – bù IMU2. Vấn đề: phản hồi chỉ tác động khi sai lệch đã xuất hiện. **(Nhấp)** Mô phỏng với khung quay 240 °/s: chỉ phản hồi e_rms 20,9°; bù hệ số cố định còn 2,29°; bù theo tốc độ còn 1,89°. **(Nhấp)** Chọn bù theo tốc độ: hệ số k tăng theo vùng tốc độ khung mang. **(Nhấp)** Trên hệ thật, cấu hình đối chứng: e_max 20,24° Yaw và 13,24° Pitch. **(Nhấp)** Sau bù IMU2 còn 18,15° và 11,89°. **(Nhấp)** Tức giảm khoảng 10 % trên cả hai trục; mức cải thiện nhỏ hơn mô phỏng vì ma sát, khe hở và trễ thực; đánh đổi là thời gian xác lập tăng 5,6 % khi khung chuyển động nhanh.

### Slide 21 · B3 · Ngoại suy bù trễ τp = 12 ms: bước cải thiện lớn nhất  _(≈ 0:50)_

Bước 3 – ngoại suy bù trễ. Vấn đề: lệnh bù đến muộn 12 ms. **(Nhấp)** Mô phỏng τ_p = 0; 8; 12; 15 ms: e_rms giảm từ 4,06 xuống 2,33°. **(Nhấp)** 15 ms tốt nhất trong mô phỏng, nhưng gia tốc góc lấy từ vi phân số có nhiễu và trễ thực thay đổi, nên em chọn 12 ms – đạt khoảng 80 % mức cải thiện của 15 ms. **(Nhấp)** Trên hệ thật, trước bước này e_max là 18,15° và 11,89°. **(Nhấp)** Sau ngoại suy còn 14,20° và 9,10°. **(Nhấp)** Giảm 21,8 % ở Yaw và 23,5 % ở Pitch – bước đóng góp lớn nhất của toàn bộ quá trình; tỉ lệ bão hòa Yaw giảm từ 4,3 xuống 2,6 %.

### Slide 22 · B4 · Giới hạn lệnh động: tỉ lệ bão hòa Yaw giảm từ 2,6 % xuống 0,8 %  _(≈ 0:40)_

Bước 4 – giới hạn lệnh động. Vấn đề: với giới hạn cố định 135 °/s, 2,6 % số mẫu Yaw bị bão hòa. **(Nhấp)** Mô phỏng ở xung 600 °/s: e_rms từ 9,91° với giới hạn cố định xuống 8,17° với hai mốc và 8,05° với bốn mốc, giảm 18,8 %. **(Nhấp)** Chọn luật bốn mốc 110, 135, 165 °/s. **(Nhấp)** Trên hệ thật, so sánh với giới hạn cố định. **(Nhấp)** Tỉ lệ bão hòa Yaw giảm từ 2,6 xuống 0,8 %, e_max Yaw giảm 4,8 %, Pitch gần như không đổi. **(Nhấp)** Mức cải thiện nhỏ hơn mô phỏng vì giá thử chỉ tạo được khoảng 240 °/s.

### Slide 23 · B5 · Xử lý đảo chiều và dừng: thời gian phục hồi giảm hơn 50 %  _(≈ 0:45)_

Bước 5 – xử lý đảo chiều và dừng. Vấn đề: khi khung dừng đột ngột, lượng bù và tích phân tồn dư kéo camera vượt ngược. **(Nhấp)** Hai phương án: ngắt bù tức thời hoặc giảm bù dần; cùng các tham số xác nhận dừng và cửa sổ đảo chiều. **(Nhấp)** Chọn giảm bù dần: giữ 150 ms, giảm trong 50 ms, xác nhận dừng 220 ms. **(Nhấp)** Hệ thật, 12 lần thử với gia tốc hãm 2 300 °/s²: nét đứt là chưa xử lý, nét liền là có xử lý. **(Nhấp)** Khi chưa xử lý, camera vượt ngược sau khi khung dừng; sai lệch đỉnh gần như không đổi vì xuất hiện trong lúc hãm. **(Nhấp)** Thời gian phục hồi giảm 52,4 % ở Yaw và 58,7 % ở Pitch; xác nhận dừng đạt 12/12; khi đảo chiều e_max giảm thêm 4,1 % và 2,8 %.

### Slide 24 · B6 · Tạo dạng lệnh: bước lệnh giảm 45 %, dòng Iq giảm 22,3 %  _(≈ 0:35)_

Bước 6 – tạo dạng lệnh. Vấn đề: lệnh nhảy 109 °/s trong một chu kỳ khi đảo chiều. **(Nhấp)** Mô phỏng bốn phương án giới hạn tốc độ biến thiên. **(Nhấp)** Chọn 18 000 °/s², nới 30 000 °/s² khi đảo chiều: năng lượng rung 10–30 Hz còn 23 %, e_max chỉ tăng 2,3 %. **(Nhấp)** Trên hệ thật, lệnh trục Yaw quanh một lần đảo chiều. **(Nhấp)** Không tạo dạng: một bước nhảy 109 °/s; có tạo dạng: mỗi chu kỳ không quá 60 °/s. **(Nhấp)** Bước lệnh lớn nhất giảm 45 %, dòng I_q hiệu dụng giảm 22,3 %; đổi lại e_rms tăng 1,4 % ở Yaw và 1,1 % ở Pitch – đánh đổi có chủ đích để bảo vệ cơ cấu.

### Slide 25 · B7 · Lịch RS485 luân phiên: Pitch cập nhật đều, độ tản mát giảm 85 %  _(≈ 0:40)_

Bước 7 – lịch RS485. Vấn đề: chế độ ưu tiên Yaw làm trục Pitch cập nhật không đều. **(Nhấp)** Mô phỏng 20 000 khe: luân phiên giới hạn khoảng cập nhật lớn nhất của Pitch từ 70 xuống 22 ms. **(Nhấp)** Chọn lịch luân phiên khe 5 ms, không thử lại trong khe. **(Nhấp)** Trên hệ thật, tải đầy đủ, chế độ ưu tiên Yaw: Pitch có lúc 62,1 ms mới được cập nhật. **(Nhấp)** Với luân phiên, cả hai trục quanh 12 ms, lớn nhất 14,1 ms. **(Nhấp)** Độ tản mát của Pitch giảm 85 %, e_max Pitch thấp hơn 18,5 %. Đánh đổi: ưu tiên Yaw cho e_rms Yaw thấp hơn 8,7 %, nhưng em chọn luân phiên vì tính tất định của trễ. Hạn chế: có giao dịch kéo dài 6,00 ms, vượt khe 5 ms.

### Slide 26 · Hoàn thiện dần qua 7 bước: emax giảm 34,9 % (Yaw) và 32,6 % (Pitch)  _(≈ 0:50)_

Ghép các bước trên cùng bài thử đảo chiều nhanh 10,1 s. **(Nhấp)** Bù IMU2 giảm khoảng 10 % trên cả hai trục. **(Nhấp)** Ngoại suy 12 ms giảm mạnh nhất, hơn 21 %. **(Nhấp)** Giới hạn động và xử lý đảo chiều, dừng giảm tiếp vài phần trăm. **(Nhấp)** Tạo dạng lệnh tăng nhẹ 1,6 % – đánh đổi có chủ đích; lịch RS485 giữ nguyên sai lệch nhưng bảo đảm cập nhật đều. **(Nhấp)** Tổng cộng e_max giảm 34,9 % ở Yaw và 32,6 % ở Pitch; e_rms giảm 23,3 % và 22,8 %; tỉ lệ bão hòa từ 6,1 xuống 0,7 %; phục hồi sau đảo chiều giảm 23,7 %, sau dừng giảm hơn 50 %.

### Slide 27 · Đánh giá kết quả theo hệ chỉ tiêu kỹ thuật  _(≈ 0:35)_

Đánh giá theo hệ chỉ tiêu. **(Nhấp)** Đạt: độ lệch chuẩn khi giữ tĩnh dưới 0,03°, độ vọt lố dưới 1 %, vòng tốc độ góc giữ đúng 2 ms, xác nhận dừng 12/12. **(Nhấp)** Cải thiện rõ ở sai lệch, thời gian phục hồi, độ đều cập nhật và dòng động cơ. **(Nhấp)** Các đánh đổi có chủ đích được lượng hóa. **(Nhấp)** Chưa đạt: tuyến RS485 chưa tất định hoàn toàn – giao dịch lớn nhất 6,00 ms, khoảng cập nhật lớn nhất 14,1 ms. Phạm vi kiểm chứng giới hạn ở tốc độ đỉnh khoảng 240 °/s.

### Slide 28 · Các nội dung đã thực hiện tạo nên hệ Gimbal hoàn thiện  _(≈ 0:30)_

Tổng hợp lại, **(Nhấp)** hệ Gimbal hoàn thiện là kết quả của thiết kế cơ khí, thiết kế mạch, lập trình NuttX, xử lý hai IMU, điều khiển nối tầng, bù IMU2, bù trễ, xử lý chuyển động nhanh, lịch RS485 và phần mềm giám sát. **(Nhấp)** Tất cả đã được thiết kế, chế tạo, lập trình, mô phỏng và kiểm chứng trên hệ thật.

### Slide 29 · Kết luận, hạn chế và hướng phát triển  _(≈ 0:50)_

**(Nhấp)** Kết luận: đồ án đã thiết kế, chế tạo và vận hành Gimbal hai trục trên STM32F407 và Apache NuttX; xây dựng bảy luồng thời gian thực, xử lý hai IMU và sáu khâu điều khiển; mô hình mô phỏng sai lệch dạng sóng 2,4 % và 2,2 %; qua bảy bước hiệu chỉnh, e_max giảm 34,9 % và 32,6 %, phục hồi sau dừng giảm hơn 50 %. **(Nhấp)** Hạn chế: RS485 chưa tất định hoàn toàn; thực nghiệm mới tới khoảng 240 °/s; mô hình chưa có ma sát, khe hở. **(Nhấp)** Hướng phát triển: bus riêng hoặc CAN với ngoại suy thích nghi, quét tần số và lọc chắn dải, giá thử kích thích lớn hơn, tham chiếu phương vị độc lập cho Yaw và điều khiển trực tiếp dòng I_q. Em xin kết thúc phần trình bày.

### Slide 30 · Cảm ơn  _(≈ 0:10)_

Em xin trân trọng cảm ơn Hội đồng đã lắng nghe và kính mong nhận được câu hỏi, ý kiến đóng góp của các thầy.

<!-- NOTES-END -->
