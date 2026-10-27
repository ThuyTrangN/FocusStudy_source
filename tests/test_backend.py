import base64,io,time
import pytest
from PIL import Image
from fastapi.testclient import TestClient
import backend.app as m
from backend.policy import evaluate
class Unavailable:
 def health(self):return {'head':{'available':False},'gaze':{'available':False}}
 def infer(self,rgb):return {'head':{'valid':False,'reason':'missing'},'gaze':{'valid':False,'reason':'missing'},'face_status':'unknown'}
@pytest.fixture
def client(tmp_path,monkeypatch):
 monkeypatch.setattr(m,'DB',str(tmp_path/'test.sqlite'));monkeypatch.setattr(m,'DOCS_DIR',str(tmp_path/'documents'));monkeypatch.setattr(m,'Vision',Unavailable);m.states.clear()
 with TestClient(m.app) as c:yield c

def register(c,email='one@example.com'):
 r=c.post('/api/auth/register',json={'email':email,'password':'StrongPass123','name':'Test'});assert r.status_code==200

def session(c):
 register(c);s=c.post('/api/sessions',json={'goal':'Read','condition':'B'}).json();return s

def cmd(c,s,t,**kw):return c.post(f"/api/sessions/{s['id']}/commands",json={'type':t,**kw})

def test_auth_isolation_and_logout(client):
 s=session(client);assert client.get('/api/auth/me').status_code==200
 assert client.post('/api/auth/logout').status_code==200
 assert client.get('/api/sessions').status_code==401
 register(client,'two@example.com')
 for suffix in ('','/report','/export'):assert client.get(f"/api/sessions/{s['id']}"+suffix).status_code==404
 assert client.delete(f"/api/sessions/{s['id']}").status_code==404

def test_csrf_and_wrong_password(client):
 assert client.post('/api/auth/register',headers={'origin':'https://evil.example'},json={'email':'x@y.com','password':'password'}).status_code==403
 register(client);client.post('/api/auth/logout')
 assert client.post('/api/auth/login',json={'email':'one@example.com','password':'WrongPass123'}).status_code==401

def test_command_idempotent_and_version(client):
 s=session(client);a=cmd(client,s,'start',event_id='fixed').json();b=cmd(client,s,'start',event_id='fixed').json();assert a['state_version']==b['state_version']
 assert cmd(client,s,'pause',expected_state_version=0).status_code==409
 assert cmd(client,s,'end').status_code==200
 assert cmd(client,s,'resume').status_code==409

def test_unavailable_models_cannot_start_calibration(client):
 s=session(client);url=f"/api/sessions/{s['id']}"
 assert client.post(url+'/calibration',json={'branch':'head','action':'start'}).status_code==409
 cmd(client,s,'start');cmd(client,s,'support_on')
 r=client.post(url+'/calibration',json={'branch':'head','action':'start'});assert r.status_code==409 and 'model head chưa sẵn sàng' in r.json()['detail']
 assert not m.states[s['id']].get('calibrating')
 assert client.post(url+'/annotations',json={'head_label':'neutral'}).status_code==200
 report=client.get(url+'/report').json();assert len(report['annotations'])==1 and report['annotations'][0]['data']['head_label']=='neutral' and report['calibrations']==[]
 assert client.delete(url).status_code==200
 assert client.get(url+'/report').status_code==404

def test_infer_uses_landmarks_bbox_when_rotation_matrix_missing():
 from types import SimpleNamespace
 from vision.adapters import Vision
 import numpy as np

 class FakeHead:
  def detect(self, image):
   landmark = [SimpleNamespace(x=0.5, y=0.5), SimpleNamespace(x=0.6, y=0.4), SimpleNamespace(x=0.4, y=0.6)]
   return SimpleNamespace(face_landmarks=[landmark], facial_transformation_matrixes=[])

 class FakeGaze:
  def step(self, frame):
   return SimpleNamespace(bboxes=np.array([[90, 70, 130, 140]], dtype=float), yaw=np.array([0.1]), pitch=np.array([0.2]))

 v = Vision.__new__(Vision)
 v.head = FakeHead()
 v.gaze = FakeGaze()
 v.mp = SimpleNamespace(Image=lambda **kwargs: object(), ImageFormat=SimpleNamespace(SRGB='srgb'))

 results = v.infer(np.zeros((200, 200, 3), dtype=np.uint8))
 assert results['head']['reason'] in (None, 'face_landmarks_detected_without_transform')
 assert results['gaze']['valid'] is True
 assert 'yaw' in results['gaze'] and 'pitch' in results['gaze']

def test_head_calibration_completes_automatically_after_stable_samples(client,monkeypatch):
 class Available:
  def health(self):return {'head':{'available':True},'gaze':{'available':True}}
  def infer(self,rgb):return {'head':{'valid':True,'yaw':2.,'pitch':1.},'gaze':{'valid':False,'reason':'not_used'},'face_status':'visible'}
 monkeypatch.setattr(m,'engine',Available())
 s=session(client);url=f"/api/sessions/{s['id']}"
 cmd(client,s,'start');cmd(client,s,'support_on')
 started=client.post(url+'/calibration',json={'branch':'head','action':'start'}).json()
 state=m.states[s['id']];state['calibration_started']=time.monotonic()-6
 image=io.BytesIO();Image.new('RGB',(4,4)).save(image,format='JPEG')
 encoded='data:image/jpeg;base64,'+base64.b64encode(image.getvalue()).decode()
 for frame_id in range(1,16):
  response=client.post(url+'/frames',json={'image':encoded,'frame_id':frame_id,'state_version':state['state_version']})
  assert response.status_code==200
 finished=response.json()['session']
 assert finished['calibrating'] is None
 assert finished['calibration']['head']['valid'] is True

def test_gaze_calibration_cycles_targets_and_completes_automatically(client,monkeypatch):
 class Available:
  def health(self):return {'head':{'available':True},'gaze':{'available':True}}
  def infer(self,rgb):return {'head':{'valid':True,'yaw':2.,'pitch':1.},'gaze':{'valid':True,'yaw':5.,'pitch':6.},'face_status':'visible'}
 monkeypatch.setattr(m,'engine',Available())
 s=session(client);url=f"/api/sessions/{s['id']}"
 cmd(client,s,'start');cmd(client,s,'support_on')
 started=client.post(url+'/calibration',json={'branch':'gaze','action':'start','target':'center'}).json()
 state=m.states[s['id']];state['calibration_started']=time.monotonic()-6
 image=io.BytesIO();Image.new('RGB',(4,4)).save(image,format='JPEG')
 encoded='data:image/jpeg;base64,'+base64.b64encode(image.getvalue()).decode()
 for frame_id in range(1,16):
  response=client.post(url+'/frames',json={'image':encoded,'frame_id':frame_id,'state_version':state['state_version']})
  assert response.status_code==200
 finished=response.json()['session']
 assert finished['calibrating'] is None
 assert finished['calibration']['gaze']['valid'] is True
 assert all(target['samples']==3 for target in finished['calibration']['gaze']['targets'].values())

def test_calibration_finish_reports_sample_progress(client,monkeypatch):
 class Available:
  def health(self):return {'head':{'available':True},'gaze':{'available':False}}
 monkeypatch.setattr(m,'engine',Available())
 s=session(client);url=f"/api/sessions/{s['id']}"
 cmd(client,s,'start');cmd(client,s,'support_on')
 started=client.post(url+'/calibration',json={'branch':'head','action':'start'}).json()
 assert started['calibration_progress']['sample_count']==0 and not started['calibration_progress']['ready']
 state=m.states[s['id']];state['calibration_samples']=[[0.,0.]]*4;state['calibration_started']=time.monotonic()-2
 progress=client.get(url).json()['calibration_progress']
 assert progress['sample_count']==4 and not progress['ready']
 response=client.post(url+'/calibration',json={'branch':'head','action':'finish'})
 assert response.status_code==422
 assert '4/15 mẫu hợp lệ' in response.json()['detail']
 assert '2.0/5 giây' in response.json()['detail']
 state['calibration_samples']=[[0.,0.]]*15;state['calibration_started']=time.monotonic()-6
 finished=client.post(url+'/calibration',json={'branch':'head','action':'finish'})
 assert finished.status_code==200 and finished.json()['calibration']['head']['valid']

def test_gaze_calibration_target_changes_are_logged(client,monkeypatch):
 class Available:
  def health(self):return {'head':{'available':True},'gaze':{'available':True}}
 monkeypatch.setattr(m,'engine',Available())
 s=session(client);url=f"/api/sessions/{s['id']}"
 cmd(client,s,'start');cmd(client,s,'support_on')
 started=client.post(url+'/calibration',json={'branch':'gaze','action':'start','target':'center'})
 assert started.status_code==200 and started.json()['calibration_progress']['target_counts']=={target:0 for target in m.GAZE_TARGETS}
 changed=client.post(url+'/calibration',json={'branch':'gaze','action':'target','target':'left'})
 assert changed.status_code==200 and m.states[s['id']]['calibrating']=='gaze'
 incomplete=client.post(url+'/calibration',json={'branch':'gaze','action':'finish'})
 assert incomplete.status_code==422 and 'center: 0/3' in incomplete.json()['detail']
 state=m.states[s['id']]
 for index,target in enumerate(m.GAZE_TARGETS):
  if state['calibration_target']!=target:
   assert client.post(url+'/calibration',json={'branch':'gaze','action':'target','target':target}).status_code==200
  samples=[[float(index*10+offset),float(index*2+offset)] for offset in range(3)]
  state['calibration_samples'].extend(samples)
  state['calibration_target_samples'][target].extend(samples)
 state['calibration_started']=time.monotonic()-6
 finished=client.post(url+'/calibration',json={'branch':'gaze','action':'finish'})
 assert finished.status_code==200 and finished.json()['calibration']['gaze']['targets']['bottom']['samples']==3
 report=client.get(url+'/report').json()
 assert any(row['kind']=='calibration_target' and row['data']['target']=='left' for row in report['logs'])
 assert len(report['calibrations'])==1 and report['calibrations'][0]['data']['branch']=='gaze'
 assert report['session']['calibration']['gaze']['targets']['center']['yaw']==1.

def test_calibration_cancel(client,monkeypatch):
 class Available:
  def health(self):return {'head':{'available':True},'gaze':{'available':True}}
 monkeypatch.setattr(m,'engine',Available())
 s=session(client);url=f"/api/sessions/{s['id']}"
 cmd(client,s,'start');cmd(client,s,'support_on')
 started=client.post(url+'/calibration',json={'branch':'head','action':'start'}).json()
 assert started['calibrating']=='head'
 cancelled=client.post(url+'/calibration',json={'branch':'head','action':'cancel'}).json()
 assert cancelled.get('calibrating') is None and 'calibration_samples' not in cancelled

def test_feedback_ab_and_rating(client):
 s=session(client);cmd(client,s,'start');state=m.states[s['id']]
 def prompt(pid):
  state['prompt']={'id':pid,'reason':'head_down','created_mono':time.monotonic(),'shown_at':None}
  cmd(client,s,'prompt_shown',prompt_id=pid)
 prompt('p1')
 assert client.post(f"/api/sessions/{s['id']}/feedback",json={'prompt_id':'p1','action':'notes'}).status_code==200
 assert state['downward_until']>time.monotonic()
 assert client.post(f"/api/sessions/{s['id']}/ratings",json={'prompt_id':'p1','rating':True}).status_code==200
 assert client.post(f"/api/sessions/{s['id']}/ratings",json={'prompt_id':'p1','rating':False}).status_code==409
 state['condition']='A';state['downward_until']=0;prompt('p2')
 client.post(f"/api/sessions/{s['id']}/feedback",json={'prompt_id':'p2','action':'notes'})
 assert state['downward_until']==0
 r=client.get(f"/api/sessions/{s['id']}/report").json();assert r['prompt_count']==2 and r['helpful_ratio']==1

def test_policy_duration_gap_invalid_snooze():
 s={'status':'active','support':True};v={'head':{'valid':True,'calibrated':True,'relative_yaw':30},'gaze':{},'face_status':'visible'}
 for t in range(8):assert evaluate(s,v,t) is None
 assert evaluate(s,v,8)['reason']=='head_turn'
 assert evaluate(s,v,12) is None
 v['head']['valid']=False;assert evaluate(s,v,13) is None
 v['head']['valid']=True;s['snooze_until']=50
 for t in range(14,24):assert evaluate(s,v,t) is None
 s['snooze_until']=0;assert evaluate(s,v,24)['reason']=='head_turn'

def test_pdf_document_upload_and_management(client):
    register(client, 'docuser@example.com')
    # Reject non-PDF
    bad_ext = client.post('/api/documents', files={'file': ('test.txt', b'hello world', 'text/plain')})
    assert bad_ext.status_code == 422
    # Reject invalid magic bytes
    fake_pdf = client.post('/api/documents', files={'file': ('fake.pdf', b'not a real pdf', 'application/pdf')})
    assert fake_pdf.status_code == 422

    # Valid PDF upload via multipart
    from pypdf import PdfWriter
    pdf=PdfWriter();pdf.add_blank_page(width=300,height=400);buffer=io.BytesIO();pdf.write(buffer);valid_pdf_content=buffer.getvalue()
    upload = client.post('/api/documents', files={'file': ('lecture_ch1.pdf', valid_pdf_content, 'application/pdf')})
    assert upload.status_code == 200
    doc = upload.json()
    assert doc['filename'] == 'lecture_ch1.pdf'
    doc_id = doc['id']

    # List documents
    docs = client.get('/api/documents').json()
    assert len(docs) == 1 and docs[0]['id'] == doc_id

    # Get single document
    doc_meta = client.get(f'/api/documents/{doc_id}').json()
    assert doc_meta['filename'] == 'lecture_ch1.pdf'

    # Download / view file
    file_res = client.get(f'/api/documents/{doc_id}/file')
    assert file_res.status_code == 200
    assert file_res.content == valid_pdf_content
    assert 'inline' in file_res.headers.get('content-disposition', '')

    # Create session with document attached
    s = client.post('/api/sessions', json={'goal': 'Doc Study', 'mode': 'reading', 'condition': 'B', 'document_id': doc_id}).json()
    assert s['document_id'] == doc_id
    assert s['document_name'] == 'lecture_ch1.pdf'

    # Switch session document
    pdf=PdfWriter();pdf.add_blank_page(width=400,height=500);buffer=io.BytesIO();pdf.write(buffer);valid_pdf_content2=buffer.getvalue()
    upload2 = client.post('/api/documents', files={'file': ('lecture_ch2.pdf', valid_pdf_content2, 'application/pdf')})
    doc2_id = upload2.json()['id']
    switched = client.post(f"/api/sessions/{s['id']}/document", json={'document_id': doc2_id}).json()
    assert switched['document_id'] == doc2_id
    assert switched['document_name'] == 'lecture_ch2.pdf'

    # User isolation: another user cannot access doc_id
    register(client, 'other@example.com')
    assert client.get(f'/api/documents/{doc_id}').status_code == 404
    assert client.get(f'/api/documents/{doc_id}/file').status_code == 404
    assert client.delete(f'/api/documents/{doc_id}').status_code == 404

    # Log back into docuser
    client.post('/api/auth/login', json={'email': 'docuser@example.com', 'password': 'StrongPass123'})
    assert client.delete(f'/api/documents/{doc_id}').status_code == 200
    assert client.get(f'/api/documents/{doc_id}').status_code == 404
