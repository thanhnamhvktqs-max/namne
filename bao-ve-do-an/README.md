# Slide bảo vệ đồ án tốt nghiệp – Gimbal trên Apache NuttX

| File | Nội dung |
|---|---|
| `Slide_Bao_ve_DATN_Gimbal_NuttX.pptx` | Bộ slide trình chiếu: 30 slide 16:9, ≈ 20 phút, có chuyển cảnh và hiệu ứng nhiều lớp, lời thoại trong Notes |
| `KICH_BAN_THUYET_TRINH.md` | Kịch bản: phân bổ thời gian, kế hoạch từng slide (nội dung – hình – hiệu ứng), lời thoại đầy đủ có mốc **(Nhấp)** |
| `Slide_Bao_ve_DATN_Gimbal_NuttX_ban_tinh.pdf` | Bản tĩnh (không hiệu ứng) để in hoặc dự phòng khi máy chiếu không có PowerPoint |
| `build/` | Mã nguồn dựng lại bộ slide, biểu đồ và số liệu |

## Khi trình chiếu

- Mở bằng **PowerPoint 2019 / Microsoft 365** để có chuyển cảnh **Morph** ở slide 19–26 (ô sáng trên thanh lộ trình trượt sang bước kế tiếp). Bản PowerPoint cũ hơn tự chuyển sang Fade.
- Bật **Presenter View** để đọc lời thoại; mỗi **(Nhấp)** trong Notes ứng với một lần bấm. Tổng cộng 109 lần bấm, slide 1, 4 và 30 chạy tự động.
- Font dùng toàn bộ là Arial, công thức dùng Cambria (có sẵn trong Windows/Office).

## Cấu trúc 30 slide

1–4 Mở đầu (lý do chọn đề tài, ứng dụng trên UAV cánh bằng, mục tiêu – yêu cầu, kết cấu) ·
5–6 Bài toán và nguyên nhân sai lệch ·
7–11 Phần cứng, sản phẩm, NuttX, hai IMU ·
12–17 Thuật toán, RS485, giám sát – bảo vệ, phần mềm máy tính ·
**18–26 Mô phỏng – hiệu chỉnh – thực nghiệm (7 bước, trước/sau cho cả Yaw và Pitch, slide tổng hợp mức cải thiện)** ·
27–30 Đánh giá, tổng hợp hệ thống, kết luận, cảm ơn.

## Nguồn số liệu và hình

- Mọi số liệu lấy từ bộ slide báo cáo gốc (các Bảng 1.4, 2.4, 2.5, 3.9, 3.13, 3.18–3.21); `build/data.py` gom toàn bộ, các phần trăm được tính lại và khớp với báo cáo.
- Biểu đồ chỉ tiêu (cột trước/sau, đường τ_p, khoảng cập nhật RS485, chuỗi e_max qua 7 bước) được **vẽ lại** từ các bảng đó.
- Đồ thị theo thời gian (Hình 3.3, 3.7, 3.17, 3.18), ảnh sản phẩm, mạch, CAD và giao diện phần mềm lấy nguyên từ bộ slide gốc vì không có số liệu thô; hình minh họa nguyên lý ngoại suy và tạo dạng lệnh có ghi chú “minh họa”.

## Dựng lại

```bash
cd build
./build.sh /duong/dan/Slide_Bao_cao_DATN_goc.pptx
```

Cần `python3` (python-pptx, matplotlib, pillow, lxml) và `node` (react-icons, react, react-dom, sharp). Sửa số liệu ở `data.py`, lời thoại ở `notes.py`, bố cục từng slide ở `build_deck.py`.
