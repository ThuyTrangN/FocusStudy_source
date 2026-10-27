# Cài hai model thật

Web/login/timer không cần checkpoint. Để nhận head/gaze, cần cài thêm thư viện và model. Thực hiện trong venv đã tạo ở README. Không có ảnh mẫu hay kết quả giả trong luồng suy luận.

## Trạng thái cài trên máy demo

MediaPipe Face Landmarker và L2CS-Net đã được cài trong `.venv`; checkpoint nằm trong `models/`. Backend cần được khởi động lại sau khi thay dependency hoặc checkpoint. Mở `/api/health` để xác nhận cả `head.available` và `gaze.available` là `true`. Việc model nạp được chưa xác nhận webcam, đơn vị/dấu góc hoặc accuracy trên máy/người học cụ thể.

## Kiểm chứng ngày 28/10/2026

Trong bản6829e9c này, runtime đã được cài riêng .venv Python3.12.14: MediaPipe0.10.35, torch2.14.1+cpu, torchvision0.29.1+cpu, L2CS0.0.1 tại commit dưới đây. Không CUDA, không đổi Python toàn máy. Xem evidence/environment.json.

Ba checkpoint đã có từ Git LFS, giữ nguyên195377107bytes, không chạy lại các lệnh tải/conversion bên dưới trên máy hiện tại. Chỉ dùng phần tải cho máy mới thiếu model. SHA256 và bytes từng file ở evidence/model-smoke.json. Đọc lại license upstream trước khi phân phối; notice HF chưa xác minh mới được qua web tool lượt này.

Chạy `.\.venv\Scripts\python.exe scripts/verify_models.py`: load hai nhánh thành công; adapter ảnh đen absent và mạng gaze forward crop tổng hợp finite. Đây là inference synthetic smoke, chưa webcam/calibration người thật, chưa accuracy hoặc latencybenchmark. Bộ sửa lỗi bbox/frame/calibration upstream được giữ nguyên.

MediaPipe Tasks gửi metrics sử dụng/hiệu năng theo [privacy notice chính thức](https://developers.google.com/edge/mediapipe/solutions/tasks#mediapipe_tasks_privacy_notice). Smoke đã ghi clearcut attempt thất bại mạng. Notice nói input không gửi Google; ứng dụng chưa audit network độc lập. ConsentUI đã giải thích; cần xác minh/kiểm soát trước pilot. Không tự đổi firewall hoặc downgrade model upstream để che log.

Cài torchCPU xong mới cài L2CS, không chạy pip song song vào một venv. RetinaFace weights đi kèm package face_detection. Giữ runtime CPU trước khi có số đo. Kiểm /api/health và thực hiện protocol người dùng riêng, không suy từ availabletrue ra nghiệm thu camera.

## MediaPipe

Tại thư mục dự án, PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-vision.txt
New-Item -ItemType Directory -Force models
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" -OutFile "models/face_landmarker.task"
```

Hoặc tải model chính thức từ https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker rồi đặt đúng đường dẫn. Khi mạng chặn tải tự động, tải bằng trình duyệt và chép file. Biến `MEDIAPIPE_MODEL` cho phép đổi đường dẫn.

## L2CS

Mã nguồn upstream: https://github.com/Ahmednull/L2CS-Net . README upstream hướng dẫn cài package từ fork duy trì tại https://github.com/edavalosanaya/L2CS-Net . Cài PyTorch CPU trước để tránh kéo nhầm wheel CUDA; lệnh bên dưới dùng commit đã kiểm tra:

```powershell
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install "git+https://github.com/edavalosanaya/L2CS-Net.git@4a0f978d5b4c426a7d37022d8c927d6ea031dcb6"
```

Tải checkpoint Gaze360 ResNet50 được re-host cùng thông báo phạm vi giấy phép tại https://huggingface.co/py-feat/l2cs :

```powershell
Invoke-WebRequest -Uri "https://huggingface.co/py-feat/l2cs/resolve/main/l2cs_gaze360_resnet50.safetensors?download=true" -OutFile "models\l2cs_gaze360_resnet50.safetensors"
.\.venv\Scripts\python.exe -m pip install safetensors
@'
from safetensors.torch import load_file
import torch
state = load_file("models/l2cs_gaze360_resnet50.safetensors", device="cpu")
torch.save(state, "models/L2CSNet_gaze360.pkl")
'@ | .\.venv\Scripts\python.exe -
```

Nguồn HF ghi checkpoint được chuyển đổi trực tiếp từ trọng số Gaze360 upstream sang safetensors; SHA-256 của file đã cài: `75405bdc01f7086b3887280fe50c28a14bc62463a53fa749781e4a3cf98eca0e`. Conversion chỉ đọc tensor safetensors và lưu state dict cục bộ theo định dạng mà L2CS Pipeline upstream đang dùng.

**Giấy phép:** mã nguồn L2CS là MIT; trọng số Gaze360 đi kèm điều khoản dữ liệu Gaze360, trong đó nêu rõ hạn chế ứng dụng thương mại. Chỉ dùng checkpoint sau khi xem `LICENSE-NOTICE.md` của model card và điều khoản nguồn; không phát tán checkpoint hoặc dùng cho mục đích thương mại nếu chưa có quyền phù hợp. Bản upstream hiện có3checkpoint qua Git LFS; nhóm cần xác minh quyền lưu/phân phối theo notice trước khi chia sẻ tiếp, không tự coi MIT của code là giấy phép trọng số. Bản CPU phù hợp kiểm tra đầu tiên; chỉ đổi `L2CS_DEVICE=cuda:0` sau khi PyTorch xác nhận CUDA hoạt động.

## Xác nhận

Khởi động lại backend để nạp model. Mở `/api/health`: head/gaze phải có `available: true`; lỗi dependency hoặc thiếu file được trả rõ. Với L2CS, nhánh gaze còn cần ghép mặt với MediaPipe, vì vậy cài cả hai để thử gaze trong pipeline kết hợp.

Sau đó thử webcam thực: trái/phải/cúi/ngẩng, nhìn giữa/biên/ngoài màn hình. Kiểm tra đơn vị độ, dấu trục, ghép mặt và độ ổn định. Chỉ sau bước này mới chọn ngưỡng. Có model nạp được không có nghĩa detector đã được xác nhận chính xác trên người dùng.
