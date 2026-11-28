#!/usr/bin/env python3
"""Verify actual WebGL ellipsoid source has outward faces and smooth analytic normals."""
from pathlib import Path
from playwright.sync_api import sync_playwright
source = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
start = source.index("ellipsoid(x,y,z,rx,ry,rz,col,emi=0,segments=10,rings=6){")
end = source.index("\n}}\nconst STEEL_HILL", start)
method = source[start:end+2]
with sync_playwright() as play:
    browser = play.chromium.launch()
    page = browser.new_page()
    result = page.evaluate("""method => {
      const sub=(a,b)=>a.map((v,i)=>v-b[i]),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],unit=a=>{const l=Math.hypot(...a)||1;return a.map(x=>x/l)},dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
      const M=new Function("sub","cross","unit","c","return class {constructor(){this.v=[]}vert(p,n,c,e){this.v.push({p,n,c,e})}tri(a,b,d,col,emi){const n=unit(cross(sub(b,a),sub(d,a)));for(const p of [a,b,d])this.vert(p,n,col,emi)}"+method+"}")(sub,cross,unit,x=>x);
      const checks=[];
      for(const [segments,rings] of [[6,3],[8,4],[12,8]]){
        const m=new M(),center=[1,2,3],r=[.5,.8,.3];m.ellipsoid(...center,...r,"#22365a",.12,segments,rings);
        const triangles=2*segments*(rings-1);
        if(m.v.length!==triangles*3)throw Error("Triangle budget changed");
        for(let i=0;i<m.v.length;i+=3){
          const [a,b,c]=m.v.slice(i,i+3),mid=a.p.map((x,j)=>(x+b.p[j]+c.p[j])/3-center[j]);
          if(dot(cross(sub(b.p,a.p),sub(c.p,a.p)),mid)<=0)throw Error("Inward triangle");
        }
        for(const v of m.v){
          const grad=unit(v.p.map((x,i)=>(x-center[i])/(r[i]*r[i])));
          if(dot(grad,v.n)<.99999||Math.abs(Math.hypot(...v.n)-1)>1e-7)throw Error("Invalid smooth normal");
        }
        checks.push({segments,rings,triangles});
      }
      return checks;
    }""", method)
    browser.close()
print("PASS: outward winding, analytic normals, unchanged triangle budget", result)
