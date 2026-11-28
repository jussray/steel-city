#!/usr/bin/env python3
"""Source-defined dual touch camera ownership and heading regression."""
from pathlib import Path
from playwright.sync_api import sync_playwright
source=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
start=source.index("window.__steelHeadingForMotion=")
end=source.index("</script>",start)
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page()
    result=page.evaluate("""source=>{
 const listeners={};const target=()=>({events:{},addEventListener(k,fn){(this.events[k]??=[]).push(fn)},fire(k,e={}){for(const fn of this.events[k]||[])fn({preventDefault(){},...e})}});
 const win=target(),doc=target(),canvas=target();let captured=null;
 canvas.setPointerCapture=id=>captured=id;canvas.hasPointerCapture=id=>captured===id;canvas.releasePointerCapture=id=>{captured=null;canvas.fire('lostpointercapture',{pointerId:id})};
 const state={started:true,yaw:0,pitch:.22},sky={active:true};let shots=0;
 win.__steelJoystick={active:true,baseYaw:0};
 new Function('window','document',source)(win,doc);
 const look=win.__steelBindLook(canvas,state,sky,()=>shots++);
 const near=(a,b)=>Math.abs(a-b)<1e-9;
 for(const [x,z] of [[1,0],[-1,0],[0,-1],[0,1],[3,-4]]){const a=win.__steelHeadingForMotion(x,z),m=Math.hypot(x,z);if(!near(-Math.sin(a),x/m)||!near(-Math.cos(a),z/m))throw Error('heading mismatch')}
 const e=(id,x,y)=>({pointerId:id,clientX:x,clientY:y,pointerType:'touch',button:0});
 canvas.fire('pointerdown',e(1,100,100));canvas.fire('pointerdown',e(2,200,200));
 canvas.fire('pointermove',e(2,300,300));if(state.yaw!==0)throw Error('foreign pointer changed camera');
 canvas.fire('pointermove',e(1,150,125));if(!near(state.yaw,.3)||!near(state.pitch,.32)||!near(win.__steelJoystick.baseYaw,.3))throw Error('dual touch look failed');
 canvas.fire('pointermove',e(1,100,100));canvas.fire('pointerup',e(1,100,100));if(shots!==0||look.active)throw Error('drag incorrectly fired');
 canvas.fire('pointerdown',e(3,100,100));canvas.fire('pointerup',e(3,101,101));if(shots!==1)throw Error('tap not preserved');
 canvas.fire('pointerdown',e(4,100,100));canvas.fire('pointercancel',e(4,100,100));if(look.active||captured!==null)throw Error('cancel stuck');
 canvas.fire('pointerdown',e(5,100,100));win.fire('blur');if(look.active||captured!==null)throw Error('blur stuck');
 canvas.fire('wheel',{deltaY:1});if(!near(state.pitch,.27))throw Error('wheel pitch');
 return {headingDirections:5,foreignPointer:true,dualTouch:true,dragNoShot:true,tap:true,cancel:true,blur:true,wheel:true};
}""",source[start:end])
    browser.close()
print("PASS:",result)
