#!/usr/bin/env python3
"""Simulation clock regression: source-defined timing, bounded physics steps."""
from pathlib import Path
from playwright.sync_api import sync_playwright
source=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
start=source.index("window.__steelSimulationClock=")
end=source.index("window.__steelHeadingForMotion=",start)
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page()
    result=page.evaluate("""source=>{
 const win={};new Function('window',source)(win);
 const run=(hz)=>{const clock=win.__steelSimulationClock();let distance=0,steps=0,maxStep=0;const tick=dt=>{if(dt<0||dt>.05000001)throw Error('unsafe step');distance+=7*dt;steps++;maxStep=Math.max(maxStep,dt)};clock.advance(0,tick);for(let i=1;i<=hz*10;i++)clock.advance(i*1000/hz,tick);return {hz,distance,steps,maxStep}};
 const samples=[2,4,10,30,60].map(run);
 if(samples.some(x=>Math.abs(x.distance-70)>1e-6))throw Error('slow-render movement loses elapsed time '+JSON.stringify(samples));
 const c=win.__steelSimulationClock();let time=0;const tick=dt=>time+=dt;
 c.advance(0,tick);c.advance(10000,tick);if(Math.abs(time-.5)>1e-8)throw Error('catch-up not bounded');
 c.advance(11000,tick,true);c.advance(60000,tick);if(Math.abs(time-.5)>1e-8)throw Error('hidden time integrated');
 c.advance(60100,tick);if(Math.abs(time-.6)>1e-8)throw Error('resume failed');
 c.reset();c.advance(99999,tick);if(Math.abs(time-.6)>1e-8)throw Error('reset failed');
 return {samples,catchupCap:.5,hiddenReset:true};
}""",source[start:end])
    browser.close()
print("PASS:",result)
