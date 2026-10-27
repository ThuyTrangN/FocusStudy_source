import React,{useEffect,useRef} from 'react';
import {X} from 'lucide-react';
export function Icon({of:Comp,...props}){return <Comp size={19} strokeWidth={1.7} aria-hidden="true" {...props}/>}
export function Button({children,variant='',className='',...props}){return <button className={`btn ${variant} ${className}`} {...props}>{children}</button>}
export function Pill({children,tone=''}){return <span className={`pill ${tone}`}>{children}</span>}
export function Field({label,children,hint}){return <label className="field"><span>{label}</span>{children}{hint&&<small>{hint}</small>}</label>}
export function Modal({title,children,onClose,wide=false}){
 const ref=useRef();useEffect(()=>{const prev=document.activeElement;const old=document.body.style.overflow;document.body.style.overflow='hidden';ref.current?.focus();const handler=e=>{if(e.key==='Escape')onClose();if(e.key==='Tab'){const items=[...ref.current.querySelectorAll('button,input,select,textarea,a[href]')].filter(x=>!x.disabled&&x.getClientRects().length>0);const first=items[0],last=items.at(-1);if(e.shiftKey&&(document.activeElement===first||document.activeElement===ref.current)){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}};document.addEventListener('keydown',handler);return()=>{document.removeEventListener('keydown',handler);document.body.style.overflow=old;prev?.focus()}},[]);
 return <div className="modal-scrim" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><section className={`modal ${wide?'wide':''}`} ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={title}><div className="section-head"><h2>{title}</h2><button className="icon-btn" aria-label="Đóng" onClick={onClose}><Icon of={X}/></button></div>{children}</section></div>
}
