#!/usr/bin/env python3
"""Fail-closed software WebGL and cinematic geometry smoke, for ubuntu Xvfb CI.

Run: xvfb-run -a python tests/verify_webgl.py
Not a physical GPU or production deployment acceptance test.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
GAME = (ROOT / "index.html").read_text(encoding="utf-8")
SKYLINE = ROOT / "assets" / "pittsburgh-night-skyline.jpg"
assert SKYLINE.is_file(), "Missing exported skyline"
assert "cinematic-geometry-v2" in GAME, "Cinematic geometry revision missing"
assert "function renderArmorFinish(m)" in GAME, "Rounded 3D armor geometry missing"

proof = ROOT / "proof" / "steel-city"
proof.mkdir(parents=True, exist_ok=True)
checks = []
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=os.getenv("CHROMIUM_PATH") or None,
        args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader",
              "--enable-unsafe-swiftshader", "--disable-dev-shm-usage"],
    )
    try:
        for label, viewport in (("desktop", {"width": 1280, "height": 760}),
                                ("mobile_emulated", {"width": 390, "height": 844})):
            page = browser.new_page(viewport=viewport, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("https://steel-city.local/assets/pittsburgh-night-skyline.jpg",
                       lambda route: route.fulfill(path=str(SKYLINE), content_type="image/jpeg"))
            page.set_content(GAME.replace("<head>", '<head><base href="https://steel-city.local/">', 1),
                             wait_until="domcontentloaded")
            page.wait_for_function("typeof window.__steelCityDebug === 'function'", timeout=20000)
            page.wait_for_function("document.getElementById('skyBackdrop').dataset.graphicsAsset === 'loaded'",
                                   timeout=15000)
            page.locator("#playMuted").click()
            before = page.evaluate("window.__steelCityDebug()")
            assert before.get("webgl") is True, f"WebGL fallback in {label}: {before}"
            assert before.get("graphicsRevision") == "cinematic-geometry-v2", before
            assert before.get("neighborhoodDetail") == "mount-washington-homes-v1", before
            info = page.evaluate("""() => {
                const c = document.getElementById('game'), gl = c.getContext('webgl');
                return {context:!!gl,version:gl?.getParameter(gl.VERSION)||null,
                    width:c.width,height:c.height};
            }""")
            assert info["context"] and info["width"] >= 350, (label, info)
            if label == "desktop":
                page.add_style_tag(content="#controls{display:block!important}")
            pad = page.locator("#moveJoystick").bounding_box()
            assert pad and pad["width"] >= 100, "Joystick touch target unavailable"
            x, y = pad["x"] + pad["width"] * .83, pad["y"] + pad["height"] * .50
            page.mouse.move(x, y)
            page.mouse.down()
            page.wait_for_timeout(700)
            moved = page.evaluate("window.__steelCityDebug()")
            page.mouse.up()
            page.wait_for_timeout(450)
            released = page.evaluate("window.__steelCityDebug()")
            assert moved["x"] > before["x"] + 0.5, (label, "WebGL joystick failed to move", {"before":before,"pressed":moved,"released":released})
            assert abs(moved["cameraYaw"] - before["cameraYaw"]) > 0.2, "WebGL camera did not follow"
            assert moved["motionBlend"] > 0.2, "3D gait stayed idle during movement"
            assert moved["gaitPhase"] > before["gaitPhase"] + 0.2, "3D gait phase did not advance"
            assert released["motionBlend"] < moved["motionBlend"] - 0.2, "Gait did not return to idle on release"
            page.wait_for_timeout(150)
            page.screenshot(path=str(proof / f"webgl-{label}.png"))
            assert not errors, (label, errors)
            checks.append({"viewport": label, "webgl": True,
                           "graphicsRevision": before["graphicsRevision"],
                           "GL": info, "browserErrors": errors})
            page.close()
    finally:
        browser.close()
(proof / "webgl-receipt.json").write_text(json.dumps({
    "status": "PASS", "rendering": "software swiftshader only",
    "physicalGpuVerified": False, "productionVerified": False,
    "checks": checks
}, indent=2), encoding="utf-8")
print(json.dumps({"status": "PASS", "software_webgl_only": True, "checks": checks}, indent=2))