# FocusStudy

Web hỗ trợ phiên tự học của Nhóm 5: React/Vite, FastAPI, SQLite và adapter MediaPipe Face Landmarker/L2CS. Chạy trên laptop; tài khoản và phiên học lưu ở backend. Camera là tùy chọn. Không có dữ liệu góc giả thay thế model thiếu.

Tài liệu thuyết trình và bàn giao kỹ thuật toàn diện (đặc tả, chức năng, vai trò file, pipeline, lưu trữ, hiệu chỉnh và lộ trình hoàn thiện): [PDF hiện hành](docs/BAO_CAO_THUYET_TRINH_BAN_MOI.pdf) · [bản Markdown nguồn](docs/BAO_CAO_THUYET_TRINH.md).

Để tự tạo lại PDF sau khi sửa Markdown, cài dependency tài liệu một lần bằng `python -m pip install -r requirements-docs.txt`, rồi chạy `python update_doc.py` từ thư mục dự án. Nếu PDF hiện hành đang được mở và Windows khóa file, script sẽ thử ghi bản dự phòng `docs/BAO_CAO_THUYET_TRINH.pdf`. Dependency này không cần cho ứng dụng web.

## Chạy nhanh trên Windows

Cài Python 3.11 và Node.js 20 trở lên. Giải nén dự án, mở PowerShell ngay trong thư mục `focusstudy` (nơi có file này). Thực hiện từng dòng:

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
