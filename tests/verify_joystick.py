"""Narrow Playwright smoke for analog movement, camera follow, reset and exported skyline.

Checks source in this repository, not a production domain or a physical GPU.
"""
from pathlib import Path
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
ART = ROOT / "assets" / "pittsburgh-night-skyline.jpg"
assert ART.is_file(), "Graphics export missing"
assert 'id="moveJoystick"' in HTML, "Analog joystick missing"
assert all(f'id="{i}"' not in HTML for i in ("up", "down", "left", "right")), "Legacy direction buttons remain"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None)
    for label, width, height in (("desktop", 1280, 760), ("mobile", 390, 844)):
        page = browser.new_page(viewport={"width": width, "height": height}, has_touch=label == "mobile")
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route("**/assets/pittsburgh-night-skyline.jpg", lambda route: route.fulfill(path=str(ART), content_type="image/jpeg"))
        page.set_content(HTML.replace("<head>", '<head><base href="https://steel-city.local/">', 1), wait_until="domcontentloaded")
        page.wait_for_function("window.__steelCityDebug && document.querySelector('#skyBackdrop').dataset.graphicsAsset === 'loaded'", timeout=20000)
        if label == "desktop":
            # Touch control is intentionally hidden at desktop width. Reveal it only for input-unit proof.
            page.add_style_tag(content="#controls{display:block!important}")
        else:
            assert page.locator("#jump2").is_visible(), "Other touch actions unexpectedly occluded"
        page.locator("#playMuted").click()
        before = page.evaluate("window.__steelCityDebug()")
        pad = page.locator("#moveJoystick").bounding_box()
        assert pad and pad["width"] >= 100, "Joystick target too small"
        x, y = pad["x"] + pad["width"] * .83, pad["y"] + pad["height"] * .50
        page.mouse.move(x, y)
        page.mouse.down()
        page.wait_for_timeout(650)
        moved = page.evaluate("window.__steelCityDebug()")
        page.mouse.up()
        release = page.evaluate("({x:window.__steelJoystick.x,y:window.__steelJoystick.y,active:window.__steelJoystick.active})")
        assert moved["started"] and moved["x"] - before["x"] > 1.0, (label, before, moved)
        assert abs(moved["cameraYaw"] - before["cameraYaw"]) > 0.4, (label, "camera did not follow")
        assert not release["active"] and release["x"] == 0 and release["y"] == 0, (label, "stuck stick")
        assert not errors, (label, errors)
        print(f"PASS {label}: joystick x {before['x']:.2f}->{moved['x']:.2f}; camera {before['cameraYaw']:.2f}->{moved['cameraYaw']:.2f}; WebGL={moved['webgl']}; exported artwork loaded")
        page.close()
    browser.close()