# Thử tín hiệu và gán nhãn

Bắt đầu bằng debug camera, chưa dùng kết quả demo như số liệu nghiên cứu. Không gán nhãn tập trung/mất tập trung. Nhãn mô tả hành vi do người quan sát xác nhận, mục tiêu gaze theo chỉ dẫn; số đo model được ghi riêng. Hướng trái/phải tính theo người tham gia.

## Kịch bản

| Tình huống | Thời lượng đề xuất | Nhãn | Cần kiểm tra |
|---|---:|---|---|
| Nhìn giữa | 5–10 giây | neutral, screen_center | Mốc và độ dao động |
| Đọc mép màn hình | 20–30 giây | head thực tế, screen_edge | Báo nhầm gaze lệch |
| Nhìn điểm mới trên màn hình | 15 giây | screen_other | Không dùng lại điểm hiệu chỉnh |
| Quay trái/phải | 12 giây mỗi hướng | turn_left/right | Dấu góc và tích lũy thời gian |
| Quay thoáng qua | 2–3 giây | turn_left/right | Không đủ 8 giây |
| Cúi ghi chép | 30 giây | down, notebook, writing_notes | Không suy ra mất tập trung |
| Đầu gần thẳng mắt lệch | 12 giây mỗi hướng | neutral, outside_left/right/down | Giá trị bổ sung của gaze |
| Nghiêng đầu | 10 giây | tilt_left/right | Không tự nhắc từ roll |
| Ra khỏi khung hình | 12–15 giây | out_of_frame | Frame vẫn tới, thông báo trung tính |
| Che mặt | 12 giây | occluded | Tách điều kiện thực tế và model |
| Đổi vị trí/ngồi xa | Lặp điểm nhìn | Ghi điều kiện | Kiểm tra hiệu chỉnh lại |

Một người thao tác, một người đánh dấu đoạn. Ghi riêng chuyển động, đoạn ổn định và đoạn không chắc. Lặp 2–3 lần; ghi mã người, máy, webcam, ánh sáng, kính và phiên bản model. Không lưu video mặc định; nếu cần xem lại để gán nhãn phải có đồng ý riêng.

## Phân tách dữ liệu

Dùng thành viên nhóm để gỡ lỗi kỹ thuật. Thử sơ bộ với 4 sinh viên để chọn cấu hình. Giữ 8 người đánh giá cuối riêng; đóng băng commit, cấu hình và model trước đánh giá. Hiệu chỉnh cá nhân là bước vận hành, không dùng nhãn đánh giá cuối để sửa ngưỡng chung.

## A và B

Cả hai dùng cùng model, ngưỡng, cooldown. A ghi nhận phản hồi ghi chép nhưng không hoãn theo nhóm. B hoãn head-down và gaze-down 3 phút. Quyền nghỉ/tắt/nhắc sau/học ngoài web tồn tại cả A và B. Chia 8 người vào A-X/B-Y, A-Y/B-X, B-X/A-Y, B-Y/A-X, mỗi tổ hợp 2 người, mỗi phiên 15 phút. Không ép diễn dấu hiệu trong phiên học tự nhiên.

## Chỉ số

Đánh giá detector trước policy: cùng loại, temporal IoU >= 0.5, ghép một-một; báo precision/recall/F1 và số sự kiện. Nhãn và dự đoán phải cùng định nghĩa đoạn thời gian; lưu riêng bắt đầu hành vi và thời điểm đủ điều kiện. Không báo MAE góc khi thiếu tham chiếu góc. Gaze theo mục tiêu chỉ dẫn không phải eye-tracker ground truth.

Đánh giá UX: tác vụ độc lập/có trợ giúp/thất bại, thời gian, SUS toàn web, gây phiền/kiểm soát sau từng điều kiện. Nhắc hữu ích chia cho số prompt có rating; phản hồi ghi chép không tự là rating không hữu ích. Mẫu số rỗng ghi không xác định. So sánh B-A từng người; mẫu nhỏ chỉ có giá trị thăm dò.
