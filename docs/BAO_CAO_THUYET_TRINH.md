# FocusStudy — Báo cáo toàn diện giới thiệu, đặc tả và bàn giao kỹ thuật

**Ngày lập:** 27/10/2026  
**Phạm vi:** Báo cáo thuyết trình và tài liệu bàn giao mô tả prototype FocusStudy theo mã nguồn/cấu hình hiện có, cách sử dụng, dữ liệu, pipeline và lộ trình hoàn thiện. Không phải chứng nhận độ chính xác mô hình hay kết quả nghiên cứu người dùng.

## 1. Tóm tắt hệ thống

FocusStudy là ứng dụng web hỗ trợ người dùng tự tổ chức phiên học: đặt mục tiêu, chạy timer, tùy chọn bật webcam để nhận một số tín hiệu tư thế đầu và hướng nhìn, phản hồi lời nhắc, ghi nhãn hành vi, lưu tài liệu PDF và xem lại dữ liệu phiên. Người dùng có thể học mà không bật camera; timer và các chức năng phiên học cơ bản không phụ thuộc mô hình thị giác.

| Thành phần | Công nghệ / vị trí |
|---|---|
| Giao diện | React, Vite; `frontend/src/main.jsx`, `frontend/src/styles.css` |
| API, xác thực, phiên, lưu trữ | FastAPI, Pydantic, SQLite; `backend/app.py` |
| Quy tắc phát hiện sự kiện | Python; `backend/policy.py` |
| Head pose | MediaPipe Face Landmarker |
| Gaze | L2CS-Net Gaze360 và PyTorch |
| Dữ liệu mặc định | `data/focusstudy.sqlite3`; tài liệu ở `data/documents/` |
| Mô hình cục bộ | `models/face_landmarker.task`, `models/L2CSNet_gaze360.pkl` |
| Chạy bản demo | `http://127.0.0.1:8000` |

**Trạng thái kiểm chứng gần nhất:** cả hai nhánh model trả `available: true`; trang web trả HTTP 200; backend tests: 9 passed; frontend build thành công. Đây là kiểm tra khởi động, API, logic và build, không thay thế kiểm tra webcam thực tế, hiệu chỉnh trên từng người dùng hoặc đánh giá độ chính xác.

## 2. Mục tiêu, phạm vi và nguyên tắc sử dụng

Ứng dụng giúp biến ý định học thành một phiên có mục tiêu và thời lượng, đồng thời cung cấp cách xem lại một số sự kiện quan sát được. Tín hiệu webcam **không đo trực tiếp** mức độ tập trung, hiểu bài, năng suất hay trạng thái tâm lý. Nhìn xuống có thể là ghi chép; mất mặt khỏi khung hình không chứng minh người dùng đã rời chỗ.

Các nguyên tắc trong prototype:

- Camera là tùy chọn; timer hoạt động khi camera tắt.
- Chỉ dùng kết quả suy luận thật; thiếu model thì nhánh đó báo không khả dụng, không bịa góc.
- Frame ảnh được gửi tới backend cục bộ để suy luận và không được ghi vào database hay lưu thành ảnh/video mặc định. Log lưu kết quả tín hiệu, không phải frame gốc.
- Model được nạp để suy luận đã huấn luyện trước; ứng dụng hiện không huấn luyện/fine-tune model từ dữ liệu người học. Calibration chỉ tạo baseline/vùng tham chiếu riêng cho phiên, không cập nhật trọng số model.
- Nhãn và log chỉ có thể được nhóm dự án dùng làm dữ liệu kiểm thử/đánh giá sau này khi có quy trình, quyền đồng ý và ẩn danh phù hợp; bản hiện tại không tự tạo dataset huấn luyện.
- Người dùng có quyền phản hồi, tắt hỗ trợ, kết thúc phiên, xem/xuất hoặc xóa dữ liệu phiên.
- Nhãn hành vi do người dùng/người quan sát nhập là dữ liệu riêng, không phải ground truth tự sinh từ model.
- Mặc định backend chỉ bind `127.0.0.1`; đây là bản phát triển/demo cục bộ, chưa phải dịch vụ production.

## 3. Đặc tả chức năng

### 3.1 Tài khoản và phân quyền

| Mã | Chức năng | Quy tắc chính |
|---|---|---|
| F-01 | Đăng ký | Nhận tên, email, mật khẩu; chuẩn hóa email; email trùng bị từ chối. |
| F-02 | Đăng nhập/đăng xuất | Kiểm tra mật khẩu băm; cookie xác thực HttpOnly, SameSite Strict, tối đa 7 ngày; đăng xuất thu hồi token. |
| F-03 | Cô lập dữ liệu | API truy cập phiên/tài liệu có xác thực và lọc theo `user_id`; tài khoản khác không được đọc dữ liệu. |
| F-04 | Kiểm tra trạng thái model | `GET /api/health` trả trạng thái khả dụng/lỗi riêng cho head và gaze. |

### 3.2 Phiên học và timer

| Mã | Chức năng | Quy tắc chính |
|---|---|---|
| F-10 | Tạo phiên | Mục tiêu 1–300 ký tự; thời lượng backend 1–240 phút (giao diện gợi ý 15/25/45/60); hoạt động `reading`, `exercise`, `watching`; điều kiện A hoặc B; có thể gắn PDF. |
| F-11 | Chuyển trạng thái | `created → active`; `active → paused`, `break` hoặc `ended`; `paused/break → active`. Chuyển không hợp lệ bị từ chối. |
| F-12 | Đếm thời gian | Theo dõi `active_seconds` và `break_seconds`; việc camera tắt không dừng timer. |
| F-13 | Chống lặp lệnh | `event_id` lưu trong bảng `commands` để lệnh gửi lặp không thực hiện hai lần. `state_version` giúp phát hiện trạng thái cũ. |
| F-14 | Lịch sử | Liệt kê phiên của tài khoản; mở phiên để xem trạng thái, báo cáo, xuất dữ liệu hoặc xóa. Sau khi backend khởi động lại, phiên chưa kết thúc được đưa về tạm dừng để người dùng chủ động tiếp tục. |

### 3.3 Camera, tín hiệu và lời nhắc

| Mã | Chức năng | Quy tắc chính |
|---|---|---|
| F-20 | Bật/tắt camera | Chỉ phiên `active` mới bật hỗ trợ. Người dùng phải cấp quyền webcam. |
| F-21 | Head pose | MediaPipe phát hiện mặt và ước lượng yaw, pitch, roll; yêu cầu một mặt phù hợp. |
| F-22 | Gaze | L2CS ước lượng yaw/pitch; kết quả phải ghép được mặt với face box từ MediaPipe. Sau hiệu chỉnh head, kiểm tra tư thế đầu nằm trong khoảng xác minh trước khi gaze được coi là hợp lệ. |
| F-23 | Thu frame | JPEG gửi qua API; giới hạn kích thước payload/ảnh, thứ tự frame và thời gian suy luận. Khi model đang bận, frame có thể bị bỏ qua (429); frame cũ/trạng thái đổi có thể bị từ chối (409). |
| F-24 | Phát hiện sự kiện | Duy trì tín hiệu qua một khoảng thời gian trước khi tạo lời nhắc; mất dữ liệu quá 2 giây sẽ xóa bộ đếm để tránh cộng dồn qua khoảng trống. |
| F-25 | Lời nhắc | Lời nhắc trung tính; hết hạn sau 15 giây; có cooldown 60 giây giữa các lần hiển thị. |
| F-26 | Phản hồi | Quay lại mục tiêu, đang ghi chép, học ngoài web, nhắc sau hoặc nghỉ. Học ngoài web tắt hỗ trợ và hoãn 5 phút; nhắc sau 3 phút. |

Ngưỡng mặc định của policy (có thể cấu hình nội bộ qua `policy_config` trong trạng thái phiên):

| Tín hiệu | Điều kiện | Thời gian duy trì |
|---|---:|---:|
| Không quan sát thấy mặt | `face_status == absent` | 10 giây |
| Quay đầu | `abs(relative_yaw) > 25°` | 8 giây |
| Cúi đầu | pitch có dấu theo cấu hình vượt 20° | 15 giây; 25 giây nếu làm bài |
| Gaze ngoài vùng | ngoài khoảng gaze đã hiệu chỉnh | 8 giây |
| Khoảng trống frame | hơn 2 giây | Xóa bộ đếm sự kiện |
| Cooldown lời nhắc | sau lần hiển thị trước | 60 giây |

Các góc, dấu trục và ngưỡng này chưa được xác nhận bằng protocol webcam trên mọi thiết bị/người dùng. Thay đổi vị trí camera, ánh sáng, tư thế và thiết bị có thể ảnh hưởng chất lượng.

### 3.4 Điều kiện A/B, gán nhãn và báo cáo

- **A:** phản hồi “đang ghi chép” được ghi nhận nhưng không hoãn nhóm nhìn xuống.
- **B:** cùng phản hồi đó hoãn nhóm nhìn xuống 3 phút. Những phản hồi khác dùng chung logic ở A/B.
- Prototype không tự phân nhóm ngẫu nhiên và chưa cung cấp bằng chứng hiệu quả từ user study.
- Phòng thử tín hiệu hiển thị trạng thái model, tín hiệu head/gaze, lý do không hợp lệ và JSON.
- Ghi nhãn thủ công gồm tư thế đầu, mục tiêu gaze, tình trạng mặt, hoạt động và trạng thái đoạn. Nhãn mô tả quan sát, không kết luận tập trung.
- Báo cáo phiên tổng hợp thời lượng, log sự kiện, tỷ lệ tín hiệu hợp lệ khi có dữ liệu, phản hồi, đánh giá và nhãn; CSV xuất log theo dòng.

### 3.5 Tài liệu PDF

- Tải PDF bằng chọn file hoặc kéo thả; tối đa 100 MB, kiểm tra đuôi `.pdf` và chữ ký mở đầu `%PDF-`.
- Tệp lưu trên filesystem; metadata và quyền sở hữu lưu trong SQLite.
- Có thể liệt kê, xem metadata, mở/đọc file, gắn vào phiên, đổi hoặc bỏ tài liệu và xóa tài liệu.
- API kiểm tra chủ sở hữu trước khi trả metadata/tệp.
- Xóa phiên không đồng nghĩa xóa tài liệu của người dùng; thao tác xóa tài liệu mới xóa file tương ứng.

## 4. Kiến trúc và luồng pipeline

### 4.1 Sơ đồ thành phần

```text
┌──────────────────── Trình duyệt ────────────────────┐
│ React UI · Timer · Webcam · PDF viewer · History    │
└─────────────────────────┬───────────────────────────┘
                          │ HTTP / JSON, JPEG, CSV
                          ▼
┌──────────────────── FastAPI ────────────────────────┐
│ Auth/ownership │ Session state │ Calibration        │
│ Frame endpoint │ Policy        │ Report/CSV/PDF API │
└───────────────┬─────────────────────┬───────────────┘
                │                     │
                ▼                     ▼
       SQLite database         Vision adapters
       sessions/logs/docs      MediaPipe + L2CS/PyTorch
                │                     │
                └── local document files under data/documents/
```

### 4.2 Pipeline webcam đến lời nhắc

1. Người dùng chọn hoặc tạo phiên, chuyển sang `active`, cấp quyền webcam và bật hỗ trợ.
2. Trình duyệt đọc frame từ video, thu nhỏ khoảng 640 px chiều rộng, mã hóa JPEG; không gửi luồng video liên tục như file.
3. API `/api/sessions/{sid}/frames` xác thực cookie/quyền phiên, kiểm tra hỗ trợ đang bật, `state_version`, `frame_id`, payload và kích thước ảnh.
4. Khóa suy luận đảm bảo một process chỉ chạy một suy luận cùng lúc. Ảnh giải mã trong bộ nhớ.
5. MediaPipe phát hiện số mặt và điểm mặt; nếu đúng một mặt, lấy vùng mặt và ước lượng góc head từ ma trận biến đổi.
6. L2CS suy luận hướng nhìn trên ảnh; kết quả chỉ giữ khi ghép được bbox với mặt MediaPipe. Gaze cần head đã hiệu chỉnh và tư thế trong phạm vi kiểm tra để được tính hợp lệ.
7. Backend kiểm tra giá trị hữu hạn, áp profile hiệu chỉnh, ghi mẫu nếu đang calibration, rồi chạy `policy.evaluate`.
8. Nếu tín hiệu duy trì vượt ngưỡng và không bị cooldown/hoãn, tạo một lời nhắc. Trạng thái tín hiệu/lời nhắc được trả cho giao diện.
9. Ghi log dạng JSON trong SQLite (signal/event/prompt/feedback/calibration/annotation). Frame ảnh gốc không được ghi bởi luồng này.

Các mã trạng thái đáng chú ý: 401 chưa đăng nhập; 403 origin không cho phép; 404 không thuộc tài khoản/không tồn tại; 409 phiên/frame đã thay đổi hoặc thao tác không hợp lệ; 422 payload/hiệu chỉnh chưa đạt; 429 model bận; 413 file PDF vượt giới hạn.

### 4.3 Pipeline PDF

Chọn file → gửi multipart tới `/api/documents` → xác thực người dùng, giới hạn 100 MB, tên/đuôi và PDF signature → ghi file bằng ID ngẫu nhiên vào `data/documents/` → ghi metadata vào bảng `documents` → giao diện dùng API file có kiểm tra user để đọc nội tuyến. Khi gắn PDF vào phiên, `document_id`/tên được cập nhật vào JSON của phiên.

### 4.4 Model, dữ liệu nguồn và giấy phép

- **MediaPipe Face Landmarker:** model asset `models/face_landmarker.task` cùng thư viện MediaPipe được nạp để phát hiện mặt và ước lượng biến đổi mặt.
- **L2CS-Net Gaze360:** mã L2CS chạy qua PyTorch; checkpoint được chuyển đổi định dạng cục bộ thành `models/L2CSNet_gaze360.pkl`. Đây là trọng số đã huấn luyện trước, không phải dữ liệu do ứng dụng tự huấn luyện.
- Checkpoint Gaze360 re-host có điều khoản sử dụng riêng và hạn chế ứng dụng thương mại; mã nguồn L2CS MIT không làm thay đổi điều khoản checkpoint. Xem `docs/models.md` và license/model card nguồn trước khi phân phối hoặc dùng thương mại.
- Cài model thành công chứng minh adapter nạp được, không chứng minh độ chính xác, khả năng khái quát, bias hay phù hợp mục đích nghiên cứu.

## 5. Hiệu chỉnh head/gaze — quy trình thao tác

### 5.1 Điều kiện trước khi hiệu chỉnh

1. Đăng nhập, tạo phiên hoặc mở lại phiên từ Lịch sử.
2. Đảm bảo trạng thái phiên là **Đang học** (`active`). Nếu đang tạm dừng/đang nghỉ, nhấn **Tiếp tục**.
3. Bật camera và hỗ trợ; chấp nhận quyền webcam trong trình duyệt.
4. Kiểm tra `/api/health` hoặc màn hình tín hiệu: nhánh cần dùng phải báo khả dụng. Nếu chưa, cài đúng thư viện/checkpoint theo `docs/models.md`, sau đó khởi động lại backend.
5. Ngồi trong khung hình, ánh sáng đủ, mặt không bị che, chỉ một khuôn mặt rõ. Dùng cùng vị trí ngồi/camera trong phiên.
6. Thực hiện hiệu chỉnh **head trước, gaze sau**. Gaze phụ thuộc vào mặt/head hợp lệ và profile head.

### 5.2 Hiệu chỉnh mốc đầu

1. Nhìn vào vùng giữa màn hình với tư thế tự nhiên, giữ đầu tương đối yên.
2. Nhấn **Thu mốc đầu**. Backend bắt đầu thu các cặp góc yaw/pitch chỉ từ frame head hợp lệ.
3. Theo dõi tiến độ: cần ít nhất **15 mẫu hợp lệ**, tối thiểu **5 giây**, và độ lệch chuẩn mỗi trục không vượt quá 5°.
4. Nút **Hoàn tất** bật khi đạt điều kiện. Nhấn để lưu; nếu thất bại, đọc số mẫu/thời gian/lý do và thu lại.

Profile head lưu số mẫu, yaw/pitch trung vị. Trong frame tiếp theo, backend tính sai lệch tương đối theo chu kỳ góc:

```text
relative_yaw   = (yaw - baseline_yaw + 180) % 360 - 180
relative_pitch = (pitch - baseline_pitch + 180) % 360 - 180
```

### 5.3 Hiệu chỉnh gaze

1. Chọn **Giữa màn hình**, nhấn bắt đầu thu gaze.
2. Nhìn đúng mục tiêu đã chọn và giữ đủ lâu để nhận ít nhất **3 mẫu gaze hợp lệ**.
3. Lần lượt chọn **Trái → Phải → Trên → Dưới**; sau mỗi lần đổi, giữ mắt nhìn vào mục tiêu cho tới khi bộ đếm đạt 3.
4. Tổng cộng cần 15 mẫu theo năm mục tiêu và tối thiểu 5 giây. Khi tất cả điều kiện đạt, nhấn **Hoàn tất**.

Profile lưu số mẫu từng điểm và góc trung vị từng điểm. Code hiện tại dùng toàn bộ mẫu để tính biên yaw/pitch theo percentile 5 và 95, nới thêm 5° mỗi phía. Bộ phân loại dùng các biên này để xác định gaze ngoài vùng. Các median theo từng điểm được lưu để truy xuất/báo cáo; code hiện tại **chưa dùng chúng làm phép ánh xạ gaze-to-screen hoặc phép hồi quy tọa độ màn hình**.

### 5.4 Kết quả điều tra lỗi “không ghi được tín hiệu/mốc”

Các nguyên nhân được xác định trong mã và trạng thái lần kiểm tra:

- **Không có phiên active/chưa chọn phiên:** camera và ghi mốc bị vô hiệu hóa. Màn hình Phòng thử tín hiệu hiện hướng dẫn tạo phiên hoặc mở phiên và tiếp tục.
- **Model không sẵn sàng:** API từ chối ngay lúc bắt đầu calibration và báo nhánh/model cần kiểm tra.
- **Mẫu không hợp lệ:** mặt vắng/multiple faces/che khuất, frame không được ghép bbox, hoặc head chưa đạt profile có thể khiến số mẫu hợp lệ không tăng. Chỉ mẫu hợp lệ mới tính.
- **Gaze không có head profile hoặc tư thế head ngoài ±15° tương đối:** gaze bị đánh dấu không hợp lệ; vì vậy hoàn tất head trước.
- **Race frame cũ (409):** lệnh calibration đổi `state_version` trong lúc frame đang bay; frontend trước đây coi mọi 409 là lỗi nghiêm trọng và đóng webcam. Đã sửa để tải trạng thái phiên mới: nếu phiên còn active và hỗ trợ bật, tiếp tục camera; chỉ dừng khi trạng thái xác nhận không còn hợp lệ hoặc không kiểm tra được trạng thái.
- **Camera đặt trên màn hình:** vị trí đó tự nó không làm API từ chối hoàn tất; tuy nhiên, góc camera khác trục nhìn màn hình có thể làm các mục tiêu gaze khó đại diện/không ổn định. Đặt gần tầm mắt, nhìn vào điểm mục tiêu thật trên màn hình và giữ nguyên bố trí trong lúc thu. Không cúi/ngẩng chỉ để “khớp” camera.

### 5.5 Bảng chẩn đoán nhanh

| Triệu chứng | Kiểm tra | Cách khắc phục |
|---|---|---|
| Nút camera không bấm được | Có phiên hiện tại? Trạng thái active? | Tạo phiên hoặc mở phiên lịch sử rồi nhấn Tiếp tục. |
| Trình duyệt không mở camera | Quyền camera, HTTPS/localhost, webcam có bị ứng dụng khác chiếm | Cấp quyền cho `127.0.0.1`, đóng ứng dụng chiếm webcam, tải lại trang. |
| Head/gaze “unavailable” | `/api/health`, file checkpoint, Python environment của server | Cài model trong đúng `.venv`, kiểm tra đường dẫn và khởi động lại server. |
| Đếm mẫu đứng yên | Signal valid/reason, mặt có rõ và duy nhất không | Tăng sáng, đưa mặt vào giữa khung, bỏ che mặt; chờ frame hợp lệ. |
| Head đủ mẫu nhưng không ổn định | Chuyển động đầu hoặc đổi tư thế trong lúc thu | Hủy/thu lại, nhìn giữa, giữ tư thế tự nhiên và yên. |
| Gaze không tăng mẫu | Head đã calibration? Gaze valid? Đúng mục tiêu đã chọn? | Hoàn tất head, giữ mặt/head trong vùng, nhìn đúng mục tiêu đến khi số đếm tăng. |
| Gaze finish báo thiếu mục tiêu | Bộ đếm một/vài mục tiêu còn dưới 3 | Chọn đúng mục tiêu thiếu, nhìn vào đó để thu đủ mẫu rồi thử hoàn tất. |
| Camera tắt sau đổi trạng thái | Thông báo 409, trạng thái phiên, hỗ trợ | Bản hiện tại tự lấy lại session khi stale frame; nếu trạng thái không còn active, tiếp tục phiên và bật camera lại. |
| Hiệu chỉnh mất sau bật lại hỗ trợ | Lệnh `support_on` khởi tạo profile calibration mới | Hiệu chỉnh sau khi đã bật camera; không tắt/bật hỗ trợ giữa các nhánh. Chụp/xuất log nếu cần lưu hồ sơ nghiên cứu. |

**Lưu ý về dữ liệu hiệu chỉnh:** profile hoàn tất được lưu vào JSON của phiên và log `calibration`. Mẫu đang thu là trạng thái tạm trong memory; khi backend khởi động lại, tiến trình thu bị xóa và phiên đang chạy được đưa về paused. Tắt hỗ trợ cũng xóa tiến trình thu đang dở. Bật hỗ trợ mới khởi tạo lại profile calibration; vì vậy hãy hoàn tất các nhánh trước khi tắt camera/hỗ trợ.

## 6. Lưu trữ và vòng đời dữ liệu

### 6.1 Vị trí

- Mặc định: `data/focusstudy.sqlite3`.
- Đổi database bằng biến môi trường `FOCUSSTUDY_DB`.
- Thư mục PDF mặc định: cùng thư mục database, tên `documents` (mặc định `data/documents/`); có thể đặt `FOCUSSTUDY_DOCS`.
- Database và file người dùng không nằm trong frontend bundle. Không commit `data/`, `.venv/`, `node_modules/` hoặc checkpoint.

### 6.2 Bảng SQLite

| Bảng | Dữ liệu lưu | Ghi chú |
|---|---|---|
| `users` | ID, tên, email, mật khẩu dạng salt/hash | Email duy nhất. |
| `tokens` | Hash token, user ID, hạn dùng | Token thô chỉ nằm trong cookie trình duyệt. |
| `sessions` | ID, user ID, JSON trạng thái phiên | Bao gồm mục tiêu, mode, condition, trạng thái/timer, calibration profile, tài liệu gắn và một số trường phiên. |
| `logs` | ID, session ID, loại, epoch timestamp, JSON data | Signal, command, annotation, calibration, feedback, prompt, rating và event liên quan. |
| `commands` | Session ID + event ID | Khóa kép chống thực thi lặp. |
| `documents` | ID, user ID, session ID, tên, đường dẫn file, kích thước, thời điểm | Nội dung PDF thực tế nằm trên filesystem. |

### 6.3 Những gì có/không được lưu

- **Có lưu:** hồ sơ hiệu chỉnh sau khi hoàn tất; log tín hiệu dạng số/valid/reason; trạng thái phiên, thời gian, lệnh, prompt/phản hồi, rating, nhãn và metadata tài liệu.
- **Không lưu mặc định:** ảnh webcam gốc hay video; frame được giải mã trong bộ nhớ để suy luận. Log tín hiệu có thể lớn dần theo số frame.
- **Cách dùng dữ liệu:** frame chỉ làm đầu vào suy luận tức thời; góc head/gaze hợp lệ đi vào bộ đếm rule-based và báo cáo. Baseline calibration dùng để tính độ lệch head hoặc vùng yaw/pitch gaze. Không có pipeline huấn luyện/fine-tune, bộ phân loại tâm lý hay cập nhật model từ log.
- **Calibration dở dang:** mẫu trong tiến trình không phải hồ sơ bền vững; không nên tắt server trước khi hoàn tất.
- **PDF:** file riêng trên filesystem, metadata/path trong DB.
- **Xóa phiên:** xóa bản ghi phiên và các log liên quan theo khóa ngoại, đồng thời xóa lệnh idempotency; tài liệu trong kho người dùng không tự bị xóa theo phiên.
- **Xóa tài liệu:** xóa metadata và file tương ứng. Code hiện có xử lý lỗi xóa file theo best effort; cần kiểm tra filesystem nếu cần bảo đảm dọn sạch.

### 6.4 Sao lưu và vận hành

1. Dừng backend trước khi sao lưu để có bản SQLite nhất quán; sao lưu database và thư mục documents cùng lúc.
2. Không gửi database, cookie, file PDF cá nhân, checkpoint hoặc ảnh/video người học lên dịch vụ công cộng.
3. Chạy một worker backend theo README; lock model và trạng thái calibration nằm trong process.
4. Với triển khai ngoài máy cá nhân cần HTTPS, cookie Secure, kiểm soát truy cập, giới hạn lưu trữ, chính sách sao lưu/khôi phục và đánh giá bảo mật riêng; cấu hình demo hiện tại không phải thiết kế production.

## 7. Vai trò các file trong dự án

### 7.1 Backend và thị giác máy tính

| File | Vai trò |
|---|---|
| `backend/app.py` | Điểm vào FastAPI; schema SQLite; xác thực/cookie; phân quyền; tạo và chuyển trạng thái phiên; timer; hiệu chỉnh; nhận frame; gọi suy luận/policy; ghi log; report/CSV; CRUD PDF; phục vụ `frontend/dist`. |
| `backend/policy.py` | Bộ phát hiện theo thời gian; ngưỡng quay đầu/cúi/gaze/face absent, gap, cooldown và hoãn; không phụ thuộc webcam để dễ kiểm thử. |
| `backend/__init__.py` | Đánh dấu package Python backend. |
| `vision/adapters.py` | Tải MediaPipe và L2CS, báo health; xử lý frame RGB; ước lượng góc head/gaze, ghép mặt và trả lỗi/validity. Không sinh tín hiệu giả khi thiếu model. |
| `vision/__init__.py` | Đánh dấu package Python vision. |

### 7.2 Frontend, kiểm thử và vận hành

| File | Vai trò |
|---|---|
| `frontend/src/main.jsx` | Ứng dụng React: auth, điều hướng, tạo/quản lý phiên, timer, camera và polling frame, xử lý trạng thái lỗi 409, calibration, báo cáo, gán nhãn, upload/đọc PDF. |
| `frontend/src/styles.css` | Layout, màu sắc, responsive, trạng thái camera, biểu mẫu và tiến độ hiệu chỉnh/PDF. |
| `frontend/index.html` | HTML entry cho Vite. |
| `frontend/package.json`, `frontend/package-lock.json` | Scripts và dependency frontend; lockfile cố định phiên bản cài đặt. |
| `frontend/vite.config.js` | Cấu hình build/dev server Vite. |
| `frontend/dist/` | Bundle tĩnh đã build; backend mount để phục vụ trang web. |
| `tests/test_backend.py` | Kiểm thử API và quy tắc: auth/isolation, trạng thái phiên, calibration, gaze target, A/B, annotation, PDF. Dùng fixture/model giả để kiểm tra logic chứ không đo accuracy. |
| `scripts/start.ps1`, `scripts/start.sh` | Lệnh hỗ trợ khởi chạy tương ứng PowerShell và shell Unix. |
| `experiments/README.md` | Ghi chú/thực hành thử nghiệm, không phải một service runtime riêng. |

### 7.3 Tài liệu và cấu hình

| File | Vai trò |
|---|---|
| `README.md` | Cài đặt, khởi chạy, thao tác cơ bản, dữ liệu và giới hạn triển khai. |
| `requirements.txt` | Dependency backend và công cụ test cơ bản. |
| `requirements-vision.txt` | Dependency bổ sung cho vision; PyTorch/checkpoint L2CS được hướng dẫn riêng. |
| `.env.example` | Tên biến cấu hình mẫu; không tự nạp `.env`. |
| `.gitignore` | Loại trừ môi trường, dữ liệu và file sinh ra khỏi Git. |
| `docs/models.md` | Hướng dẫn cài model, nguồn/checksum và lưu ý điều khoản checkpoint. |
| `docs/PROTOCOL_THU_TIN_HIEU.md` | Kịch bản thử tín hiệu/gán nhãn; phân biệt quan sát hành vi với kết quả model. |
| `docs/GIOI_HAN.md` | Giới hạn và các giả định chưa được xác nhận. |
| `docs/KET_QUA_KIEM_TRA.md` | Trạng thái kiểm thử/build/demo đã ghi nhận. |
| `docs/BAO_CAO_THUYET_TRINH.md` / `docs/BAO_CAO_THUYET_TRINH_BAN_MOI.pdf` | Báo cáo toàn diện này; Markdown là nội dung nguồn, PDF là bản để đọc/in/trình bày. |
| `update_doc.py` | Chuyển báo cáo Markdown sang PDF có hỗ trợ tiếng Việt, bảng, danh sách và khối mã. |
| `requirements-docs.txt` | Dependency chỉ cần khi tái tạo PDF; không cần để chạy ứng dụng. |

## 8. API chính

Tất cả đường dẫn được khai báo dưới prefix `/api`:

| Method | Đường dẫn | Chức năng |
|---|---|---|
| POST | `/auth/register`, `/auth/login`, `/auth/logout` | Tạo tài khoản, đăng nhập, đăng xuất |
| GET | `/auth/me`, `/health` | Người dùng hiện tại, health/model status |
| POST / GET | `/sessions` | Tạo phiên, liệt kê phiên của tài khoản |
| GET / DELETE | `/sessions/{sid}` | Đọc hoặc xóa phiên |
| POST | `/sessions/{sid}/commands` | Lệnh trạng thái, bật/tắt hỗ trợ, hiển thị prompt |
| POST | `/sessions/{sid}/frames` | Gửi một frame camera và nhận tín hiệu |
| POST | `/sessions/{sid}/calibration` | Bắt đầu/hoàn tất head/gaze hoặc đổi mục tiêu gaze |
| POST | `/sessions/{sid}/feedback`, `/ratings` | Lưu phản hồi và đánh giá prompt |
| POST | `/sessions/{sid}/annotations` | Ghi mốc hành vi |
| GET | `/sessions/{sid}/report`, `/export` | Báo cáo JSON hoặc CSV |
| POST / GET / DELETE | `/documents` và `/documents/{id}` | Upload/list/get/delete PDF |
| GET | `/documents/{id}/file` | Trả PDF nội tuyến sau kiểm tra quyền |
| POST | `/sessions/{sid}/document` | Gắn hoặc bỏ tài liệu trên phiên |

## 9. Build, kiểm thử và hướng dẫn trình diễn

### 9.1 Khởi chạy trên Windows

Từ thư mục dự án:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Build frontend sau khi sửa giao diện:

```powershell
cd frontend
npm ci
npm run build
cd ..
```

Kiểm thử backend:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### 9.2 Kịch bản trình bày 5–7 phút

1. Giới thiệu nguyên tắc: timer trước, camera tùy chọn; không gọi webcam là phép đo tập trung.
2. Tạo phiên học, chọn mục tiêu, hoạt động, thời lượng, A/B và có thể gắn PDF.
3. Chạy/tạm dừng/tiếp tục timer; cho thấy timer vẫn hoạt động không cần camera.
4. Vào Phòng thử tín hiệu, xác nhận session active và health hai model.
5. Bật camera, hiệu chỉnh head; sau đó chỉ demo gaze nếu tín hiệu đủ ổn định và có thời gian.
6. Thử ghi nhãn hành vi thủ công, giải thích nhãn không phải dự đoán.
7. Kết thúc/mở báo cáo, chỉ ra lưu lượng sự kiện và CSV, vị trí DB cục bộ.

Nếu webcam không hoạt động, dùng báo cáo API/test và demo không-camera; không trình bày dữ liệu giả như dữ liệu người thật.

## 10. Giới hạn đã biết

- Webcam thực tế chưa được xác nhận trên mọi thiết bị; quyền hệ điều hành/trình duyệt, ánh sáng và bố trí camera vẫn cần kiểm tra.
- Chưa xác nhận dấu/đơn vị góc, sai số, độ trễ, ngưỡng tối ưu hay accuracy với người dùng. Test suite xác nhận logic phần mềm, không phải hiệu năng mô hình.
- Gaze profile hiện là vùng yaw/pitch và lưu median mục tiêu; chưa hiệu chỉnh tọa độ điểm nhìn trên màn hình và không phải eye tracker.
- Mẫu calibration dở dang chưa bền vững qua restart; cần lưu/khôi phục tiến độ có kiểm soát nếu cần.
- `support_on` làm mới profile calibration; UX nên cảnh báo trước khi bật lại để tránh người dùng nghĩ profile cũ vẫn còn.
- Log signal theo frame có thể làm SQLite tăng nhanh; cần chính sách retention, sampling hoặc archive trước khi thu dữ liệu dài hạn.
- Upload PDF đang kiểm tra phần mở đầu `%PDF-`, nhưng chưa phải kiểm tra nội dung PDF chuyên sâu/antivirus.
- Chưa có cơ chế reset mật khẩu/email, quản trị tài khoản hay hardening triển khai public; không mở ra Internet nếu chưa có rà soát bảo mật/vận hành.
- Cần pilot webcam có consent, protocol thống nhất, người gán nhãn, kiểm tra góc/sign và phân tích lỗi trước khi dùng làm kết quả nghiên cứu.

## 11. Lộ trình nâng cấp prototype thành sản phẩm hoàn thiện

Không nên bắt đầu bằng cách tăng số lời nhắc hoặc đưa model lên cloud. Hoàn thiện theo các cổng chất lượng dưới đây để giữ dữ liệu có ý nghĩa và không biến tín hiệu thử nghiệm thành kết luận quá mức.

| Giai đoạn | Việc cần làm | Điều kiện nghiệm thu đề xuất |
|---|---|---|
| 0. Đóng băng nền hiện tại | Lưu source, version dependency/model/checkpoint, hash model, cấu hình ngưỡng, schema DB và test baseline. Sao lưu database demo trước thay đổi. | Máy khác cài theo README; backend/frontend build và test lặp lại được; model/version/điều khoản được ghi rõ. |
| 1. Kiểm chứng webcam | Thử nhiều camera/độ phân giải/ánh sáng/khoảng cách; ghi latency và lỗi `absent`, `multiple`, `unmatched_face`; xác minh dấu và đơn vị góc head/gaze. | Protocol thử nghiệm định trước; dữ liệu gán nhãn tách khỏi dữ liệu tune; ngưỡng và giới hạn được báo cáo có số liệu. |
| 2. Cải thiện calibration | Cho phép bỏ/thu lại mục tiêu, hủy và tiếp tục calibration an toàn; tránh xóa profile cũ khi người dùng chưa xác nhận; lưu tiến độ nếu cần; xác minh vùng gaze với target mới không dùng để fit. | Có test state transition/persistence và kiểm thử camera thực; báo rõ profile nào đang có hiệu lực, khi nào mất và cách reset. |
| 3. Hoàn thiện trải nghiệm | Hướng dẫn quyền camera, health model, session active, lỗi frame, tiến độ mẫu, accessibility, responsive và hướng dẫn demo không-camera. | User test task-based; lỗi phổ biến có thông báo/action rõ; không phụ thuộc DevTools để biết lỗi. |
| 4. Quản trị dữ liệu | Thiết lập retention/giới hạn log signal, xuất dữ liệu có cấu trúc, backup/restore, kiểm tra xóa PDF/file mồ côi, xử lý tải file theo streaming. | Kiểm thử khôi phục bản sao lưu; thử xóa tài khoản/phiên/tài liệu và xác nhận không còn dữ liệu thuộc phạm vi xóa. |
| 5. Bảo mật và triển khai | Rà soát auth/CSRF/origin/cookie, giới hạn request, quản lý secret, TLS, logging và cập nhật dependency; thiết kế database/worker phù hợp môi trường đích. | Có security review, threat model, deployment runbook và kiểm thử trên môi trường staging trước production. |
| 6. Nghiên cứu hiệu quả (nếu thuộc mục tiêu) | Hoàn thiện protocol, consent, tiêu chí tuyển mẫu, phân nhóm A/B, ground truth, cỡ mẫu và phân tích thống kê. | Đề cương được duyệt; dữ liệu thu có consent và quy trình ẩn danh/retention; kết quả không suy ra trực tiếp từ demo phần mềm. |

### Cách dùng báo cáo khi tiếp nhận dự án

1. Dùng mục 1–3 để hiểu mục tiêu, công nghệ và phạm vi chức năng hiện có.
2. Dùng mục 4–8 để lần theo pipeline, file thực thi, API và nơi dữ liệu được ghi.
3. Dùng mục 5–6 để vận hành webcam, hiệu chỉnh, khắc phục lỗi và bảo toàn dữ liệu.
4. Chạy đúng lệnh ở mục 9 và đối chiếu `docs/KET_QUA_KIEM_TRA.md`; nếu kết quả khác, kiểm tra phiên bản Python/Node/model trước khi chỉnh code.
5. Chọn giai đoạn tiếp theo trong roadmap; tạo tiêu chí nghiệm thu và baseline trước khi sửa để phân biệt cải tiến thật với thay đổi chưa kiểm chứng.

### Nội dung của bản hiện tại

Bản này là **prototype cục bộ có thể chạy**, nhằm chứng minh tích hợp được quy trình phiên học, PDF, webcam tùy chọn, suy luận head/gaze, calibration cơ bản, policy theo thời gian, phản hồi, nhãn và báo cáo. Đây chưa phải bản sản phẩm hoàn thiện: model chưa được đánh giá accuracy, calibration dở dang không bền vững qua restart, lưu trữ/log chưa có retention, và cấu hình triển khai chưa dành cho public Internet. Người tiếp nhận nên coi các mục tiêu/ngưỡng thị giác là giả thuyết cần kiểm chứng, không phải chuẩn y khoa hay thước đo hiệu suất.

## 12. Kết luận

FocusStudy hiện cung cấp một luồng học cục bộ gồm tài khoản, phiên/timer, PDF, webcam tùy chọn, hai nhánh tín hiệu, hiệu chỉnh, lời nhắc phản hồi được, gán nhãn, báo cáo và CSV. Hồ sơ calibration hoàn tất cùng sự kiện và tín hiệu được lưu trong SQLite; ảnh webcam gốc không được lưu mặc định; file PDF nằm riêng trên filesystem.

Trong lần xác minh gần nhất, server và hai model khởi động được, API health thành công, frontend build và 9 test backend đạt. Bước bắt buộc trước khi kết luận về hiệu quả là kiểm tra camera thật và hiệu chuẩn trên máy/người sẽ trình bày.
