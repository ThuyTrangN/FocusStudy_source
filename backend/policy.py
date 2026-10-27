"""Time-based detector; functions can be replayed without webcam or ML packages."""
import time, os

DEFAULTS = dict(turn_deg=25, down_deg=20, turn_s=8, down_s=15, exercise_down_s=25, gaze_s=8, absent_s=10, cooldown_s=60, gap_s=2)

def evaluate(state, signal, now=None):
    now = time.monotonic() if now is None else now
    config={**DEFAULTS,**state.get('policy_config',{})}
    counters = state.setdefault('counters', {})
    if state.get('status') != 'active' or not state.get('support'):
        counters.clear(); return None
    last = state.get('last_sample')
    if last is not None and now-last > config['gap_s']: counters.clear()
    state['last_sample'] = now
    head=signal.get('head',{}); gaze=signal.get('gaze',{})
    checks = {
        'face_not_observed': (signal.get('face_status') == 'absent',config['absent_s']),
        'head_turn': (head.get('valid',False) and head.get('calibrated',False) and abs(head.get('relative_yaw',0))>config['turn_deg'],config['turn_s']),
        'head_down': (head.get('valid',False) and head.get('calibrated',False) and float(os.getenv('HEAD_DOWN_SIGN','1'))*head.get('relative_pitch',0)>config['down_deg'],config['exercise_down_s'] if state.get('mode')=='exercise' else config['down_s']),
        'gaze_away': (gaze.get('valid',False) and gaze.get('calibrated',False) and gaze.get('outside',False),config['gaze_s']),
    }
    ready=[]
    for kind,(active,duration) in checks.items():
        if not active: counters.pop(kind,None)
        else:
            counters.setdefault(kind,now)
            if now-counters[kind]>=duration: ready.append(kind)
    state['detected_events']=ready
    if state.get('prompt') or now<state.get('snooze_until',0) or now-state.get('last_shown',-1e9)<config['cooldown_s']: return None
    for kind in ready:
        downward=kind=='head_down' or kind=='gaze_away' and gaze.get('direction')=='down'
        if downward and now<state.get('downward_until',0): continue
        return {'reason':kind,'started_at_mono':counters[kind]}
    return None
