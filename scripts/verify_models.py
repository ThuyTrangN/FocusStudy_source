"""Real checkpoint smoke test; blank inputs are explicitly synthetic, never webcam evaluation."""
import hashlib,json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import torch
from vision.adapters import Vision

def main():
    torch.set_num_threads(2)
    engine=Vision()
    result={'test':'synthetic_blank_smoke_only','torch':torch.__version__,'cuda_runtime':torch.version.cuda,'models':engine.health(),'checkpoints':[]}
    for p in sorted(Path('models').glob('*')):
        if p.is_file():result['checkpoints'].append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    started=time.perf_counter();result['adapter_blank_result']=engine.infer(np.zeros((480,640,3),dtype=np.uint8));result['adapter_wall_ms']=(time.perf_counter()-started)*1000
    if engine.gaze:
        with torch.inference_mode():
            started=time.perf_counter();pitch,yaw=engine.gaze.predict_gaze(np.zeros((1,224,224,3),dtype=np.uint8))
            result['gaze_network_synthetic_crop']={'ran':True,'finite':bool(np.isfinite(pitch).all() and np.isfinite(yaw).all()),'wall_ms':(time.perf_counter()-started)*1000,'meaning':'network execution only; no face, no calibration or accuracy evidence'}
    result['webcam_verified']=False;result['calibration_on_person_verified']=False
    output=Path('docs/evidence/model-smoke.json');output.parent.mkdir(exist_ok=True,parents=True);output.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(result,indent=2,ensure_ascii=True))
if __name__=='__main__':main()
