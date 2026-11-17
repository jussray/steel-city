#!/usr/bin/env python3
"""Storyboard cast gate (lane C): hero, Mara + Market Square clock, Steel Stars,
Circuit Crew and alien bugs, in WebGL AND the forced canvas fallback.

Run: xvfb-run -a python3 tests/verify_cast.py
Software SwiftShader WebGL + Chromium canvas only. Not physical GPU, device,
deployment or painted-art parity proof. Every scene is reached with real
game controls (keyboard, E, F, story route button); no gameplay hooks.
"""
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
ASSET = ROOT / "assets" / "pittsburgh-night-skyline.jpg"
PROOF = ROOT / "proof" / "steel-city"
CAST_REVISION = "storyboard-cast-v1"
assert ASSET.is_file(), "Approved skyline export missing"
assert HTML.count("const CAST_REVISION='" + CAST_REVISION + "'") == 2, "cast revision must exist in both renderers"
assert HTML.count("castRevision:CAST_REVISION") == 2, "both renderers must expose the cast revision"
PROOF.mkdir(parents=True, exist_ok=True)

FORCE_FALLBACK = """(() => {
  const original = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function(type, ...args) {
    if (/webgl/i.test(type)) return null;
    return original.call(this, type, ...args);
  };
})();"""


def gold_ratio(page, clip):
    """Share of warm gold pixels inside a clip of the visible frame (canvas readback of a screenshot)."""
    png = page.screenshot(clip=clip)
    return page.evaluate("""async (b64) => {
        const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
        const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        const x = c.getContext('2d'); x.drawImage(img, 0, 0);
        const d = x.getImageData(0, 0, c.width, c.height).data; let gold = 0, cyan = 0, magenta = 0;
        for (let i = 0; i < d.length; i += 4) {
          const r = d[i], g = d[i+1], b = d[i+2];
          if (r > 200 && g > 150 && b < 150 && r > b + 80) gold++;
          if (g > 190 && b > 200 && r < 160) cyan++;
          if (r > 170 && b > 170 && g < 120) magenta++;
        }
        const n = d.length / 4; return {gold: gold / n, cyan: cyan / n, magenta: magenta / n};
    }""", __import__("base64").b64encode(png).decode())


def run(browser, mode):
    page = browser.new_page(viewport={"width": 1280, "height": 760}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    if mode == "fallback":
        page.add_init_script(FORCE_FALLBACK)
    page.route("https://steel-city.local/assets/pittsburgh-night-skyline.jpg",
               lambda route: route.fulfill(path=str(ASSET), content_type="image/jpeg"))
    page.route("https://steel-city.local/", lambda route: route.fulfill(body=HTML, content_type="text/html"))
    page.goto("https://steel-city.local/", wait_until="domcontentloaded")
    page.wait_for_function("typeof window.__steelCityDebug === 'function'", timeout=20000)
    page.wait_for_function("document.querySelector('#skyBackdrop').dataset.graphicsAsset === 'loaded'", timeout=20000)
    page.locator("#playMuted").click()
    dbg = lambda: page.evaluate("window.__steelCityDebug()")
    state = dbg()
    assert state["webgl"] is (mode == "webgl"), (mode, state)
    assert state["castRevision"] == CAST_REVISION, (mode, state)
    shots, metrics = {}, {}

    def shot(name, clip=None):
        rel = f"proof/steel-city/storyboard-cast-{mode}-{name}.png"
        page.wait_for_timeout(250)
        page.screenshot(path=str(ROOT / rel), clip=clip)
        data = (ROOT / rel).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) > 4096, rel
        shots[name] = rel

    def hold(key, until, timeout=30000):
        page.keyboard.down(key)
        try:
            page.wait_for_function(until, timeout=timeout)
        finally:
            page.keyboard.up(key)

    center = {"x": 440, "y": 200, "width": 400, "height": 460}
    # 1. Hero from behind on foot (walk forward so the camera trails the back).
    hold("KeyW", "window.__steelCityDebug().z < 25.6")
    page.wait_for_timeout(500)
    s = dbg()["castStats"]
    assert s["heroEmblems"] >= 1, (mode, s)
    assert s["maraParts"] > 0 and s["clockParts"] > 0, (mode, s)
    assert s["starPickups"] >= 5 and s["starSparkles"] >= 15, (mode, s)
    shot("hero-back")
    shot("hero-back-closeup", center)
    metrics["heroBackGold"] = gold_ratio(page, center)
    assert metrics["heroBackGold"]["gold"] > 0.002, (mode, "no gold emblem/trim on hero back", metrics)

    # 2. Mara + Market Square clock: step back toward Market Square so both are in front of the camera.
    hold("KeyA", "window.__steelCityDebug().x < -1.6")
    page.wait_for_timeout(400)
    shot("mara-clock")
    metrics["maraClock"] = gold_ratio(page, {"x": 560, "y": 120, "width": 520, "height": 520})
    assert metrics["maraClock"]["gold"] > 0.002, (mode, "clock face / sign not lit", metrics)

    # 3. Steel Star close-up: approach the star at z=15 without collecting it.
    hold("KeyD", "window.__steelCityDebug().x > -0.2")
    hold("KeyW", "window.__steelCityDebug().z < 19.2")
    page.wait_for_timeout(400)
    assert dbg()["stars"] == 0, "close-up must not collect the star"
    shot("star")
    metrics["star"] = gold_ratio(page, {"x": 340, "y": 60, "width": 600, "height": 500})
    assert metrics["star"]["gold"] > 0.01, (mode, "Steel Star is not reading as bright gold", metrics)

    # 4. Circuit Crew: talk to Mara with E (Act 1 -> Act 2), then use the story route button.
    hold("KeyS", "window.__steelCityDebug().z > 25.5")
    page.keyboard.press("KeyE")
    page.wait_for_function("window.__steelCityDebug().campaignStage === 1", timeout=5000)
    page.evaluate("document.getElementById('storyRoute').click()")
    page.wait_for_function("window.__steelCityDebug().z < -20", timeout=5000)
    hold("KeyS", "window.__steelCityDebug().z > -19.5")
    hold("KeyW", "window.__steelCityDebug().z < -19.8", 15000)
    page.wait_for_function("window.__steelCityDebug().castStats.crewHooded === 3", timeout=15000)
    page.wait_for_timeout(400)
    s = dbg()["castStats"]
    assert s["crewHooded"] == 3, (mode, s)
    shot("circuit-crew")
    metrics["crew"] = gold_ratio(page, {"x": 240, "y": 80, "width": 800, "height": 560})
    assert metrics["crew"]["cyan"] + metrics["crew"]["magenta"] > 0.0008, (mode, "no neon crew trim", metrics)

    # 5. Sky Mode hero + alien bugs: back at downtown, fly (F), climb toward the first bug.
    page.evaluate("document.getElementById('restart').click()")
    page.wait_for_function("window.__steelCityDebug().campaignStage === 0 && window.__steelCityDebug().z > 26", timeout=5000)
    page.keyboard.press("KeyF")
    page.wait_for_function("window.__steelCityDebug().skyMode === true", timeout=5000)
    hold("Space", "window.__steelCityDebug().y > 10.8", 30000)
    # Software frames can take hundreds of ms: wait for a rendered Sky Mode frame, not a fixed sleep.
    page.wait_for_function("window.__steelCityDebug().castStats.bootJets >= 2", timeout=15000)
    page.wait_for_timeout(400)
    s = dbg()["castStats"]
    assert s["bootJets"] >= 2 and s["heroEmblems"] >= 1, (mode, s)
    assert s["bugsWinged"] >= 4, (mode, s)
    shot("sky-hero")
    shot("sky-hero-closeup", center)
    metrics["skyHero"] = gold_ratio(page, center)
    assert metrics["skyHero"]["cyan"] > 0.002, (mode, "no cyan boot thrusters", metrics)
    hold("KeyW", "window.__steelCityDebug().z < 20.5", 30000)
    page.wait_for_timeout(400)
    shot("alien-bugs")
    metrics["bugs"] = gold_ratio(page, {"x": 0, "y": 0, "width": 1280, "height": 760})
    assert metrics["bugs"]["magenta"] > 0.0003, (mode, "alien bugs show no magenta glow", metrics)
    final = dbg()
    assert not errors, (mode, errors)
    page.close()
    return {"mode": mode, "castRevision": final["castRevision"], "castStats": final["castStats"],
            "marketClock": final["marketClock"], "screenshots": shots, "pixelShares": metrics,
            "jsErrors": errors}


def main():
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader",
                  "--enable-unsafe-swiftshader", "--disable-dev-shm-usage"])
        try:
            for mode in ("webgl", "fallback"):
                checks.append(run(browser, mode))
        finally:
            browser.close()
    receipt = {"status": "PASS", "castRevision": CAST_REVISION,
               "rendering": "software swiftshader WebGL + Chromium canvas fallback",
               "physicalGpuVerified": False, "paintedArtParity": False, "checks": checks}
    (PROOF / "storyboard-cast-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "castRevision": CAST_REVISION,
                      "screenshots": [v for c in checks for v in c["screenshots"].values()]}, indent=2))


if __name__ == "__main__":
    main()
