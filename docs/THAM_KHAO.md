# Nguồn tham khảo và phạm vi sử dụng

- Bản đề xuất FocusStudy của Nhóm 5: nguồn yêu cầu chức năng, quy tắc, phân công, protocol.
- https://github.com/NguyenTuan-UET/Hmi-VoiceController-Website : đã đọc README, package.json và cấu trúc src. Dự án React/Vite điều khiển YouTube bằng giọng nói. Tham khảo cách tách component theo màn hình, service tương tác và trang hướng dẫn. Không tái sử dụng chức năng YouTube/giọng nói, không dùng repo này làm bằng chứng có backend/auth.
- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill : hướng thiết kế giao diện nhất quán, khoảng cách, contrast, keyboard focus, responsive và trạng thái tương tác. Chi tiết thực tế áp dụng xem tài liệu frontend.

Mã FocusStudy được triển khai riêng cho yêu cầu của nhóm. Model/checkpoint bên thứ ba có giấy phép và điều kiện sử dụng riêng; đọc upstream trước khi phân phối lại checkpoint.

## Nguồn kiểm tra lượt 28/10/2026

- MediaPipe Face Landmarker: https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker ; output matrices/landmarks và num_faces, không là phép đo tập trung.
- MediaPipe Tasks privacy notice: https://developers.google.com/edge/mediapipe/solutions/tasks#mediapipe_tasks_privacy_notice ; usage/performance metrics và input processing. Có log clearcut attempt trong smoke cục bộ, chưa network audit.
- PDF.js package đã cài6.4.299, licenseApache2, enginesNode>=22.13; API/types package dùng cho PdfReader.jsx. https://mozilla.github.io/pdf.js/
- L2CS/fork/checkpoint: xem models.md; preprocessing đọc pipeline.py/utils.py package đã cài. License noticeHF truy cập mới chưa thành công, không xác nhận thương mại.
