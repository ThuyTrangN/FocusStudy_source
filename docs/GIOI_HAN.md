# Phạm vi bản chạy thử

Đây là triển khai phục vụ phát triển và demo cục bộ. Account/password thật lưu backend, cookie phiên HttpOnly, SQLite tách phiên theo chủ sở hữu. Không có cơ chế xác minh email/khôi phục mật khẩu qua email hay vận hành production.

Frame hiện truyền bằng REST tuần tự thay vì WebSocket trong đề xuất ban đầu. Cách này đơn giản hóa kiểm thử, giữ tối đa một yêu cầu frame đang đợi ở client; backend bỏ yêu cầu khi model bận. Nếu chuyển WebSocket, giữ nguyên kiểm tra session/frame/state version và cơ chế dừng camera.

Hai adapter dùng model thật khi đủ thư viện/checkpoint; thiếu model báo unavailable. Không có kết quả webcam thực hoặc accuracy đã đo trong gói mã nguồn. Chưa thể xác nhận hướng góc, ngưỡng, khả năng phân biệt gaze trong/ngoài màn hình cho từng máy/người nếu chưa chạy pilot. Các ngưỡng là khởi tạo; cần chỉnh trên dữ liệu phát triển và đóng băng trước đánh giá cuối.

Các kiểm thử phần mềm không thay thế kiểm thử webcam, quyền camera trình duyệt, kính/ánh sáng yếu, máy CPU chậm và UX thực tế. Không suy từ nhìn màn hình ra tập trung, từ nhìn xuống ra mất tập trung hoặc từ không thấy mặt ra chắc chắn rời chỗ.

Cần giữ dữ liệu thử sơ bộ và 8 người đánh giá cuối riêng. Ghi video chỉ khi có đồng ý riêng; không bật ghi ảnh mặc định. Phiên A/B tự nhiên không trộn với kịch bản diễn hành vi kỹ thuật.
