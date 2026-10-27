# Giới hạn kiểm chứng - 28/10/2026

Prototype cục bộ, chưa đủ nghiệm thu toàn bộ. Đọc REQUIREMENTS_TRACEABILITY/DECISIONS và evidence thay các kết quả lịch sử.

- Model3file giữ nguyên, nạp CPU cả hai; blank adapter và gaze crop tổng hợp forward chạy thật. Chưa camera vật lý, trục/calibration/held-out/accuracy, ánh sáng/kính/multiple-face hoặc FPS/latency người thật.
- Offline retry giữ ID/version nhưng chưa tái dựng thời điểm pause; crash có thể mất phần sau snapshot cuối. Backend checkpoint5s/shutdown độc lập browser; event start/end và blocked log đã có, nhưng state intervals/replay offline chưa đầy đủ.
- PDF.js đã render chữ trong IAB; chưa Chrome/Edge độc lập, textlayer/chọn chữ/screenreader. Canvas nội dung PDF chưa accessible đầy đủ.
- Xóa PDF unlink lỗi giữ DB; crash giữa unlink và commit vẫn cần reconciliation/tombstone. Backup SQLite fixture đạt, backup bộ PDF/đường dẫn khác máy chưa tự động.
- MediaPipe có metrics theo privacy notice chính thức; smoke log thử clearcut thất bại. Chưa audit network độc lập. Không tuyên bố toàn bộ dependency offline tuyệt đối; app không lưu frame mặc định.
- Browser CSV download tool timeout; API CSV/BOM/null/formula kiểm được. Zoom200/screenreader/camera permission thực chưa đủ. Responsive DOM/ảnh không thay toàn bộ UX.
- Không có SUS/4pilot/8evaluation/accuracy/hiệu quả học đã đo. A/B cùng model; timer-only không baselineA. Kế hoạch nghiên cứu vẫn chưa thực hiện.

Không commit/push/deploy, không sửa/xóa data người dùng, không tự mở webcam hoặc thay bản model/frame upstream.
