> Trạng thái sau triển khai: xem CODEX_HANDOFF.md và mục cập nhật cuối file. Phần chuẩn bị bên dưới được giữ để truy vết, không phải kết quả cuối.

# Bắt đầu với bản GitHub mới nhất

Mở folder C:\Users\THINKBOOK\Documents\ChatGPT\HMI\FocusStudy_source_git_latest trong Codex. Đây là bản có code/model upstream tại 6829e9c, không phải folder cũ đã chỉnh UI.

Đã có skill tại .agents/skills/ui-ux-pro-max; hai PDF tại docs/inputs; bốn ảnh tại docs/design-references. Skill khôi phục bằng Skill Installer từ repository tác giả, gồm data/scripts/references. Lượt tiếp theo Codex có thể nhận diện; đọc SKILL.md trực tiếp nếu chưa xuất hiện.

.venv được tạo từ Python 3.12.14 nội bộ Codex. README gốc khuyến nghị 3.11; không suy rằng dependency vision đã tương thích/chạy được khi chỉ test web.

## Lệnh PowerShell từ gốc dự án
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-docs.txt
npm --prefix frontend ci
npm --prefix frontend run build
.\.venv\Scripts\python.exe -m pytest -q
```
Backend, terminal 1:
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```
Frontend, terminal 2:
```powershell
npm --prefix frontend run dev -- --port 5173 --strictPort
```
Mở http://127.0.0.1:5173; API health http://127.0.0.1:8000/api/health. Nếu cổng đã có process, xác định đúng process trước khi dừng. Bản build được backend phục vụ ở 8000 sau khi build rồi restart. Đăng ký tài khoản riêng, không có account mặc định. .env không tự nạp; xem .env.example và README.

## Vision riêng
Ba checkpoint đã tải đủ qua Git LFS, tổng 195,377,107 bytes, SHA-256 khớp. Không cần tải checkpoint lần nữa. Thư viện MediaPipe/L2CS/PyTorch vẫn phải kiểm tra và cài đúng docs/models.md. Có model file không đồng nghĩa health available hoặc webcam đã kiểm chứng. Giữ runtime CPU trước, xác minh dependency/nguồn/version và kiểm tra model load rồi calibration thực. Không tự đổi sang CUDA hoặc cập nhật torch toàn máy.

## Tái tạo PDF
```powershell
.\.venv\Scripts\python.exe update_doc.py
```
Agent cần kiểm script, cập nhật nguồn Markdown theo code mới, render và kiểm PDF; lệnh sinh PDF thành công không đủ xác nhận chất lượng bố cục.

## Nếu clone trên máy khác
```powershell
git lfs install
git clone --branch feature/focusstudy-dashboard-handoff-20261028 --single-branch https://github.com/ThuyTrangN/FocusStudy_source.git
Set-Location FocusStudy_source
git lfs pull
git lfs fsck
py -3.11 -m venv .venv
npx ui-ux-pro-max-cli init --ai codex
```
Chỉ dùng khối này cho máy/bản clone mới. Máy hiện tại đã có repo, model và skill. Xem hướng dẫn tác giả trước khi cập nhật CLI/skill, không cài đè bản đã tùy chỉnh.

## Cập nhật sau triển khai 28/10/2026

Đọc CODEX_HANDOFF.md mới và evidence, không dùng trạng thái chuẩn bị cũ làm kết quả cuối. Node>=22.13 do PDF.js6; máy này Node24.22.1. Runtime MediaPipe/L2CS/PyTorchCPU đã cài và smoke thật, chưa webcamngười. Model3file giữ nguyên, không tải lại. Build/tests cuối xem KET_QUA_KIEM_TRA và rawlogs. Backendtest dùng18000 với DB/PDF riêng tmp/browser; cổng8000 người dùng giữ nguyên. API có checkpoint5s/shutdown, request_id, eventinterval/audit và CSVphẳng; offline timing còn thiếu. Chỉ một worker; .env không autoload. Tái tạo phụ lục bằng scripts/build_reference.py trước update_doc.py, sau đó renderPDFQA.
