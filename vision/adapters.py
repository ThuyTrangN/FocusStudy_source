"""Optional genuine inference adapters. Never synthesize model results."""
import os, time, math
import numpy as np

class Vision:
    def __init__(self):
        self.head=None; self.gaze=None
        self.errors={}
        try:
            import mediapipe as mp
            path=os.environ.get('MEDIAPIPE_MODEL','models/face_landmarker.task')
            if not os.path.isfile(path): raise FileNotFoundError('Thiếu '+path)
            opts=mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=path),num_faces=2,output_facial_transformation_matrixes=True)
            self.head=mp.tasks.vision.FaceLandmarker.create_from_options(opts); self.mp=mp
        except Exception as e: self.errors['head']=str(e)
        try:
            from l2cs import Pipeline
            import torch
            path=os.environ.get('L2CS_MODEL','models/L2CSNet_gaze360.pkl')
            if not os.path.isfile(path): raise FileNotFoundError('Thiếu '+path)
            self.gaze=Pipeline(weights=path,arch='ResNet50',device=torch.device(os.environ.get('L2CS_DEVICE','cpu')))
        except Exception as e: self.errors['gaze']=str(e)
    def health(self):
        return {k:{'available':getattr(self,k) is not None,'error':self.errors.get(k)} for k in ('head','gaze')}
    def infer(self,rgb):
        started=time.monotonic()
        out={'head':{'valid':False,'reason':'model_unavailable'},'gaze':{'valid':False,'reason':'model_unavailable'},'face_status':'unknown'}
        bbox=None
        if self.head:
            try:
                r=self.head.detect(self.mp.Image(image_format=self.mp.ImageFormat.SRGB,data=rgb))
                n=len(r.face_landmarks);out['face_status']='absent' if n==0 else 'multiple' if n>1 else 'visible'
                if n==1 and len(r.facial_transformation_matrixes):
                    m=np.array(r.facial_transformation_matrixes[0])[:3,:3]
                    u,_,v=np.linalg.svd(m)
                    if np.linalg.det(u@v)<0:u[:,-1]*=-1
                    rot=u@v
                    # Convention must be verified with user's camera before research.
                    pitch=math.degrees(math.atan2(rot[2,1],rot[2,2]))
                    yaw=math.degrees(math.atan2(-rot[2,0],math.hypot(rot[2,1],rot[2,2])))
                    roll=math.degrees(math.atan2(rot[1,0],rot[0,0]))
                    out['head']={'valid':True,'reason':None,'yaw':yaw,'pitch':pitch,'roll':roll}
                    xs=[p.x*rgb.shape[1] for p in r.face_landmarks[0]];ys=[p.y*rgb.shape[0] for p in r.face_landmarks[0]]
                    bbox=[min(xs),min(ys),max(xs),max(ys)]
                else:out['head']['reason']=out['face_status']
            except Exception as e:out['head']['reason']='inference_error: '+str(e)
        if self.gaze and bbox is not None:
            try:
                r=self.gaze.step(rgb[:,:,::-1].copy())
                boxes=np.asarray(r.bboxes)
                if len(boxes)!=1: raise ValueError('multiple_or_missing_faces')
                b=boxes[0];ix=max(0,min(b[2],bbox[2])-max(b[0],bbox[0]));iy=max(0,min(b[3],bbox[3])-max(b[1],bbox[1]));inter=ix*iy
                union=(b[2]-b[0])*(b[3]-b[1])+(bbox[2]-bbox[0])*(bbox[3]-bbox[1])-inter
                if union<=0 or inter/union<.25:raise ValueError('unmatched_face')
                # L2CS pipeline pitch/yaw arrays are radians.
                out['gaze']={'valid':True,'reason':None,'yaw':float(np.degrees(r.yaw[0])),'pitch':float(np.degrees(r.pitch[0]))}
            except Exception as e:out['gaze']['reason']='inference_error: '+str(e)
        elif self.gaze:out['gaze']['reason']='head_face_unavailable_for_matching'
        out['processing_ms']=(time.monotonic()-started)*1000
        return out
