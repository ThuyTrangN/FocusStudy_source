# Kiểm tra bản bàn giao

- npm run build: thành công với Node.js tại `C:\Program Files\nodejs`.
- pytest -q: 9 passed; một cảnh báo deprecation từ Starlette/httpx.
- Đã khởi động lại backend bằng Python 3.12.2 trên `127.0.0.1:8000`.
- Trang `/` trả HTTP 200; `/api/health` trả `ok: true`, `mode: real-inference-only`, cả hai model đều `available: true`.
- MediaPipe Face Landmarker và L2CS-Net Gaze360 đã nạp thành công trên CPU (`head.available: true`, `gaze.available: true`).
- SHA-256 checkpoint safetensors khớp mã LFS của model card; adapter smoke-test bằng frame trống trả `face_status=absent`, không có góc giả.
- API trả tiến độ mẫu và thời gian; gaze yêu cầu ít nhất 3 mẫu hợp lệ tại mỗi mục tiêu giữa/trái/phải/trên/dưới. Test xác nhận profile hoàn tất và được lưu vào phiên/báo cáo.
- Frontend xử lý frame 409 do state thay đổi mà không tự đóng camera nếu phiên vẫn active; build có chỉ dẫn khi chưa chọn phiên và hiển thị tiến độ calibration.
- Kiểm tra API xác nhận mốc hành vi được lưu và xuất hiện trong báo cáo phiên.
- Chưa xác nhận camera thật, calibration từ webcam, dấu/đơn vị góc hoặc accuracy model trên người dùng.
- Frontend build mới trong `frontend/dist` được backend phục vụ.
- Cần tiếp tục kiểm tra webcam thật, hiệu chỉnh từ camera, dấu/đơn vị góc và độ trễ theo `docs/models.md` và protocol.
- Báo cáo thuyết trình/bàn giao PDF được tạo từ `docs/BAO_CAO_THUYET_TRINH.md` bằng `python update_doc.py`; bản mới hiện hành là `docs/BAO_CAO_THUYET_TRINH_BAN_MOI.pdf` (10 trang).
- Đây là bản phát triển chạy cục bộ, không phải chứng nhận hoàn tất toàn bộ nghiệm thu/user study.
