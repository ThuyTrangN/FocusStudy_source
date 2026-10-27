# PDF QA - báo cáo mở rộng 28/10/2026

Output: `docs/BAO_CAO_THUYET_TRINH_BAN_MOI.pdf`, 41 trang A4.

SHA256: `94d472a8ea0f095affa302f4756765b7dab30ab0c9015a26726cfff3048734ac`.

- Mở rộng tổng quan, cẩm nang hai model và W01-W10; giữ phụ lục kiến trúc/API/file/ma trận. Có 4 sơ đồ giải thích mới, 3 sơ đồ kỹ thuật và ảnh browser từ đợt trước. Các số trong hình vùng gaze là giả định, không phải kết quả nghiên cứu.
- Tạo bằng ReportLab 4.5.1, Arial hỗ trợ tiếng Việt; tăng cỡ chữ, khoảng dòng và độ rõ thứ bậc. Mục lục/bookmark lấy chương và mục có số. Bảng có header lặp khi qua trang.
- Render toàn bộ 41 trang bằng Poppler pdftoppm 85 dpi vào `tmp/pdfs/final-guide-*.png`. Đã xem cả 6 contact sheets `guide-pdf-contact-1.png` đến `guide-pdf-contact-6.png`, xem riêng trang 13-16, 25, 27, 30, 32 qua các vòng QA. Sửa ký tự tập hợp không được font của hình hỗ trợ thành chữ "trong" rồi tạo/render lại.
- Kiểm pdfplumber/pypdf: không trang rỗng, 0 ký tự ngoài pagebox, 0 ký tự ô vuông đen, 0 marker HTML/TOC thô. Chi tiết `pdf-check.json`. Kiểm hình không thấy bảng/chữ chồng hoặc cắt; công thức, bảng model và sơ đồ đọc được. Trang 1 là bìa có hướng dẫn đọc, 2-3 mục lục, 41 manifest model riêng.
- Hash 13 file runtime/test/requirements so với đầu đợt giữ nguyên, 3 checkpoint khớp manifest, 2 PDF nguồn khớp bản người dùng cung cấp. Chi tiết `report-guide-check.json`. Không chạy lại test ứng dụng vì chỉ sửa tài liệu/công cụ tài liệu.
- 27 test đạt và synthetic inference smoke là bằng chứng từ đợt trước. Không có kết quả webcam/người thật, accuracy, pilot hoặc SUS mới. PDF chưa tagged; đây không phải chứng nhận accessibility hoặc độ chính xác khoa học.

Tái tạo bằng môi trường repo đã cài ReportLab/Pillow: chạy `scripts/report_guide_figures.py`, `scripts/build_reference.py`, rồi `update_doc.py`. Sau khi tạo lại phải render/kiểm lại; hash PDF thay đổi do metadata thời gian tạo. Không đánh đồng tạo PDF thành công với QA. Hai PDF nguồn không bị ghi đè. Bản trước mở rộng được giữ tại `tmp/report-guide-backup/` của workspace hiện tại.
