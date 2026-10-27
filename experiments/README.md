# Thử tín hiệu trước khi chốt logic

1. Tạo tài khoản, tạo phiên và bật camera sau khi cài model.
2. Hiệu chỉnh head và gaze riêng; kiểm tra chiều góc bằng động tác có chỉ dẫn.
3. Trong màn hình tín hiệu, chọn nhãn hành vi/mục tiêu. Nhãn do người điều khiển xác nhận; không lấy dự đoán làm ground truth.
4. Ghi các đoạn nhìn giữa/mép màn hình, quay đầu, cúi ghi chép, đầu thẳng mắt lệch, che mặt, ra khỏi khung hình. Đoạn chuyển động ghi transition/unknown.
5. Xuất CSV và báo cáo. Mỗi mốc nhãn áp dụng từ timestamp đó đến mốc kế tiếp; mốc cuối kết thúc ở thời điểm phiên kết thúc. Không kéo nhãn qua khoảng mất dữ liệu.
6. Các ngưỡng hiện tại chỉ là khởi tạo; chỉnh trên pilot, giữ riêng dữ liệu đánh giá cuối.

Chạy unit test policy để kiểm tra quy tắc với timestamp tổng hợp. Các mẫu tổng hợp chỉ phục vụ test phần mềm, không được báo như kết quả model.
