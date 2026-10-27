# FocusStudy

Web hỗ trợ phiên tự học của Nhóm 5: React/Vite, FastAPI, SQLite và adapter MediaPipe Face Landmarker/L2CS. Chạy trên laptop; tài khoản và phiên học lưu ở backend. Camera là tùy chọn. Không có dữ liệu góc giả thay thế model thiếu.

## Nhánh bàn giao đầy đủ

Nhánh `feature/focusstudy-dashboard-handoff-20261028` tập hợp code ứng dụng, cải tiến dashboard/PDF/session, test, tài liệu thiết kế, skill UI UX Pro Max và báo cáo bàn giao 41 trang. Phát triển tiếp từ `6829e9c`, giữ nguyên `vision/adapters.py` và ba checkpoint upstream qua Git LFS. Đây là prototype có giới hạn đã ghi nhận, chưa phải phiên bản đã kiểm chứng độ chính xác model trên người thật.

Clone đúng nhánh trên máy mới:

```powershell
git lfs install
git clone --branch feature/focusstudy-dashboard-handoff-20261028 --single-branch https://github.com/ThuyTrangN/FocusStudy_source.git
Set-Location FocusStudy_source
git lfs pull
git lfs fsck
```

Tiếp tục các bước cài và chạy bên dưới. File ZIP từ GitHub có thể không chứa nội dung checkpoint LFS; nên clone bằng Git và kiểm hash theo `docs/models.md`. Skill đã nằm trong `.agents/skills/ui-ux-pro-max`, gồm cả thư mục dữ liệu tra cứu; không cần cài đè để dùng bản bàn giao.

Không thêm `.venv`, `node_modules`, bản build, database, `.env`, uploads mới hoặc file tạm của máy này vào nhánh. Các PDF trong `data/documents` đã được theo dõi từ upstream được giữ nguyên; `.gitignore` không tự bỏ theo dõi các file cũ. Tài liệu/ảnh tham chiếu trong `docs/inputs`, `docs/design-references` và bằng chứng trong `docs/evidence` thuộc gói bàn giao.

Đọc nhanh: chương 1 của báo cáo để hiểu hiện trạng, chương 4 để hiểu hai model và cách tính góc, chương 9 hoặc [bản chia việc](docs/CONG_VIEC_TIEP_THEO.md) để nhận việc tiếp theo. Những câu “không commit/push” trong bản báo cáo và nhật ký trước đây mô tả phạm vi đợt triển khai cũ; việc xuất bản nhánh này đã được người dùng yêu cầu riêng sau đó.

Tài liệu thuyết trình và bàn giao kỹ thuật toàn diện (đặc tả, chức năng, vai trò file, pipeline, lưu trữ, hiệu chỉnh và lộ trình hoàn thiện): [PDF hiện hành](docs/BAO_CAO_THUYET_TRINH_BAN_MOI.pdf) · [bản Markdown nguồn](docs/BAO_CAO_THUYET_TRINH.md).

Để tự tạo lại PDF sau khi sửa Markdown, cài dependency tài liệu một lần bằng `python -m pip install -r requirements-docs.txt`, rồi chạy `python update_doc.py` từ thư mục dự án. Nếu PDF hiện hành đang được mở và Windows khóa file, script sẽ thử ghi bản dự phòng `docs/BAO_CAO_THUYET_TRINH.pdf`. Dependency này không cần cho ứng dụng web.

## Bản cập nhật 28/10/2026

Nền commit `6829e9c`, giữ model/frame upstream. Có dashboard theo ảnh, shared components, PDF.js đọc trang thật, quản lý PDF/ownership/dedup, đổi tên tài khoản, FAQ search, motion, ACK/version và CSV có cột đơn vị/null rỗng/formula defense. Không dùng số liệu minh họa thay API.

- [Ma trận UC/FR/NFR/AT](docs/REQUIREMENTS_TRACEABILITY.md), [quyết định](docs/DECISIONS.md), [kiểm thử](docs/KET_QUA_KIEM_TRA.md), [handoff](docs/CODEX_HANDOFF.md).
- `pytest`: 27 passed/1 warning; build đạt. Browser đã chạy timer/PDF có chữ/settings/help/modal, dashboard375/768/1024/1440. Evidence trong `docs/evidence/`.
- MediaPipe và L2CS đã nạp CPU; synthetic smoke thật ở `docs/evidence/model-smoke.json`. Chưa webcam/calibration người thật hoặc accuracy. MediaPipe gửi metrics sử dụng theo privacy notice; chưa network audit độc lập.
- Chưa hoàn thiện offline interval replay; backend có checkpoint 5 giây/shutdown, nhưng crash có thể mất thời gian sau snapshot cuối. Đây là prototype, chưa đủ nghiệm thu toàn bộ.
- Bản kiểm thử dùng `http://127.0.0.1:18000`, DB/PDF riêng ở `tmp/browser`. Cổng8000 có tiến trình khác được giữ nguyên. Không đưa data test vào data thật.

Tái tạo tài liệu nguồn/phụ lục và PDF:

```powershell
.\.venv\Scripts\python.exe scripts/build_reference.py
.\.venv\Scripts\python.exe update_doc.py
```

Chạy `build_reference.py` cần model-smoke/evidence đã có, không mở webcam hoặc đọc DB người dùng. Sau sinh PDF phải render/kiểm trang; xem `docs/evidence/PDF_QA.md`.

## Chạy nhanh trên Windows

Cài Python 3.11 và Node.js 22.13 trở lên (PDF.js yêu cầu), máy kiểm thử dùng Node 24.22.1. Giải nén dự án, mở PowerShell ngay trong thư mục `focusstudy` (nơi có file này). Thực hiện từng dòng:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm ci
npm run build
cd ..
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000 và chọn **Đăng ký** để tạo tài khoản của bạn. Không có tài khoản/mật khẩu mặc định. Giữ terminal chạy server; Ctrl+C để dừng. Không cần kích hoạt venv hoặc đổi ExecutionPolicy.

Lần sau chỉ chạy dòng `uvicorn` cuối cùng từ thư mục dự án. Khi sửa frontend, chạy lại `npm run build` rồi khởi động lại backend.

## Linux và macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cd frontend
npm ci
npm run build
cd ..
.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

## Dùng bản web

1. Đăng ký/đăng nhập tài khoản cá nhân.
2. Quản lý tài liệu học tập: Vào **Kho tài liệu PDF** để đẩy tài liệu PDF từ máy tính lên (giáo trình, slide bài giảng, đề ôn tập...), hoặc kéo thả trực tiếp khi tạo phiên học.
3. Tạo mục tiêu, thời lượng, chọn chế độ (đọc tài liệu/làm bài/xem) và gắn tài liệu PDF muốn học cùng.
4. Bắt đầu phiên: Giao diện học cung cấp khung đọc tài liệu PDF song song với Timer và Webcam, hỗ trợ đọc trực tiếp trên web mà không cần chuyển tab (tránh việc camera bị ngắt do ẩn tab).
5. Bật camera sau khi đọc giải thích (nếu muốn). Frame được gửi tới backend trên máy này; không lưu ảnh/video mặc định.
6. Cài model theo `docs/models.md` để có tín hiệu thật. Xem `/api/health` hoặc màn hình trạng thái để kiểm tra nhánh nào sẵn sàng.
7. Hiệu chỉnh đầu khi nhìn giữa màn hình; hiệu chỉnh gaze bằng các mục tiêu. Kiểm tra chiều góc và vùng tham chiếu trước thử nghiệm chính.
8. Dùng khu vực debug/gán nhãn để ghi hành vi theo kịch bản; nhãn không phải kết luận tập trung.
9. Kết thúc, xem báo cáo, xuất CSV hoặc xóa phiên. Mỗi tài khoản chỉ truy cập dữ liệu của mình.

## Chế độ A và B

Cả A/B dùng cùng model, detector và cooldown. Ở B, “Đang ghi chép” hoãn nhóm nhìn xuống 3 phút; ở A phản hồi này chỉ được ghi nhận. Nhắc sau/nghỉ/tắt/học ngoài web vẫn hoạt động trong cả hai. Không dùng timer-only làm A của protocol này.

## Cấu trúc và người sửa chính

| Thư mục | Nội dung | Người phụ trách đề xuất |
|---|---|---|
| frontend | UI, camera, timer và gọi API | Trang |
| backend | Auth, phiên, policy, SQLite, báo cáo | Huy |
| vision | Adapter head và gaze thật | Linh và Kha |
| tests | Kiểm thử API và logic bằng dữ liệu kiểm thử | Cả nhóm |
| docs | Cài model, kịch bản thu và giới hạn | Cả nhóm |
| scripts | Lệnh khởi động | Huy |

`data/` được tạo khi chạy, không đưa lên Git. Không commit `.venv`, `node_modules`, file checkpoint, ảnh/video hoặc database người dùng.

## Môi trường và lưu trữ

Mặc định database ở `data/focusstudy.sqlite3`. Biến môi trường tham khảo `.env.example`; file `.env` không tự được nạp. Trong PowerShell dùng `$env:TEN_BIEN = "gia_tri"` trước lệnh chạy server. Mỗi lần khởi động chỉ dùng **một worker**, vì trạng thái xử lý và khóa model được quản lý trong một process.

Backend bind `127.0.0.1` phục vụ demo cá nhân. Đưa lên Internet cần HTTPS, cookie Secure, quản trị secret, giới hạn truy cập và vận hành riêng; bản này chưa phải dịch vụ production. Không đổi sang `0.0.0.0` chỉ để thử camera từ điện thoại: trình duyệt cần secure context để cấp quyền camera.

## Kiểm tra

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Các test dùng tín hiệu kiểm thử để xác nhận code; không phải số liệu accuracy model. Xem `docs/PROTOCOL_THU_TIN_HIEU.md` cho thử webcam và `docs/GIOI_HAN.md` cho phạm vi kiểm chứng.


## Báo cáo chi tiết và việc nhóm làm tiếp

[Báo cáo Markdown](docs/BAO_CAO_THUYET_TRINH.md) và [bản PDF](docs/BAO_CAO_THUYET_TRINH_BAN_MOI.pdf) đã mở rộng ngày 28/10/2026. Chương 1 mô tả hiện trạng; chương 4 giải thích hai model, công thức SVD/Euler/softmax, mốc head và vùng gaze; chương 9 có W01-W10, phân công đề xuất và tiêu chí hoàn thành. Bản đọc riêng: [Công việc tiếp theo](docs/CONG_VIEC_TIEP_THEO.md).

Ưu tiên nhóm: xác minh trục/dấu/đơn vị và mapping tensor L2CS; kiểm calibration trên điểm mới; thiết kế và replay fusion/policy; hoàn thiện offline/time recovery; pilot rồi đóng băng cấu hình trước đánh giá cuối. Các ngưỡng hiện tại là giả thuyết chưa kiểm chứng, không phải accuracy hoặc nhãn chuẩn do model trả sẵn.

Tái tạo tài liệu bằng môi trường dự án (ReportLab và Pillow):

```powershell
.\.venv\Scripts\python.exe scripts/report_guide_figures.py
.\.venv\Scripts\python.exe scripts/build_reference.py
.\.venv\Scripts\python.exe update_doc.py
```

Sau khi tạo phải render và kiểm PDF theo `docs/evidence/PDF_QA.md`. Sơ đồ góc/vùng gaze dùng số minh họa, không phải dữ liệu thử nghiệm. Đợt bổ sung này chỉ sửa tài liệu/công cụ sinh tài liệu, không sửa logic ứng dụng.
