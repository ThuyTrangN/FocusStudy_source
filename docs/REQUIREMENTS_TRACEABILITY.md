# Ma trận truy vết - 28/10/2026

Nguồn S: FocusStudy_Dac_ta_Thiet_ke_Ke_hoach.pdf15trang; P: De_xuat_HCI_Nhom_5.pdf9trang; R:4ảnh design-references. A=code và test; B=kiểm một phần; C=còn thiếu. Evidence ở docs/evidence và KET_QUA_KIEM_TRA.md. Không dùng fixture như kết quả webcam.

| UC / FR / nguồn | Code và khoảng thiếu | Ưu tiên / tiêu chí / bằng chứng |
|---|---|---|
| UC01 FR01 S2-3 | A NewSession/create, Dashboard; ownership PDF, single active | P0: goal trắng/duration sai/owner sai bị từ chối; regression/browser |
| UC01 FR02 S3 | B accrue/view timer monotonic, active/break/paused, restart paused | P0: timer độc lập camera; exact_timer/restart + browser pause/resume/break/end; crash sau snapshot cuối còn mất |
| UC02 FR03 S3 P2 | B consent trước getUserMedia; camera tùy chọn | P0: timer-off browser đạt; từ chối quyền OS thật chưa thử |
| UC02 FR04 S3 P3 | B calibration15mẫu/5s, riêng head/gaze, missing409/422 | P0: upstream tests đạt; cần người thật/held-out/dwell target |
| UC02 FR05 S3/9 | B adapters upstream: bbox fallback/match/frame/finite/null | P0: upstream test đạt; kính/ánh sáng/nhiều mặt thật chưa kiểm |
| UC03 FR06 S4/10 | B policy timestamp/gap2/invalid/outoforder, detector_event riêng prompt | P0: boundary7.9/8 đạt; start/end/duration và blocked log đã có; pilot thiếu |
| UC03 FR07 S4/10 | B priority absent/head/gaze, cooldown shown ACK, một prompt | P0: policy/feedback test; blocked_reason log đã có; camera prompt chưa kiểm |
| UC03 FR08 S4 | B5feedback, timeout15s, rating riêng, late409 không áp | P0: expired_feedback/rating test; late_feedback log tùy chọn chưa có |
| UC04 FR09 S4-5 | B stop tracks/gen, hidden/nav/pause/break/end/logout/error | P0: worker delete regression; stream/đèn camera vật lý chưa kiểm |
| UC04 FR10 S7 | C create request_id + command event_id atomic, expected_version409, pending retry/resync | P0: duplicate/conflict đạt; offline timing replay/crash đầy đủ chưa đạt |
| UC05 FR11 S11 | B report union missing/null/timeline, CSV UTF8, delete cascade | P0: fixture/worker/CSV API đạt; download browser timeout; tombstone và state intervals đầy đủ thiếu |
| UC03 FR12 S15 | B cùng defaults/model A-B, chỉ B notes downward180s | P0: test feedback_ab đạt; chưa pilot/evaluation người |
| R01 auth/dashboard | A pages/components/CSS/MASTER; API real, không achievement giả | P1: screenshot375/768/1024/1440 |
| R02 PDF | B PdfReader PDF.js/pypdf100MB/hash/search/delete references | P0: screenshot có chữ; chưa Chrome/Edge độc lập/text layer |
| R03 sessions/report | B session/history/report/timeline/export/delete | P1: timer browser+API regression; chưa full delete UI |
| R04 settings/help | A PATCH auth/me/trim/persist/email readonly/motion/FAQ search | P1: profile test + browser name/FAQ/focus |

| NFR / nguồn S5 | Hiện trạng / tiêu chí | Phần còn lại |
|---|---|---|
| NFR01 privacy | App không lưu frame/video/landmarks; owner isolation | Runtime MediaPipe clearcut attempt; network audit trước pilot |
| NFR02 interaction | focus/label/modal trap/Escape/return/motion; toast không focus | Zoom200/screenreader toàn bộ/PDF text layer |
| NFR03 consistency | version/frame/session/late guards, event unique | Audit sâu race snapshot/feedback đa tab |
| NFR04 performance | worker/one pending/locks/load once350ms scheduler | Chưa FPS/p50/p95/CPU/RAM webcam; synthetic không benchmark |
| NFR05 recovery | errors đóng stream/warning/pending retry | Offline intervals chính xác còn thiếu; checkpoint5s/shutdown đã có |
| NFR06 traceability | frame/state/config/signal/event/prompt/shown/feedback; hash evidence | Phiên mới manifest/config và event ID/end/blocked log đã có; chưa người thật/legacy provenance |
| NFR07 report | active/break/paused và missing union riêng; null denominator | Event intervals đã có; state intervals đầy đủ còn thiếu; missing cũ không suy ngược |

| AT | Kiểm chứng hiện có | Điều kiện đóng hoàn toàn |
|---|---|---|
| AT01 | Timer không camera trong browser | Từ chối quyền camera thật, không frame |
| AT02 | Calibration thiếu/auto-complete/cancel fixture + health load thật | Head/gaze người thật + held-out |
| AT03 | boundary7.9/8/gap/invalid/outoforder tests | Snapshot defaults/manifest và interval unit đã có; replay mở rộng |
| AT04 | Single prompt/cooldown có logic/test | Blocked log đã có; replay cặp candidate/ACK mở rộng |
| AT05 | A/B notes và rating test | Đủ5feedback trên replay; nghiên cứu chưa chạy |
| AT06 | Delete khi worker chờ thật trả409, không hồi sinh | Physical camera/tabhidden/pause/backenderror |
| AT07 | Duplicate/version/end guards đạt | Offline timing/replay đầy đủ |
| AT08 | Known-clock report/null, cascade, CSV API200BOM | Browser download, reconciliation file/DB |
| AT09 | Load model + blank adapter + synthetic gaze forward | Người thật, nhiều mặt/kính/ánh sáng/trục/timing |
| AT10 | Modal ShiftTab/Escape/return; responsive DOM | Zoom200/screenreader/network audit |

Definition of Done: mọi UC/FR/NFR/AT có code và evidence đúng loại, đóng P0, end-to-end hai model/camera thật/calibration/feedback/report, frozen config sau pilot, không dữ liệu giả hoặc accuracy bịa; README/PDF/handoff đúng code cuối. Prototype hiện chạy được nhưng chưa nghiệm thu toàn bộ.
