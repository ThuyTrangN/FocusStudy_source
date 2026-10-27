"""Regression cases for ownership, persistence, coverage and concurrency. No ML accuracy claims."""
import base64,io,json,sqlite3,time,threading
from pathlib import Path
import pytest
from pypdf import PdfWriter
from test_backend import client,register,session,cmd
import backend.app as m
from backend.policy import evaluate

def pdf_bytes():
    w=PdfWriter();w.add_blank_page(width=300,height=400);b=io.BytesIO();w.write(b);return b.getvalue()
def upload(c,**kw):return c.post('/api/documents',files={'file':('sample.pdf',pdf_bytes(),'application/pdf')},**kw)

def test_profile_validation_persistence(client):
    register(client)
    assert client.patch('/api/auth/me',json={'name':'  '}).status_code==422
    assert client.patch('/api/auth/me',json={'name':'Nguyễn thử'}).json()['name']=='Nguyễn thử'
    client.post('/api/auth/logout');client.post('/api/auth/login',json={'email':'one@example.com','password':'StrongPass123'})
    assert client.get('/api/auth/me').json()['name']=='Nguyễn thử'

def test_pdf_structural_dedup_ownership_and_detach(client):
    first=session(client);d=upload(client).json()
    assert upload(client).json()['id']==d['id']
    assert client.post('/api/documents',files={'file':('bad.pdf',b'%PDF-1.7 not valid','application/pdf')}).status_code==422
    attached=client.post(f"/api/sessions/{first['id']}/document",json={'document_id':d['id']}).json()
    second=client.post('/api/sessions',json={'goal':'Second','document_id':d['id']}).json()
    register(client,'two@example.com')
    assert client.post('/api/sessions',json={'goal':'Steal','document_id':d['id']}).status_code==404
    assert upload(client,data={'session_id':first['id']}).status_code==404
    client.post('/api/auth/login',json={'email':'one@example.com','password':'StrongPass123'})
    assert client.delete('/api/documents/'+d['id']).status_code==200
    for sid in [first['id'],second['id']]:
        snap=client.get('/api/sessions/'+sid).json();assert snap['document_id'] is None and snap['document_name'] is None
        with m.db() as c:assert json.loads(c.execute('SELECT data FROM sessions WHERE id=?',(sid,)).fetchone()['data'])['document_id'] is None

def test_pdf_unlink_failure_preserves_references(client,monkeypatch):
    s=session(client);d=upload(client).json();client.post(f"/api/sessions/{s['id']}/document",json={'document_id':d['id']})
    def fail(*args,**kwargs):raise PermissionError('locked')
    monkeypatch.setattr(Path,'unlink',fail)
    assert client.delete('/api/documents/'+d['id']).status_code==503
    assert client.get('/api/documents/'+d['id']).status_code==200
    assert client.get('/api/sessions/'+s['id']).json()['document_id']==d['id']

def test_single_active_reload_restart_and_logout(client):
    s=session(client);assert cmd(client,s,'start').status_code==200
    t=client.post('/api/sessions',json={'goal':'Other'}).json();assert cmd(client,t,'start').status_code==409
    assert client.get('/api/sessions/'+s['id']).json()['status']=='active'
    state=m.states[s['id']];state['tick']-=10
    snapshot=client.get('/api/sessions/'+s['id']).json();assert snapshot['active_seconds']>=10
    m.states.clear()
    restored=client.get('/api/sessions/'+s['id']).json();assert restored['status']=='paused' and not restored['support']
    assert restored['active_seconds']==pytest.approx(snapshot['active_seconds'],abs=.1)
    cmd(client,s,'resume');client.post('/api/auth/logout')
    client.post('/api/auth/login',json={'email':'one@example.com','password':'StrongPass123'})
    assert client.get('/api/sessions/'+s['id']).json()['status']=='paused'

def test_exact_timer_coverage_and_zero_denominator(client,monkeypatch):
    s=session(client);cmd(client,s,'start');state=m.states[s['id']]
    monkeypatch.setattr(m.time,'monotonic',lambda:100)
    state.update(tick=90,active_seconds=0,support=True,signal_mono=94,signal_valid={'head':True,'gaze':False},head_missing_seconds=0,gaze_missing_seconds=0,camera_missing_seconds=0)
    m.accrue(state)
    assert state['active_seconds']==10 and state['head_missing_seconds']==4 and state['gaze_missing_seconds']==10 and state['camera_missing_seconds']==4
    state['status']='paused';state['tick']=96;m.accrue(state);assert state['paused_seconds']==4
    report=client.get('/api/sessions/'+s['id']+'/report').json();assert report['response_rate'] is None and report['helpful_ratio'] is None

def test_expired_feedback_does_not_apply_and_timeout_is_idempotent(client):
    s=session(client);cmd(client,s,'start');st=m.states[s['id']]
    st['prompt']={'id':'p','shown_at':time.time(),'created_mono':time.monotonic()-20}
    assert client.post('/api/sessions/'+s['id']+'/feedback',json={'prompt_id':'p','action':'notes'}).status_code==409
    assert st.get('downward_until',0)==0
    assert cmd(client,s,'prompt_timeout',prompt_id='p',event_id='timeout').status_code==200
    assert cmd(client,s,'prompt_timeout',prompt_id='p',event_id='timeout').status_code==200

def test_policy_out_of_order_resets_and_boundaries():
    s={'status':'active','support':True};sig={'head':{'valid':True,'calibrated':True,'relative_yaw':26}}
    for n in [0,1,2,3,4,5,6,7,7.9]:assert evaluate(s,sig,n) is None
    assert evaluate(s,sig,8)['reason']=='head_turn'
    assert evaluate(s,sig,7) is None
    assert evaluate(s,sig,11) is None

def test_delete_during_worker_no_resurrection(client,monkeypatch):
    from PIL import Image
    entered=threading.Event();release=threading.Event()
    class Slow:
        def health(self):return {'head':{'available':True},'gaze':{'available':True}}
        def infer(self,rgb):
            entered.set();release.wait(5)
            return {'head':{'valid':True,'yaw':0,'pitch':0},'gaze':{'valid':False},'face_status':'visible'}
    monkeypatch.setattr(m,'engine',Slow());s=session(client);cmd(client,s,'start');state=cmd(client,s,'support_on').json()
    b=io.BytesIO();Image.new('RGB',(4,4)).save(b,format='JPEG');result=[]
    thread=threading.Thread(target=lambda:result.append(client.post('/api/sessions/'+s['id']+'/frames',json={'image':base64.b64encode(b.getvalue()).decode(),'frame_id':1,'state_version':state['state_version']})))
    thread.start();assert entered.wait(3)
    assert client.delete('/api/sessions/'+s['id']).status_code==200
    release.set();thread.join(5);assert result[0].status_code==409
    assert client.get('/api/sessions/'+s['id']).status_code==404
    with m.db() as c:assert c.execute('SELECT COUNT(*) FROM logs WHERE session_id=?',(s['id'],)).fetchone()[0]==0

def test_upgrade_old_schema_and_backup_restore(client,tmp_path):
    s=session(client)
    with m.db() as c:
        c.execute('ALTER TABLE documents DROP COLUMN sha256');c.execute('PRAGMA user_version=0')
    m.init();m.init()
    with m.db() as c:
        assert c.execute('PRAGMA user_version').fetchone()[0]==1
        assert c.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]==1
        backup=sqlite3.connect(tmp_path/'backup.sqlite');c.backup(backup);backup.close()
    recovered=sqlite3.connect(tmp_path/'backup.sqlite');assert recovered.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert recovered.execute('SELECT id FROM sessions').fetchone()[0]==s['id'];recovered.close()

def test_create_request_id_avoids_duplicate_retry(client):
    register(client)
    payload={'goal':'Retry create','request_id':'same-intent'}
    a=client.post('/api/sessions',json=payload).json();b=client.post('/api/sessions',json=payload).json()
    assert a['id']==b['id'] and len(client.get('/api/sessions').json())==1
    register(client,'two@example.com');c=client.post('/api/sessions',json=payload).json();assert c['id']!=a['id']

def test_csv_units_null_and_formula_defense(client):
    import csv
    register(client);s=client.post('/api/sessions',json={'goal':'=HYPERLINK("bad")'}).json()
    state=m.states[s['id']];m.log(state,'signal',{'frame_id':1,'head':{'valid':False,'yaw':None,'pitch':None},'gaze':{'valid':False,'yaw':None,'pitch':None}})
    r=client.get('/api/sessions/'+s['id']+'/export');assert r.content.startswith(b'\xef\xbb\xbf')
    rows=list(csv.DictReader(io.StringIO(r.text.lstrip('\ufeff'))));assert rows[0]['type']=='summary'
    assert rows[0]['goal'].startswith("'=") and rows[1]['head_yaw_deg']=='' and rows[1]['gaze_pitch_deg']==''
    assert float(rows[0]['active_seconds'])==0

def test_annotation_deleted_while_reading_body_returns_404(client):
    import asyncio
    from fastapi import HTTPException
    s=session(client);u=client.get('/api/auth/me').json()
    class RequestBody:
        async def json(self):
            m.delete(s['id'],u)
            return {'activity':'test'}
    with pytest.raises(HTTPException) as error:
        asyncio.run(m.annotation(s['id'],RequestBody(),u))
    assert error.value.status_code==404
    with m.db() as c:assert c.execute('SELECT COUNT(*) FROM logs').fetchone()[0]==0

def test_periodic_checkpoint_survives_without_browser(client):
    s=session(client);cmd(client,s,'start');state=m.states[s['id']];state['tick']-=6
    m.checkpoint_states();m.states.clear()
    restored=client.get('/api/sessions/'+s['id']).json()
    assert restored['status']=='paused' and restored['active_seconds']>=6
    assert restored['model_manifest']['checkpoints'][0]['sha256'] is not None

def test_detector_interval_independent_of_prompt_and_gap(client):
    s=session(client);state=m.states[s['id']];state['counters']={'head_turn':10};state['detected_events']=['head_turn']
    m.record_detector_events(state,18,1);m.record_detector_events(state,19,2)
    state['detected_events']=[];m.record_detector_events(state,24,3)
    r=client.get('/api/sessions/'+s['id']+'/report').json()
    starts=[x for x in r['detector_events'] if x['kind']=='detector_event'];ends=[x for x in r['detector_events'] if x['kind']=='detector_event_end']
    assert len(starts)==len(ends)==1 and starts[0]['data']['id']==ends[0]['data']['id']
    assert ends[0]['data']['duration_seconds']==9 and r['prompt_count']==0
