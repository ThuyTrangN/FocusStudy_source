"""Refresh code/API/environment appendices and rendered architecture diagrams; no user DB access."""
import ast,json,platform,re,subprocess,sys
from pathlib import Path
from importlib import metadata
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image,ImageDraw,ImageFont
from backend.app import app
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence';E.mkdir(parents=True,exist_ok=True)

def diagram(name,title,rows):
    image=Image.new('RGB',(1600,180+len(rows)*180),'#faf8f4');d=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',36)
    d.text((65,40),title,fill='#075658',font=bold)
    for i,(heading,detail) in enumerate(rows):
        y=130+i*180;d.rounded_rectangle((60,y,1540,y+130),radius=20,fill='#e2f1eb',outline='#96bcb7',width=2)
        d.text((90,y+17),heading,fill='#101d2c',font=bold);d.text((90,y+70),detail,fill='#354b60',font=font)
        if i<len(rows)-1:d.line((800,y+135,800,y+174),fill='#075658',width=5);d.polygon([(788,y+160),(812,y+160),(800,y+175)],fill='#075658')
    image.save(E/(name+'.png'))

def main():
    diagram('architecture','FocusStudy: kiến trúc thực tế',[
        ('Trình duyệt: React / Vite / CSS / Lucide / PDF.js','UI, timer monotonic, camera tùy chọn; cookie auth; một frame pending'),
        ('REST API: FastAPI / Pydantic','Auth / owner / session / version / ACK; infer trong threadpool'),
        ('Vision CPU: MediaPipe + L2CS / RetinaFace','Cùng frame, ghép mặt, góc độ, validity, calibration, detector, policy'),
        ('SQLite + filesystem PDF','users / tokens / sessions JSON / logs / commands / documents; ảnh RAM')])
    diagram('session-states','Phiên học: state chính ở backend',[
        ('created -> start -> active','Chỉ một active hoặc break mỗi tài khoản; camera vẫn do người dùng bật'),
        ('active -> pause -> paused; active -> break','Camera đóng ngay; học / tạm dừng / nghỉ tích lũy riêng'),
        ('paused hoặc break -> resume -> active','Tiếp tục timer, không tự mở camera; kiểm state_version'),
        ('mọi trạng thái chưa kết thúc -> end -> ended','Ended là cuối; không nhận resume/frame; worker cũ bị loại'),
        ('restart -> snapshot -> paused','Không cộng thời gian process ngừng; có thể mất phần sau snapshot cuối')])
    diagram('vision-pipeline','Từ frame gốc đến lời nhắc',[
        ('Consent -> getUserMedia -> canvas JPEG','Preview lật bằng CSS; frame không lật; session / frame_id / version'),
        ('Owner / status / order / size -> global vision lock','Threadpool infer; quá 2 giây bỏ kết quả; kiểm lại state/version'),
        ('MediaPipe RGB + L2CS BGR -> ghép bbox','Yaw/pitch/roll độ; invalid/multiple/error rõ; thiếu angle = null'),
        ('Calibration -> relative head / gaze region -> detector','Head >=15 mẫu/5s; gaze5targets; gap<=2s; không cộng điểm tập trung'),
        ('Policy -> proposed -> UI shown ACK -> feedback','Cooldown60s; một prompt; B notes hoãn downward180s; timeout15s'),
        ('Snapshot / log -> report / CSV / delete','Không lưu frame; event độc lập prompt; model người thật chưa kiểm')])
    env={'python':sys.version,'platform':platform.platform(),'packages':{}}
    for name in ['fastapi','starlette','uvicorn','pydantic','numpy','Pillow','httpx','pytest','pypdf','reportlab','mediapipe','torch','torchvision','l2cs','face_detection','opencv-python']:
        try:env['packages'][name]=metadata.version(name)
        except metadata.PackageNotFoundError:env['packages'][name]=None
    import cv2
    env['opencv_runtime']=cv2.__version__
    env['node']=subprocess.check_output(['node','--version'],text=True).strip()
    env['frontend_declared']=json.loads((ROOT/'frontend/package.json').read_text(encoding='utf-8-sig'))
    lock=json.loads((ROOT/'frontend/package-lock.json').read_text());env['frontend_installed']={n:lock['packages'].get('node_modules/'+n,{}).get('version') for n in ['react','react-dom','vite','lucide-react','pdfjs-dist']}
    (E/'environment.json').write_text(json.dumps(env,ensure_ascii=False,indent=2),encoding='utf-8')
    api=app.openapi();(E/'openapi.json').write_text(json.dumps(api,ensure_ascii=False,indent=2),encoding='utf-8')
    out=['## 11. Phiên bản thực cài','', '| Thành phần | Version |','|---|---|',f"|Python|{platform.python_version()}|",f"|Node|{env['node']}|"]
    out += [f'|{k}|{v}|' for k,v in {**env['packages'],**env['frontend_installed']}.items()]
    out += ['','## 12. API thực tế và schema','', 'Tất cả /api trừ health/register/login cần auth; logout dùng cookie. Phiên/tài liệu kiểm ownership404, không tiết lộ đối tượng user khác. Lỗi chung401/403Origin/422validation. Snapshot JSON là ACK hiện tại, không có lớp accepted/event_id riêng trong response. OpenAPI JSON lưu evidence; API thực không dùng /v1 hoặc WebSocket.','', '| Method / path | Request / validation / response |','|---|---|']
    details={
        'register':'Auth: email/password/name; emailtrùng409; trả user và setcookie', 'login':'Auth; sai401; user và setcookie', 'me':'GET trả id/name/email', 'profile':'Profile name trim1-80; trả user đã lưu', 'logout':'Không body; pause active/break, thu hồi cookie; ok', 'health':'Không auth; models.head/gaze.available/error và real-inference-only',
        'create':'NewSession request_id dedup theo user; ownerPDF404; mode/A-B422; trả created snapshot', 'listing':'Danh sách snapshot mới nhất trước, owner; không paging', 'detail':'Snapshot; restart có recovery vềpaused', 'command':'Command; trùngID không áp lại;409version/transition/ended/multi-active; snapshot', 'feedback':'Feedback prompt/action;409closed/expired/unshown; snapshot', 'calibration':'Calibrate branch/action/target;409unavailable/off,422mẫuthiếu; snapshot progress', 'frame':'Frame image/frame_id/state_version;422image,429busy,409stale/order/version; signal+prompt+session', 'annotation':'JSON tự do<=4000ký tự; ok/at', 'report':'Report JSON session/logs/events/prompts/calibrations/annotations/ratings/ratios', 'rate':'Rating prompt_id/bool;404notshown,409duplicate; ok', 'export':'CSV UTF8BOM17cột, angles_deg/time_seconds/nullblank/formulaescape, summaryrow, attachment', 'delete':'Xóa session/logs/commands, giữPDF; ok', 'session_document':'SessionDocument document_id/null; owner404; snapshot/version++', 'upload_document':'multipart file(+session_id) hoặc raw PDF query filename;100MB413,invalid422; metadata, hashdedup', 'list_documents':'query session_id tùy chọn; listmetadata owner', 'get_document':'Metadata owner404', 'get_document_file':'application/pdf inline,404missing file/owner', 'delete_document':'Dọn file+JSON/RAM,503unlinkfailed,404owner; ok'}
    for path,methods in api['paths'].items():
        for method,v in methods.items():
            name=v.get('operationId','').split('_api_')[0]
            out.append(f"|{method.upper()} {path}|{details.get(name,v.get('summary',''))}|")
    out += ['', '### 12.1 JSON request models','']
    for name,schema in api['components']['schemas'].items():
        if name in ['HTTPValidationError','ValidationError']:continue
        out += [f'### {name}', '', '| Field | Type / required / constraints |','|---|---|']
        for k,v in schema.get('properties',{}).items():
            desc={a:b for a,b in v.items() if a!='title'}
            out.append('|'+k+'|'+('Bắt buộc; ' if k in schema.get('required',[]) else 'Tùy chọn; ')+json.dumps(desc,ensure_ascii=False).replace('|','/')+'|')
    out += ['', '### 12.2 Ví dụ fixture và response','', 'Ví dụ không phải dữ liệu người dùng. POST /api/sessions nhận {"goal":"Đọc chương 2","duration_minutes":25,"mode":"reading","condition":"B"}; trả UUID/status created/state_version0/active_seconds0. POST commands {"type":"start","event_id":"qa-start-1","expected_state_version":0} trả status active/version1. Gửi lại cùng event_id trả snapshot không áp lại. End rồi resume409. Report không sample trả head_valid_ratio/gaze_valid_ratio/response_rate/helpful_ratio=null. Frame invalid trả409/422, không angle giả.','', '## 13. Cây repo và nhiệm vụ từng file','']
    roles={
      'backend/app.py':'Entry FastAPI: lifespan initDB/loadVision/checkpointloop5s/shutdown; model_manifest hash/version cache; event start/end và blocked status; origin guard/auth/password/token; CRUD user/session/PDF, accrue/view/load/save/log; command ACK/version; calibration/frame/feedback/rating/report/export/delete. Input HTTP/Pydantic và RGB; output JSON/CSV/PDF; side effects SQLite, filesystemPDF, RAMstates. Gọi bởi uvicorn và tests.',
      'backend/policy.py':'evaluate(state,signal,now): input validity/calibration và timestamp; mutate counters/detected_events/last_sample; output candidate hoặc None. DEFAULTS ngưỡng; không I/O hoặc ML. Gọi mỗi frame và replay test.',
      'vision/adapters.py':'Vision init nạp MediaPipe/L2CS optional, health trả availability/errors, _bbox_from_landmarks fallback, infer cùng RGB -> head/gaze/face_status/processing_ms. Dùng numpy/SVD/L2CSpipeline; giữ nguyên upstream, frame chỉ RAM, không ghi DB/file.',
      'frontend/src/main.jsx':'Auth, PdfDropzone, PdfStudyViewer, App orchestration: request/post/API, hashnav, session/timer/pending sync, camera consent/generation/watchdog/frame, upload/attach/delete, calibration/annotation, feedback/report/logout. Stat/SignalCard/SessionList/ReportModal còn ở file này. State React và browserstorage; effects HTTP và MediaStream. Đã tách shared/pages/PDF, chưa tách toàn bộ orchestration.',
      'frontend/src/components.jsx':'Icon/Button/Pill/Field primitives; Modal ref/effect: focus/trap/Escape/return/body-scroll. Input props/event handlers, output semantic React, không API. Gọi toàn trang.',
      'frontend/src/pages.jsx':'Dashboard API-derived stats/day/create/resume/document; Ribbon CSS markup; Help FAQ filter và topicnav; AccountSettings form/change name callback/local motion. Không giả dataset, lưu motionlocalStorage, API qua callbackmain.',
      'frontend/src/PdfReader.jsx':'PDF.js getDocument/worker; document/render effects cancel; ResizeObserver/fitwidth/DPR; prevnext/zoom/retry/canvas/loading/error. URLfile owner cookie -> trang hiển thị, không sửa PDFnguồn; chưa textlayer.',
      'frontend/src/styles.css':'Base CSS upstream + override reference tokens/shell/auth/dashboard/pages/reader/responsive/focus/reducedmotion. Không dữ liệu hoặc nghiệp vụ; cần dọn cascade thành module sau khi UI ổn định.',
      'frontend/package.json':'Scripts dev/build/preview; React/Lucide/PDF.js dependencies, Vite/pluginReact devdeps. npm đọc để cài/build.',
      'frontend/package-lock.json':'Khóa versions và integrity dependency frontend, npmci tái tạo. Không tự sửa bằng tay.',
      'frontend/vite.config.js':'defineConfig React plugin, devproxy /api ->127.0.0.1:8000, changeOriginfalse/ws flag. Built app dùng sameorigin backend, chưa WebSocketendpoint.',
      'frontend/index.html':'HTML langvi/metaviewport/theme/description/root; bootstrap src/main.jsx. Không khóa zoom.',
      'requirements.txt':'Web/API/test dependencies +pypdf; khoảng version không lock toàn bộ. Không cần vision để chạy timer/PDF.',
      'requirements-docs.txt':'ReportLab optional cho update_doc.py, không ảnh hưởng web/runtime.',
      'requirements-vision.txt':'Includes webrequirements, MediaPipe/OpenCV optional; Torch/L2CS cài CPU riêng theo models.md.',
      'scripts/start.ps1':'Windows launcher kiểm venv/dist, cwdrepo, uvicorn loopback8000, propagate exitcode; không tự cài/build hoặc nạp .env.',
      'scripts/start.sh':'POSIX launcher venv/bin/python/dist, uvicorn loopback8000; không dữ liệu migration ngoài app.init.',
      'scripts/verify_models.py':'Load checkpoint thật CPU, hash3files, adapterblank và gazenetworkcrop tổng hợp; JSON evidence/model-smoke. Không mở webcam/ghi frame, không accuracy.',
      'scripts/report_guide_figures.py':'Tạo bốn sơ đồ giải thích góc, lớp nhãn, vùng gaze và lộ trình bằng Pillow; ví dụ giả định, không chạy model hoặc đọc dữ liệu người dùng.',
      'scripts/build_reference.py':'Script này đọc code/metadata/OpenAPI, tạo diagramPNG/environment/OpenAPI và thay phần generatedreference trong Markdown; không userDB. Chạy trước update_doc.py khi code đổi.',
      'update_doc.py':'ReportLab Markdownparser: fontViệt, heading/table/code/image/TOC/bookmark/chrome; render tạm rồi replace output, fallback khi khóa. Không đọc/ghi2PDFnguồn. Cần PopplerQA sau build.',
      'tests/test_backend.py':'Fixture tmp_path DB/PDF và Unavailable adapter; auth/CSRF/ownership, command idempotency/version/ended, calibrationprogress/auto/target/cancel, upstreambboxfallback, A-B/rating, policyduration/gap, realPDFmanagement. Test đổi PDF giả thành PDF có cấu trúc; modelstub không quality.',
      'tests/test_regressions.py':'Regression profile, PDF structure/dedup/isolation/detach/unlinkfailure, single-active/restart/logout, exactclock unionmissing/paused/null, timeoutlate, outoforder/boundary, workerdelete race, schema upgrade/backuprestore. Tất cả disposablefixtures.',
      '.env.example':'Tên env DB/model/device/cookie; không chứa secret thật, .env không autoload.',
      '.gitignore':'Ignore venv/caches/node_modules/dist/env/data/tmp/models; trackedmodel LFS hiện tại vẫn giữ trong Git. Không xóa checkpoint vì bị ignore.',
      '.gitattributes':'LFS filters cho checkpoint hiện tracked; giữ nguyên.',
      'AGENTS.md':'Hướng dẫn repo đọc setup/handoff/master, bảo toàn upstream/data, UI/PDF/test/no commit. Không runtime.',
      'README.md':'Entry setup/run/test/model/report links; người nhận đọc trước, không tài khoản mẫu.',
      'experiments/README.md':'Protocol A/B/log/pilot/evaluation và giới hạn; tài liệu, không nghiên cứu đã chạy.'}
    # Includes all project code/config, excludes dependencies/generated files.
    files=sorted(roles)
    out += ['```text']+[f for f in files]+['```','']
    for file in files:
        if not (ROOT/file).exists():continue
        out += ['### '+file,'',roles[file],'']
        if file.endswith('.py'):
            tree=ast.parse((ROOT/file).read_text(encoding='utf-8-sig'))
            symbols=[]
            for n in tree.body:
                if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):symbols.append(n.name)
            if symbols:out += ['Ký hiệu chính: '+', '.join('`'+n+'`' for n in symbols)+'.','']
    for file in ['backend/__init__.py','vision/__init__.py']:
        out += ['### '+file,'','Package marker để import backend/vision; không nghiệp vụ hoặc I/O.','']
    out += ['### Tài liệu, asset và output','', 'docs/inputs2PDF là đặc tả bất biến; design-references4PNG là ảnh ý tưởng. docs/BAO_CAO_THUYET_TRINH.md nguồn báo cáo; PDF BAN_MOI là outputQA; PDF khác có sẵn là lịch sử. CODEX_SETUP/HANDOFF/MASTER_PROMPT hướng dẫn tiếp tục; REQUIREMENTS_TRACEABILITY ma trận UC/FR/NFR/AT; DECISIONS quyết định/khác biệt; KET_QUA_KIEM_TRA bằng chứng; GIOI_HAN giới hạn; models.md setup/license/hash; PROTOCOL_THU_TIN_HIEU protocol chưa thực nghiệm; THAM_KHAO nguồn. design-system/focusstudy/MASTER.md tokens/skill. docs/evidence JSON/PNG/testlogs/PDF_QA là evidence tạo từ đợt này, không dữ liệu nghiên cứu. .agents/skills/ui-ux-pro-max là công cụ hướng dẫn có sẵn, không app dependency. models3file là pretrained assets, không liệt kê node_modules/venv/dist/generated code. File lẻ tên bắt đầu -files là artifact shell có sẵn, không module runtime; giữ nguyên.','', '## 14. Ma trận nghiệm thu đầy đủ','']
    trace=(ROOT/'docs/REQUIREMENTS_TRACEABILITY.md').read_text(encoding='utf-8-sig')
    out += [re.sub(r'^# .*\n','',trace,count=1)]
    out += ['', '## 15. Manifest model và bằng chứng cuối','']
    smoke=json.loads((E/'model-smoke.json').read_text(encoding='utf-8'))
    for m in smoke['checkpoints']:out += [f"- {m['file']}: {m['bytes']} bytes; SHA256 {m['sha256']}."]
    out += ['', 'Các hash xác minh byte hiện có; không xác minh quyền thương mại. CodeL2CS MIT theo upstream, checkpoint Gaze360 có điều khoản riêng; HF license notice không tải xác minh mới được lượt này. Không phát tán/tự khẳng định license model khi chưa review notice.','']
    target=ROOT/'docs/BAO_CAO_THUYET_TRINH.md';text=target.read_text(encoding='utf-8-sig').split('<!-- GENERATED_REFERENCE_START -->')[0].rstrip()
    target.write_text(text+'\n\n<!-- GENERATED_REFERENCE_START -->\n\n'+'\n'.join(out).rstrip()+'\n',encoding='utf-8')
    print('Reference/diagrams/environment generated without user DB')
if __name__=='__main__':main()
