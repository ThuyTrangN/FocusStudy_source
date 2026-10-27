import asyncio,contextlib,base64,csv,hashlib,hmac,io,json,os,secrets,sqlite3,time,uuid,threading
from pathlib import Path
from functools import wraps,lru_cache
from importlib import metadata
from pypdf import PdfReader
from contextlib import asynccontextmanager
import numpy as np
from PIL import Image
from fastapi import FastAPI,Request,Response,HTTPException,Depends,UploadFile,File
from fastapi.responses import StreamingResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from starlette.concurrency import run_in_threadpool
from backend.policy import evaluate,DEFAULTS
from vision.adapters import Vision

DB=os.getenv('FOCUSSTUDY_DB','data/focusstudy.sqlite3'); DOCS_DIR=os.getenv('FOCUSSTUDY_DOCS',str(Path(DB).parent/'documents')); GAZE_TARGETS=('center','left','right','top','bottom'); GAZE_SAMPLES_PER_TARGET=3; states={}; lock=threading.RLock(); vision_lock=threading.Lock(); engine=None

def serialized(function):
    @wraps(function)
    def wrapped(*args,**kwargs):
        with lock:return function(*args,**kwargs)
    return wrapped

def db():
    Path(DB).parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c

def init():
    Path(DOCS_DIR).mkdir(parents=True,exist_ok=True)
    with db() as c:c.executescript('''CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,name TEXT,email TEXT UNIQUE,password TEXT); CREATE TABLE IF NOT EXISTS tokens(token TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id),expires REAL); CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id),data TEXT); CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY,session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,kind TEXT,at REAL,data TEXT); CREATE TABLE IF NOT EXISTS commands(session_id TEXT,event_id TEXT,PRIMARY KEY(session_id,event_id)); CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id),session_id TEXT,filename TEXT,file_path TEXT,file_size INTEGER,created_at REAL);''')
    with db() as c:
        columns={r['name'] for r in c.execute('PRAGMA table_info(documents)')}
        if 'sha256' not in columns:c.execute('ALTER TABLE documents ADD COLUMN sha256 TEXT')
        c.execute('PRAGMA user_version=1')
@lru_cache(maxsize=1)
def model_manifest():
    result={'packages':{},'checkpoints':[],'kind':'pretrained','unit':'degrees','axis_version':'upstream-6829e9c-unverified-on-person'}
    for name in ('mediapipe','torch','torchvision','l2cs'):
        try:result['packages'][name]=metadata.version(name)
        except metadata.PackageNotFoundError:result['packages'][name]=None
    for path in (os.getenv('MEDIAPIPE_MODEL','models/face_landmarker.task'),os.getenv('L2CS_MODEL','models/L2CSNet_gaze360.pkl')):
        p=Path(path)
        result['checkpoints'].append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None})
    return result

def checkpoint_states():
    with lock:
        for state in list(states.values()):accrue(state);save(state)

async def checkpoint_loop():
    while True:
        await asyncio.sleep(5)
        await run_in_threadpool(checkpoint_states)

@asynccontextmanager
async def lifespan(app):
    global engine
    init();engine=await run_in_threadpool(Vision)
    await run_in_threadpool(model_manifest)
    task=asyncio.create_task(checkpoint_loop())
    try:yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):await task
        await run_in_threadpool(checkpoint_states)
        if getattr(engine,'head',None):engine.head.close()
app=FastAPI(title='FocusStudy',lifespan=lifespan)

@app.middleware('http')
async def origin_guard(request,call_next):
    if request.method not in ('GET','HEAD','OPTIONS'):
        origin=request.headers.get('origin')
        allowed={str(request.base_url).rstrip('/'),'http://localhost:5173','http://127.0.0.1:5173','http://localhost:8000','http://127.0.0.1:8000'}
        if origin and origin not in allowed:
            if not (origin.startswith('http://localhost:') or origin.startswith('http://127.0.0.1:')):
                return Response('Origin not allowed',403)
    return await call_next(request)

def user(request:Request):
    token=request.cookies.get('focusstudy') or request.query_params.get('token')
    with db() as c:r=c.execute('SELECT users.id,name,email FROM tokens JOIN users ON users.id=tokens.user_id WHERE token=? AND expires>?',(hashlib.sha256((token or '').encode()).hexdigest(),time.time())).fetchone()
    if not r:raise HTTPException(401,'Vui lòng đăng nhập')
    return dict(r)

def password(p,salt=None):
    salt=salt or secrets.token_hex(16)
    return salt+':'+hashlib.scrypt(p.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()
class Auth(BaseModel):
    email:str=Field(min_length=3,max_length=254);password:str=Field(min_length=8,max_length=128);name:str=Field(default='Sinh viên',max_length=80)

def login_cookie(uid,response):
    token=secrets.token_urlsafe(32)
    with db() as c:c.execute('INSERT INTO tokens VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,time.time()+86400*7))
    response.set_cookie('focusstudy',token,httponly=True,samesite='lax',secure=os.getenv('COOKIE_SECURE')=='1',max_age=604800)
@app.post('/api/auth/register')
def register(a:Auth,response:Response):
    email=a.email.strip().lower()
    if '@' not in email:raise HTTPException(422,'Email không hợp lệ')
    uid=str(uuid.uuid4())
    try:
        with db() as c:c.execute('INSERT INTO users VALUES(?,?,?,?)',(uid,a.name.strip() or 'Sinh viên',email,password(a.password)))
    except sqlite3.IntegrityError:raise HTTPException(409,'Email đã được sử dụng')
    login_cookie(uid,response);return dict(id=uid,name=a.name,email=email)
@app.post('/api/auth/login')
def login(a:Auth,response:Response):
    with db() as c:r=c.execute('SELECT * FROM users WHERE email=?',(a.email.strip().lower(),)).fetchone()
    if not r or not hmac.compare_digest(password(a.password,r['password'].split(':')[0]),r['password']):raise HTTPException(401,'Email hoặc mật khẩu không đúng')
    login_cookie(r['id'],response);return {k:r[k] for k in ('id','name','email')}
@app.get('/api/auth/me')
def me(u=Depends(user)):return u
class Profile(BaseModel):
    name:str=Field(min_length=1,max_length=80)
@app.patch('/api/auth/me')
def profile(a:Profile,u=Depends(user)):
    name=a.name.strip()
    if not name:raise HTTPException(422,'Tên không được để trống')
    with db() as c:c.execute('UPDATE users SET name=? WHERE id=?',(name,u['id']))
    return {**u,'name':name}
@app.post('/api/auth/logout')
def logout(request:Request,response:Response,u=Depends(user)):
    with lock:
        for s in listing(u):
            if s['status'] in ('active','break'):
                state=accrue(load(s['id'],u));close_detector_events(state,'logout');state.update(status='paused',support=False,prompt=None,counters={},state_version=state['state_version']+1);save(state);log(state,'command',{'type':'logout_pause','status':'paused'})
    with db() as c:c.execute('DELETE FROM tokens WHERE token=?',(hashlib.sha256(request.cookies.get('focusstudy','').encode()).hexdigest(),))
    response.delete_cookie('focusstudy');return {'ok':True}
@app.get('/api/health')
def health():return {'ok':True,'models':engine.health() if engine else {},'mode':'real-inference-only'}

@serialized
def load(sid,u):
    with db() as c:r=c.execute('SELECT * FROM sessions WHERE id=? AND user_id=?',(sid,u['id'])).fetchone()
    if not r:raise HTTPException(404,'Không tìm thấy phiên')
    if sid not in states:
        s=json.loads(r['data']);s.update(support=False,prompt=None,counters={},last_sample=None)
        if s['status'] in ('active','break'):s['status']='paused'
        close_detector_events(s,'process_restart');s['state_version']+=1;s['active_events']={}
        for key in ('last_shown','snooze_until','downward_until','last_frame','calibrating','calibration_samples','calibration_target_samples','calibration_target','calibration_started'):s.pop(key,None)
        s['tick']=time.monotonic();states[sid]=s;save(s);log(s,'recovery',{'status':s['status'],'reason':'process_restart','unobserved_time_excluded':True})
    return states[sid]
def close_detector_events(s,cause,kinds=None):
    active=s.setdefault('active_events',{})
    for kind in list(active):
        if kinds is not None and kind not in kinds:continue
        event=active.pop(kind)
        finish=event['last_valid_mono']
        log(s,'detector_event_end',{'id':event['id'],'type':kind,'start_at':event['start_at'],'end_at':event['start_at']+max(0,finish-event['start_mono']),'duration_seconds':max(0,finish-event['start_mono']),'cause':cause})

def record_detector_events(s,now,frame_id):
    ready=set(s.get('detected_events',[]));active=s.setdefault('active_events',{})
    close_detector_events(s,'condition_invalid_or_gap',set(active)-ready)
    for kind in ready:
        if kind not in active:
            start=s['counters'][kind]
            active[kind]={'id':str(uuid.uuid4()),'start_mono':start,'start_at':time.time()-max(0,now-start),'last_valid_mono':now}
            log(s,'detector_event',{'id':active[kind]['id'],'type':kind,'start_at':active[kind]['start_at'],'eligible_at':time.time(),'frame_id':frame_id,'state_version':s['state_version']})
        active[kind]['last_valid_mono']=now

@serialized
def accrue(s):
    now=time.monotonic();previous=s.get('tick',now);dt=max(0,now-previous);s['tick']=now
    if s['status']=='active':
        s['active_seconds']+=dt
        fresh=max(0,min(now,s.get('signal_mono',-1e9)+2)-previous) if s.get('support') else 0
        validity=s.get('signal_valid',{})
        for branch in (('head','gaze','camera') if s.get('schema_version')==1 else ()):
            covered=fresh if (any(validity.values()) if branch=='camera' else validity.get(branch,False)) else 0
            key=branch+'_missing_seconds';s[key]=s.get(key,0)+max(0,dt-covered)
    if s['status']=='break':s['break_seconds']+=dt
    if s['status']=='paused':s['paused_seconds']=s.get('paused_seconds',0)+dt
    if s.get('prompt') and now-s['prompt'].get('created_mono',now)>15:
        log(s,'prompt_expired',s['prompt']);s['prompt']=None
    if now-s.get('signal_mono',-1e9)>2:
        close_detector_events(s,'stale');s['counters']={};s['detected_events']=[]
    return s

@serialized
def view(s):
    accrue(s);save(s);out={k:v for k,v in s.items() if k not in ('counters','calibration_samples','calibration_target_samples','tick','last_sample','signal_mono','signal_valid')}
    now=time.monotonic();out['snooze_remaining']=max(0,s.get('snooze_until',0)-now);out['downward_remaining']=max(0,s.get('downward_until',0)-now)
    if s.get('calibrating'):
        samples=s.get('calibration_samples',[])
        stable=True
        if s['calibrating']=='head' and len(samples)>=2:
            stable=bool(np.max(np.std(np.asarray(samples[-15:],dtype=float),axis=0))<=7.5)
        elapsed=max(0,now-s.get('calibration_started',now))
        progress={'branch':s['calibrating'],'sample_count':len(samples),'required_samples':15,'elapsed_seconds':elapsed,'required_seconds':5,'stable':stable}
        if s['calibrating']=='gaze':
            target_samples=s.get('calibration_target_samples',{})
            progress['target_counts']={target:len(target_samples.get(target,[])) for target in GAZE_TARGETS}
            progress['required_per_target']=GAZE_SAMPLES_PER_TARGET
            progress['ready']=elapsed>=5 and all(count>=GAZE_SAMPLES_PER_TARGET for count in progress['target_counts'].values())
        else:
            progress['ready']=len(samples)>=15 and elapsed>=5 and stable
        out['calibration_progress']=progress
    return out

def complete_calibration(s,branch):
    samples=s['calibration_samples']
    arr=np.asarray(samples[-15:] if branch=='head' else samples,dtype=float)
    profile={'samples':len(samples),'valid':True}
    if branch=='head':
        profile.update(yaw=float(np.median(arr[:,0])),pitch=float(np.median(arr[:,1])))
    else:
        target_samples=s['calibration_target_samples']
        target_profiles={target:{'samples':len(target_samples[target]),'yaw':float(np.median(np.asarray(target_samples[target])[:,0])),'pitch':float(np.median(np.asarray(target_samples[target])[:,1]))} for target in GAZE_TARGETS}
        profile.update(yaw_min=float(np.percentile(arr[:,0],5)-5),yaw_max=float(np.percentile(arr[:,0],95)+5),pitch_min=float(np.percentile(arr[:,1],5)-5),pitch_max=float(np.percentile(arr[:,1],95)+5),targets=target_profiles)
    s['calibration'][branch]=profile;s['calibrating']=None
    for key in ('calibration_samples','calibration_target_samples','calibration_target','calibration_started'):s.pop(key,None)
    s['state_version']+=1;s['counters']={};log(s,'calibration',{'branch':branch,**profile})
    return profile

@serialized
def save(s):
    with db() as c:c.execute('UPDATE sessions SET data=? WHERE id=?',(json.dumps(s),s['id']))
@serialized
def log(s,kind,data):
    with db() as c:c.execute('INSERT INTO logs(session_id,kind,at,data) VALUES(?,?,?,?)',(s['id'],kind,time.time(),json.dumps(data)))
class NewSession(BaseModel):
    goal:str=Field(min_length=1,max_length=300);duration_minutes:int=Field(default=25,ge=1,le=240);mode:str='reading';condition:str='B';document_id:str|None=None;request_id:str|None=Field(default=None,max_length=128)
@app.post('/api/sessions')
@serialized
def create(a:NewSession,u=Depends(user)):
    if a.request_id:
        with db() as c:previous=c.execute("SELECT id FROM sessions WHERE user_id=? AND json_extract(data,'$.request_id')=?",(u['id'],a.request_id)).fetchone()
        if previous:return view(load(previous['id'],u))
    if a.mode not in ('reading','exercise','watching') or a.condition not in ('A','B'):raise HTTPException(422,'Chế độ không hợp lệ')
    if not a.goal.strip():raise HTTPException(422,'Mục tiêu không được để trống')
    doc_name=None
    if a.document_id:
        with db() as c:
            d=c.execute('SELECT id,filename FROM documents WHERE id=? AND user_id=?',(a.document_id,u['id'])).fetchone()
            if not d:raise HTTPException(404,'Không tìm thấy tài liệu')
            doc_name=d['filename']
    s=dict(id=str(uuid.uuid4()),**a.model_dump(),document_name=doc_name,status='created',support=False,state_version=0,active_seconds=0.,break_seconds=0.,created_at=time.time(),tick=time.monotonic(),calibration={},prompt=None,counters={},policy_config={**DEFAULTS,'gap_s':2},model_manifest=model_manifest(),schema_version=1,paused_seconds=0.,head_missing_seconds=0.,gaze_missing_seconds=0.,camera_missing_seconds=0.)
    with db() as c:c.execute('INSERT INTO sessions VALUES(?,?,?)',(s['id'],u['id'],json.dumps(s)))
    states[s['id']]=s;return view(s)
@app.get('/api/sessions')
@serialized
def listing(u=Depends(user)):
    with db() as c:rows=c.execute('SELECT id FROM sessions WHERE user_id=? ORDER BY rowid DESC',(u['id'],)).fetchall()
    return [view(load(r['id'],u)) for r in rows]
@app.get('/api/sessions/{sid}')
@serialized
def detail(sid:str,u=Depends(user)):return view(load(sid,u))
def ensure_single_active(sid,u):
    with db() as c:rows=c.execute('SELECT id FROM sessions WHERE user_id=? AND id<>?',(u['id'],sid)).fetchall()
    for row in rows:
        if load(row['id'],u)['status'] in ('active','break'):
            raise HTTPException(409,'Hãy tạm dừng hoặc kết thúc phiên đang diễn ra trước')

class Command(BaseModel):
    type:str;event_id:str=Field(default_factory=lambda:str(uuid.uuid4()));prompt_id:str|None=None;expected_state_version:int|None=None
@app.post('/api/sessions/{sid}/commands')
def command(sid:str,a:Command,u=Depends(user)):
    with lock:
        s=accrue(load(sid,u))
        with db() as c:
            if c.execute('SELECT 1 FROM commands WHERE session_id=? AND event_id=?',(sid,a.event_id)).fetchone():return view(s)
        if a.expected_state_version is not None and a.expected_state_version!=s['state_version']:raise HTTPException(409,'Phiên đã thay đổi, tải lại trạng thái')
        if s['status']=='ended':raise HTTPException(409,'Phiên đã kết thúc')
        if a.type=='prompt_timeout':
            if s.get('prompt') and s['prompt']['id']==a.prompt_id:
                log(s,'prompt_expired',s['prompt']);s['prompt']=None
        elif a.type=='prompt_shown':
            if s['prompt'] and s['prompt']['id']==a.prompt_id and not s['prompt'].get('shown_at'):
                s['last_shown']=time.monotonic();s['prompt']['shown_at']=time.time();log(s,'prompt_shown',s['prompt'])
        else:
            transitions={'start':('created','active'),'pause':('active','paused'),'break':('active','break')}
            if a.type in transitions:
                prev,nxt=transitions[a.type]
                if s['status']!=prev:raise HTTPException(409,'Chuyển trạng thái không hợp lệ')
                ensure_single_active(sid,u) if nxt=='active' else None
                s['status']=nxt
            elif a.type=='resume':
                if s['status'] not in ('paused','break'):raise HTTPException(409,'Phiên không tạm dừng')
                ensure_single_active(sid,u);s['status']='active'
            elif a.type=='end':s['status']='ended';s['ended_at']=time.time()
            elif a.type=='support_on':
                if s['status']!='active':raise HTTPException(409,'Hãy bắt đầu phiên trước')
                if time.monotonic()<s.get('outside_until',0):raise HTTPException(409,'Đang tạm ngừng hỗ trợ khi học ngoài web')
                s['support']=True
            elif a.type=='support_off':s['support']=False
            else:raise HTTPException(422,'Lệnh không hợp lệ')
            if a.type not in ('support_on','start'):s['support']=False
            if a.type=='support_on':
                s['calibration']={};s.pop('last_frame',None)
            if not s['support']:
                for key in ('calibrating','calibration_samples','calibration_target_samples','calibration_target','calibration_started'):s.pop(key,None)
            close_detector_events(s,a.type);s['prompt']=None;s['counters']={};s['state_version']+=1
        with db() as c:
            c.execute('INSERT INTO logs(session_id,kind,at,data) VALUES(?,?,?,?)',(sid,'command',time.time(),json.dumps({**a.model_dump(),'status':s['status']})))
            c.execute('UPDATE sessions SET data=? WHERE id=?',(json.dumps(s),sid))
            c.execute('INSERT INTO commands VALUES(?,?)',(sid,a.event_id))
        return view(s)
class Feedback(BaseModel):
    prompt_id:str;action:str;rating:int|None=Field(default=None,ge=1,le=5)
@app.post('/api/sessions/{sid}/feedback')
def feedback(sid:str,a:Feedback,u=Depends(user)):
    with lock:
        s=accrue(load(sid,u));p=s.get('prompt')
        if s['status']!='active' or not p or not p.get('shown_at') or p['id']!=a.prompt_id:raise HTTPException(409,'Lời nhắc đã đóng hoặc hết hạn')
        if a.action not in ('return','notes','outside','snooze','break'):raise HTTPException(422,'Phản hồi không hợp lệ')
        now=time.monotonic()
        if a.action=='notes' and s['condition']=='B':s['downward_until']=now+180
        if a.action=='snooze':s['snooze_until']=now+180
        if a.action=='outside':s['support']=False;s['snooze_until']=now+300;s['outside_until']=now+300
        if a.action=='break':s['status']='break';s['support']=False
        close_detector_events(s,'feedback_'+a.action);s['prompt']=None;s['counters']={};s['state_version']+=1
        log(s,'feedback',a.model_dump());save(s);return view(s)
class Calibrate(BaseModel):
    branch:str;action:str;target:str|None=None
@app.post('/api/sessions/{sid}/calibration')
def calibration(sid:str,a:Calibrate,u=Depends(user)):
    with lock:
        s=accrue(load(sid,u))
        if s['status']!='active' or not s['support']:raise HTTPException(409,'Bật hỗ trợ trước khi hiệu chỉnh')
        if a.branch not in ('head','gaze') or a.action not in ('start','finish','target','cancel'):raise HTTPException(422,'Hiệu chỉnh không hợp lệ')
        branch_health=(engine.health() if engine else {}).get(a.branch,{})
        if a.action=='cancel':
            s['calibrating']=None
            for key in ('calibration_samples','calibration_target_samples','calibration_target','calibration_started'):s.pop(key,None)
            s['state_version']+=1;s['counters']={};save(s);return view(s)
        if a.action=='target':
            if a.branch!='gaze' or s.get('calibrating')!='gaze':raise HTTPException(409,'Chỉ đổi mục tiêu khi đang hiệu chỉnh gaze')
            if a.target not in GAZE_TARGETS:raise HTTPException(422,'Mục tiêu gaze không hợp lệ')
            s['calibration_target']=a.target;log(s,'calibration_target',{'target':a.target});save(s);return view(s)
        if a.action=='start':
            if not branch_health.get('available'):
                raise HTTPException(409,f"Không thể bắt đầu: model {a.branch} chưa sẵn sàng. Kiểm tra /api/health.")
            if a.branch=='gaze' and a.target not in GAZE_TARGETS:raise HTTPException(422,'Mục tiêu gaze không hợp lệ')
            s['calibrating']=a.branch;s['calibration_samples']=[];s['calibration'].pop(a.branch,None);s['state_version']+=1;s['counters']={};s['calibration_started']=time.monotonic()
            if a.branch=='gaze':
                s['calibration_target']=a.target;s['calibration_target_samples']={target:[] for target in GAZE_TARGETS}
        else:
            if a.action=='finish' and s.get('calibration',{}).get(a.branch,{}).get('valid'):
                return view(s)
            samples=s.get('calibration_samples',[])
            if s.get('calibrating')!=a.branch:
                if s.get('calibration',{}).get(a.branch,{}).get('valid'):
                    return view(s)
                raise HTTPException(422,'Hiệu chỉnh chưa được bắt đầu; thử lại')
            if a.branch=='gaze':
                target_samples=s.get('calibration_target_samples',{})
                progress=', '.join(f"{target}: {len(target_samples.get(target,[]))}/{GAZE_SAMPLES_PER_TARGET}" for target in GAZE_TARGETS if len(target_samples.get(target,[]))<GAZE_SAMPLES_PER_TARGET)
                if progress:raise HTTPException(422,f"Chưa đủ mẫu gaze theo từng mục tiêu ({progress}). Chọn từng mục tiêu, nhìn vào đó và chờ đủ mẫu.")
            if len(samples)<15:
                if not branch_health.get('available'):raise HTTPException(422,f"Không thể hoàn tất: model {a.branch} chưa sẵn sàng. Kiểm tra /api/health và docs/models.md.")
                elapsed=max(0,time.monotonic()-s.get('calibration_started',time.monotonic()))
                raise HTTPException(422,f"Mới nhận {len(samples)}/15 mẫu hợp lệ trong {elapsed:.1f}/5 giây. Giữ camera ổn định và đợi đủ mẫu rồi thử lại.")
            arr=np.array(samples)
            elapsed=max(0,time.monotonic()-s.get('calibration_started',0))
            if not np.isfinite(arr).all():raise HTTPException(422,'Mẫu hiệu chỉnh không hữu hạn; hãy thu lại.')
            if elapsed<5:raise HTTPException(422,f"Đã nhận đủ mẫu nhưng mới thu {elapsed:.1f}/5 giây. Chờ thêm rồi thử lại.")
            if a.branch=='head' and np.max(np.std(np.asarray(arr[-15:],dtype=float),axis=0))>7.5:raise HTTPException(422,'Tư thế chưa ổn định trong các mẫu gần nhất. Nhìn giữa màn hình, giữ đầu yên rồi chờ thêm.')
            profile=complete_calibration(s,a.branch)
        save(s);return view(s)
class Frame(BaseModel):
    image:str=Field(max_length=3000000);frame_id:int;state_version:int
@app.post('/api/sessions/{sid}/frames')
async def frame(sid:str,a:Frame,u=Depends(user)):
    s=accrue(load(sid,u))
    if s['status']!='active' or not s['support'] or a.state_version!=s['state_version']:raise HTTPException(409,'Frame không còn hợp lệ')
    if a.frame_id<=s.get('last_frame',-1):
        s['counters']={};raise HTTPException(409,'Frame sai thứ tự')
    if not vision_lock.acquire(blocking=False):raise HTTPException(429,'Model đang xử lý, bỏ frame này')
    try:
        try:
            raw=base64.b64decode(a.image.split(',')[-1],validate=True)
            im=Image.open(io.BytesIO(raw))
            if im.width*im.height>1920*1080:raise ValueError('Ảnh quá lớn')
            rgb=np.array(im.convert('RGB'))
        except Exception:raise HTTPException(422,'Ảnh không hợp lệ hoặc quá lớn')
        inference_started=time.monotonic()
        result=await run_in_threadpool(engine.infer,rgb)
        with lock:
            if time.monotonic()-inference_started>2:
                close_detector_events(s,'stale_inference');s['counters']={};s['prompt']=None;raise HTTPException(409,'Kết quả quá cũ; giảm độ phân giải hoặc kiểm tra máy')
            if s['status']!='active' or not s['support'] or a.state_version!=s['state_version']:raise HTTPException(409,'Bỏ kết quả muộn')
            s['last_frame']=a.frame_id
            for branch in ('head','gaze'):
                v=result[branch]
                if v.get('valid') and not all(np.isfinite(v.get(k,float('nan'))) for k in ('yaw','pitch')):v.update(valid=False,reason='non_finite')
            for branch in ('head','gaze'):
                v=result[branch];profile=s['calibration'].get(branch);v['calibrated']=bool(profile)
                if v['valid'] and s.get('calibrating')==branch:
                    sample=[v['yaw'],v['pitch']]
                    s.setdefault('calibration_samples',[]).append(sample)
                    if branch=='gaze' and s.get('calibration_target') in GAZE_TARGETS:
                        s.setdefault('calibration_target_samples',{}).setdefault(s['calibration_target'],[]).append(sample)
                if v['valid'] and profile:
                    if branch=='head':v['relative_yaw']=(v['yaw']-profile['yaw']+180)%360-180;v['relative_pitch']=(v['pitch']-profile['pitch']+180)%360-180
                    else:
                        h=result['head'];posture=h.get('calibrated') and abs(h.get('relative_yaw',999))<15 and abs(h.get('relative_pitch',999))<15
                        v['valid']=bool(posture)
                        if not posture:v['reason']='head_outside_verified_range'
                        v['outside']=not(profile['yaw_min']<=v['yaw']<=profile['yaw_max'] and profile['pitch_min']<=v['pitch']<=profile['pitch_max'])
                        v['direction']='down' if (v['pitch']>profile['pitch_max'] if float(os.getenv('GAZE_DOWN_SIGN','1'))>0 else v['pitch']<profile['pitch_min']) else 'other'
            if s.get('calibrating')=='gaze':
                target_samples=s.get('calibration_target_samples',{})
                target=s.get('calibration_target')
                if target in GAZE_TARGETS and len(target_samples.get(target,[]))>=GAZE_SAMPLES_PER_TARGET:
                    next_target=next((item for item in GAZE_TARGETS if len(target_samples.get(item,[]))<GAZE_SAMPLES_PER_TARGET),None)
                    if next_target:
                        s['calibration_target']=next_target
                        log(s,'calibration_target',{'target':next_target,'automatic':True})
                all_targets_complete=all(len(target_samples.get(target,[]))>=GAZE_SAMPLES_PER_TARGET for target in GAZE_TARGETS)
                elapsed=time.monotonic()-s.get('calibration_started',time.monotonic())
                if all_targets_complete and elapsed>=5:
                    complete_calibration(s,'gaze')
            elif s.get('calibrating')=='head':
                samples=s.get('calibration_samples',[])
                elapsed=time.monotonic()-s.get('calibration_started',time.monotonic())
                stable=len(samples)>=15 and np.max(np.std(np.asarray(samples[-15:],dtype=float),axis=0))<=7.5
                if len(samples)>=15 and elapsed>=5 and stable:
                    complete_calibration(s,'head')
            for b in ('head','gaze'):
                for key in ('yaw','pitch'):
                    if not result[b].get('valid'):result[b][key]=None
            accrue(s)
            s['signal_mono']=time.monotonic();s['signal_valid']={b:bool(result[b].get('valid') and result[b].get('calibrated')) for b in ('head','gaze')}
            evaluated_at=time.monotonic();candidate=evaluate(s,result,evaluated_at)
            record_detector_events(s,evaluated_at,a.frame_id)
            blocked=None
            if s.get('calibrating'):blocked='calibrating'
            elif s.get('detected_events') and not candidate:
                if s.get('prompt'):blocked='active_prompt'
                elif evaluated_at<s.get('snooze_until',0):blocked='snoozed'
                elif evaluated_at-s.get('last_shown',-1e9)<DEFAULTS['cooldown_s']:blocked='cooldown'
                elif evaluated_at<s.get('downward_until',0):blocked='downward_snoozed'
                else:blocked='no_eligible_candidate'
            if blocked!=s.get('last_blocked_reason'):
                log(s,'policy_status',{'blocked_reason':blocked,'frame_id':a.frame_id,'events':s.get('detected_events',[])})
                s['last_blocked_reason']=blocked
            if candidate and not s.get('calibrating'):
                s['prompt']={'id':str(uuid.uuid4()),**candidate,'state_version':s['state_version'],'frame_id':a.frame_id,'evidence_event_ids':[s['active_events'][candidate['reason']]['id']] if candidate['reason'] in s.get('active_events',{}) else [],'created_mono':time.monotonic(),'shown_at':None};log(s,'prompt_proposed',s['prompt'])
            log(s,'signal',{'frame_id':a.frame_id,**result});save(s)
            result.update(session_id=sid,frame_id=a.frame_id,state_version=s['state_version'])
            return {'signal':result,'prompt':s.get('prompt'),'session':view(s)}
    finally:vision_lock.release()
@app.post('/api/sessions/{sid}/annotations')
async def annotation(sid:str,request:Request,u=Depends(user)):
    data=await request.json()
    if len(json.dumps(data))>4000:raise HTTPException(422,'Nhãn quá dài')
    with lock:
        s=load(sid,u);log(s,'annotation',data)
    return {'ok':True,'at':time.time()}
@app.get('/api/sessions/{sid}/report')
@serialized
def report(sid:str,u=Depends(user)):
    s=load(sid,u);view(s)
    with db() as c:rows=c.execute('SELECT kind,at,data FROM logs WHERE session_id=? ORDER BY id',(sid,)).fetchall()
    logs=[dict(kind=r['kind'],at=r['at'],data=json.loads(r['data'])) for r in rows]
    signals=[r['data'] for r in logs if r['kind']=='signal'];shown=sum(r['kind']=='prompt_shown' for r in logs);feedbacks=sum(r['kind']=='feedback' for r in logs)
    prompts={}
    for row in logs:
        if row['kind'] in ('prompt_proposed','prompt_shown','prompt_expired'):prompts[row['data']['id']]=row['data']
    ratings=[r['data'] for r in logs if r['kind']=='rating']
    return {'prompts':list(prompts.values()),'annotations':[r for r in logs if r['kind']=='annotation'],'calibrations':[r for r in logs if r['kind']=='calibration'],'events':[r for r in logs if r['kind']=='command'],'detector_events':[r for r in logs if r['kind'] in ('detector_event','detector_event_end')],'policy_statuses':[r for r in logs if r['kind']=='policy_status'],'ratings':ratings,'helpful_ratio':sum(r['rating'] for r in ratings)/len(ratings) if ratings else None,'session':view(s),'prompt_count':shown,'feedback_count':feedbacks,'rating_count':len(ratings),'missing_convention':'Active seconds without a calibrated valid branch in the preceding 2 seconds; camera is union, not head+gaze sum','response_rate':feedbacks/shown if shown else None,'signal_count':len(signals),'head_valid_ratio':sum(x['head']['valid'] for x in signals)/len(signals) if signals else None,'gaze_valid_ratio':sum(x['gaze']['valid'] for x in signals)/len(signals) if signals else None,'logs':logs}
class Rating(BaseModel):
    prompt_id:str
    rating:bool
@app.post('/api/sessions/{sid}/ratings')
def rate(sid:str,a:Rating,u=Depends(user)):
    with lock:
        s=load(sid,u)
        with db() as c:rows=c.execute("SELECT data FROM logs WHERE session_id=? AND kind='prompt_shown'",(sid,)).fetchall()
        if not any(json.loads(r['data'])['id']==a.prompt_id for r in rows):raise HTTPException(404,'Không có lời nhắc đã hiển thị')
        with db() as c:previous=c.execute("SELECT data FROM logs WHERE session_id=? AND kind='rating'",(sid,)).fetchall()
        if any(json.loads(r['data'])['prompt_id']==a.prompt_id for r in previous):raise HTTPException(409,'Đã đánh giá lời nhắc')
        log(s,'rating',a.model_dump());return {'ok':True}
@app.get('/api/sessions/{sid}/export')
def export(sid:str,u=Depends(user)):
    r=report(sid,u);s=r['session'];buf=io.StringIO();w=csv.writer(buf)
    fields=['time_utc_epoch','type','frame_id','head_yaw_deg','head_pitch_deg','gaze_yaw_deg','gaze_pitch_deg','head_valid','gaze_valid','active_seconds','break_seconds','paused_seconds','head_missing_seconds','gaze_missing_seconds','camera_missing_seconds','goal','data_json']
    w.writerow(fields)
    def cell(v):
        if v is None:return ''
        if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@','\t','\r','\n')):return "'"+v
        return v
    totals=[s.get(k) for k in fields[9:15]]
    w.writerow([s['created_at'],'summary',*(['']*7),*totals,cell(s['goal']),''])
    for x in r['logs']:
        data=x['data'];signal=x['kind']=='signal';head=data.get('head',{}) if signal else {};gaze=data.get('gaze',{}) if signal else {}
        row=[x['at'],x['kind'],data.get('frame_id'),head.get('yaw'),head.get('pitch'),gaze.get('yaw'),gaze.get('pitch'),head.get('valid'),gaze.get('valid'),*(['']*6),s['goal'],json.dumps(data,ensure_ascii=False)]
        w.writerow([cell(v) for v in row])
    return Response('\ufeff'+buf.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="focusstudy-{sid}.csv"'})

@app.delete('/api/sessions/{sid}')
def delete(sid:str,u=Depends(user)):
    with lock:
        s=load(sid,u);close_detector_events(s,'delete');s['status']='ended';s['support']=False;s['state_version']+=1
        with db() as c:c.execute('DELETE FROM sessions WHERE id=?',(sid,));c.execute('DELETE FROM commands WHERE session_id=?',(sid,));c.execute('UPDATE documents SET session_id=NULL WHERE session_id=?',(sid,))
        states.pop(sid,None)
    return {'ok':True}

MAX_DOC_SIZE=100*1024*1024

class SessionDocument(BaseModel):
    document_id:str|None=None

@app.post('/api/sessions/{sid}/document')
def session_document(sid:str,a:SessionDocument,u=Depends(user)):
    with lock:
        s=load(sid,u)
        doc_name=None
        if a.document_id:
            with db() as c:
                d=c.execute('SELECT id,filename FROM documents WHERE id=? AND user_id=?',(a.document_id,u['id'])).fetchone()
                if not d:raise HTTPException(404,'Không tìm thấy tài liệu')
                doc_name=d['filename']
                c.execute('UPDATE documents SET session_id=? WHERE id=?',(sid,a.document_id))
            s['document_id']=a.document_id
            s['document_name']=doc_name
        else:
            s['document_id']=None
            s['document_name']=None
        s['state_version']+=1
        save(s);return view(s)

@app.post('/api/documents')
async def upload_document(request:Request,session_id:str|None=None,u=Depends(user)):
    Path(DOCS_DIR).mkdir(parents=True,exist_ok=True)
    raw_content=None;orig_name=None;ctype=request.headers.get('content-type','')
    if 'multipart/form-data' in ctype:
        try:
            form=await request.form()
            uploaded_file=form.get('file')
            if uploaded_file and hasattr(uploaded_file,'read'):
                orig_name=getattr(uploaded_file,'filename',None) or 'document.pdf'
                raw_content=await uploaded_file.read(MAX_DOC_SIZE+1)
                session_id=form.get('session_id') or session_id
        except Exception:
            pass
    if raw_content is None:
        orig_name=request.query_params.get('filename') or request.headers.get('x-filename') or 'document.pdf'
        chunks=[];length=0
        async for chunk in request.stream():
            length+=len(chunk)
            if length>MAX_DOC_SIZE:raise HTTPException(413,'Dung lượng file vượt quá giới hạn 100MB')
            chunks.append(chunk)
        raw_content=b''.join(chunks)
    if session_id:load(session_id,u)
    if not raw_content:raise HTTPException(422,'Nội dung file không được để trống')
    if len(raw_content)>MAX_DOC_SIZE:raise HTTPException(413,'Dung lượng file vượt quá giới hạn 100MB')
    orig_name=Path(orig_name).name
    if not orig_name.lower().endswith('.pdf'):raise HTTPException(422,'Chỉ chấp nhận tài liệu định dạng PDF (.pdf)')
    if b'%PDF-' not in raw_content[:1024]:raise HTTPException(422,'File không phải là định dạng PDF hợp lệ (thiếu tiêu đề %PDF-)')
    try:
        pdf=PdfReader(io.BytesIO(raw_content),strict=False)
        if pdf.is_encrypted or len(pdf.pages)==0:raise ValueError('encrypted_or_empty')
    except Exception:raise HTTPException(422,'PDF bị hỏng, mã hóa hoặc không có trang; hãy chọn PDF đọc được')
    digest=hashlib.sha256(raw_content).hexdigest()
    with db() as c:
        duplicate=c.execute('SELECT id,filename,file_size,session_id,created_at FROM documents WHERE user_id=? AND sha256=?',(u['id'],digest)).fetchone()
    if duplicate:return dict(duplicate)
    doc_id=str(uuid.uuid4())
    safe_name="".join(c for c in orig_name if c.isalnum() or c in (' ','.','_','-')).strip() or 'document.pdf'
    target_path=Path(DOCS_DIR)/f"{doc_id}_{safe_name}"
    target_path.write_bytes(raw_content)
    created_at=time.time();file_size=len(raw_content)
    with db() as c:
        c.execute('INSERT INTO documents(id,user_id,session_id,filename,file_path,file_size,created_at,sha256) VALUES(?,?,?,?,?,?,?,?)',
                  (doc_id,u['id'],session_id,orig_name,str(target_path),file_size,created_at,digest))
    return {'id':doc_id,'filename':orig_name,'file_size':file_size,'session_id':session_id,'created_at':created_at}

@app.get('/api/documents')
def list_documents(session_id:str|None=None,u=Depends(user)):
    with db() as c:
        if session_id:
            rows=c.execute('SELECT id,user_id,session_id,filename,file_size,created_at FROM documents WHERE user_id=? AND session_id=? ORDER BY created_at DESC',(u['id'],session_id)).fetchall()
        else:
            rows=c.execute('SELECT id,user_id,session_id,filename,file_size,created_at FROM documents WHERE user_id=? ORDER BY created_at DESC',(u['id'],)).fetchall()
    return [dict(r) for r in rows]

@app.get('/api/documents/{doc_id}')
def get_document(doc_id:str,u=Depends(user)):
    with db() as c:
        row=c.execute('SELECT id,user_id,session_id,filename,file_size,created_at FROM documents WHERE id=? AND user_id=?',(doc_id,u['id'])).fetchone()
    if not row:raise HTTPException(404,'Không tìm thấy tài liệu')
    return dict(row)

@app.get('/api/documents/{doc_id}/file')
def get_document_file(doc_id:str,u=Depends(user)):
    with db() as c:
        row=c.execute('SELECT filename,file_path FROM documents WHERE id=? AND user_id=?',(doc_id,u['id'])).fetchone()
    if not row:raise HTTPException(404,'Không tìm thấy tài liệu')
    p=Path(row['file_path'])
    if not p.exists():raise HTTPException(404,'Tập tin không tồn tại trên hệ thống')
    return FileResponse(str(p),media_type='application/pdf',filename=row['filename'],content_disposition_type='inline')

@app.delete('/api/documents/{doc_id}')
def delete_document(doc_id:str,u=Depends(user)):
    with lock:
        with db() as c:
            row=c.execute('SELECT file_path FROM documents WHERE id=? AND user_id=?',(doc_id,u['id'])).fetchone()
            if not row:raise HTTPException(404,'Không tìm thấy tài liệu')
            try:Path(row['file_path']).unlink(missing_ok=True)
            except OSError:raise HTTPException(503,'Không thể xóa file; tài liệu và tham chiếu được giữ để thử lại')
            rows=c.execute('SELECT id,data FROM sessions WHERE user_id=?',(u['id'],)).fetchall()
            updates=[]
            for row in rows:
                snapshot=states.get(row['id']) or json.loads(row['data'])
                if snapshot.get('document_id')==doc_id:
                    snapshot={**snapshot,'document_id':None,'document_name':None,'state_version':snapshot['state_version']+1}
                    c.execute('UPDATE sessions SET data=? WHERE id=?',(json.dumps(snapshot),row['id']))
                    updates.append(snapshot)
            c.execute('DELETE FROM documents WHERE id=?',(doc_id,))
        for snapshot in updates:
            if snapshot['id'] in states:states[snapshot['id']].update(snapshot)
    return {'ok':True}

static=Path(__file__).resolve().parents[1]/'frontend'/'dist'
if static.exists():app.mount('/',StaticFiles(directory=static,html=True),name='frontend')
