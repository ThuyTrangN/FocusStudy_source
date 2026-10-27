import React, {useState,useEffect,useRef,useCallback} from 'react';
import {createRoot} from 'react-dom/client';
import {Leaf,LayoutDashboard,History,SlidersHorizontal,LogOut,ArrowUpRight,ArrowRight,Plus,Play,Pause,Square,Camera,CameraOff,Check,CheckCircle2,AlertCircle,ChevronRight,Clock3,Target,ShieldCheck,Download,Trash2,X,Activity,Eye,ScanFace,BookOpen,Settings2,Loader2,RefreshCw,FlaskConical,NotebookPen,ExternalLink,Coffee,TimerReset,FileText,FileUp,Maximize2,Minimize2} from 'lucide-react';
import './styles.css';

const API='/api';
async function request(path,options={}) {
 const res=await fetch(API+path,{credentials:'include',...options,headers:{'Content-Type':'application/json',...options.headers}});
 let data; try{data=await res.json()}catch{data={}};
 if(!res.ok){const e=new Error(typeof data.detail==='string'?data.detail:typeof data.error==='string'?data.error:res.status===401?'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.':JSON.stringify(data.detail||data));e.status=res.status;throw e;}return data;
}
const post=(path,data={})=>request(path,{method:'POST',body:JSON.stringify(data)});
const uid=()=>crypto.randomUUID();
const formatTime=seconds=>{const n=Math.max(0,Math.floor(seconds||0));return `${String(Math.floor(n/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`};
const formatBytes=b=>{if(!b&&b!==0)return'—';if(b<1024)return b+' B';if(b<1024*1024)return(b/1024).toFixed(1)+' KB';return(b/(1024*1024)).toFixed(1)+' MB'};
const dateText=s=>s?new Date(typeof s==='number'?s*1000:s).toLocaleString('vi-VN',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}):'—';
const modes={reading:'Đọc tài liệu',exercise:'Làm bài tập',watching:'Xem bài giảng'};
const statuses={created:'Chưa bắt đầu',active:'Đang học',paused:'Tạm dừng',break:'Đang nghỉ',ended:'Đã kết thúc'};
const reasons={head_turn:'Bạn đã nhìn sang bên một lúc.',head_down:'Bạn đang ghi chép hay muốn quay lại mục tiêu?',gaze_away:'Hướng nhìn đang lệch khỏi vùng đã hiệu chỉnh.',gaze_down:'Bạn đang nhìn xuống. Bạn có đang ghi chép không?',face_absent:'Hiện chưa quan sát được khuôn mặt của bạn.'};
function Icon({of:Comp,...props}){return <Comp size={19} strokeWidth={1.7} aria-hidden="true" {...props}/>}
function Button({children,variant='',className='',...props}){return <button className={`btn ${variant} ${className}`} {...props}>{children}</button>}
function Pill({children,tone=''}){return <span className={`pill ${tone}`}>{children}</span>}
function Field({label,children,hint}){return <label className="field"><span>{label}</span>{children}{hint&&<small>{hint}</small>}</label>}
function Modal({title,children,onClose,wide=false}){
 const ref=useRef();useEffect(()=>{const prev=document.activeElement;ref.current?.focus();const handler=e=>{if(e.key==='Escape')onClose();if(e.key==='Tab'){const items=[...ref.current.querySelectorAll('button,input,select,textarea,a[href]')].filter(x=>!x.disabled);const first=items[0],last=items.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}};document.addEventListener('keydown',handler);return()=>{document.removeEventListener('keydown',handler);prev?.focus()}},[]);
 return <div className="modal-scrim" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><section className={`modal ${wide?'wide':''}`} ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={title}><div className="section-head"><h2>{title}</h2><button className="icon-btn" aria-label="Đóng" onClick={onClose}><Icon of={X}/></button></div>{children}</section></div>
}
function Auth({onAuth}){
 const [register,setRegister]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
 async function submit(e){e.preventDefault();setBusy(true);setError('');const data=Object.fromEntries(new FormData(e.currentTarget));try{await post(register?'/auth/register':'/auth/login',data);onAuth(await request('/auth/me'))}catch(e){setError(e.message)}finally{setBusy(false)}}
 return <main className="auth-page"><section className="auth-story"><div className="brand"><span className="brand-icon"><Leaf/></span>FocusStudy<span className="beta">BETA</span></div><div className="auth-copy"><span className="eyebrow">MỘT KHÔNG GIAN CHO VIỆC HỌC</span><h1>Từng chút một.<br/>Tiến xa hơn.</h1><p>Đặt một mục tiêu nhỏ. Dành thời gian cho nó.<br/>Và tìm nhịp học phù hợp với bạn.</p><div className="orbit" aria-hidden="true"><div className="orbit-line"></div><div className="orbit-inner"><BookOpen size={54} strokeWidth={1}/></div><span className="orbit-tag one"><Leaf size={16}/> Nhẹ nhàng, chủ động</span><span className="orbit-tag two"><CheckCircle2 size={16}/> Theo nhịp của bạn</span></div></div><div className="auth-foot"><ShieldCheck size={17}/> Bạn luôn có quyền bật, tắt và xóa dữ liệu.</div></section><section className="auth-form-wrap"><div className="auth-form"><span className="eyebrow">CHÀO MỪNG ĐẾN FOCUSSTUDY</span><h2>{register?'Bắt đầu hành trình của bạn':'Chào bạn trở lại'}</h2><p className="muted">{register?'Tạo tài khoản để lưu và xem lại các phiên học.':'Một khoảng thời gian nhỏ cho điều bạn muốn làm.'}</p><form onSubmit={submit}>{register&&<Field label="Tên của bạn"><input name="name" required maxLength={80} autoComplete="name" placeholder="Nguyễn Thuỳ Trang"/></Field>}<Field label="Email"><input name="email" type="email" required autoComplete="email" placeholder="ban@example.com"/></Field><Field label="Mật khẩu" hint={register?'Ít nhất 10 ký tự. Hãy dùng mật khẩu riêng cho ứng dụng này.':null}><input name="password" type="password" required minLength={register?10:1} maxLength={128} autoComplete={register?'new-password':'current-password'} placeholder="Nhập mật khẩu của bạn"/></Field>{error&&<div className="alert error" role="alert">{error}</div>}<Button className="full" disabled={busy}>{busy?<Icon of={Loader2} className="spin"/>:null}{register?'Tạo tài khoản':'Đăng nhập'}<Icon of={ArrowRight}/></Button></form><p className="auth-switch">{register?'Đã có tài khoản?':'Lần đầu đến đây?'} <button onClick={()=>{setRegister(!register);setError('')}}>{register?'Đăng nhập':'Tạo tài khoản'}</button></p><div className="privacy-note"><Icon of={ShieldCheck}/><p>Camera là tùy chọn. Bạn vẫn có thể học với timer. Ảnh được xử lý tại backend và không được lưu mặc định.</p></div></div></section></main>
}

function PdfDropzone({onUpload,uploading,compact=false,hint}){
 const [drag,setDrag]=useState(false);
 const inputRef=useRef();
 const inputId=useRef('pdf-input-'+Math.random().toString(36).slice(2,8));
 return (
  <label
   htmlFor={inputId.current}
   className={`pdf-dropzone ${drag?'dragover':''} ${compact?'compact':''}`}
   onDragOver={e=>{e.preventDefault();setDrag(true)}}
   onDragLeave={()=>setDrag(false)}
   onDrop={e=>{e.preventDefault();setDrag(false);const f=e.dataTransfer?.files?.[0];if(f)onUpload(f)}}
  >
   <input
    id={inputId.current}
    ref={inputRef}
    type="file"
    accept=".pdf,application/pdf"
    style={{display:'none'}}
    onChange={e=>{const f=e.target?.files?.[0];if(f){onUpload(f);e.target.value=''}}}
   />
   <div className="pdf-dropzone-content">
    <span className="dropzone-icon">{uploading?<Loader2 size={compact?18:24} className="spin"/>:<FileUp size={compact?18:24}/>}</span>
    <div>
     <strong>{uploading?'Đang tải tài liệu PDF lên…':'Kéo thả file PDF vào đây hoặc nhấn để chọn từ máy'}</strong>
     <small>{hint||'Hỗ trợ giáo trình, slide bài giảng, đề ôn thi định dạng .pdf (tối đa 100MB)'}</small>
    </div>
   </div>
  </label>
 );
}

function PdfStudyViewer({docId,docName,documents,onSwitchDoc,onUploadNew,onClose,expanded,onToggleExpand}){
 const doc=documents.find(d=>d.id===docId)||{id:docId,filename:docName||'Tài liệu PDF'};
 if(!doc||!doc.id)return null;
 const fileUrl=`${API}/documents/${doc.id}/file`;
 return (
  <section className={`card pdf-study-card ${expanded?'expanded':''}`}>
   <div className="pdf-study-header">
    <div className="pdf-study-title">
     <span className="pdf-icon-badge"><FileText size={18}/></span>
     <div>
      <strong title={doc.filename}>{doc.filename}</strong>
      <small>{doc.file_size?formatBytes(doc.file_size):'PDF'} · Đang học</small>
     </div>
    </div>
    <div className="pdf-study-actions">
     {documents.length>1&&<select aria-label="Đổi tài liệu đang đọc" className="pdf-select-compact" value={doc.id} onChange={e=>onSwitchDoc(e.target.value)}>{documents.map(d=><option key={d.id} value={d.id}>{d.filename}</option>)}</select>}
     <label className="btn outline small pdf-upload-btn" title="Tải file PDF khác từ máy tính"><FileUp size={14}/><span>Thêm PDF</span><input type="file" accept=".pdf,application/pdf" style={{display:'none'}} onChange={e=>{if(e.target.files?.[0]){onUploadNew(e.target.files[0]);e.target.value=''}}}/></label>
     <a className="btn ghost small" href={fileUrl} target="_blank" rel="noopener noreferrer" title="Mở trong tab riêng của trình duyệt"><ExternalLink size={15}/><span>Tab riêng</span></a>
     <button className="icon-btn" onClick={onToggleExpand} title={expanded?'Thu gọn':'Phóng to đọc tài liệu'} aria-label={expanded?'Thu gọn':'Phóng to đọc tài liệu'}><Icon of={expanded?Minimize2:Maximize2}/></button>
     <button className="icon-btn" onClick={onClose} title="Ẩn khung đọc tài liệu" aria-label="Ẩn khung đọc tài liệu"><Icon of={X}/></button>
    </div>
   </div>
   <div className="pdf-frame-wrapper">
    <object data={`${fileUrl}#toolbar=1&navpanes=1`} type="application/pdf" className="pdf-frame">
     <iframe src={`${fileUrl}#toolbar=1&navpanes=1`} title={doc.filename} className="pdf-frame">
      <p>Trình duyệt chưa hỗ trợ nhúng PDF. <a href={fileUrl} target="_blank" rel="noreferrer">Mở file tab riêng</a>.</p>
     </iframe>
    </object>
   </div>
   <div className="pdf-study-footer">
    <ShieldCheck size={14}/><span>Đọc tài liệu trực tiếp trên web giúp duy trì kết nối webcam và nhận diện tập trung mà không bị ngắt do tab ẩn.</span>
   </div>
  </section>
 );
}

function App(){
 const [user,setUser]=useState(null),[loading,setLoading]=useState(true),[tab,setTab]=useState('study'),[sessions,setSessions]=useState([]),[current,setCurrent]=useState(null),[health,setHealth]=useState(null),[error,setError]=useState(''),[notice,setNotice]=useState(''),[busy,setBusy]=useState(false),[report,setReport]=useState(null),[confirmDelete,setConfirmDelete]=useState(null);
 const [documents,setDocuments]=useState([]),[selectedDocId,setSelectedDocId]=useState(''),[uploadingDoc,setUploadingDoc]=useState(false),[previewDoc,setPreviewDoc]=useState(null),[confirmDeleteDoc,setConfirmDeleteDoc]=useState(null),[readerExpanded,setReaderExpanded]=useState(false),[showReader,setShowReader]=useState(true);
 const [camera,setCamera]=useState(false),[signal,setSignal]=useState(null),[tick,setTick]=useState(0),[consent,setConsent]=useState(false),[calibrationBranch,setCalibrationBranch]=useState(null),[gazeTarget,setGazeTarget]=useState('center'),[debug,setDebug]=useState(false);
 const videoRef=useRef(null),streamRef=useRef(null),canvasRef=useRef(null),currentRef=useRef(null),cameraRef=useRef(false),generation=useRef(0),frameId=useRef(0),inflight=useRef(false),snapshotTime=useRef(performance.now()),shownPrompt=useRef(null),dismissed=useRef(new Set());
 const [annotation,setAnnotation]=useState({head_label:'neutral',gaze_target:'screen_center',face_condition:'visible',activity:'scripted_test',annotation_status:'stable'});
 const [annotationCount,setAnnotationCount]=useState(0),[goal,setGoal]=useState(''),[duration,setDuration]=useState(25),[mode,setMode]=useState('reading'),[condition,setCondition]=useState('B');
 const updateCurrent=useCallback(s=>{if(!s)return;snapshotTime.current=performance.now();currentRef.current=s;setCurrent(s)},[]);
 const stopCamera=useCallback(()=>{generation.current++;cameraRef.current=false;streamRef.current?.getTracks().forEach(t=>t.stop());streamRef.current=null;if(videoRef.current)videoRef.current.srcObject=null;setCamera(false);setCalibrationBranch(null);},[]);
 async function refresh(){const list=await request('/sessions');setSessions(Array.isArray(list)?list:list.sessions||[])}
 async function loadDocuments(){try{const list=await request('/documents');setDocuments(Array.isArray(list)?list:[])}catch{}}
 async function loadHealth(){try{setHealth(await request('/health'))}catch(e){setHealth({error:e.message})}}
 useEffect(()=>{request('/auth/me').then(setUser).catch(()=>{}).finally(()=>setLoading(false));loadHealth();return stopCamera},[]);
 useEffect(()=>{if(user){refresh().catch(e=>setError(e.message));loadDocuments();}},[user]);
 useEffect(()=>{currentRef.current=current},[current]);
 useEffect(()=>{const id=setInterval(()=>setTick(t=>t+1),1000);return()=>clearInterval(id)},[]);
 useEffect(()=>{
  if(current?.document_id){
   setSelectedDocId(current.document_id);
   setShowReader(true);
  }
 },[current?.document_id]);
 useEffect(()=>{const hidden=()=>{if(document.hidden&&cameraRef.current){stopCamera();setNotice('Tab đã ẩn: camera được đóng. Khi quay lại, hãy chủ động bật camera.');const s=currentRef.current;if(s)post(`/sessions/${s.id}/commands`,{type:'support_off',event_id:uid()}).then(updateCurrent).catch(()=>setError('Chưa đồng bộ thao tác tắt camera với backend.'))}};document.addEventListener('visibilitychange',hidden);window.addEventListener('pagehide',stopCamera);return()=>{document.removeEventListener('visibilitychange',hidden);window.removeEventListener('pagehide',stopCamera)}},[stopCamera]);
 useEffect(()=>{if(!camera||!current)return;let cancelled=false;const id=setInterval(async()=>{if(cancelled||!cameraRef.current||inflight.current||document.hidden)return;const video=videoRef.current;if(!video||video.readyState<2)return;const s=currentRef.current;if(!s||s.status!=='active')return;const gen=generation.current;inflight.current=true;try{const canvas=canvasRef.current||(canvasRef.current=document.createElement('canvas'));canvas.width=640;canvas.height=Math.round(640*video.videoHeight/video.videoWidth);canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);const result=await post(`/sessions/${s.id}/frames`,{image:canvas.toDataURL('image/jpeg',.7),frame_id:++frameId.current,state_version:s.state_version});if(cancelled||gen!==generation.current||!cameraRef.current)return;setSignal(result.signal);if(result.session)updateCurrent(result.session)}catch(e){if(e.status===429)return;if(e.status===409&&(e.message==='Frame không còn hợp lệ'||e.message==='Bỏ kết quả muộn'||e.message==='Frame sai thứ tự'))return;if(gen===generation.current){stopCamera();setError(`Đã đóng camera: ${e.message}. Timer vẫn tiếp tục cục bộ; dữ liệu chưa đồng bộ.`)}}finally{inflight.current=false}},350);return()=>{cancelled=true;clearInterval(id)}},[camera,current?.id]);
 // Confirm prompts actually rendered; cooldown is owned by the server.
 useEffect(()=>{const prompt=current?.prompt;if(!prompt||prompt.shown_at||shownPrompt.current===prompt.id||dismissed.current.has(prompt.id))return;shownPrompt.current=prompt.id;post(`/sessions/${current.id}/commands`,{type:'prompt_shown',event_id:uid(),prompt_id:prompt.id}).then(updateCurrent).catch(e=>setError(e.message))},[current?.prompt?.id]);
 useEffect(()=>{const prompt=current?.prompt;if(!prompt)return;const id=setTimeout(()=>{dismissed.current.add(prompt.id);setTick(t=>t+1)},15000);return()=>clearTimeout(id)},[current?.prompt?.id]);
 async function command(type){const s=currentRef.current;if(!s)return;if(['pause','break','end','support_off'].includes(type))stopCamera();setBusy(true);setError('');try{updateCurrent(await post(`/sessions/${s.id}/commands`,{type,event_id:uid()}));if(type==='end'){setSignal(null);await refresh();setNotice('Phiên học đã kết thúc và được lưu. Bạn có thể xem báo cáo.')}}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function create(e){e.preventDefault();setBusy(true);setError('');try{const s=await post('/sessions',{goal,duration_minutes:Number(duration),mode,condition,document_id:selectedDocId||undefined});updateCurrent(await post(`/sessions/${s.id}/commands`,{type:'start',event_id:uid()}));setSignal(null);setAnnotationCount(0);setTab('study');setShowReader(true);await refresh()}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function openSession(s){stopCamera();setSignal(null);setBusy(true);try{updateCurrent(await request(`/sessions/${s.id}`));if(s.document_id){setSelectedDocId(s.document_id);setShowReader(true)}setTab('study')}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function uploadDocument(file,autoAttach=false){
  if(!file)return;
  if(!file.name.toLowerCase().endsWith('.pdf')){setError('Chỉ chấp nhận file định dạng PDF (.pdf)');return;}
  setUploadingDoc(true);setError('');
  try{
   let data;
   try{
    const fd=new FormData();
    fd.append('file',file);
    if(current&&current.status==='active')fd.append('session_id',current.id);
    const res=await fetch(`${API}/documents`,{method:'POST',credentials:'include',body:fd});
    if(res.ok){data=await res.json()}
    else{
     const errData=await res.json().catch(()=>({}));
     throw new Error(typeof errData.detail==='string'?errData.detail:'Lỗi tải file');
    }
   }catch(err){
    const res=await fetch(`${API}/documents?filename=${encodeURIComponent(file.name)}`,{
     method:'POST',
     credentials:'include',
     headers:{'Content-Type':'application/pdf'},
     body:file
    });
    if(!res.ok){
     const errData=await res.json().catch(()=>({}));
     throw new Error(typeof errData.detail==='string'?errData.detail:err.message);
    }
    data=await res.json();
   }
   setNotice(`Đã tải lên tài liệu: ${data.filename}`);
   await loadDocuments();
   setSelectedDocId(data.id);
   setShowReader(true);
   setPreviewDoc(data);
   if(autoAttach||(current&&current.status==='active')){
    const updated=await post(`/sessions/${current.id}/document`,{document_id:data.id});
    updateCurrent(updated);
   }
   return data;
  }catch(e){setError(e.message)}finally{setUploadingDoc(false)}
 }
 async function attachDoc(docId){
  if(!current)return;
  setBusy(true);setError('');
  try{
   const updated=await post(`/sessions/${current.id}/document`,{document_id:docId||null});
   updateCurrent(updated);
   setSelectedDocId(docId||'');
   if(docId)setShowReader(true);
   setNotice(docId?'Đã mở tài liệu trong phiên học.':'Đã bỏ tài liệu khỏi phiên.');
  }catch(e){setError(e.message)}finally{setBusy(false)}
 }
 async function removeDoc(){
  if(!confirmDeleteDoc)return;
  setBusy(true);try{
   await request(`/documents/${confirmDeleteDoc.id}`,{method:'DELETE'});
   if(selectedDocId===confirmDeleteDoc.id){
    setSelectedDocId('');
    if(current?.document_id===confirmDeleteDoc.id){
     updateCurrent({...current,document_id:null,document_name:null});
    }
   }
   if(previewDoc?.id===confirmDeleteDoc.id)setPreviewDoc(null);
   setConfirmDeleteDoc(null);
   await loadDocuments();
   setNotice('Đã xóa tài liệu khỏi danh sách.');
  }catch(e){setError(e.message)}finally{setBusy(false)}
 }
 function startStudyWithDoc(doc){
  setSelectedDocId(doc.id);
  setGoal(`Đọc ${doc.filename.replace(/\.pdf$/i,'')}`);
  setMode('reading');
  setTab('study');
  setShowReader(true);
  setNotice(`Đã chọn tài liệu "${doc.filename}". Bạn có thể bắt đầu phiên học ngay.`);
 }
 async function startCamera(){if(!current||current.status!=='active')return;setBusy(true);setError('');let stream;const gen=++generation.current;try{if(!navigator.mediaDevices?.getUserMedia)throw new Error('Trình duyệt cần localhost hoặc HTTPS để sử dụng webcam.');stream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:640},height:{ideal:480}},audio:false});if(gen!==generation.current||document.hidden){stream.getTracks().forEach(t=>t.stop());return;}const s=await post(`/sessions/${current.id}/commands`,{type:'support_on',event_id:uid()});if(gen!==generation.current){stream.getTracks().forEach(t=>t.stop());return;}updateCurrent(s);streamRef.current=stream;cameraRef.current=true;setCamera(true);setConsent(false);requestAnimationFrame(()=>{if(videoRef.current){videoRef.current.srcObject=stream;videoRef.current.play().catch(()=>{})}});setNotice('Camera đã bật. Hãy hiệu chỉnh từng nhánh trước khi sử dụng lời nhắc.')}catch(e){stream?.getTracks().forEach(t=>t.stop());setError(e.name==='NotAllowedError'?'Bạn chưa cho phép camera. Timer vẫn hoạt động bình thường.':e.message)}finally{setBusy(false)}}
 async function calibrate(branch,action,target){
  setBusy(true);setError('');
  try{
   const result=await post(`/sessions/${current.id}/calibration`,{branch,action,target:target||gazeTarget});
   const sess=result.session??result;
   if(sess?.id)updateCurrent(sess);
   const serverCalibrating=sess?.calibrating??null;
   setCalibrationBranch(serverCalibrating);
   if(action==='cancel'){
    setNotice(`Đã hủy thu mẫu ${branch==='head'?'mốc đầu':'vùng gaze'}.`);
   }else if(action==='finish'){
    setNotice(`Đã hoàn tất hiệu chỉnh ${branch==='head'?'mốc đầu':'vùng gaze'} thành công.`);
   }else if(action==='target'){
    setNotice(`Mục tiêu gaze: nhìn vào ${target==='center'?'giữa màn hình':target==='left'?'biên trái':target==='right'?'biên phải':target==='top'?'biên trên':'biên dưới'}.`);
   }else{
    setNotice(`Đang thu mẫu ${branch==='head'?'đầu: giữ yên nhìn giữa màn hình':'gaze: hãy chọn và nhìn vào từng mục tiêu'}.`);
   }
  }catch(e){
   setError(e.message);
  }finally{
   setBusy(false);
  }
 }
 async function feedback(action){const prompt=current?.prompt;if(!prompt)return;if(['outside','break'].includes(action))stopCamera();setBusy(true);try{updateCurrent(await post(`/sessions/${current.id}/feedback`,{prompt_id:prompt.id,action}));dismissed.current.add(prompt.id);setNotice(action==='notes'?(current.condition==='B'?'Đã hoãn nhóm nhìn xuống 3 phút.':'Chế độ A: phản hồi chỉ được ghi nhận, không hoãn nhóm.'):'Phản hồi đã được lưu.')}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function annotate(){if(!current)return;try{await post(`/sessions/${current.id}/annotations`,annotation);setAnnotationCount(n=>n+1);setNotice('Đã ghi mốc hành vi. Chuyển nhãn khi bắt đầu đoạn tiếp theo.')}catch(e){setError(e.message)}}
 async function showReport(s){setBusy(true);try{setReport(await request(`/sessions/${s.id}/report`))}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function remove(){if(!confirmDelete)return;setBusy(true);try{if(current?.id===confirmDelete.id)stopCamera();await request(`/sessions/${confirmDelete.id}`,{method:'DELETE'});if(current?.id===confirmDelete.id){updateCurrent(null);currentRef.current=null;setCurrent(null)}setConfirmDelete(null);setReport(null);await refresh();setNotice('Đã xóa phiên và dữ liệu liên quan.')}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function logout(){stopCamera();try{if(current&&current.status==='active')await post(`/sessions/${current.id}/commands`,{type:'support_off',event_id:uid()});await post('/auth/logout');setUser(null);setCurrent(null);currentRef.current=null;setSessions([])}catch(e){setError(e.message)}}
 const localExtra=current?.status==='active'?(performance.now()-snapshotTime.current)/1000:0;
 const elapsed=(current?.active_seconds||0)+localExtra,remaining=(current?.duration_minutes||25)*60-elapsed;
 const totalMinutes=Math.round(sessions.reduce((a,s)=>a+(s.active_seconds||0),0)/60),ended=sessions.filter(s=>s.status==='ended');
 const active=!!current&&current.status!=='ended',prompt=current?.prompt&&!dismissed.current.has(current.prompt.id)?current.prompt:null;
 const currentDocId=selectedDocId||current?.document_id;
 const activeDoc=currentDocId?(documents.find(d=>d.id===currentDocId)||{id:currentDocId,filename:current?.document_name||'Tài liệu PDF'}):null;
 const models=health?.models||{};
 if(loading)return <div className="loading-page"><Leaf size={32}/><p>Đang mở không gian học…</p></div>;
 if(!user)return <Auth onAuth={setUser}/>;
 return <div className="app-shell"><aside className="sidebar"><a href="#study" className="brand" onClick={()=>setTab('study')}><span className="brand-icon"><Leaf/></span>FocusStudy</a><div className="workspace-tag">KHÔNG GIAN CÁ NHÂN</div><nav aria-label="Điều hướng chính">{[['study',LayoutDashboard,'Không gian học'],['docs',BookOpen,'Kho tài liệu PDF'],['history',History,'Lịch sử phiên học'],['lab',FlaskConical,'Phòng thử tín hiệu'],['settings',SlidersHorizontal,'Thiết lập']].map(([key,ico,label])=><button key={key} onClick={()=>setTab(key)} className={tab===key?'nav-item selected':'nav-item'}><Icon of={ico}/><span>{label}</span>{tab===key&&<span className="nav-dot"/>}</button>)}</nav><div className="sidebar-note"><span className="small-icon"><Leaf size={20}/></span><h3>Học theo nhịp của bạn</h3><p>Một mục tiêu vừa sức.<br/>Một khoảng thời gian trọn vẹn.</p></div><div className="profile"><div className="avatar">{user.name?.slice(0,1).toUpperCase()||'B'}</div><div><strong>{user.name}</strong><small>Tài khoản cá nhân</small></div><button className="icon-btn" aria-label="Đăng xuất" title="Đăng xuất" onClick={logout}><Icon of={LogOut}/></button></div></aside><main className="main"><header className="topbar"><div className="breadcrumb">Không gian cá nhân <ChevronRight size={14}/><strong>{tab==='study'?'Không gian học':tab==='docs'?'Kho tài liệu PDF':tab==='history'?'Lịch sử':tab==='lab'?'Thử nghiệm':'Thiết lập'}</strong></div><span className="today">{new Date().toLocaleDateString('vi-VN',{weekday:'long',day:'numeric',month:'long'})}</span><span className="mobile-brand">FocusStudy</span></header><div className="page-content">{error&&<div className="alert error" role="alert"><Icon of={AlertCircle}/><span>{error}</span><button className="icon-btn" aria-label="Đóng thông báo lỗi" onClick={()=>setError('')}><X size={16}/></button></div>}{notice&&<div className="alert notice" role="status"><Icon of={CheckCircle2}/><span>{notice}</span><button className="icon-btn" aria-label="Đóng thông báo" onClick={()=>setNotice('')}><X size={16}/></button></div>}
 {(tab==='study'||tab==='lab')&&<><div className="page-heading"><div><span className="eyebrow">{tab==='lab'?'QUAN SÁT · HIỆU CHỈNH · GÁN NHÃN':'MỖI PHIÊN HỌC LÀ MỘT BƯỚC TIẾN'}</span><h1>{tab==='lab'?'Phòng thử tín hiệu':`Chào ${user.name?.split(' ').at(-1)||'bạn'}, hôm nay học gì?`}</h1><p>{tab==='lab'?'Dữ liệu thật từ webcam. Nhãn hành vi được ghi độc lập với dự đoán.':'Dành một khoảng thời gian cho điều quan trọng với bạn.'}</p></div><Pill tone="green"><span className="status-dot"/> Không gian của bạn</Pill></div>
 {tab==='study'&&<div className="stats-row"><Stat icon={Clock3} label="Thời gian học đã ghi" value={`${totalMinutes}`} unit="phút"/><Stat icon={CheckCircle2} label="Phiên đã hoàn thành" value={ended.length} unit="phiên"/><Stat icon={BookOpen} label="Tài liệu đã tải" value={documents.length} unit="tài liệu"/></div>}

 {tab==='study'&&active&&activeDoc&&showReader&&(
  <div className={`pdf-study-layout ${readerExpanded?'full-reader':''}`}>
   <PdfStudyViewer docId={activeDoc.id} docName={activeDoc.filename} documents={documents} onSwitchDoc={attachDoc} onUploadNew={f=>uploadDocument(f,true)} onClose={()=>setShowReader(false)} expanded={readerExpanded} onToggleExpand={()=>setReaderExpanded(!readerExpanded)}/>
   {!readerExpanded&&(
    <div className="study-sidebar-column">
     <section className="card session-card">
      <div className="section-head"><div className="section-title"><span className="small-icon"><BookOpen size={19}/></span><h2>Phiên học của bạn</h2></div><Pill>{statuses[current.status]}</Pill></div>
      <div className="session-goal"><span className="eyebrow">MỤC TIÊU PHIÊN NÀY</span><h3>{current.goal}</h3><p>{modes[current.mode]} <span className="separator">·</span> {current.duration_minutes} phút <span className="separator">·</span> Chế độ {current.condition}</p></div>
      <div className="timer-wrap"><div className="timer-orbit" style={{'--progress':`${Math.min(100,elapsed/(current.duration_minutes*60)*100)}%`}}><div className="timer-inner"><span>{current.status==='break'?'ĐANG NGHỈ':current.status==='paused'?'ĐÃ TẠM DỪNG':remaining<=0?'ĐÃ ĐẠT MỤC TIÊU':'THỜI GIAN CÒN LẠI'}</span><strong>{formatTime(remaining)}</strong><small>{Math.floor(elapsed/60)} phút đã học</small></div></div></div>
      <div className="timer-controls">{current.status==='active'?<Button variant="secondary" disabled={busy} onClick={()=>command('pause')}><Icon of={Pause}/>Tạm dừng</Button>:<Button disabled={busy} onClick={()=>command('resume')}><Icon of={Play}/>Tiếp tục</Button>}{current.status==='active'&&<Button variant="ghost" disabled={busy} onClick={()=>command('break')}><Icon of={Coffee}/>Nghỉ</Button>}<Button variant="ghost" disabled={busy} onClick={()=>command('end')}><Icon of={Square}/>Kết thúc</Button></div>
      <div className="session-footer"><ShieldCheck size={16}/><span>Timer hoạt động cả khi camera tắt.</span></div>
      {current.snooze_remaining>0&&<div className="inline-note">Đang hoãn mọi lời nhắc: {formatTime(current.snooze_remaining)}</div>}
      {current.downward_remaining>0&&<div className="inline-note">Hoãn nhóm nhìn xuống: {formatTime(current.downward_remaining)}</div>}
     </section>
     <section className="card camera-card">
      <div className="section-head"><div className="section-title"><Icon of={ScanFace}/><h2>Hỗ trợ qua camera</h2></div><Pill tone={camera?'green':''}>{camera?'Đang bật':'Đang tắt'}</Pill></div>
      <div className={`camera-preview ${camera?'live':''}`}><video ref={videoRef} autoPlay muted playsInline aria-label="Xem trước webcam" hidden={!camera}/>{!camera&&<div className="camera-placeholder"><span className="camera-circle"><CameraOff size={28} strokeWidth={1.3}/></span><h3>Một lựa chọn, không bắt buộc</h3><p>Bật camera để hiệu chỉnh và nhận<br/>phản hồi từ tín hiệu đầu, hướng nhìn.</p></div>}{camera&&<span className="live-tag"><span className="status-dot"/> LIVE · Ảnh không lưu</span>}</div>
      <p className="camera-note"><ShieldCheck size={15}/> Frame được gửi đến backend để xử lý. Không lưu ảnh/video mặc định.</p>
      <Button variant={camera?'secondary':'outline'} className="full" disabled={busy||!active||current.status!=='active'} onClick={()=>camera?command('support_off'):setConsent(true)}><Icon of={camera?CameraOff:Camera}/>{camera?'Tắt camera và hỗ trợ':'Bật camera'}</Button>
     </section>
    </div>
   )}
  </div>
 )}

 {tab==='study'&&(!active||!activeDoc||!showReader)&&(
  <>
   {active&&!showReader&&activeDoc&&(
    <div className="active-doc-banner">
     <div><FileText size={20}/><div><strong>Tài liệu đang học: {activeDoc.filename}</strong><small>{activeDoc.file_size?formatBytes(activeDoc.file_size):'PDF'} · Đang ẩn khung đọc</small></div></div>
     <div className="button-row" style={{margin:0}}><Button variant="secondary" className="small" onClick={()=>setShowReader(true)}><FileText size={15}/>Mở đọc tài liệu</Button><Button variant="ghost" className="small" onClick={()=>attachDoc(null)}><X size={15}/>Bỏ chọn</Button></div>
    </div>
   )}
   {active&&!activeDoc&&(
    <div className="active-doc-banner">
     <div><FileUp size={20}/><div><strong>Đọc tài liệu PDF khi học</strong><small>Tải lên hoặc chọn file PDF để đọc trực tiếp trên web, giữ camera luôn hoạt động</small></div></div>
     <div className="button-row" style={{margin:0}}>
      {documents.length>0&&<select className="pdf-select-compact" value={selectedDocId} onChange={e=>attachDoc(e.target.value)}><option value="">-- Chọn tài liệu đã có ({documents.length}) --</option>{documents.map(d=><option key={d.id} value={d.id}>{d.filename}</option>)}</select>}
      <label className="btn outline small pdf-upload-btn"><FileUp size={14}/><span>Tải PDF từ máy</span><input type="file" accept=".pdf,application/pdf" style={{display:'none'}} onChange={e=>{if(e.target.files?.[0]){uploadDocument(e.target.files[0],true);e.target.value=''}}}/></label>
     </div>
    </div>
   )}
   <div className="study-grid">
    <section className="card session-card">
     <div className="section-head"><div className="section-title"><span className="small-icon"><BookOpen size={19}/></span><h2>{active?'Phiên học của bạn':'Bắt đầu một phiên học'}</h2></div><Pill>{active?statuses[current.status]:'BƯỚC NHỎ, ĐỀU ĐẶN'}</Pill></div>
     {active?<><div className="session-goal"><span className="eyebrow">MỤC TIÊU PHIÊN NÀY</span><h3>{current.goal}</h3><p>{modes[current.mode]} <span className="separator">·</span> {current.duration_minutes} phút <span className="separator">·</span> Chế độ {current.condition}</p></div><div className="timer-wrap"><div className="timer-orbit" style={{'--progress':`${Math.min(100,elapsed/(current.duration_minutes*60)*100)}%`}}><div className="timer-inner"><span>{current.status==='break'?'ĐANG NGHỈ':current.status==='paused'?'ĐÃ TẠM DỪNG':remaining<=0?'ĐÃ ĐẠT MỤC TIÊU':'THỜI GIAN CÒN LẠI'}</span><strong>{formatTime(remaining)}</strong><small>{Math.floor(elapsed/60)} phút đã học</small></div></div></div><div className="timer-controls">{current.status==='active'?<Button variant="secondary" disabled={busy} onClick={()=>command('pause')}><Icon of={Pause}/>Tạm dừng</Button>:<Button disabled={busy} onClick={()=>command('resume')}><Icon of={Play}/>Tiếp tục</Button>}{current.status==='active'&&<Button variant="ghost" disabled={busy} onClick={()=>command('break')}><Icon of={Coffee}/>Nghỉ</Button>}<Button variant="ghost" disabled={busy} onClick={()=>command('end')}><Icon of={Square}/>Kết thúc</Button></div><div className="session-footer"><ShieldCheck size={16}/><span>Timer hoạt động cả khi camera tắt.</span></div>{current.snooze_remaining>0&&<div className="inline-note">Đang hoãn mọi lời nhắc: {formatTime(current.snooze_remaining)}</div>}{current.downward_remaining>0&&<div className="inline-note">Hoãn nhóm nhìn xuống: {formatTime(current.downward_remaining)}</div>}</>:<form onSubmit={create} className="session-form">
      <Field label="Bạn muốn hoàn thành điều gì?"><input name="goal" value={goal} onChange={e=>setGoal(e.target.value)} required maxLength={300} placeholder="Ví dụ: Đọc xong chương 2 và ghi lại ý chính"/></Field>
      <div className="field"><span>Thời lượng phiên học</span><div className="duration-options">{[15,25,45,60].map(n=><button type="button" key={n} onClick={()=>setDuration(n)} aria-pressed={duration===n} className={duration===n?'chosen':''}>{n}<small>phút</small></button>)}</div></div>
      <div className="two-fields"><Field label="Hoạt động"><select value={mode} onChange={e=>setMode(e.target.value)}>{Object.entries(modes).map(([k,v])=><option key={k} value={k}>{v}</option>)}</select></Field><Field label="Cơ chế hỗ trợ"><select value={condition} onChange={e=>setCondition(e.target.value)}><option value="B">B · Điều chỉnh theo phản hồi</option><option value="A">A · Chỉ ghi nhận ngữ cảnh</option></select></Field></div>

      <div className="field">
       <span>Tài liệu học kèm theo (PDF từ máy tính)</span>
       <PdfDropzone compact onUpload={f=>uploadDocument(f,false)} uploading={uploadingDoc} hint="Kéo thả hoặc chọn file PDF giáo trình/slide bài giảng để đọc khi học"/>
       {documents.length>0&&(
        <select value={selectedDocId} onChange={e=>setSelectedDocId(e.target.value)}>
         <option value="">-- Hoặc chọn tài liệu đã tải lên ({documents.length} file) --</option>
         {documents.map(d=><option key={d.id} value={d.id}>{d.filename} ({formatBytes(d.file_size)})</option>)}
        </select>
       )}
       {activeDoc&&(
        <div className="doc-badge">
         <FileText size={15}/>
         <span>Đã chọn: <strong>{activeDoc.filename}</strong></span>
         <button type="button" className="text-btn" style={{fontSize:11,marginLeft:6,padding:'2px 6px',background:'#e0ebd8',borderRadius:4}} onClick={()=>setPreviewDoc(activeDoc)}>
          <Eye size={13}/> Xem tài liệu
         </button>
         <button type="button" aria-label="Bỏ chọn tài liệu" onClick={()=>setSelectedDocId('')}><X size={14}/></button>
        </div>
       )}
      </div>

      <p className="form-help">Ở chế độ B, phản hồi “Đang ghi chép” sẽ hoãn nhóm lời nhắc nhìn xuống. Quyền nghỉ và tắt hỗ trợ luôn được giữ ở cả hai chế độ.</p><Button className="full" disabled={busy}><Icon of={Play}/>{busy?'Đang tạo phiên…':'Bắt đầu phiên học'}<Icon of={ArrowRight}/></Button>
     </form>}
     {current?.status==='ended'&&<div className="ended-summary"><CheckCircle2 size={20}/><span>Phiên “{current.goal}” đã được lưu.</span><button className="text-btn" onClick={()=>showReport(current)}>Xem báo cáo</button></div>}
    </section>
    <div className="right-column">
     <section className="card camera-card">
      <div className="section-head"><div className="section-title"><Icon of={ScanFace}/><h2>Hỗ trợ qua camera</h2></div><Pill tone={camera?'green':''}>{camera?'Đang bật':'Đang tắt'}</Pill></div>
      <div className={`camera-preview ${camera?'live':''}`}><video ref={videoRef} autoPlay muted playsInline aria-label="Xem trước webcam" hidden={!camera}/>{!camera&&<div className="camera-placeholder"><span className="camera-circle"><CameraOff size={28} strokeWidth={1.3}/></span><h3>Một lựa chọn, không bắt buộc</h3><p>Bật camera để hiệu chỉnh và nhận<br/>phản hồi từ tín hiệu đầu, hướng nhìn.</p></div>}{camera&&<span className="live-tag"><span className="status-dot"/> LIVE · Ảnh không lưu</span>}</div>
      <p className="camera-note"><ShieldCheck size={15}/> Frame được gửi đến backend để xử lý. Không lưu ảnh/video mặc định.</p>
      <Button variant={camera?'secondary':'outline'} className="full" disabled={busy||!active||current.status!=='active'} onClick={()=>camera?command('support_off'):setConsent(true)}><Icon of={camera?CameraOff:Camera}/>{camera?'Tắt camera và hỗ trợ':'Bật camera'}</Button>{!active&&<small className="center muted">Bắt đầu phiên học để sử dụng camera.</small>}
     </section>
     <section className="gentle-card"><Leaf size={23} strokeWidth={1.4}/><div><h3>Không cần hoàn hảo, chỉ cần bắt đầu.</h3><p>Nhìn xuống có thể là đang ghi chép. Tín hiệu webcam không phải điểm đánh giá sự tập trung.</p></div></section>
    </div>
   </div>
  </>
 )}

 {(camera||tab==='lab')&&<section className="card debug-card"><div className="section-head"><div className="section-title"><Icon of={Activity}/><h2>Tín hiệu và hiệu chỉnh</h2></div><div style={{display:'flex',gap:10,alignItems:'center'}}>{!camera&&active&&current?.status==='active'&&<Button variant="outline" className="small" onClick={()=>setConsent(true)}><Icon of={Camera}/>Bật camera</Button>}<button className="text-btn" onClick={()=>setDebug(!debug)}>{debug?'Ẩn JSON':'Xem JSON'}</button></div></div>{!camera&&<div className="inline-note" style={{marginTop:0,marginBottom:18}}>Camera đang tắt. Vui lòng bấm <strong>Bật camera</strong> để xem tín hiệu và thực hiện hiệu chỉnh mốc đầu / hướng mắt.</div>}<div className="signal-grid"><SignalCard name="Head · MediaPipe" icon={ScanFace} data={signal?.head} available={models.head?.available} calibration={current?.calibration?.head} progress={current?.calibration_progress}/><SignalCard name="Gaze · L2CS" icon={Eye} data={signal?.gaze} available={models.gaze?.available} calibration={current?.calibration?.gaze} progress={current?.calibration_progress}/></div><div className="calibration-grid"><div className="calibration-block"><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><h3>1. Mốc đầu (Head Baseline)</h3>{current?.calibration?.head?.valid&&<Pill tone="green"><Check size={12}/> Đã đạt</Pill>}</div><p>Nhìn thẳng giữa màn hình, giữ tư thế tự nhiên trong 5 giây (cần ít nhất 15 mẫu hợp lệ).</p>{current?.calibrating==='head'&&(
<div className="calibration-progress"><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><strong>Đang thu mẫu đầu…</strong><small>{current?.calibration_progress?.sample_count||0} / {current?.calibration_progress?.required_samples||15} mẫu ({Math.min(100,Math.round(((current?.calibration_progress?.sample_count||0)/(current?.calibration_progress?.required_samples||15))*100))}%)</small></div><div style={{width:'100%',height:6,background:'#dde4d8',borderRadius:3,overflow:'hidden'}}><div style={{width:`${Math.min(100,((current?.calibration_progress?.sample_count||0)/(current?.calibration_progress?.required_samples||15))*100)}%`,height:'100%',background:'#3f694c',transition:'width .2s'}}/></div><span>Thời gian: {(current?.calibration_progress?.elapsed_seconds||0).toFixed(1)}s / 5s · Trạng thái: {current?.calibration_progress?.stable?'Tư thế ổn định ✓':'Đang cử động, hãy nhìn thẳng giữa màn hình'}</span></div>)}<div className="button-row">{current?.calibrating!=='head'?(<Button variant="outline" disabled={!camera||busy||Boolean(current?.calibrating)} onClick={()=>calibrate('head','start')}>{current?.calibration?.head?.valid?'Thu lại mốc đầu':'Thu mốc đầu'}</Button>):(<><Button variant={current?.calibration_progress?.ready?'primary':'secondary'} disabled={busy} onClick={()=>calibrate('head','finish')}>{current?.calibration_progress?.ready?'✓ Hoàn tất mốc đầu':`Hoàn tất (${current?.calibration_progress?.sample_count||0}/15)`}</Button><Button variant="ghost" disabled={busy} onClick={()=>calibrate('head','cancel')}>Hủy</Button></>)}</div></div><div className="calibration-block"><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><h3>2. Vùng hướng nhìn (Gaze Range)</h3>{current?.calibration?.gaze?.valid&&<Pill tone="green"><Check size={12}/> Đã đạt</Pill>}</div><p>Nhìn lần lượt vào giữa và 4 biên màn hình (mỗi vị trí cần ít nhất 3 mẫu).</p>{current?.calibrating==='gaze'&&(
<div className="calibration-progress"><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><strong>Mục tiêu hiện tại: {gazeTarget==='center'?'Giữa màn hình':gazeTarget==='left'?'Biên trái':gazeTarget==='right'?'Biên phải':gazeTarget==='top'?'Biên trên':'Biên dưới'}</strong><small>{current?.calibration_progress?.sample_count||0} / 15 mẫu</small></div><div className="target-progress">{[['center','Giữa'],['left','Trái'],['right','Phải'],['top','Trên'],['bottom','Dưới']].map(([tgtKey,tgtLabel])=>{const count=(current?.calibration_progress?.target_counts||{})[tgtKey]||0;const isCurrent=(current?.calibration_target||gazeTarget)===tgtKey;const isDone=count>=3;return(<button type="button" key={tgtKey} onClick={()=>{setGazeTarget(tgtKey);calibrate('gaze','target',tgtKey)}} style={{padding:'6px 11px',borderRadius:7,fontSize:12,border:isCurrent?'2px solid #315b47':'1px solid #d5ded0',background:isDone?'#eaf3e5':isCurrent?'#edf4e7':'#fff',color:isDone?'#2b5735':'#333',fontWeight:isCurrent?'700':'500',cursor:'pointer'}}>{tgtLabel}: {count}/3 {isDone?'✓':''}</button>);})}</div><span>Bấm vào từng vị trí ở trên và nhìn vào đó cho đến khi đủ 3/3 mẫu.</span></div>)}<div className="button-row">{current?.calibrating!=='gaze'?(<Button variant="outline" disabled={!camera||busy||Boolean(current?.calibrating)} onClick={()=>calibrate('gaze','start',gazeTarget)}>{current?.calibration?.gaze?.valid?'Thu lại vùng gaze':'Thu vùng gaze'}</Button>):(<><Button variant={current?.calibration_progress?.ready?'primary':'secondary'} disabled={busy} onClick={()=>calibrate('gaze','finish')}>{current?.calibration_progress?.ready?'✓ Hoàn tất gaze':`Hoàn tất (${Object.values(current?.calibration_progress?.target_counts||{}).reduce((a,b)=>a+Math.min(3,b),0)}/15)`}</Button><Button variant="ghost" disabled={busy} onClick={()=>calibrate('gaze','cancel')}>Hủy</Button></>)}</div></div></div>{debug&&<pre className="json-view">{JSON.stringify({signal,calibration:current?.calibration,progress:current?.calibration_progress},null,2)}</pre>}</section>}
 {tab==='lab'&&<section className="card"><div className="section-head"><div className="section-title"><Icon of={NotebookPen}/><h2>Gán nhãn hành vi theo thời gian</h2></div><Pill>{annotationCount} mốc trong lần mở này</Pill></div><p className="muted">Chọn nhãn theo hành vi thực hiện, không theo góc model dự đoán. Nhấn ghi mốc khi bắt đầu mỗi đoạn; dùng “transition” khi đang chuyển động.</p><div className="annotation-grid">{Object.entries({head_label:['neutral','turn_left','turn_right','down','up','tilt_left','tilt_right','unknown'],gaze_target:['screen_center','screen_edge','screen_other','outside_left','outside_right','outside_up','outside_down','notebook','unknown'],face_condition:['visible','out_of_frame','occluded','multiple_faces','uncertain'],activity:['reading','writing_notes','exercise','watching','scripted_test'],annotation_status:['stable','transition','uncertain']}).map(([key,values])=><Field key={key} label={{head_label:'Tư thế đầu',gaze_target:'Mục tiêu nhìn',face_condition:'Điều kiện mặt',activity:'Hoạt động',annotation_status:'Trạng thái nhãn'}[key]}><select value={annotation[key]} onChange={e=>setAnnotation({...annotation,[key]:e.target.value})}>{values.map(v=><option key={v}>{v}</option>)}</select></Field>)}</div><Button disabled={!active} onClick={annotate}><Icon of={Plus}/>Ghi mốc hành vi</Button><p className="form-help">Nhãn gaze là mục tiêu được hướng dẫn nhìn, không phải phép đo eye tracker. Các kịch bản thử riêng không thay thế user study A/B.</p></section>}
 {tab==='study'&&<section className="card recent-card"><div className="section-head"><h2>Những phiên học gần đây</h2><button className="text-btn" onClick={()=>setTab('history')}>Xem tất cả <ArrowUpRight size={15}/></button></div><SessionList sessions={sessions.slice(0,3)} onOpen={openSession} onReport={showReport}/></section>}</>}

 {tab==='docs'&&<>
  <div className="page-heading">
   <div>
    <span className="eyebrow">TẬP TRUNG · ĐỌC SÁCH · TÀI LIỆU HỌC</span>
    <h1>Kho tài liệu học tập PDF</h1>
    <p>Đẩy giáo trình, bài giảng, đề thi từ máy tính lên để đọc trực tiếp khi học mà không cần rời tab.</p>
   </div>
   <label className="btn pdf-upload-btn">
    <FileUp size={17}/>
    <span>Tải PDF từ máy</span>
    <input type="file" accept=".pdf,application/pdf" style={{display:'none'}} onChange={e=>{if(e.target.files?.[0]){uploadDocument(e.target.files[0]);e.target.value=''}}}/>
   </label>
  </div>
  <div className="stats-row">
   <Stat icon={BookOpen} label="Tài liệu đã tải" value={documents.length} unit="file"/>
   <Stat icon={Clock3} label="Dung lượng lưu trữ" value={formatBytes(documents.reduce((a,d)=>a+(d.file_size||0),0))} unit=""/>
   <Stat icon={Target} label="Đang học cùng" value={current?.document_name?1:0} unit="tài liệu"/>
  </div>
  <section className="card">
   <div className="section-head"><div className="section-title"><Icon of={FileUp}/><h2>Đẩy tài liệu PDF mới từ máy tính</h2></div></div>
   <PdfDropzone onUpload={uploadDocument} uploading={uploadingDoc}/>
  </section>
  <section className="card">
   <div className="section-head">
    <div className="section-title"><Icon of={BookOpen}/><h2>Danh sách tài liệu của bạn ({documents.length})</h2></div>
    <button className="text-btn" onClick={loadDocuments}><Icon of={RefreshCw}/>Làm mới</button>
   </div>
   {!documents.length?(
    <div className="empty-state">
     <span className="small-icon"><BookOpen size={26}/></span>
     <h3>Chưa có tài liệu PDF nào</h3>
     <p>Kéo thả hoặc nhấn vào ô tải lên ở trên để thêm tài liệu PDF từ máy tính của bạn.<br/>Tài liệu sẽ sẵn sàng để mở đọc ngay trong các phiên học.</p>
    </div>
   ):(
    <div className="doc-list">
     {documents.map(d=>(
      <div key={d.id} className={`doc-card ${currentDocId===d.id?'active':''}`}>
       <div className="doc-card-info">
        <span className="pdf-icon-badge"><FileText size={20}/></span>
        <div>
         <strong>{d.filename}</strong>
         <small>{formatBytes(d.file_size)} · Tải lên {dateText(d.created_at)}{currentDocId===d.id?' · Đang gắn với phiên học':''}</small>
        </div>
       </div>
       <div className="doc-card-actions">
        <Button variant="secondary" className="small" onClick={()=>startStudyWithDoc(d)} title="Bắt đầu phiên học với tài liệu này"><Play size={14}/><span>Học tài liệu này</span></Button>
        <Button variant="outline" className="small" onClick={()=>setPreviewDoc(d)} title="Đọc tài liệu ngay trên trang"><BookOpen size={14}/><span>Đọc ngay</span></Button>
        <a className="btn ghost small" href={`${API}/documents/${d.id}/file`} target="_blank" rel="noopener noreferrer" title="Mở trong tab riêng của trình duyệt"><ExternalLink size={15}/></a>
        <button className="icon-btn danger-text" onClick={()=>setConfirmDeleteDoc(d)} title="Xóa tài liệu" aria-label={`Xóa tài liệu ${d.filename}`}><Trash2 size={16}/></button>
       </div>
      </div>
     ))}
    </div>
   )}
  </section>
 </>}

 {tab==='history'&&<><div className="page-heading"><div><span className="eyebrow">NHÌN LẠI ĐỂ HIỂU MÌNH HƠN</span><h1>Lịch sử phiên học</h1><p>Thời gian, dấu hiệu và phản hồi — không có điểm tập trung.</p></div><Button variant="outline" onClick={()=>refresh().catch(e=>setError(e.message))}><Icon of={RefreshCw}/>Làm mới</Button></div><div className="stats-row"><Stat icon={Clock3} label="Tổng thời gian đã ghi" value={totalMinutes} unit="phút"/><Stat icon={BookOpen} label="Tổng số phiên" value={sessions.length} unit="phiên"/><Stat icon={CheckCircle2} label="Đã kết thúc" value={ended.length} unit="phiên"/></div><section className="card"><SessionList sessions={sessions} onOpen={openSession} onReport={showReport} onDelete={setConfirmDelete}/></section></>}
 {tab==='settings'&&<><div className="page-heading"><div><span className="eyebrow">MINH BẠCH VÀ CHỦ ĐỘNG</span><h1>Thiết lập không gian học</h1><p>Kiểm tra kết nối và hiểu cách dữ liệu của bạn được xử lý.</p></div></div><div className="settings-grid"><section className="card"><div className="section-head"><h2>Tài khoản</h2><Icon of={ShieldCheck}/></div><Field label="Tên hiển thị"><input readOnly value={user.name||''}/></Field><Field label="Email"><input readOnly value={user.email||''}/></Field><Button variant="outline" onClick={logout}><Icon of={LogOut}/>Đăng xuất</Button></section><section className="card"><div className="section-head"><h2>Trạng thái model</h2><button className="icon-btn" aria-label="Kiểm tra lại model" onClick={loadHealth}><Icon of={RefreshCw}/></button></div>{['head','gaze'].map(k=><div className="model-status" key={k}><div><strong>{k==='head'?'MediaPipe Face Landmarker':'L2CS-Net'}</strong><p>{models[k]?.available?'Đã nạp, sẵn sàng suy luận':models[k]?.error||'Chưa có dữ liệu trạng thái. Kiểm tra backend.'}</p></div><Pill tone={models[k]?.available?'green':'amber'}>{models[k]?.available?'Sẵn sàng':'Chưa sẵn sàng'}</Pill></div>)}</section><section className="card privacy-card"><h2>Dữ liệu và quyền kiểm soát</h2><div className="privacy-items"><div><Icon of={CameraOff}/><h3>Camera do bạn quyết định</h3><p>Từ chối camera vẫn dùng được timer. Tab ẩn, nghỉ, kết thúc và đăng xuất sẽ đóng stream. Camera không tự mở lại.</p></div><div><Icon of={ShieldCheck}/><h3>Không lưu hình ảnh mặc định</h3><p>Frame gửi tới backend để suy luận. Lịch sử lưu số liệu, sự kiện, phản hồi và nhãn bạn ghi; không lưu nội dung bàn phím.</p></div><div><Icon of={Trash2}/><h3>Xuất hoặc xóa từng phiên</h3><p>Vào Lịch sử để tải CSV, xem báo cáo hoặc xóa dữ liệu của phiên. Không thể khôi phục sau khi xóa.</p></div></div></section></div></>}
 <footer className="page-footer"><span>FocusStudy · Nhóm 5 · HMI</span><span>Học chủ động. Phản hồi nhẹ nhàng.</span></footer></div></main>
 {prompt&&active&&<aside className="prompt-toast" aria-live="polite"><div className="section-head"><span className="eyebrow">MỘT LỜI NHẮC NHẸ</span><span className="pill">Có thể bỏ qua</span></div><h3>{reasons[prompt.reason]||prompt.message||'Bạn có muốn điều chỉnh nhịp học một chút?'}</h3><p>Đây là dấu hiệu quan sát, không phải kết luận mất tập trung.</p><div className="prompt-actions">{[['return','Quay lại học'],['notes','Đang ghi chép'],['outside','Học ngoài web'],['snooze','Nhắc sau'],['break','Nghỉ một chút']].map(([a,t])=><Button key={a} variant="outline" disabled={busy} onClick={()=>feedback(a)}>{t}</Button>)}</div></aside>}
 {consent&&<Modal title="Bật hỗ trợ qua camera" onClose={()=>setConsent(false)}><p>Ảnh webcam sẽ được truyền đến backend của ứng dụng để MediaPipe và L2CS xử lý. Với cấu hình chạy cục bộ, backend ở trên máy của bạn.</p><div className="privacy-note"><Icon of={ShieldCheck}/><p>Không lưu ảnh/video mặc định. Bạn có thể tắt bất cứ lúc nào. Hướng đầu và mắt không chứng minh bạn có tập trung hay không.</p></div><p className="muted">Sau khi bật, hãy hiệu chỉnh đầu và gaze. Nhánh chưa sẵn sàng sẽ được báo rõ, không dùng số liệu giả.</p><div className="button-row"><Button variant="outline" onClick={()=>setConsent(false)}>Dùng timer thôi</Button><Button disabled={busy} onClick={startCamera}><Icon of={Camera}/>Đồng ý và bật camera</Button></div></Modal>}
 {confirmDelete&&<Modal title="Xóa phiên học này?" onClose={()=>setConfirmDelete(null)}><p>Toàn bộ log, phản hồi và nhãn của “{confirmDelete.goal}” sẽ được xóa. Thao tác này không thể hoàn tác.</p><div className="button-row"><Button variant="outline" onClick={()=>setConfirmDelete(null)}>Giữ lại</Button><Button variant="danger" disabled={busy} onClick={remove}><Icon of={Trash2}/>Xóa phiên</Button></div></Modal>}
 {confirmDeleteDoc&&<Modal title="Xóa tài liệu này?" onClose={()=>setConfirmDeleteDoc(null)}><p>Tài liệu <strong>{confirmDeleteDoc.filename}</strong> ({formatBytes(confirmDeleteDoc.file_size)}) sẽ bị xóa vĩnh viễn khỏi danh sách học tập.</p><div className="button-row"><Button variant="outline" onClick={()=>setConfirmDeleteDoc(null)}>Giữ lại</Button><Button variant="danger" disabled={busy} onClick={removeDoc}><Icon of={Trash2}/>Xóa tài liệu</Button></div></Modal>}
 {previewDoc&&<Modal wide title={`Tài liệu: ${previewDoc.filename}`} onClose={()=>setPreviewDoc(null)}>
  <div className="pdf-study-header" style={{margin:'0 0 10px',padding:0,border:0}}>
   <small>{previewDoc.file_size?formatBytes(previewDoc.file_size):'PDF'} · {previewDoc.created_at?`Tải lên ${dateText(previewDoc.created_at)}`:''}</small>
   <div className="button-row" style={{margin:0}}>
    <Button variant="secondary" className="small" onClick={()=>{const d=previewDoc;setPreviewDoc(null);startStudyWithDoc(d);}}><Play size={14}/>Học với tài liệu này</Button>
    <a className="btn outline small" href={`${API}/documents/${previewDoc.id}/file`} target="_blank" rel="noopener noreferrer"><ExternalLink size={14}/>Mở tab riêng</a>
   </div>
  </div>
  <div className="pdf-frame-wrapper" style={{height:'75vh',minHeight:'500px'}}>
   <object data={`${API}/documents/${previewDoc.id}/file#toolbar=1`} type="application/pdf" className="pdf-frame">
    <iframe src={`${API}/documents/${previewDoc.id}/file#toolbar=1`} title={previewDoc.filename} className="pdf-frame">
     <p>Trình duyệt chưa hỗ trợ nhúng PDF. <a href={`${API}/documents/${previewDoc.id}/file`} target="_blank" rel="noreferrer">Mở tab riêng</a>.</p>
    </iframe>
   </object>
  </div>
 </Modal>}
 {report&&<ReportModal report={report} onClose={()=>setReport(null)} onRating={async(promptId,rating)=>{try{await post(`/sessions/${(report.session||report).id}/ratings`,{prompt_id:promptId,rating});setReport(await request(`/sessions/${(report.session||report).id}/report`));setNotice('Đã lưu đánh giá hữu ích riêng.')}catch(e){setError(e.message)}}}/>}
 </div>
}
function Stat({icon,label,value,unit}){return <div className="stat"><span className="stat-icon"><Icon of={icon}/></span><div><p>{label}</p><strong>{value}<small>{unit}</small></strong></div></div>}
function SignalCard({name,icon,data,available,calibration,progress}){const angle=key=>{const v=data?.[`${key}_deg`]??data?.[key];return typeof v==='number'?`${v.toFixed(1)}°`:'—'};const isCalibrating=progress?.branch===(name.startsWith('Head')?'head':'gaze');return <div className="signal-card"><div className="section-head"><span className="section-title"><Icon of={icon}/><strong>{name}</strong></span><Pill tone={data?.valid?'green':'amber'}>{data?.valid?'Hợp lệ':available?'Chưa hợp lệ':'Chưa sẵn sàng'}</Pill></div><div className="angle-row">{['yaw','pitch',...(name.startsWith('Head')?['roll']:[])].map(k=><div key={k}><span>{k}</span><strong>{angle(k)}</strong></div>)}</div><small>{data?.reason||(data?.valid?'Tín hiệu ổn định':'Chưa có mẫu webcam')}</small><p className="calibration-status">Hiệu chỉnh: {calibration?.valid?'Đã đạt ✓':isCalibrating?`Đang thu (${progress?.sample_count||0}/${progress?.required_samples||15})`:'Chưa đạt'}{calibration?.samples?` · ${calibration.samples} mẫu`:''}</p></div>}
function SessionList({sessions,onOpen,onReport,onDelete}){if(!sessions.length)return <div className="empty-state"><span className="small-icon"><BookOpen size={26}/></span><h3>Trang mới cho việc học của bạn</h3><p>Phiên học đầu tiên sẽ xuất hiện tại đây.<br/>Bắt đầu bằng một mục tiêu nhỏ nhé.</p></div>;return <div className="session-list">{sessions.map(s=><div className="session-row" key={s.id}><span className="session-type-icon"><BookOpen size={20}/></span><div className="session-description"><strong>{s.goal}</strong><small>{dateText(s.created_at)} · {modes[s.mode]} · {s.condition}{s.document_name?` · 📄 ${s.document_name}`:''}</small></div><div className="session-minutes"><strong>{Math.floor((s.active_seconds||0)/60)} phút</strong><Pill tone={s.status==='ended'?'green':''}>{statuses[s.status]||s.status}</Pill></div><div className="row-actions">{s.status!=='ended'&&<button className="icon-btn" title="Mở phiên" aria-label={`Mở phiên ${s.goal}`} onClick={()=>onOpen(s)}><Play size={17}/></button>}<button className="icon-btn" title="Xem báo cáo" aria-label={`Báo cáo ${s.goal}`} onClick={()=>onReport(s)}><ArrowUpRight size={18}/></button>{onDelete&&<button className="icon-btn danger-text" title="Xóa phiên" aria-label={`Xóa phiên ${s.goal}`} onClick={()=>onDelete(s)}><Trash2 size={17}/></button>}</div></div>)}</div>}
function ReportModal({report,onClose,onRating}){const s=report.session||report,metrics=report.metrics||report.summary||report,prompts=report.prompts||(report.logs||[]).filter(x=>x.kind==='prompt_shown').map(x=>({...x.data,created_at:x.at})),events=report.events||(report.logs||[]).filter(x=>x.kind==='event'),annotations=report.annotations||(report.logs||[]).filter(x=>x.kind==='annotation');return <Modal wide title="Báo cáo phiên học" onClose={onClose}><div className="report-heading"><h3>{s.goal}</h3><p>{modes[s.mode]} · Chế độ {s.condition} · {dateText(s.created_at)}</p></div><div className="report-stats"><Stat icon={Clock3} label="Thời gian học" value={Math.floor((s.active_seconds||metrics.active_seconds||0)/60)} unit="phút"/><Stat icon={Coffee} label="Thời gian nghỉ" value={Math.floor((s.break_seconds||metrics.break_seconds||0)/60)} unit="phút"/><Stat icon={Activity} label="Lời nhắc đã hiện" value={metrics.prompt_count??prompts.filter(p=>p.shown_at).length} unit="lần"/></div><div className="alert notice"><ShieldCheck size={18}/><span>Không có dấu hiệu không đồng nghĩa chắc chắn tập trung. Thời gian thiếu dữ liệu và nghỉ cần được xem riêng.</span></div><div className="section-head"><h3>Lời nhắc và đánh giá hữu ích</h3><a className="btn outline" href={`${API}/sessions/${s.id}/export`}><Download size={16}/>Xuất CSV</a></div>{prompts.length?<div className="report-prompts">{prompts.map(p=><div className="report-prompt" key={p.id}><div><strong>{reasons[p.reason]||p.reason}</strong><small>{p.shown_at?'Đã hiển thị':'Chưa hiển thị'} · {dateText(p.shown_at||p.created_at)}</small></div>{p.shown_at&&<div className="button-row"><button className="btn outline small" onClick={()=>onRating(p.id,true)}>Hữu ích</button><button className="btn outline small" onClick={()=>onRating(p.id,false)}>Chưa hữu ích</button></div>}</div>)}</div>:<p className="muted">Chưa có lời nhắc trong phiên này. Chưa đủ quan sát để tính tỷ lệ hữu ích.</p>}<h3>Dữ liệu phiên</h3><p className="muted">{events.length} sự kiện · {annotations.length} mốc gán nhãn. Dữ liệu thiếu giữ giá trị null, không thay bằng góc 0.</p><details><summary>Xem dữ liệu báo cáo chi tiết</summary><pre className="json-view">{JSON.stringify(report,null,2)}</pre></details></Modal>}
createRoot(document.getElementById('root')).render(<App/>);
