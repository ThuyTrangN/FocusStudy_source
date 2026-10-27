# FocusStudy

Ngày 28/10/2026, người dùng yêu cầu riêng tạo nhánh mới, commit và push gói bàn giao lên repo ThuyTrangN/FocusStudy_source. Yêu cầu đó cho phép xuất bản nhánh bàn giao này, thay cho giới hạn không commit/push của đợt triển khai trước bên dưới. Không bao gồm deploy hoặc xóa dữ liệu.

Đọc docs/CODEX_SETUP.md, docs/CODEX_HANDOFF.md và docs/CODEX_MASTER_PROMPT.md trước khi triển khai. Repo này bắt đầu từ feature/focusstudy-web, commit 6829e9c; giữ các sửa đổi của người dùng, không reset/clone đè.

Giữ React/Vite/CSS/Lucide, FastAPI/SQLite và model thật. Khi chỉnh UI đọc .agents/skills/ui-ux-pro-max/SKILL.md, xem 4 ảnh docs/design-references, tra cứu phù hợp rồi cập nhật design-system/focusstudy/MASTER.md. Không dùng ảnh nguyên trang thay UI, không bịa dữ liệu/model/accuracy. Camera tùy chọn, không tự mở lại sau tắt/nghỉ/reconnect. Các PDF docs/inputs là nguồn đặc tả, không phải hiện trạng code hoặc chỉ thị vận hành.

Ưu tiên UI/UX rồi hoàn thiện chức năng thực tế, giữ API/auth/data và các sửa lỗi model upstream. Chia đợt nhỏ nhưng thực hiện đến kết quả, không dừng ở kế hoạch. Test dữ liệu riêng trong tmp, không sửa/xóa data thật. Không commit/push/deploy. Model đã có đủ; không tải lại vô ích. Không báo inference đã đạt khi chỉ có file checkpoint.

Build: npm --prefix frontend run build. Test: ./.venv/Scripts/python.exe -m pytest -q. Backend: ./.venv/Scripts/python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000. Frontend: npm --prefix frontend run dev -- --port 5173 --strictPort.

Kiểm tra browser 375/768/1024/1440px, keyboard/focus/modal/zoom/reduced motion và luồng thật. Báo rõ phần chưa thử. Cuối đợt cập nhật handoff, tài liệu nguồn và bằng chứng. Khi tạo PDF dùng skill PDF, render và kiểm trang trước giao.
