# Kết quả kiểm tra - 28/10/2026

## Môi trường và baseline

Nền6829e9c, feature/focusstudy-web; dirty có sẵn AGENTS/docs/skill được giữ. Python3.12.14, Node24.22.1; phiên bản đầy đủ ở evidence/environment.json. Git safe.directory chỉ dùng -c theo lệnh, không thay global. Build cần chạy ngoài hạn chế đọc thư mục cha esbuild của sandbox. Không commit/push/deploy.

Baseline13passed1warning; build Vite6.4.5 đạt. Runtime vision ban đầu thiếu, được cài riêng .venv CPU, không tải lại3checkpoint. Cổng8000 đã dùng nên giữ process đó, backendtest18000/DB tmp/browser/documents riêng.

## Kết quả cuối

- Pytest27passed1warning (Starlette/httpx deprecation). Upstream calibration/bbox/model/frame tests được giữ; chỉ PDFfixture đổi thành PDF có cấu trúc. Regression profile/PDFownership/dedup/unlink/references/singleactive/recovery/timerunion/null/workerdelete/migrationbackup/createid/CSVformula.
- npm build đạt; PDF.js lớn được lazyload khỏi bundle auth/dashboard; không thay stack React/Vite/CSS/Lucide. Kết quả/log cuối xem evidence/build.txt.
- Browser IAB Chromium: registertest/login, create/timer/pause/resume/break/end/report; filechooserupload PDF1trang thật, PDF.js render thấy chữ; settings đổi tên ACK/motion; FAQ searchcamera; modal ShiftTab/Escape/return focus. Không suy browserChrome/Edge độc lập.
- Responsive dashboard375/768/1024/1440: DOMscrollWidth=clientWidth, ảnh đúng viewport trong evidence/dashboard-*.png và responsive.json; màn phiên375 kiểm không tràn ngang. Ảnh screenshot có thể loại thanh cuộn15px, JSON ghi CSSviewport.
- CSVAPI200 UTF8BOM; phẳng nullblank/deg/seconds/formulaescape regression. Browser download event timeout, chưa xác nhận file downloadUI. DeleteUI chưa chạy, APIdelete fixture/worker race đạt.
- Model CPUload head/gaze availabletrue;3hash/bytes model-smoke.json. Adapterblank absent, mạng gaze forward crop tổng hợp finite. Đây là inference kỹ thuật trên input synthetic, không webcam hoặc accuracy.
- Report Markdown/PDF có TOC/bookmark/sốtrang/fontViệt/bảng/3diagramPNG/ảnhbrowser; render mọi trang và QA theo evidence/PDF_QA.md. NguồnPDFinput giữ nguyên.

## Chưa kiểm/chưa hoàn thiện

Webcam/calibrationngười/dấutrục/heldout/đa mặt/kính/ánhsáng/timing; offline interval replay chính xác; checkpoint5s/shutdown đã có; event audit trên người/legacy provenance; reconciliation fileDB khi crash; fullzoom200/screenreader/PDFtextlayer; Chrome/Edge thật; CSVdownloadUI. MediaPipe clearcut attempt có thật và privacy notice nói SDK gửi metrics; chưa networkaudit độc lập. Không coi fixture hoặc checkpoint là hoàn tất model/nghiên cứu.

Bổ sung regression: annotation bị xóa trong khi đọc requestbody trả404; backend checkpoint không browser và manifest; detectorstart/end giữ ID/duration9s khi gap, độc lập prompt0. Kết quả cuối27passed; log thật evidence/pytest-final.txt.

Live API sau restart cuối: request_id dedup cùngID, khôngGET6s vẫn có5.547s active trong snapshot SQLite từ checkpoint nền; manifest có, report detector_events200, CSV17cột/BOM200. Xem evidence/api-smoke.json. Git LFS fsckOK, vision/adapters.py khôngdiff.


## Bổ sung báo cáo - không thay đổi ứng dụng (28/10/2026)

Báo cáo hiện có 41 trang, thêm tổng quan, công thức head/gaze, mốc tham chiếu, sổ tay ngưỡng, cách thu thử, 10 gói việc nhóm và 4 hình minh họa. Đã render/kiểm toàn bộ trang và kiểm text/pagebox; xem `evidence/PDF_QA.md`, `pdf-check.json` và `report-guide-check.json`.

SHA 13 file runtime/test/requirements đầu-cuối đợt trùng nhau; 3 checkpoint khớp manifest; 2 PDF nguồn khớp bản người dùng cung cấp. Không chạy lại pytest/build vì không sửa ứng dụng; 27 passed và model smoke là bằng chứng từ đợt trước, không phải kiểm chứng góc/calibration người thật. Cần audit mapping tensor L2CS và head Euler/dấu, cùng giới hạn gaze dưới 15 độ so với detector head_turn trên 25 độ trước khi tuyên bố fusion đã đúng.
