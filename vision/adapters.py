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

    def _bbox_from_landmarks(self, face_landmarks, width, height):
        if not face_landmarks:
            return None
        xs=[p.x*width for p in face_landmarks]; ys=[p.y*height for p in face_landmarks]
        if not xs or not ys:
            return None
        return [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))]

    def health(self):
        return {k:{'available':getattr(self,k) is not None,'error':self.errors.get(k)} for k in ('head','gaze')}

    def infer(self,rgb):
        started=time.monotonic()
        out={'head':{'valid':False,'reason':'model_unavailable'},'gaze':{'valid':False,'reason':'model_unavailable'},'face_status':'unknown'}
        bbox=None
        if self.head:
            try:
                r=self.head.detect(self.mp.Image(image_format=self.mp.ImageFormat.SRGB,data=np.ascontiguousarray(rgb)))
                n=len(r.face_landmarks);out['face_status']='absent' if n==0 else 'multiple' if n>1 else 'visible'
                if n==1:
                    bbox=self._bbox_from_landmarks(r.face_landmarks[0], rgb.shape[1], rgb.shape[0])
                    if len(r.facial_transformation_matrixes):
                        m=np.array(r.facial_transformation_matrixes[0])[:3,:3]
                        u,_,v=np.linalg.svd(m)
                        if np.linalg.det(u@v)<0:u[:,-1]*=-1
                        rot=u@v
                        pitch=math.degrees(math.atan2(rot[2,1],rot[2,2]))
                        yaw=math.degrees(math.atan2(-rot[2,0],math.hypot(rot[2,1],rot[2,2])))
                        roll=math.degrees(math.atan2(rot[1,0],rot[0,0]))
                        out['head']={'valid':True,'reason':None,'yaw':yaw,'pitch':pitch,'roll':roll}
                    else:
                        out['head']={'valid':False,'reason':'face_landmarks_detected_without_transform'}
                else:
                    out['head']['reason']=out['face_status']
            except Exception as e:out['head']['reason']='inference_error: '+str(e)

        if self.gaze:
            try:
                try:
                    r=self.gaze.step(rgb[:,:,::-1].copy())
                except Exception as _step_err:
                    # L2CS Pipeline.step() crashes with ValueError when:
                    # (a) faces detected but all below confidence threshold -> np.stack([]) fails
                    # (b) faces is None -> np.stack(bboxes=[]) fails in GazeResultContainer
                    # Treat both as no detectable face.
                    raise ValueError('no_face_detected: '+str(_step_err))
                raw_boxes=r.bboxes if r.bboxes is not None else []
                boxes=np.asarray(raw_boxes, dtype=float).reshape(-1,4) if len(raw_boxes) else np.empty((0,4))
                if boxes.size == 0:
                    raise ValueError('multiple_or_missing_faces')
                if len(boxes) != 1:
                    raise ValueError('multiple_or_missing_faces')
                b=boxes[0]
                if bbox is None:
                    raise ValueError('head_face_unavailable_for_matching')
                ix=max(0.0,min(b[2],bbox[2])-max(b[0],bbox[0]))
                iy=max(0.0,min(b[3],bbox[3])-max(b[1],bbox[1]))
                inter=ix*iy
                union=(b[2]-b[0])*(b[3]-b[1])+(bbox[2]-bbox[0])*(bbox[3]-bbox[1])-inter
                iou = inter/union if union>0 else 0
                if iou < .15:
                    bc_x = (b[0] + b[2]) / 2; bc_y = (b[1] + b[3]) / 2
                    mc_x = (bbox[0] + bbox[2]) / 2; mc_y = (bbox[1] + bbox[3]) / 2
                    bw = max(1.0, b[2] - b[0]); bh = max(1.0, b[3] - b[1])
                    if abs(bc_x - mc_x) > bw * 0.45 or abs(bc_y - mc_y) > bh * 0.45:
                        raise ValueError('unmatched_face')
                if len(r.yaw) == 0 or len(r.pitch) == 0:
                    raise ValueError('empty_gaze_prediction')
                out['gaze']={'valid':True,'reason':None,'yaw':float(np.degrees(r.yaw[0])),'pitch':float(np.degrees(r.pitch[0]))}
            except Exception as e:out['gaze']['reason']='inference_error: '+str(e)
        elif self.gaze is None:
            out['gaze']['reason']='model_unavailable'

        out['processing_ms']=(time.monotonic()-started)*1000
        return out
