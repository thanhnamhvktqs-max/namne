# Chương 3 (từ mục 3.1.3 đến hết) – bản viết lại

- `Chuong3_3.1.3_den_het.docx`: nội dung Word, dựng trên chính file báo cáo gốc làm mẫu (style Heading 2/3, FigCap, TblCap, TableGrid1; công thức OMML). Đánh số: công thức (3.5)–(3.7), Hình 3.5–3.22, Bảng 3.2–3.16.
- `Chuong3_3.1.3_den_het.pdf`: bản xem trước (xuất bằng LibreOffice, 23 trang).
- `hinh/`: 18 hình PNG 300 dpi.
- `mo_phong/`: mã nguồn tái tạo toàn bộ số liệu và hình.

## Nguồn số liệu

- **Đo (log A)**: `mo_phong/log_A.txt` – cấu hình hoàn thiện.
- **Mô phỏng khảo sát**: mô hình danh định (τd = 12 ms; Tm = 13 / 4 ms – Bảng 3.1).
- **Mô phỏng tái hiện**: mô hình hiệu chỉnh khớp log A (τe = 8 / 10 ms; hệ số đường bù IMU2 1,06 / 1,02), kích thích là chuyển động khung mang do IMU2 ghi trong log A. Mọi số liệu của các cấu hình trung gian thuộc loại này và được ghi nhãn trong báo cáo.

## Chạy lại

```
pip install numpy scipy matplotlib python-docx
cd mo_phong
python retime.py          # dựng lại thời điểm thật của các mẫu log A -> t_true.npy
python run_all.py         # kiểm chứng, chuỗi 8 cấu hình, khảo sát nối tầng / bù / ngoại suy / giới hạn / đảo chiều
python run_part2.py       # tạo dạng lệnh, lịch RS485, mẫu IMU2 lỗi, dừng đột ngột
python run_part3.py       # ràng buộc K_pω, sự kiện đổi chiều theo cấu hình
python figs.py            # hình -> figs/
cp <báo cáo gốc>.docx report.docx
cat build_head.py build_body.py > build_ch3.py && python build_ch3.py
```
