#!/usr/bin/env python3
"""Software WebGL proof: actual bloom shaders, glow spread, alpha, resize, opt-out.
Does not prove physical GPU performance or artistic parity.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
GAME = (ROOT / "index.html").read_text(encoding="utf-8")
SKYLINE = ROOT / "assets" / "pittsburgh-night-skyline.jpg"
PROOF = ROOT / "proof" / "steel-city"
PROOF.mkdir(parents=True, exist_ok=True)
start = GAME.index("function createSteelBloom(){")
end = GAME.index("const steelBloom=createSteelBloom();", start)
bloom_source = GAME[start:end]
fixture = r"""source => {
    const canvas=document.createElement('canvas');
    canvas.width=128;canvas.height=128;
    const gl=canvas.getContext('webgl',{alpha:true,preserveDrawingBuffer:true});
    if(!gl)throw Error('Fixture requires WebGL');
    function sh(t,s){const x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);
      if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(x));return x}
    const pr=gl.createProgram();
    gl.attachShader(pr,sh(gl.VERTEX_SHADER,'void main(){gl_Position=vec4(0.,0.,0.,1.);}'));
    gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,'precision mediump float;void main(){gl_FragColor=vec4(1.);}'));
    gl.linkProgram(pr);
    if(!gl.getProgramParameter(pr,gl.LINK_STATUS))throw Error('Fixture program link failed');
    gl.useProgram(pr);
    const loc={p:-1,n:-1,c:-1,e:-1};
    const make=new Function('gl','canvas','sh','pr','loc','location',source+';return createSteelBloom();');
    const bloom=make(gl,canvas,sh,pr,loc,{search:'?bloom=on'});
    if(!bloom||!bloom.stats.enabled)throw Error('Bloom setup: '+JSON.stringify(bloom?.stats));
    const pixel=(x,y)=>{const p=new Uint8Array(4);gl.readPixels(x,y,1,1,gl.RGBA,gl.UNSIGNED_BYTE,p);return [...p]};
    function draw(){
       gl.viewport(0,0,128,128);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
       gl.enable(gl.SCISSOR_TEST);gl.scissor(56,56,16,16);
       gl.clearColor(1,.76,.04,1);gl.clear(gl.COLOR_BUFFER_BIT);gl.disable(gl.SCISSOR_TEST);
    }
    draw();
    const before=pixel(54,64),farBefore=pixel(8,8);
    bloom.apply();
    const after=pixel(54,64),farAfter=pixel(8,8),center=pixel(64,64);
    const error=gl.getError();
    if(error!==gl.NO_ERROR)throw Error('Bloom WebGL error '+error);
    if(before[0]!==0||before[3]!==0||after[0]<8||after[3]<8)throw Error('No measured gold spill '+JSON.stringify({before,after}));
    if(farBefore.some((v,i)=>v!==farAfter[i]))throw Error('Unlit transparent background changed');
    if(center[0]<240||center[3]!==255)throw Error('Bright source was damaged');
    if(!bloom.stats.enabled||bloom.stats.frames!==1||bloom.stats.bufferWidth!==64||bloom.stats.bufferHeight!==64)throw Error('Unexpected buffer '+JSON.stringify(bloom.stats));
    if(gl.getParameter(gl.CURRENT_PROGRAM)!==pr||!gl.isEnabled(gl.DEPTH_TEST)||!gl.isEnabled(gl.CULL_FACE))throw Error('Scene state not restored');
    return {before,after,farAfter,center,stats:bloom.stats,error};
}"""
results = {}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,
        executable_path=os.getenv("CHROMIUM_PATH") or None,
        args=["--no-sandbox","--use-gl=angle","--use-angle=swiftshader",
              "--enable-unsafe-swiftshader","--disable-dev-shm-usage"])
    try:
        page = browser.new_page()
        results["pixel_fixture"] = page.evaluate(fixture, bloom_source)
        page.close()
        for label, viewport, enabled in (
            ("desktop", {"width":1280,"height":760}, True),
            ("mobile_emulated", {"width":390,"height":844}, True),
            ("opt_out", {"width":390,"height":844}, False),
            ("default_safe", {"width":390,"height":844}, False),
        ):
            page = browser.new_page(viewport=viewport, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("https://steel-city.local/index.html*", lambda route: route.fulfill(body=GAME, content_type="text/html"))
            page.route("https://steel-city.local/assets/pittsburgh-night-skyline.jpg",
                       lambda route: route.fulfill(path=str(SKYLINE), content_type="image/jpeg"))
            page.goto("https://steel-city.local/index.html" + ("?bloom=on" if enabled else ("" if label == "default_safe" else "?bloom=off")),wait_until="domcontentloaded")
            page.wait_for_function("typeof window.__steelCityDebug === 'function'",timeout=20000)
            assert page.evaluate("window.__steelCityDebug().webgl"), label
            page.locator("#playMuted").click()
            if enabled:
                page.wait_for_function("window.__steelCityDebug().bloom?.frames >= 2",timeout=30000)
                first=page.evaluate("window.__steelCityDebug().bloom")
                assert first["enabled"] and max(first["bufferWidth"],first["bufferHeight"]) <= 640, first
                page.set_viewport_size({"width":760,"height":440})
                page.wait_for_function("""previous => {
                    const b=window.__steelCityDebug().bloom;
                    return b.frames>previous.frames && b.bufferWidth===380 && b.bufferHeight===220;
                }""",arg=first,timeout=30000)
            else:
                assert page.evaluate("window.__steelCityDebug().bloom.enabled === false && window.__steelCityDebug().bloom.frames === 0")
            page.keyboard.press("f")
            page.wait_for_function("window.__steelCityDebug().skyMode",timeout=15000)
            assert not errors,(label,errors)
            page.screenshot(path=str(PROOF / f"bloom-{label}.png"))
            results[label]=page.evaluate("window.__steelCityDebug().bloom")
            page.close()
    finally:
        browser.close()
(PROOF / "bloom-receipt.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
print(json.dumps(results,indent=2))
