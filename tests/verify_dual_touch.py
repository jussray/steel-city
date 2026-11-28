#!/usr/bin/env python3
"""Real Chromium touch events in both renderers; not physical-device proof."""
import json
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
ART = ROOT / "assets" / "pittsburgh-night-skyline.jpg"
PROOF = ROOT / "proof" / "steel-city"
PROOF.mkdir(parents=True, exist_ok=True)
FORCE_FALLBACK = """(() => {
 const original=HTMLCanvasElement.prototype.getContext;
 HTMLCanvasElement.prototype.getContext=function(type,...args){
  return /webgl/i.test(type)?null:original.call(this,type,...args);
 };
})();"""

def verify(browser, mode, width, height):
    label = f"{mode}-{width}x{height}"
    context = browser.new_context(viewport={"width":width,"height":height},
                                  has_touch=True,is_mobile=True,device_scale_factor=1)
    try:
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        if mode == "fallback":
            page.add_init_script(FORCE_FALLBACK)
        page.route("https://steel-city.local/",lambda route:route.fulfill(body=HTML,content_type="text/html"))
        page.route("**/assets/pittsburgh-night-skyline.jpg",lambda route:route.fulfill(path=str(ART),content_type="image/jpeg"))
        page.goto("https://steel-city.local/",wait_until="domcontentloaded")
        page.wait_for_function("typeof window.__steelCityDebug === 'function'",timeout=30000)
        play = page.locator("#playMuted").bounding_box()
        assert play and 0 <= play["x"] and play["x"]+play["width"] <= width, (label,play)
        assert 0 <= play["y"] and play["y"]+play["height"] <= height, (label,play)
        page.touchscreen.tap(play["x"]+play["width"]/2,play["y"]+play["height"]/2)
        page.wait_for_function("window.__steelCityDebug().started",timeout=15000)
        page.wait_for_function("getComputedStyle(document.querySelector('#titlecover')).pointerEvents === 'none'",timeout=15000)
        dbg = lambda:page.evaluate("window.__steelCityDebug()")
        assert dbg()["webgl"] is (mode=="webgl"), (label,dbg())
        stick = page.locator("#moveJoystick").bounding_box()
        assert stick and stick["width"]>=100,(label,stick)
        jx,jy=stick["x"]+stick["width"]/2,stick["y"]+stick["height"]/2
        # Find an unobscured horizontal camera lane in the real on-screen layout.
        lane=page.evaluate("""() => {
          const canvas=document.querySelector('#game');
          for(const y of [.48,.54,.42,.60].map(v=>Math.round(innerHeight*v))){
            for(const x of [.38,.44,.50,.30].map(v=>Math.round(innerWidth*v))){
              if([0,22,44,66].every(d=>document.elementFromPoint(x+d,y)===canvas))return {x,y};
            }
          }
          return null;
        }""")
        assert lane,(label,"no free camera drag lane")
        cx,cy=lane["x"],lane["y"]
        cdp=context.new_cdp_session(page)
        def pt(i,x,y):return {"id":i,"x":x,"y":y,"radiusX":5,"radiusY":5,"force":1}
        def touch(kind,points):cdp.send("Input.dispatchTouchEvent",{"type":kind,"touchPoints":points})
        before=dbg()
        touch("touchStart",[pt(1,jx,jy),pt(2,cx,cy)])
        try:
            page.wait_for_function("window.__steelJoystick.active && window.__steelLook.active",timeout=10000)
            # Both contacts remain down while the hero walks and the other finger looks.
            touch("touchMove",[pt(1,jx,jy-stick["height"]*.30),pt(2,cx+60,cy)])
            page.wait_for_function("""start=>{
                const d=window.__steelCityDebug();
                return d.lookActive && Math.abs(d.cameraYaw-start.cameraYaw)>.25 &&
                  Math.hypot(d.x-start.x,d.z-start.z)>1;
            }""",arg=before,timeout=20000)
            held=dbg()
            assert abs(held["cameraYaw"]-before["cameraYaw"]-.36)<.08,(label,"camera auto-follow fought drag",held)
            assert page.evaluate("window.__steelJoystick.active && window.__steelLook.active"),label
            page.screenshot(path=str(PROOF/f"dual-touch-{label}-held.png"))
        finally:
            touch("touchEnd",[])
        page.wait_for_function("!window.__steelJoystick.active && !window.__steelLook.active",timeout=10000)
        stopped=dbg()
        page.wait_for_timeout(350)
        after=dbg()
        assert math.hypot(after["x"]-stopped["x"],after["z"]-stopped["z"])<.15,(label,"movement stuck",stopped,after)
        assert page.evaluate("window.__steelJoystick.x===0 && window.__steelJoystick.y===0 && scrollX===0 && scrollY===0"),label
        touch("touchStart",[pt(3,jx,jy),pt(4,cx,cy)])
        page.wait_for_function("window.__steelJoystick.active && window.__steelLook.active",timeout=10000)
        touch("touchCancel",[])
        page.wait_for_function("!window.__steelJoystick.active && !window.__steelLook.active",timeout=10000)
        # Controls still reachable after gestures; the full layout suite checks every act.
        for selector in ("#moveJoystick","#talkMobile","#skyMobile","#fireMobile","#descendMobile","#sprint","#jump2"):
            assert page.locator(selector).is_visible(),(label,selector)
        assert not errors,(label,errors)
        page.screenshot(path=str(PROOF/f"dual-touch-{label}-released.png"))
        return {"renderer":mode,"viewport":[width,height],"distance":round(math.hypot(held["x"]-before["x"],held["z"]-before["z"]),2),"yawDelta":round(held["cameraYaw"]-before["cameraYaw"],3),"release":True,"cancel":True,"scroll":[0,0],"pageErrors":errors}
    finally:
        context.close()

with sync_playwright() as p:
    browser=p.chromium.launch(headless=False,executable_path=os.getenv("CHROMIUM_PATH") or None,
      args=["--no-sandbox","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--disable-dev-shm-usage"])
    results={}
    try:
        for mode in ("webgl","fallback"):
            for width,height in ((390,664),(750,342)):
                label=f"{mode}-{width}x{height}"
                results[label]=verify(browser,mode,width,height)
                print("PASS",label,json.dumps(results[label]),flush=True)
    finally:
        browser.close()
(PROOF/"dual-touch-receipt.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
