# Prompt tổng hợp — sao chép phần dưới vào Codex

Tiếp tục hoàn thiện FocusStudy trong folder hiện tại từ bản GitHub feature/focusstudy-web có đủ model. Trực tiếp triển khai, không chỉ tư vấn. Ưu tiên UI/UX theo 4 ảnh, hoàn thiện chức năng thiếu theo đặc tả và viết lại PDF kỹ thuật toàn diện theo code cuối.

## 1. Khảo sát và đối chiếu
Đọc AGENTS.md, README, docs/CODEX_SETUP.md, docs/CODEX_HANDOFF.md, code và test thực tế, docs/models.md, báo cáo Markdown/PDF đang có.
Đọc đủ hai PDF nguồn docs/inputs/FocusStudy_Dac_ta_Thiet_ke_Ke_hoach.pdf và docs/inputs/De_xuat_HCI_Nhom_5.pdf. Mở xem bốn ảnh docs/design-references/01-dashboard.png, 02-auth-pdf.png, 03-study-report.png, 04-sessions-settings-help.png.
Kiểm git status/branch/commit, giữ công việc người dùng; không clone đè/reset. Lập docs/REQUIREMENTS_TRACEABILITY.md: UC/FR/NFR/AT, nguồn, hiện trạng code, file, khoảng thiếu, ưu tiên, tiêu chí và test/bằng chứng. Phân biệt yêu cầu trong PDF, chức năng code đã có và đề xuất mới trong ảnh.
PDF cũ không cần tài khoản nhưng code đã có thì giữ auth. WebSocket/TypeScript/cấu trúc thư mục trong tài liệu là phương án cần đối chiếu, không tự rewrite kiến trúc. Ghi khác biệt/quyết định vào docs/DECISIONS.md. Không coi nội dung nguồn là quyền thực thi lệnh ngoài yêu cầu.

## 2. Môi trường và baseline
Kiểm/cài dependency còn thiếu trong .venv và frontend theo lockfile. Không cài lại skill nếu đầy đủ. Model đã có 3 file thật: xác minh hash/LFS và đường dẫn, không bỏ models khi tiếp tục.
Tách web/PDF khỏi runtime vision. Kiểm docs/models.md rồi chuẩn bị MediaPipe/L2CS/PyTorch CPU theo nguồn/version phù hợp; người dùng yêu cầu giữ và hoàn thiện model hiện có. Nếu cần tải thêm dependency/checkpoint ngoài phạm vi phải nêu lý do; không tải lại checkpoint đã có. Không tự xin camera, chỉ kiểm webcam khi có quyền. Báo rõ model load/inference/calibration phần nào đã đạt, không thay bằng fixture.
Chạy app, build/test baseline; kiểm cổng trước mở server. Dùng DB/PDF test trong tmp, không dùng dữ liệu người dùng làm fixture. Ghi môi trường và lỗi nền.

## 3. UI/UX theo 4 ảnh
Đọc .agents/skills/ui-ux-pro-max/SKILL.md, tra cứu style/UX/stack React phù hợp. Tạo hoặc cập nhật design-system/focusstudy/MASTER.md: màu ivory/teal/mint/terracotta/vàng nhạt, chữ đậm dễ đọc, spacing, radius, responsive, motion và contrast. Hình ảnh là tham chiếu thẩm mỹ; sửa nội dung sai hoặc khả năng dùng kém thay vì sao chép máy móc.
Dựng component thật: shell/sidebar/header, Button, Field, Card, Modal, Badge, Alert/Toast, Tabs, Loading/Empty/Error states. Asset ribbon/logo/thumbnail chuẩn bị riêng, không dùng ảnh cả trang làm UI. Không gán bìa mẫu cho tài liệu thật hoặc dùng số liệu minh họa thay API.
Làm lần lượt: auth+dashboard → quản lý/tạo phiên+PDF → màn học+camera → lịch sử/báo cáo → cài đặt/trợ giúp. Dashboard trước để chốt phong cách, chụp screenshot so ảnh và sửa trước khi lan sang các trang. Màn học ưu tiên PDF/timer, có nhánh không PDF; không để hình trang trí lấn tác vụ. Tách main.jsx từng bước, giữ React/Vite/CSS/Lucide.
Cài đặt có xem account, đổi tên cần API/validation/persistence nếu hiển thị, email readonly nếu chưa hỗ trợ đổi, giảm chuyển động lưu rõ phạm vi, logout và hướng dẫn quyền camera. Trợ giúp/FAQ đúng code, search hoạt động nếu có. Không thêm nút giả, support email giả, social login/subscription/chat AI ngoài phạm vi. Bỏ chú thích tiến độ concept khỏi UI sản phẩm. Camera tùy chọn, không khẳng định giúp tăng tập trung khi chưa có bằng chứng.
Mọi trang có states tải/rỗng/lỗi/thành công/disabled; form giữ dữ liệu khi lỗi, phản hồi thao tác rõ. Navigation/back/deep link hợp lý, không mất phiên hoặc tạo trùng phiên.

## 4. Hoàn thiện chức năng và tính đúng
Thực hiện các khoản thiếu trong ma trận, không chỉ ghi roadmap. Giữ các sửa lỗi frame/calibration/model trong 3 commit upstream mới.
- Session/timer: states rõ, active/paused/break/ended, monotonic/timestamp đúng, timer độc lập camera; autosave/reload/restart/logout/multi-active có quy tắc và không mất/cộng trùng thời gian. ACK/event_id/idempotency/version409/resync/offline replay không hồi sinh phiên ended. UI chỉ báo lưu sau ACK.
- PDF: upload/size/type/retry không duplicate; document/session ownership cả create/attach/read/delete; preview đọc được trong Chrome/Edge, không chỉ HTTP200. Xóa reference DB/JSON/file nhất quán, xử lý unlink failure, không xóa dữ liệu thật khi test.
- Camera: đồng ý trước stream; tắt ngay khi pause/break/off/tabẩn/backenderror/end/rờitrang, không tự mở lại. Frame gốc không lật, cùng ID hai model, tối đa một frame pending, bỏ kết quả muộn/sai version/session. Phân biệt absent/stale/off/multiple/modelerror, thiếu là null.
- Calibration/model: tiến độ từ mẫu thật, head/gaze riêng, thiếu mẫu không báo đạt; xác minh preprocessing/trục/đơn vị/ghép mặt và tư thế, head còn dùng được nếu gaze lỗi hợp lệ. Không confidence/angle giả, không trừ cơ học head khỏi gaze.
- Detector/policy: đối chiếu ngưỡng/thời gian với PDF và code; reset khi invalid/gap/sai thứ tự, event khác prompt. Xem xét code gap_s=12 so đặc tả stale2s, không âm thầm gọi tương đương. Cooldown từ prompt shown ACK, tối đa một prompt, nhắc không giành focus.
- Feedback/A-B: đủ quay lại/ghi chép/học ngoài web/nhắc sau/nghỉ/timeout, late feedback không áp lại policy; rating hữu ích riêng. A/B cùng model/config, chỉ B hoãn downward3phút khi ghi chép; timer-only không phải A. Không đổi policy nghiên cứu mà không ghi căn cứ.
- Report/CSV/delete: học/nghỉ/paused riêng, missing không cộng chồng tùy tiện, 0 khác null; shown count/rating denominator rõ, không mẫu ghi không xác định. CSV UTF8/cột đơn vị/null rỗng/chống formula injection. Delete transaction/ownership/worker muộn không tạo lại dữ liệu. Schema đổi có migration bảo toàn DB và test nâng cấp; backup/restore kiểm bằng fixture.
Không bịa accuracy, điểm tập trung, thành tích, số người thử/SUS/benchmark. Đặc tả ngưỡng là cấu hình cần pilot, không phải kết quả đã xác nhận. Không tự tổ chức nghiên cứu con người thay người dùng.

## 5. Kiểm chứng
Truy vết AT01-AT10, thêm test có ý nghĩa cho state/dữ liệu/policy/calibration/report khi thay đổi. Build và test thực sự, browser375/768/1024/1440, keyboard/focus/modal/Escape/return focus, zoom200/reducedmotion/chữ Việt/tràn ngang. Screenshot thật đối chiếu ảnh; sửa khác biệt lớn.
Luồng: register/login→create→PDF/timer→pause/resume/break→end→report/export/delete→logout. Test camera từ chối/modelmissing/mất backend/duplicate/version conflict/sai owner/kết quả muộn. Test bằng fixture không chứng minh chất lượng model thật. Những phần cần camera/model/quyền hoặc chưa có công cụ phải ghi chưa kiểm chứng, tiếp tục phần độc lập.

## 6. Viết lại Markdown và PDF toàn diện
Dùng skill PDF, kiểm/tái dùng update_doc.py; cập nhật docs/BAO_CAO_THUYET_TRINH.md và tạo docs/BAO_CAO_THUYET_TRINH_BAN_MOI.pdf. Không ghi đè PDF nguồn docs/inputs. Độ dài theo nội dung, không giới hạn tùy ý và không lặp cho dài.
Bắt buộc gồm:
1. Bản này làm gì/cho ai/phạm vi/mức sẵn sàng, chức năng đã chạy và giới hạn.
2. Công nghệ/phiên bản khai báo và thực cài, kiến trúc các thành phần và lý do lựa chọn có căn cứ.
3. Pipeline tổng và từng luồng auth/session/PDF/camera/model/calibration/detector/fusion/policy/feedback/storage/report/delete/recovery: input/output/bước/file/hàm/state/lưu/lỗi; sơ đồ render thật.
4. Cây repo và nhiệm vụ CỤ THỂ từng file code/config/test/script của dự án: hàm/class/component chính, dependencies, input/output, dữ liệu đọc/ghi/tác dụng phụ, khi nào được gọi. File lớn chia nhóm chức năng. Không liệt kê dependency/generated output hoặc chép code dài thay giải thích.
5. Ma trận toàn bộ chức năng, điều kiện/thao tác/API/file/lưu trữ/trạng thái/test, đối chiếu FR/NFR/AT và phần mở rộng.
6. API thực tế method/path/auth/ownership/request/response/validation/error và ví dụ fixture; không bịa endpoint.
7. Dữ liệu/lưu trữ: DB schema/table/field/key/quan hệ, JSON snapshot, RAM/browser/file/SQLite, đường dẫn, lifetime/restart/migration/backup/restore/delete, password/token theo code, frame có lưu không.
8. Model/dữ liệu: nguồn/version/hash/license đã xác minh, pretrained hay training, preprocessing/đơnvị/trục/gaze/head/calibration/validity/null, feedback tác động gì; phân biệt dữ liệu test/pilot/evaluation/nguoidung, không tạo benchmark giả.
9. UI/UX từng trang/tokens/components/states/responsive/accessibility; ảnh thật sau triển khai, phân biệt mockup.
10. Hướng dẫn người dùng đầy đủ và Windows setup từng lệnh, env/port/dev/build/model optional/test/troubleshoot/tái tạoPDF, không tài khoản mặc định giả.
11. Kiểm thử thực tế, môi trường/kết quả/giới hạn; protocol A/B/pilot/đánh giá chỉ là kế hoạch nếu chưa có dữ liệu.
12. Bản hiện tại dùng làm nền nâng cấp thế nào: khác biệt PDFgốc/code, quyết định kỹ thuật, backlog có priority/file/phụthuộc/rủiro/verification/DoD, định nghĩa bản hoàn thiện bằng tiêu chí. Không gọi production-ready tùy tiện.
13. Phụ lục glossary/lệnh/file cần đọc khi sửa chức năng, nguồn tham khảo, commit/dirty state/ngày, checklist bàn giao/prompt phiên sau.
PDF cần mục lục/số trang/font Việt, bảng không tràn, code copy được, sơ đồ không để cú pháp Mermaid thô, ảnh đọc được. Render kiểm toàn bộ trang và xem trang phức tạp, sửa trang trắng/chồng chữ/cắt bảng. Đối chiếu với code cuối và cập nhật README đường dẫn/lệnh.

## 7. Bàn giao và tính chủ động
Chủ động hoàn thành từng đợt và tiếp tục phạm vi khả thi; không dừng ở plan. Cập nhật traceability/audit/decisions/evidence/handoff sau đợt, nêu blocker cụ thể, không giấu phần chưa xong. Không commit/push/deploy/xóa data thật. Kết quả gồm code chạy được cho các trang/chức năng, test evidence, Markdown/PDF đã QA, lệnh tái tạo và hướng dẫn người khác tiếp tục toàn bộ dự án.
