#!/usr/bin/env python3
"""Verify actual hillside homes in WebGL AND forced software fallback.

Uses real Chromium Playwright with SwiftShader for WebGL. This is not physical
GPU, real phone, deployed URL, or commercial-game visual-quality proof.
"""
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
ASSET = ROOT / "assets" / "pittsburgh-night-skyline.jpg"
PROOF = ROOT / "proof" / "steel-city"
assert ASSET.is_file(), "Approved skyline export missing"
PROOF.mkdir(parents=True, exist_ok=True)

def inspect(browser, label, width, height, force_fallback):
    page = browser.new_page(viewport={"width": width, "height": height},
                            device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.route("https://steel-city.local/assets/pittsburgh-night-skyline.jpg",
               lambda route: route.fulfill(path=str(ASSET), content_type="image/jpeg"))

    if force_fallback:
        # Patch the browser's existing realm BEFORE set_content executes game JS.
        page.evaluate("""() => {
          const original = HTMLCanvasElement.prototype.getContext;
          HTMLCanvasElement.prototype.getContext = function(type, ...args) {
            if (/webgl/i.test(type)) return null;
            return original.call(this, type, ...args);
          };
        }""")

    page.set_content(
        HTML.replace("<head>", '<head><base href="https://steel-city.local/">', 1),
        wait_until="domcontentloaded")
    page.wait_for_function("typeof window.__steelCityDebug === 'function'",
                           timeout=20000)
    page.wait_for_function(
        "document.querySelector('#skyBackdrop').dataset.graphicsAsset === 'loaded'",
        timeout=20000)
    state = page.evaluate("window.__steelCityDebug()")
    mode = "fallback" if force_fallback else "webgl"
    assert state["webgl"] is (not force_fallback), (label, mode, state)
    assert state["graphicsRevision"] == "cinematic-geometry-v3", state
    assert state["neighborhoodDetail"] == "mount-washington-homes-v2", state
    assert state["lightingRevision"] == "rain-slick-neon-v2", state
    assert state["bridgeDetail"] == "three-rivers-lattice-v1", state
    assert state["bridgeTrussSegments"] == 120, (label, mode, state)
    assert state["hillsideHomeCount"] == 11, (label, mode, state)
    assert state["hillsideSolidCount"] == 11, (label, mode, state)

    homes = state["hillsideHomeFootprints"]
    expected_xs = [-82 + i * 6.5 for i in range(2, 24, 2)]
    assert len(homes) == 11 and [h["x"] for h in homes] == expected_xs, homes
    assert all(h["z"] == -75.5 and h["w"] == 4.2 and h["d"] == 3.5
               and h["h"] == 2.7 for h in homes), homes
    assert page.evaluate("window.__steelHillsideSmoke().passed"), mode

    # Verify minimap actually draws a house footprint, rather than just exposing
    # counts. Choose x=-56 where no original high-rise covers the house.
    scale, center_z = (1.7, 158) if force_fallback else (1.72, 159)
    house_x, house_z = -56, -75.5
    pixel_x = round(150 + house_x * scale)
    pixel_y = round(center_z + house_z * scale)
    page.wait_for_function("""({x,y}) => {
      const c = document.getElementById('map');
      const rgb = c.getContext('2d').getImageData(x,y,1,1).data;
      return rgb[0] === 201 && rgb[1] === 159 && rgb[2] === 107;
    }""", arg={"x":pixel_x,"y":pixel_y}, timeout=10000)

    page.locator("#playMuted").click()
    page.wait_for_timeout(450)
    image = PROOF / f"hillside-{label}-{mode}.png"
    page.screenshot(path=str(image))
    assert not errors, (label, mode, errors)
    page.close()
    return {
        "viewport": label, "mode": mode, "webgl": not force_fallback,
        "count": state["hillsideHomeCount"], "solids": state["hillsideSolidCount"],
        "bridgeDetail": state["bridgeDetail"],
        "bridgeTrussSegments": state["bridgeTrussSegments"],
        "footprints": homes, "minimapPixel": [201, 159, 107],
        "screenshot": str(image.relative_to(ROOT)), "jsErrors": errors,
    }

with sync_playwright() as play:
    browser = play.chromium.launch(
        headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
        args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader",
              "--enable-unsafe-swiftshader", "--disable-dev-shm-usage"])
    try:
        results = [
            inspect(browser, label, width, height, forced)
            for label, width, height in (
                ("desktop", 1280, 760), ("mobile-emulated", 390, 844))
            for forced in (False, True)
        ]
    finally:
        browser.close()

for label in ("desktop", "mobile-emulated"):
    pair = [r for r in results if r["viewport"] == label]
    assert len(pair) == 2
    assert pair[0]["bridgeTrussSegments"] == pair[1]["bridgeTrussSegments"] == 120, (
        label, "WebGL/fallback steel bridge truss drift", pair)
    assert pair[0]["footprints"] == pair[1]["footprints"], (
        label, "WebGL/fallback hillside layout drift", pair)

receipt = {
    "status": "PASS", "renderer": "software Chromium / SwiftShader",
    "hardwareGpuVerified": False, "liveDeploymentVerified": False,
    "checks": results,
}
(PROOF / "hillside-parity-receipt.json").write_text(
    json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "status": "PASS", "renderers": 2, "viewports": 2,
    "homesPerRenderer": 11, "minimap": "verified colored footprints",
    "realDeviceOrProduction": "not verified",
}, indent=2))
