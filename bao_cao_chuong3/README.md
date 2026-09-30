# Chương 3 (từ mục 3.1.3 đến hết) – bản viết lại

- `Chuong3_3.1.3_den_het.docx`: nội dung Word, dựng trên chính file báo cáo gốc làm mẫu (style Heading 2/3, FigCap, TblCap, TableGrid1; công thức OMML). Đánh số: công thức (3.5)–(3.7), Hình 3.5–3.22, Bảng 3.2–3.16.
- `Chuong3_3.1.3_den_het.pdf`: bản xem trước (xuất bằng LibreOffice, 26 trang).
- `hinh/`: 18 hình PNG 600 dpi, vẽ đúng kích thước trên trang A4 (rộng ≤ 16 cm) và chèn vào Word không co giãn.
- `mo_phong/`: mã nguồn tái tạo toàn bộ số liệu và hình.
- `Muc_3.4.1_lich_RS485_4_trang.docx` / `.pdf`: bản 4 trang mục 3.4.1 (bản đề xuất dùng): Hình 3.19 (cơ chế), Hình 3.20 (khảo sát và lựa chọn phương án, ngân sách thời gian khe), Hình 3.21 (trước / sau), Bảng 3.12, 3.13, công thức (3.7); trên hình chỉ có số liệu mô phỏng, số đo log A nằm trong lời văn và cột "đo" của Bảng 3.13. Khi ghép vào chương, các hình sau Hình 3.21 tăng số thứ tự 1, số bảng giữ nguyên.
- `Muc_3.4.1_lich_RS485_rut_gon.docx` / `.pdf`: bản rút gọn mục 3.4.1 (2 trang A4): một hình (Hình 3.19, chỉ số liệu mô phỏng, không có số đo log A trên hình) và một bảng (Bảng 3.12); số đo log A chỉ nêu trong lời văn. Khi ghép vào chương, bản này có ít hơn bản cũ một hình và một bảng nên các hình, bảng phía sau giảm số thứ tự 1.
- `Muc_3.4.1_lich_RS485.docx` / `.pdf`: bản đầy đủ mục 3.4.1 (Hình 3.19 – 3.21, Bảng 3.12 – 3.13, công thức (3.7)); hình ở `hinh_3.4.1/`. Khi ghép vào chương, mục này có thêm một hình nên các hình sau nó tăng số thứ tự thêm 1 (Hình 3.21 cũ thành 3.22, Hình 3.22 cũ thành 3.23).

## Chuẩn trình bày hình

- Phông Liberation Serif (cùng kích thước chữ với Times New Roman): số trên trục 10 pt, tên trục 11 pt, chú giải 10 pt, tên hình con 11 pt đặt ở giữa, ngay dưới từng hình con.
- Yaw dùng họ màu xanh lam, Pitch dùng họ màu cam, giữ cố định ở mọi hình.
- Trước hiệu chỉnh: nét đứt đen. Sau hiệu chỉnh: nét liền màu chính. Số đo log A: chấm tròn rỗng đen.
- Trong hình khảo sát, phương án chọn là nét liền màu chính, dày nhất, ghi "(chọn)". Giá trị thấp hơn dùng màu nhạt, nét đứt. Giá trị cao hơn dùng màu đậm, nét chấm gạch.
- Trên biểu đồ cột, phương án chọn có nền xám và nhãn in đậm.
- Chú giải luôn đặt trong dải riêng phía trên hình, không đè lên dữ liệu.
- Hình không ghi chú nội bộ và không ghi "(mô phỏng tái hiện)"; nguồn số liệu ghi ở tên hình trong Word.
- `figs.py` tự kiểm tra chữ chồng chữ, chú giải nằm trong vùng dữ liệu và chữ bị cắt khi xuất hình.

## Nguồn số liệu

- **Đo (log A)**: `mo_phong/log_A.txt` – cấu hình hoàn thiện.
- **Mô phỏng khảo sát**: mô hình danh định (τd = 12 ms; Tm = 13 / 4 ms – Bảng 3.1).
- **Mô phỏng tái hiện**: mô hình hiệu chỉnh khớp log A (τe = 8 / 10 ms; hệ số đường bù IMU2 1,06 / 1,02), kích thích là chuyển động khung mang do IMU2 ghi trong log A. Mọi số liệu của các cấu hình trung gian thuộc loại này và được ghi nhãn trong báo cáo.

## Chạy lại

```
pip install numpy scipy matplotlib python-docx pillow
cd mo_phong
python retime.py          # dựng lại thời điểm thật của các mẫu log A -> t_true.npy
python run_all.py         # kiểm chứng, chuỗi 8 cấu hình, khảo sát nối tầng / bù / ngoại suy / giới hạn / đảo chiều
python run_part2.py       # tạo dạng lệnh, lịch RS485, mẫu IMU2 lỗi, dừng đột ngột
python run_part3.py       # ràng buộc K_pω, sự kiện đổi chiều theo cấu hình
python run_part4.py       # chạy bổ sung để mọi ô bảng đều có giá trị
python figs.py            # hình -> figs/ (600 dpi, kèm kiểm tra bố cục)
cp <báo cáo gốc>.docx report.docx
cat build_head.py build_body.py > build_ch3.py && python build_ch3.py
# riêng mục 3.4.1
python run_part5.py       # thử cặp lịch Pitch, khảo sát lịch / độ dài khe, bộ đếm bus log A
python figs341.py figs log_A.txt
python build341.py        # bản đầy đủ
python build341_ngan.py   # bản rút gọn 2 trang
python build341_4tr.py    # bản 4 trang (figs341.py figs log_A.txt 4tr)
```
