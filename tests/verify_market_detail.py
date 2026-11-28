#!/usr/bin/env python3
"""Static storefront geometry contract, not GPU or visual acceptance."""
from pathlib import Path
from playwright.sync_api import sync_playwright
source=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
start=source.index("function addMarketStorefronts(")
end=source.index("const marketDetail=addMarketStorefronts",start)
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page()
    result=page.evaluate("""source=>{
 const buildings=[{"x":-23,"z":16,"w":8,"d":8,"h":9},{"x":23,"z":39,"w":9,"d":8,"h":10},{"x":-17,"z":-7,"w":9,"d":11,"h":16},{"x":0,"z":27,"w":4,"d":4,"h":5},{"x":-23,"z":-50,"w":8,"d":8,"h":9},{"x":23,"z":16,"w":8,"d":8,"h":10,"kind":"hillside-home"},{"x":23,"z":16,"w":8,"d":8,"h":40}],before=JSON.stringify(buildings),calls=[];
 const result=new Function('mesh','buildings',source+';return addMarketStorefronts(mesh,buildings)')({box:(...a)=>calls.push(a)},buildings);
 if(JSON.stringify(buildings)!==before||result.facades!==3||result.pieces!==66||calls.length!==66)throw Error('wrong count or collision mutation');
 for(let i=0;i<calls.length;i++){const b=buildings[Math.floor(i/22)],a=calls[i],face=b.x+Math.sign(-b.x)*b.w/2;if(!a.slice(0,6).every(Number.isFinite)||Math.abs(a[0]-face)+a[3]/2>.101||Math.abs(a[2]-b.z)+a[5]/2>b.d/2||a[1]-a[4]/2<0||a[1]+a[4]/2>3)throw Error('cladding out of bounds')}
 return result;
}""",source[start:end])
    browser.close()
print("PASS:",result)
