#!/usr/bin/env python3
"""Focused checks of extracted production JS with deterministic fixtures.

These verify the collection boundary and light selection, not actual movement,
GPU performance, shader compilation or visual fidelity.
"""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "index.html").read_text(encoding="utf-8")

def extract(pattern):
    result = re.findall(pattern, source)
    assert len(result) == 1, f"Expected one source seam, got {len(result)}: {pattern}"
    return result[0]

webgl = extract(r"sagaTick\(dt\);(for\(let p of pickups\)[^\n]+)")
canvas = extract(r"sagaTick\(dt\);(for\(let p of stars\).*?)(?=if\(state\.stars>=5&&Math\.hypot)")
glow = extract(r"(function selectLocalGlow\([\s\S]*?\n\})")
with sync_playwright() as play:
    browser = play.chromium.launch()
    page = browser.new_page()
    results = page.evaluate("""([webgl, canvas, glow]) => {
        const assert = (condition, label) => { if (!condition) throw new Error(label); };
        const results = [];
        for (const [renderer, code] of [['WebGL', webgl], ['Canvas', canvas]]) {
            const state = {pos:{x:0,y:0,z:0},x:0,y:0,z:0,stars:0};
            const list = Array.from({length:7}, () => ({x:0,y:1.5,z:0,taken:false}));
            const node = {textContent:''};
            let events = 0;
            const run = new Function('state','pickups','stars','el','$','toast','note',code);
            const tick = () => run(state,list,list,()=>node,()=>node,()=>events++,()=>{});
            tick();
            assert(state.stars === 5 && list.filter(p=>p.taken).length === 5, renderer+' collection cap');
            assert(events === 5, renderer+' exactly five collection events');
            tick();
            assert(state.stars === 5 && events === 5, renderer+' no repeated events');
            state.stars=0; list.forEach(p=>p.taken=false); events=0;
            list[0].x=100; list[1].x=100;
            tick();
            assert(state.stars === 5 && list[6].taken, renderer+' alternate routes');
            results.push(renderer+' collection contract');
        }
        const select = new Function(glow+';return selectLocalGlow;')();
        const p={x:0,y:0,z:0}, star={x:1,y:1,z:2,taken:false},
              far={x:60,y:0,z:0,taken:false}, shot={x:2,y:1,z:0};
        const check = (test,label) => {assert(test,label);results.push(label)};
        check(select(p,false,0,[star],[shot],0).gold[3]===0,'No title-scene glow');
        check(select(p,true,0,[far,star],[shot],0).gold[0]===1,'Nearest eligible star');
        check(select(p,true,0,[{...star,taken:true}],[shot],0).gold[3]===0,'Collected star excluded');
        check(select(p,true,5,[star],[shot],0).gold[3]===0,'Goal completion disables gold spill');
        check(select(p,true,0,[star],[shot],0).cyan[0]===2,'Active cyan pulse');
        check(select(p,true,0,[far],[far],0).cyan[3]===0,'Distant pulse excluded');
        return results;
    }""", [webgl,canvas,glow])
    browser.close()
print("PASS:", "; ".join(results))
