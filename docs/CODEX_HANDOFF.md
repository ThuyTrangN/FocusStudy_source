# Bàn giao ngày 28/10/2026 - sau triển khai

## Xuất bản nhánh theo yêu cầu mới

Người dùng đã yêu cầu tạo nhánh mới, commit và push lên `https://github.com/ThuyTrangN/FocusStudy_source`. Nhánh bàn giao: `feature/focusstudy-dashboard-handoff-20261028`, xuất phát từ nền `6829e9c`. Các ghi chú không commit/push bên dưới là phạm vi của đợt triển khai trước, không phải giới hạn của yêu cầu xuất bản này. Không deploy hoặc sửa logic model. README có hướng dẫn clone Git LFS; dữ liệu skill được đưa đủ bằng cách chỉ ignore `/data/` ở gốc. Không thêm database/upload/file tạm mới; giữ nguyên file đã theo dõi từ upstream.

## Nền và bảo toàn

Repo FocusStudy_source_git_latest, branch feature/focusstudy-web, nền6829e9c6abacabe160175d7fc66baca34cc16af9. Không commit/push/deploy/reset/clone đè. Các file chuẩn bị AGENTS/.agents/docs/inputs/design-references được giữ. vision/adapters.py không có diff: giữ bbox fallback/model/frame upstream. Git LFS fsck OK,3checkpoint195377107bytes; hashes trong evidence/model-smoke.json. Data thật không dùng làm fixture, không xóa. tmp/data được ignore.

## Đã triển khai

- Dashboard/shell/auth theo ivory-teal-mint; ribbon CSS, API real/no achievement giả; components.jsx/pages.jsx tách dần main.jsx.
- PDF.js lazy worker reader có trang/zoom/retry/cookie, đã nhìn thấy chữ PDF thật trong IAB. pypdf structural validation100MB, ownership create/attach/upload/read/delete, SHA256retrydedup, unlink503 và JSON/RAMreference cleanup.
- Session create request_id idempotent, single active/break peruser, commands event_id+version409 atomic snapshot/log/ACK. Logoutpause, reload/restartpaused, monotonic totalsactive/break/paused.
- Backend checkpoint5s/shutdown không phụ thuộc browser. Modelmanifest/hash/version/config snapshot cho phiên mới; missingunion2s không cộng nhánh. Hardcrash vẫn chỉ phục hồi snapshot cuối.
- Scheduler350ms/gap2s/infer stale2s/watchdog2.5s; trackstop/gen/currentid/version/hidden/navigation/error guards, labvideo, gaze targetmarker. Không mở webcam trong lượt này.
- Detector eventstart/end IDs/duration tại mẫu quan sát cuối, không nối gap; prompt evidence_event_ids và policy_status blockedreason khi đổi. A/Bnotes180s, feedback/rating riêng, timeout15s/late409.
- Report timeline/missing/null/ratios; CSV17cột códeg/seconds/nullblank/formulaescape/summary; delete worker race/annotations race guards.
- Settings PATCHname validation/persist, emailreadonly, localreducedmotion; FAQsearch đúng code; skipnav/modalShiftTab/Escape/returnfocus.

## Kiểm chứng thực tế

- Baseline13tests; cuối27passed1warning Starlette/httpx, pipcheck không lỗi. Log thật evidence/pytest-final.txt; build evidence/build.txt. Vite6.4.5, React19.3.1, Node24.22.1, PDF.js6.4.299 yêu cầu Node>=22.13. PDFreader lazy, main~321KB.
- ModelCPUload MediaPipe0.10.35 và L2CS0.0.1, torch2.14.1+cpu/torchvision0.29.1+cpu. Blankadapter absent và networkgaze crop tổng hợp forwardfinite là smoke thật, KHÔNG webcam/calibration/accuracy. Không tải lại3checkpoint.
- IAB browser thực: register/login, create/timer/pause/resume/break/end/report; uploadchooser/PDFcó chữ; settingsname/motion; FAQsearch; modalfocus/Escape. DOM dashboard375/768/1024/1440 không tràn ngang; screenshot/responsive.json. CSVAPI200/BOM/columns, downloadUI tool timeout. DeleteUI chưa thử; APIfixture/deletelateworker đạt.
- PDF/Markdown đã viết lại, gồm sơ đồPNG/API/schema/file roles/versions/ma trận/data/model/pipeline/setup/DoD/backlog. Render/QA cuối ở evidence/PDF_QA.md; nguồnPDF2file không sửa.

## Chạy bản test và dữ liệu

Backend kiểm thử ở http://127.0.0.1:18000, DB tmp/browser/focusstudy.sqlite3, PDF tmp/browser/documents. Cổng8000 có process khác nên giữ nguyên. Không coi accounttest như account mặc định. Đăng ký tài khoản mới nếu cần. Dừng servertest bằng terminal đang chạy khi không dùng; không dừng server8000 tùy tiện.

```powershell
$env:FOCUSSTUDY_DB='tmp/browser/focusstudy.sqlite3'
$env:FOCUSSTUDY_DOCS='tmp/browser/documents'
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 18000
npm --prefix frontend run build
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/verify_models.py
.\.venv\Scripts\python.exe scripts/build_reference.py
.\.venv\Scripts\python.exe update_doc.py
```

DevVite proxy8000 theo config; khi dùng18000 nên mở builtapp cùng backend hoặc đổi devproxy có chủ đích. .env không autoload. Chỉ một worker. Không pip song song vào venv. Chi tiết môi trường evidence/environment.json; OpenAPI evidence/openapi.json.

## Còn thiếu/chưa kiểm chứng - không gọi hoàn tất toàn bộ

1. P0: offline interval replay chưa tái dựng thời điểm pause/resume; pending retry giữ event_id/version nhưng server áp lúc nhận,409resync. State intervals đầy đủ chưa có, hardcrash sau checkpoint cuối còn mất thời gian.
2. P0: webcam/người thật, permissiondeny/streamphysical/tabhidden/error, signs/headposture/face matching/heldoutgaze/dwelltarget/qualityoverlap. Không tự xin quyền; cần người dùng chủ động cho phép và chạy protocol.
3. P0: MediaPipe privacy notice xác nhận usage/performance metrics; smoke logged clearcutattemptfailed. UIconsent giải thích, nhưng chưa networkaudit độc lập hoặc policy ngăntelemetry. Không tự đổi firewall/downgrade upstream.
4. P1: event/multisignalA-B audit mở rộng, full state intervals; fileDB tombstone/reconciliation crash; restore DB+PDF khácpath; PDFtextlayer/screenreader/ChromeEdge độc lập/zoom200; CSVdownloadUI.
5. P2:4pilot/8evaluation/protocol/frozenconfig/SUS/accuracy/benchmark chưa thực hiện. Không bịa kết quả.

## Prompt tiếp tục

Đọc AGENTS, CODEX_SETUP, CODEX_MASTER_PROMPT toàn bộ, handoff này, REQUIREMENTS_TRACEABILITY/DECISIONS/KET_QUA_KIEM_TRA và báo cáo nguồn. Giữ toàn bộ worktree và model/frame upstream6829e9c. Ưu tiên P0 offline intervals bằng schema/migration/test bảo toàn dữ liệu; rồi chạy camera/model/calibration người thật chỉ khi được quyền, xác minh telemetry. Mở evidence trước, không gọi model load/synthetic smoke là webcam accuracy. Sau sửa cập nhật build_reference/Markdown/PDF và render QA. Không commit/push/deploy/xóa data thật.


## Bổ sung báo cáo chi tiết 28/10/2026

Yêu cầu mới chỉ mở rộng báo cáo; không sửa logic ứng dụng hoặc mapping model. Báo cáo chương 1/4/9 bổ sung tổng quan, công thức/từng mốc, sổ tay thông số, hướng dẫn thu thử và W01-W10 với phân công/đầu ra/nghiệm thu. `CONG_VIEC_TIEP_THEO.md` là bản trích công việc. `scripts/report_guide_figures.py` tạo 4 sơ đồ giải thích không dùng dữ liệu nghiên cứu. Renderer tăng cỡ chữ và mục lục chỉ lấy chương/mục có số.

Ưu tiên model cần chuyển giao: audit tensor L2CS (tên trả model.forward so với tên nhận predict_gaze; chưa kết luận đảo trục), quy ước head Euler/dấu và mốc gần biên góc; xác nhận calibration bằng điểm held-out. Cổng head dưới 15 độ cho gaze và head_turn trên 25 độ khiến gaze không luôn tham gia xác nhận head_turn; evidence_event_ids không chứng minh fusion đầy đủ. Không tự thay upstream/đổi dấu khi chưa có bằng chứng.

Đây là phần giải thích/kế hoạch, không phải kết quả model mới. 27 test và synthetic inference smoke là bằng chứng từ đợt trước; webcam người thật, pilot và evaluation vẫn chưa chạy. QA PDF và kiểm SHA của các file runtime được ghi riêng trong `docs/evidence/report-guide-check.json` và `PDF_QA.md`.


Kiểm tra trước commit nhánh bàn giao: pytest chạy lại đạt 27 passed, 1 warning Starlette/httpx (30,67 giây); Vite production build thành công (6,32 giây). Build lần đầu trong sandbox lỗi quyền đọc esbuild; chạy lại với quyền phù hợp đã đạt. `git lfs fsck` đạt; adapter/checkpoint không có diff. Các kiểm tra này không bổ sung bằng chứng webcam hoặc accuracy. Chi tiết `evidence/publish-check.json`.
