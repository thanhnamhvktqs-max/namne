# -*- coding: utf-8 -*-
"""Loi thoai thuyet trinh (Notes) cho tung slide. (Nhấp) = bam chuot de chay lop hieu ung tiep theo.
So lan (Nhấp) khop voi so nhom hieu ung theo lan nhap tren slide tuong ung."""

NOTES = {
    1: "[0:20] Kính thưa đồng chí Trưởng tiểu ban, các thầy trong Hội đồng chấm đồ án tốt nghiệp cùng toàn thể các "
       "đồng chí. Dưới sự hướng dẫn khoa học của Trung tá, TS. Nguyễn Ngọc Hưng và Trung tá, ThS. Lê Văn Huy, em đã "
       "hoàn thành đồ án với đề tài: “Thiết kế bộ điều khiển Gimbal trên cơ sở hệ điều hành thời gian thực NuttX”. "
       "Sau đây em xin trình bày tóm tắt kết quả nghiên cứu trong khoảng 20 phút.",

    2: "[0:55] Về lý do chọn đề tài. Camera trên máy bay không người lái là phương tiện quan sát chủ yếu trong cả "
       "lĩnh vực quân sự và dân sự, đặc biệt trên UAV cánh bằng. "
       "(Nhấp) UAV cánh bằng bay nhanh, không thể treo tại chỗ, liên tục lượn vòng và đổi hướng, lại chịu rung động "
       "cơ và nhiễu động khí quyển. Nếu camera gắn cứng, đường ngắm bị kéo lệch, ảnh rung, nhòe và dễ mất mục tiêu. "
       "(Nhấp) Vì vậy hệ ổn định camera là thành phần không thể thiếu trong các nhiệm vụ trinh sát – giám sát, bám và "
       "chỉ thị mục tiêu, tuần tra – tìm kiếm cứu nạn và khảo sát. "
       "(Nhấp) Gimbal giữ cho đường ngắm luôn hướng vào mục tiêu. Từ đó em chọn đề tài thiết kế bộ điều khiển Gimbal "
       "chạy trên Apache NuttX – hệ điều hành thời gian thực mã nguồn mở, chuẩn POSIX, cũng là nền của bộ điều khiển "
       "bay PX4 – để bảo đảm tính tất định thời gian và dễ tích hợp trên UAV.",

    3: "[0:35] (Nhấp) Mục tiêu của đồ án là thiết kế, chế tạo bộ điều khiển Gimbal hai trục Yaw – Pitch trên NuttX, "
       "giữ ổn định đường ngắm khi khung mang chuyển động nhanh, đảo chiều và dừng đột ngột. "
       "(Nhấp) Chất lượng được đánh giá theo bốn nhóm yêu cầu: độ chính xác giữ hướng; đáp ứng động; khả năng khử "
       "nhiễu và bảo vệ cơ cấu chấp hành; và tính tất định thời gian. "
       "(Nhấp) Ba ngưỡng thời gian thực là vòng tốc độ góc 2 ms, khe RS485 5 ms và cập nhật mỗi trục 10 ms. Phạm vi: "
       "điều khiển Yaw và Pitch, Roll chỉ ước lượng; phương pháp kết hợp lý thuyết, mô phỏng và thực nghiệm.",

    4: "[0:15] Đồ án gồm năm nội dung: bài toán và nguyên nhân sai lệch; thiết kế phần cứng và phần mềm thời gian "
       "thực; thuật toán điều khiển; mô phỏng, hiệu chỉnh và thực nghiệm – là phần trọng tâm; cuối cùng là đánh giá và "
       "kết luận.",

    5: "[0:50] Đối tượng nghiên cứu là Gimbal hai trục. "
       "(Nhấp) Các khâu nối tiếp nhau: khung mang, trục Yaw, trục Pitch rồi tới camera; động cơ Pitch nằm trên khung "
       "Yaw. "
       "(Nhấp) Góc đường ngắm bằng góc khung mang cộng góc quay các khớp, nên Gimbal phải quay bù ngược chuyển động "
       "khung mang để đường ngắm đứng yên trong không gian. "
       "(Nhấp) Hệ dùng hai cảm biến: IMU1 gắn trên camera đo tư thế đường ngắm làm tín hiệu phản hồi; IMU2 gắn trên đế "
       "đo trực tiếp chuyển động khung mang để bù trước. "
       "(Nhấp) Bài toán là giữ sai lệch nhỏ trên cả hai trục trong các tình huống khó: khung quay nhanh, đảo chiều, "
       "dừng đột ngột, với trễ khoảng 12 ms trên đường tín hiệu.",

    6: "[1:05] Vì sao chỉ dùng phản hồi thì chưa đủ? "
       "(Nhấp) Theo (1.28), sai lệch xác lập tỉ lệ thuận với tốc độ khung mang và tỉ lệ nghịch với hệ số vòng góc: "
       "khung quay 8 °/s với K_p^θ = 9,5 cho sai lệch khoảng 0,84°; muốn giảm 10 lần phải tăng hệ số 10 lần. "
       "(Nhấp) Nhưng trên đường tín hiệu có bốn nguồn trễ: lấy mẫu và lọc, tính toán, chờ khe RS485 và đáp ứng động "
       "cơ; trễ hiệu dụng cần bù khoảng 12 ms. "
       "(Nhấp) Trễ làm mất 43° pha ở 10 Hz và 86° ở 20 Hz, nên không thể tăng hệ số tùy ý. "
       "(Nhấp) Từ đó em xác định năm nhóm nguyên nhân và ảnh hưởng: nhiễu đo; trễ và biên ổn định; truyền thông không "
       "tất định; chuyển động nhanh, đảo chiều, dừng; và giới hạn lệnh cố định. "
       "(Nhấp) Mỗi nhóm tương ứng một hướng giải pháp, đánh số từ ① đến ⑥, được thiết kế ở Phần 3 và kiểm chứng ở "
       "Phần 4.",

    7: "[0:40] Phần cứng được tổ chức thành ba miền. "
       "(Nhấp) Miền cảm biến: hai IMU ICM20948 – IMU1 trên camera, IMU2 trên khung mang – lấy mẫu 500 Hz. "
       "(Nhấp) Hai IMU đi trên hai bus SPI riêng tới miền xử lý: vi điều khiển STM32F407VET6 168 MHz có FPU, chạy "
       "Apache NuttX. "
       "(Nhấp) Miền truyền động: qua UART5 và MAX485, hai động cơ MS3506 dùng chung một bus RS485 bán song công – "
       "đây là gốc của bài toán lập lịch. "
       "(Nhấp) Nguồn 12 V hạ xuống 5 V và 3,3 V; kênh USART qua USB–TTL nối máy tính giám sát, tách khỏi kênh điều "
       "khiển.",

    8: "[0:30] (Nhấp) Mạch điều khiển được thiết kế trên Altium gồm năm khối: vi điều khiển, giao tiếp cảm biến kép, "
       "RS485, chuyển mức logic và nguồn – từ sơ đồ nguyên lý, mạch in hai lớp, mô hình 3D đến mạch đã chế tạo. "
       "(Nhấp) Khung cơ khí hai trục gồm 12 chi tiết: đế sợi carbon trên bốn đệm cao su mang IMU2; trục Yaw mang toàn "
       "bộ khung Pitch; trục Pitch đỡ giá chữ L mang camera và IMU1.",

    9: "[0:30] (Nhấp) Đây là cơ cấu Gimbal hai trục đã chế tạo hoàn chỉnh: động cơ Pitch ở trên, động cơ Yaw ở dưới "
       "tấm quay, giá camera cùng IMU1 trên trục Pitch, IMU2 gắn trên đế carbon có đệm cao su. "
       "(Nhấp) Các thành phần chính: mạch điều khiển STM32F407 tự thiết kế, hai động cơ MS3506 giao tiếp RS485 và "
       "hai cảm biến ICM20948.",

    10: "[0:45] (Nhấp) Phần mềm chạy trên Apache NuttX, tổ chức năm tầng: phần cứng, driver truy cập qua /dev, nhân "
        "với bộ lập lịch SCHED_FIFO, tầng đồng bộ bằng semaphore, mutex và tầng ứng dụng gồm bảy luồng. "
        "(Nhấp) Trong mỗi chu kỳ 2 ms, luồng IMU ưu tiên 120 đọc hai cảm biến rồi phát semaphore đánh thức luồng điều "
        "khiển ưu tiên 115; vòng góc chạy mỗi 10 ms, vòng tốc độ góc mỗi 2 ms trong cùng một luồng. "
        "(Nhấp) Luồng RS485 làm việc theo khe 5 ms, luân phiên Yaw và Pitch; các luồng giám sát, khôi phục IMU2, báo cáo "
        "và LED có ưu tiên thấp hơn. "
        "(Nhấp) Ba quyết định thiết kế: chờ semaphore có hạn 6 ms, chỉ dùng mẫu mới nhất để trễ không tích lũy, và "
        "nâng ưu tiên RS485 lên 116 khi phát khung.",

    11: "[0:40] (Nhấp) Mỗi chu kỳ 2 ms: đọc hai IMU, kiểm tra hợp lệ và tuổi mẫu, kiểm tra độ lệch thời gian hai mẫu "
        "không quá 1,5 ms, hiệu chuẩn tỉ lệ, lệch trục, điểm không, lọc rồi ước lượng tư thế bằng Mahony kết hợp Kalman. "
        "(Nhấp) IMU1 cho góc và tốc độ góc đường ngắm – tín hiệu phản hồi; mất IMU1 thì dừng an toàn. "
        "(Nhấp) IMU2 cho tốc độ góc khung mang và gia tốc góc; vì động cơ Pitch nằm trên khung Yaw nên tốc độ khung được "
        "chiếu lên từng trục theo góc q_y. Mất IMU2 thì chỉ mất khâu bù, vòng kín vẫn làm việc. "
        "(Nhấp) Điểm kỳ dị tại q_p = ±90° được chặn; IMU2 chỉ được dùng sau khi chờ yên, hiệu chuẩn và kiểm chứng.",

    12: "[0:40] (Nhấp) Cấu trúc điều khiển là nối tầng: vòng góc 100 Hz thuần tỉ lệ tạo tốc độ đặt, có giới hạn theo "
        "quãng đường dừng; vòng tốc độ góc 500 Hz là PI có truyền thẳng, khử nhiễu nhanh; cả hai lấy phản hồi từ IMU1. "
        "(Nhấp) Các khâu bổ sung gắn vào vòng trong: lệnh bù từ IMU2 có ngoại suy được cộng vào đầu ra vòng tốc độ, sau "
        "đó qua giới hạn động, xử lý đảo chiều – dừng – tạo dạng, rồi lịch RS485 tới động cơ. "
        "(Nhấp) Hệ số Pitch lớn hơn vì quán tính nhỏ hơn; vòng ngoài giữ thuần P để tránh hai tích phân lồng nhau; lệnh "
        "bù cộng trước khâu giới hạn nên không phá giới hạn an toàn.",

    13: "[0:45] (Nhấp) Khâu ② – bù IMU2: thay vì chờ sai lệch xuất hiện, tốc độ góc khung mang đo bởi IMU2 nhân hệ số k "
        "được cộng thẳng vào lệnh tốc độ. "
        "(Nhấp) Theo (1.30), với k = 0,9 sai lệch xác lập giảm 10 lần mà không phải tăng hệ số vòng kín, nên không lấn "
        "vào dự trữ ổn định; k tăng theo vùng tốc độ từ 0,85 đến 0,98. "
        "(Nhấp) Khâu ③ – lệnh bù đến động cơ trễ khoảng 12 ms. Ngoại suy dùng khai triển Taylor bậc nhất: dùng tiếp "
        "tuyến tại thời điểm hiện tại để dự báo tốc độ khung sau τ_p. "
        "(Nhấp) Lượng ngoại suy bị chặn 90 °/s, gia tốc góc lọc 18 Hz có vùng chết; IMU2 quá 12 ms thì giảm bù về 0 "
        "trong 30 ms.",

    14: "[0:30] (Nhấp) Giới hạn lệnh cố định thấp thì bão hòa khi khung quay nhanh, cao thì lệnh lớn ngay cả khi tĩnh. "
        "(Nhấp) Giải pháp là bốn vùng theo tốc độ khung mang: chậm, thường, nhanh, rất nhanh với giới hạn 110, 135, "
        "165 °/s và hệ số bù tăng dần. "
        "(Nhấp) Ngưỡng ra thấp hơn ngưỡng vào 25–30 % để không chuyển vùng qua lại; giới hạn được nội suy nên lệnh "
        "không nhảy bậc. (Nhấp) Bảng ngưỡng cho cả hai trục.",

    15: "[0:40] (Nhấp) Khi đảo chiều, chương trình dự báo thời điểm tốc độ khung qua không t_0 = −ω_b/α_b; khi t_0 ≤ "
        "20 ms thì mở cửa sổ, giảm biên độ phía cũ, chỉ đổi phía khi dấu mới được xác nhận hai chu kỳ. "
        "(Nhấp) Khi khung dừng đột ngột, hệ đi qua các trạng thái phanh, ổn định, đã dừng; dừng được xác nhận bằng ba "
        "điều kiện trong 220 ms, sau đó bù giảm dần về 0 để camera không vượt ngược. "
        "(Nhấp) Tạo dạng lệnh giới hạn tốc độ biến thiên 18 000 °/s², nới 30 000 °/s² khi đảo chiều, và giới hạn độ "
        "giật để lệnh không nhảy bậc.",

    16: "[0:40] (Nhấp) Hai động cơ chung bus bán song công; nếu lập lịch ưu tiên động, trễ truyền thông trở thành ngẫu "
        "nhiên, trái với giả thiết trễ hằng của khâu ngoại suy. "
        "(Nhấp) Vì vậy em dùng lịch luân phiên: khe cố định 5 ms, khe chẵn Yaw, khe lẻ Pitch. "
        "(Nhấp) Mỗi trục được cập nhật đều 10 ms; phản hồi quá 3 ms ghi lỗi, không thử lại trong khe, 5 lỗi liên tiếp "
        "báo sự cố. "
        "(Nhấp) Hệ có bốn chế độ: khởi tạo, sẵn sàng, điều khiển và dừng an toàn. "
        "(Nhấp) Luồng giám sát ưu tiên 118 theo dõi mất IMU1, tuổi mẫu và lỗi RS485: có sự cố thì dừng động cơ, ghi mã "
        "lỗi; mất IMU2 thì tắt bù và khôi phục nền.",

    17: "[0:40] Để vận hành và thu thập số liệu, em xây dựng phần mềm giám sát trên máy tính bằng Python – PySide6. "
        "(Nhấp) Khu vực kết nối cổng nối tiếp và nút bắt đầu – dừng điều khiển. "
        "(Nhấp) Đặt góc, tốc độ và điều chỉnh nhanh cho từng trục. "
        "(Nhấp) Theo dõi sai số Yaw, Pitch, mô hình 3D và tư thế từ IMU. "
        "(Nhấp) Trạng thái cảm biến, nguồn, nhiệt độ động cơ, bus RS485 và nhịp thời gian thực; tab Động cơ hiển thị "
        "dòng điện và tốc độ. "
        "(Nhấp) Đồ thị thời gian thực, chỉ tiêu chất lượng và nhật ký sự kiện, lỗi. "
        "(Nhấp) Dữ liệu được ghi với chu kỳ 10 ms, là nguồn số liệu thực nghiệm của Phần 4.",

    18: "[0:45] Phần trọng tâm là quá trình hoàn thiện hệ thống. "
        "(Nhấp) Lộ trình đi từ cấu hình ban đầu, qua bảy bước hiệu chỉnh, tới cấu hình hoàn thiện. "
        "(Nhấp) Mỗi bước theo cùng một quy trình: nêu vấn đề, mô phỏng khảo sát các phương án, chọn tham số, áp dụng lên "
        "hệ thật, so sánh trước – sau và lượng hóa mức cải thiện trên cả Yaw và Pitch; cấu hình sau mỗi bước là đối "
        "chứng của bước tiếp theo. "
        "(Nhấp) Mô hình cơ cấu chấp hành là khâu quán tính bậc nhất nối tiếp trễ thuần 12 ms, hằng số thời gian 13 ms "
        "với Yaw, 4 ms với Pitch. "
        "(Nhấp) Mô hình tái tạo đáp ứng bậc thang hệ thật với sai lệch dạng sóng 2,4 % và 2,2 %, đủ tin cậy để khảo sát "
        "xu hướng; quyết định cuối cùng dựa trên số đo hệ thật.",

    19: "[0:50] Bước 1 – hiệu chỉnh cascade. Vấn đề: cần bộ hệ số vừa bám nhanh vừa còn dự trữ lệnh cho các khâu bù. "
        "(Nhấp) Mô phỏng khảo sát K_p^θ = 6; 9,5; 13: tăng lên 9,5 thời gian lên giảm từ 299,6 xuống 162,7 ms; lên 13 "
        "nhanh hơn nhưng lệnh chiếm 76 % giới hạn, không còn dự trữ. "
        "(Nhấp) Chọn K_p^θ = 9,5 cho Yaw, 38 cho Pitch; tích phân vòng tốc độ giảm J_e 85,7 % trong mô phỏng. "
        "(Nhấp) Trên hệ thật, 13 lần thử bậc thang của cả hai trục bám sát nhau. "
        "(Nhấp) Thời gian lên 224,5 và 108,6 ms, độ vọt lố 0,398 và 0,716 %, độ lệch chuẩn khi giữ tĩnh 0,0205° và "
        "0,0068°. "
        "(Nhấp) Đây là cấu hình đối chứng: ở bài thử đảo chiều nhanh 10,1 s, e_max là 20,24° với Yaw và 13,24° với "
        "Pitch.",

    20: "[0:40] Bước 2 – bù IMU2. Vấn đề: phản hồi chỉ tác động khi sai lệch đã xuất hiện. "
        "(Nhấp) Mô phỏng với khung quay 240 °/s: chỉ phản hồi e_rms 20,9°; bù hệ số cố định còn 2,29°; bù theo tốc độ "
        "còn 1,89°. "
        "(Nhấp) Chọn bù theo tốc độ: hệ số k tăng theo vùng tốc độ khung mang. "
        "(Nhấp) Trên hệ thật, cấu hình đối chứng: e_max 20,24° Yaw và 13,24° Pitch. "
        "(Nhấp) Sau bù IMU2 còn 18,15° và 11,89°. "
        "(Nhấp) Tức giảm khoảng 10 % trên cả hai trục; mức cải thiện nhỏ hơn mô phỏng vì ma sát, khe hở và trễ thực; "
        "đánh đổi là thời gian xác lập tăng 5,6 % khi khung chuyển động nhanh.",

    21: "[0:50] Bước 3 – ngoại suy bù trễ. Vấn đề: lệnh bù đến muộn 12 ms. "
        "(Nhấp) Mô phỏng τ_p = 0; 8; 12; 15 ms: e_rms giảm từ 4,06 xuống 2,33°. "
        "(Nhấp) 15 ms tốt nhất trong mô phỏng, nhưng gia tốc góc lấy từ vi phân số có nhiễu và trễ thực thay đổi, nên em "
        "chọn 12 ms – đạt khoảng 80 % mức cải thiện của 15 ms. "
        "(Nhấp) Trên hệ thật, trước bước này e_max là 18,15° và 11,89°. "
        "(Nhấp) Sau ngoại suy còn 14,20° và 9,10°. "
        "(Nhấp) Giảm 21,8 % ở Yaw và 23,5 % ở Pitch – bước đóng góp lớn nhất của toàn bộ quá trình; tỉ lệ bão hòa Yaw "
        "giảm từ 4,3 xuống 2,6 %.",

    22: "[0:40] Bước 4 – giới hạn lệnh động. Vấn đề: với giới hạn cố định 135 °/s, 2,6 % số mẫu Yaw bị bão hòa. "
        "(Nhấp) Mô phỏng ở xung 600 °/s: e_rms từ 9,91° với giới hạn cố định xuống 8,17° với hai mốc và 8,05° với bốn "
        "mốc, giảm 18,8 %. "
        "(Nhấp) Chọn luật bốn mốc 110, 135, 165 °/s. "
        "(Nhấp) Trên hệ thật, so sánh với giới hạn cố định. "
        "(Nhấp) Tỉ lệ bão hòa Yaw giảm từ 2,6 xuống 0,8 %, e_max Yaw giảm 4,8 %, Pitch gần như không đổi. "
        "(Nhấp) Mức cải thiện nhỏ hơn mô phỏng vì giá thử chỉ tạo được khoảng 240 °/s.",

    23: "[0:45] Bước 5 – xử lý đảo chiều và dừng. Vấn đề: khi khung dừng đột ngột, lượng bù và tích phân tồn dư kéo "
        "camera vượt ngược. "
        "(Nhấp) Hai phương án: ngắt bù tức thời hoặc giảm bù dần; cùng các tham số xác nhận dừng và cửa sổ đảo chiều. "
        "(Nhấp) Chọn giảm bù dần: giữ 150 ms, giảm trong 50 ms, xác nhận dừng 220 ms. "
        "(Nhấp) Hệ thật, 12 lần thử với gia tốc hãm 2 300 °/s²: nét đứt là chưa xử lý, nét liền là có xử lý. "
        "(Nhấp) Khi chưa xử lý, camera vượt ngược sau khi khung dừng; sai lệch đỉnh gần như không đổi vì xuất hiện "
        "trong lúc hãm. "
        "(Nhấp) Thời gian phục hồi giảm 52,4 % ở Yaw và 58,7 % ở Pitch; xác nhận dừng đạt 12/12; khi đảo chiều e_max "
        "giảm thêm 4,1 % và 2,8 %.",

    24: "[0:35] Bước 6 – tạo dạng lệnh. Vấn đề: lệnh nhảy 109 °/s trong một chu kỳ khi đảo chiều. "
        "(Nhấp) Mô phỏng bốn phương án giới hạn tốc độ biến thiên. "
        "(Nhấp) Chọn 18 000 °/s², nới 30 000 °/s² khi đảo chiều: năng lượng rung 10–30 Hz còn 23 %, e_max chỉ tăng "
        "2,3 %. "
        "(Nhấp) Trên hệ thật, lệnh trục Yaw quanh một lần đảo chiều. "
        "(Nhấp) Không tạo dạng: một bước nhảy 109 °/s; có tạo dạng: mỗi chu kỳ không quá 60 °/s. "
        "(Nhấp) Bước lệnh lớn nhất giảm 45 %, dòng I_q hiệu dụng giảm 22,3 %; đổi lại e_rms tăng 1,4 % ở Yaw và 1,1 % "
        "ở Pitch – đánh đổi có chủ đích để bảo vệ cơ cấu.",

    25: "[0:40] Bước 7 – lịch RS485. Vấn đề: chế độ ưu tiên Yaw làm trục Pitch cập nhật không đều. "
        "(Nhấp) Mô phỏng 20 000 khe: luân phiên giới hạn khoảng cập nhật lớn nhất của Pitch từ 70 xuống 22 ms. "
        "(Nhấp) Chọn lịch luân phiên khe 5 ms, không thử lại trong khe. "
        "(Nhấp) Trên hệ thật, tải đầy đủ, chế độ ưu tiên Yaw: Pitch có lúc 62,1 ms mới được cập nhật. "
        "(Nhấp) Với luân phiên, cả hai trục quanh 12 ms, lớn nhất 14,1 ms. "
        "(Nhấp) Độ tản mát của Pitch giảm 85 %, e_max Pitch thấp hơn 18,5 %. Đánh đổi: ưu tiên Yaw cho e_rms Yaw thấp "
        "hơn 8,7 %, nhưng em chọn luân phiên vì tính tất định của trễ. Hạn chế: có giao dịch kéo dài 6,00 ms, vượt khe "
        "5 ms.",

    26: "[0:50] Ghép các bước trên cùng bài thử đảo chiều nhanh 10,1 s. "
        "(Nhấp) Bù IMU2 giảm khoảng 10 % trên cả hai trục. "
        "(Nhấp) Ngoại suy 12 ms giảm mạnh nhất, hơn 21 %. "
        "(Nhấp) Giới hạn động và xử lý đảo chiều, dừng giảm tiếp vài phần trăm. "
        "(Nhấp) Tạo dạng lệnh tăng nhẹ 1,6 % – đánh đổi có chủ đích; lịch RS485 giữ nguyên sai lệch nhưng bảo đảm cập "
        "nhật đều. "
        "(Nhấp) Tổng cộng e_max giảm 34,9 % ở Yaw và 32,6 % ở Pitch; e_rms giảm 23,3 % và 22,8 %; tỉ lệ bão hòa từ 6,1 "
        "xuống 0,7 %; phục hồi sau đảo chiều giảm 23,7 %, sau dừng giảm hơn 50 %.",

    27: "[0:35] Đánh giá theo hệ chỉ tiêu. "
        "(Nhấp) Đạt: độ lệch chuẩn khi giữ tĩnh dưới 0,03°, độ vọt lố dưới 1 %, vòng tốc độ góc giữ đúng 2 ms, xác nhận "
        "dừng 12/12. "
        "(Nhấp) Cải thiện rõ ở sai lệch, thời gian phục hồi, độ đều cập nhật và dòng động cơ. "
        "(Nhấp) Các đánh đổi có chủ đích được lượng hóa. "
        "(Nhấp) Chưa đạt: tuyến RS485 chưa tất định hoàn toàn – giao dịch lớn nhất 6,00 ms, khoảng cập nhật lớn nhất "
        "14,1 ms. Phạm vi kiểm chứng giới hạn ở tốc độ đỉnh khoảng 240 °/s.",

    28: "[0:30] Tổng hợp lại, (Nhấp) hệ Gimbal hoàn thiện là kết quả của thiết kế cơ khí, thiết kế mạch, lập trình "
        "NuttX, xử lý hai IMU, điều khiển nối tầng, bù IMU2, bù trễ, xử lý chuyển động nhanh, lịch RS485 và phần mềm "
        "giám sát. "
        "(Nhấp) Tất cả đã được thiết kế, chế tạo, lập trình, mô phỏng và kiểm chứng trên hệ thật.",

    29: "[0:50] (Nhấp) Kết luận: đồ án đã thiết kế, chế tạo và vận hành Gimbal hai trục trên STM32F407 và Apache NuttX; "
        "xây dựng bảy luồng thời gian thực, xử lý hai IMU và sáu khâu điều khiển; mô hình mô phỏng sai lệch dạng sóng "
        "2,4 % và 2,2 %; qua bảy bước hiệu chỉnh, e_max giảm 34,9 % và 32,6 %, phục hồi sau dừng giảm hơn 50 %. "
        "(Nhấp) Hạn chế: RS485 chưa tất định hoàn toàn; thực nghiệm mới tới khoảng 240 °/s; mô hình chưa có ma sát, "
        "khe hở. "
        "(Nhấp) Hướng phát triển: bus riêng hoặc CAN với ngoại suy thích nghi, quét tần số và lọc chắn dải, giá thử "
        "kích thích lớn hơn, tham chiếu phương vị độc lập cho Yaw và điều khiển trực tiếp dòng I_q. Em xin kết thúc "
        "phần trình bày.",

    30: "[0:10] Em xin trân trọng cảm ơn Hội đồng đã lắng nghe và kính mong nhận được câu hỏi, ý kiến đóng góp của "
        "các thầy.",
}
