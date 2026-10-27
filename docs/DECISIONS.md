# Quyết định triển khai - 28/10/2026

1. Giữ nền 6829e9c, React JSX/Vite/CSS/Lucide, FastAPI/SQLite/auth. vision/adapters.py nguyên upstream; không copy code cũ. Không commit/push/deploy.
2. Hai PDF nguồn là đặc tả/đề xuất, bốn PNG là tham chiếu thẩm mỹ; không phải kết quả hiện tại hoặc quyền vận hành. Không chép số liệu/bìa sách giả vào UI.
3. Giữ REST /frames tuần tự thay vì rewrite WS/TypeScript theo phương án PDF. Một frame pending, global vision lock, threadpool; hiệu năng thực phải đo sau.
4. Sửa gap12s về2s và scheduler5s về350ms. Inference>2s bị bỏ, watchdog UI2.5s đóng camera. Các ngưỡng còn lại giữ cấu hình khởi tạo cần pilot.
5. Một phiên active/break mỗi user; logout pause. Restart dùng snapshot, về paused và không cộng thời gian process ngừng. Snapshot lưu khi view/command/frame và checkpoint5s/shutdown độc lập browser; hardcrash có thể mất phần sau snapshot cuối.
6. Retry lệnh lỗi mạng giữ event_id/version trong sessionStorage theo user; conflict tải snapshot. Chưa tái dựng thời điểm chuyển trạng thái offline; áp dụng lúc backend nhận. FR10/NFR05 còn thiếu, không gọi recovery đầy đủ.
7. PDF.js bổ sung vì object/iframe hiện khung trống dù HTTP200. Canvas có phân trang/zoom/retry; chưa text layer/chọn chữ/screen reader PDF. IAB Chromium không thay Chrome/Edge độc lập.
8. pypdf kiểm cấu trúc/có trang/không mã hóa; hash dedup theo user. PDF unlink lỗi503 giữ DB/reference; unlink thành công dọn JSON/RAM. Filesystem và DB không chung transaction; crash giữa unlink/commit cần tombstone/reconciliation.
9. Migration v1 thêm documents.sha256, không dựng lại DB. Snapshot mới schema1 có paused/missing totals. Phiên cũ không suy ra missing lịch sử. Backup SQLite fixture đạt; backup PDF cần cùng cửa sổ không ghi.
10. Missing camera là active không có nhánh hợp lệ đã calibrated trong2s; không cộng head-missing+gaze-missing. Null khác0. Không phải thước đo tập trung.
11. Nghỉ gợi ý duration/3, không cưỡng chế tiếp tục hoặc tự bật camera. Mẫu số cần nhóm chốt trước pilot.
12. Model CPU load/synthetic smoke thật ở evidence/model-smoke.json; chưa webcam/calibration người/accuracy. MediaPipe logged portable_clearcut_uploader thử gửi telemetry thất bại mạng: chưa chứng minh dependency hoàn toàn offline, phải kiểm soát trước pilot.
13. Giữ auto-complete calibration upstream. Chưa bổ sung dwell/confirm mỗi mục tiêu hoặc kiểm held-out; valid profile hiện chỉ là điều kiện code, không chất lượng gaze đã xác nhận. Không thêm EMA khi chưa pilot chọn tau.

14. CSV phẳng bổ sung17cột có deg/seconds, summaryrow, nullblank và formulaescape; create request_id retry dedup. PDF.js lazy/Suspense, Node>=22.13. MediaPipe privacy notice chính thức xác nhận metrics sử dụng/hiệu năng; UI consent thêm giải thích, không tự đổi firewall hoặc model upstream.

15. Backend checkpoint5s và graceful shutdown độc lập browser; hardcrash chỉ phục hồi snapshot gần nhất, không tuyên bố zero-loss. Event start/end duration dừng ở mẫu quan sát cuối, không nối gap; policy_status chỉ log khi đổi để giảm lặp. Prompt liên kết event IDs, session mới snapshot toàn bộ defaults và manifest runtime/checkpoint. Phiên cũ không retroactively gán model provenance.
