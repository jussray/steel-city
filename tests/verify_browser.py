#!/usr/bin/env python3
"""Playwright smoke gate for the Steel City browser prototype.

Install: pip install playwright && python -m playwright install chromium
Run offline: python tests/verify_browser.py
Run a *real deployed URL*: python tests/verify_browser.py --url https://YOUR-EXISTING-ROUTE/steel-city/
Require hardware WebGL proof on a physical device: python tests/verify_browser.py --url URL --headed --require-hardware

Offline DOM testing, viewport emulation, and software WebGL do NOT establish
real device, GPU, Meta-glasses, production-route, or console-quality proof.
"""
import argparse
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]


def verify(page, url, require_webgl, require_hardware):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    if url:
        response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
        assert response and response.status == 200, f"Deployed route not HTTP 200: {response.status if response else 'none'}"
        assert url.rstrip("/") in page.url.rstrip("/"), f"Unexpected redirect to {page.url}"
        source = "deployed_http"
    else:
        source = "offline_dom_only"
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        # The graphics branch uses document.baseURI for its checked-in skyline.
        # set_content() otherwise runs at about:blank, which cannot resolve relative URLs.
        if "assets/pittsburgh-night-skyline.jpg" in html:
            asset = ROOT / "assets" / "pittsburgh-night-skyline.jpg"
            assert asset.is_file(), "Checked-in skyline asset is missing"
            page.route(
                "https://steel-city.test/assets/pittsburgh-night-skyline.jpg",
                lambda route: route.fulfill(path=str(asset), content_type="image/jpeg"),
            )
            html = html.replace("<head>", '<head><base href="https://steel-city.test/">', 1)
        page.set_content(html, wait_until="domcontentloaded")
    page.wait_for_function("typeof window.__steelCityDebug === 'function'", timeout=10000)
    before = page.evaluate("window.__steelCityDebug()")
    assert before.get("neighborhoodDetail") == "mount-washington-homes-v1", before
    assert before.get("campaignStage") == 0 and before.get("started") is False, before
    # Visual-to-code gate: key art belongs to the title, not the rendered world.
    title_art = page.evaluate("""() => getComputedStyle(document.querySelector('#titlecover')).backgroundImage""")
    assert "data:image/jpeg" in title_art, "Cinematic title image absent"
    assert page.locator("#playMuted").is_visible(), "Start control must be readable"
    assert not page.locator("#hud").is_visible(), "Gameplay HUD must not overlap title art"
    page.locator("#playMuted").click()
    # The title fades to opacity 0 instead of being display:none.
    page.wait_for_function("""() => {
        const title = document.querySelector('#titlecover');
        const style = getComputedStyle(title);
        return title.classList.contains('hidden') &&
               Number(style.opacity) === 0 &&
               style.pointerEvents === 'none';
    }""", timeout=3000)
    assert page.locator("#hud").is_visible(), "Gameplay HUD missing after play"
    proof = ROOT / "proof" / "steel-city"
    proof.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(proof / f"fallback-{page.viewport_size['width']}px.png"))
    page.locator("#storyOpen").click()
    assert page.locator(".storyAct").count() == 7, "Expected seven acts in journal"
    page.locator("#storyClose").click()
    page.locator("#storyRoute").click()
    page.keyboard.press("e")
    page.wait_for_timeout(80)
    assert page.evaluate("window.__steelCityDebug().campaignStage") == 1, "Mara mission cannot progress"
    page.keyboard.press("f")
    page.wait_for_timeout(60)
    flying = page.evaluate("window.__steelCityDebug()")
    assert flying.get("skyMode") is True, "Sky Mode did not activate"
    y = flying["y"]
    page.keyboard.down("Space")
    page.wait_for_timeout(250)
    page.keyboard.up("Space")
    assert page.evaluate("window.__steelCityDebug().y") > y, "Flight ascend did not work"
    page.keyboard.press("j")
    page.wait_for_timeout(30)
    assert not errors, f"Browser JS exceptions: {errors}"
    page.locator("#restart").click()
    page.wait_for_timeout(80)
    state = page.evaluate("window.__steelCityDebug()")
    assert state["campaignStage"] == 0 and state["skyMode"] is False, "Reset did not return to initial mode"
    assert not errors, errors
    gl = page.evaluate("""() => {
      const canvas = document.querySelector('#game');
      const context = canvas && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
      if (!context) return {webglContext:false, renderer:null, vendor:null};
      const ext = context.getExtension('WEBGL_debug_renderer_info');
      return {webglContext:true,
          renderer:ext ? context.getParameter(ext.UNMASKED_RENDERER_WEBGL) : null,
          vendor:ext ? context.getParameter(ext.UNMASKED_VENDOR_WEBGL) : null};
    }""")
    assert not require_webgl or state.get("webgl") is True, f"WebGL renderer not active: {state}"
    if require_hardware:
        assert source == "deployed_http", "Hardware release gate requires a real deployed URL"
        assert state.get("webgl") is True and gl["webglContext"], "WebGL rendering not active"
        vendor = (gl.get("vendor") or "").lower()
        renderer = (gl.get("renderer") or "").lower()
        assert vendor and renderer, "GPU identity inaccessible; hardware verification remains UNKNOWN"
        assert not any(t in vendor + renderer for t in ("swiftshader", "software", "llvmpipe", "mesa offscreen")), "Software rendering is not physical GPU proof"
    return {"source": source, "campaign_stage_after_reset": state["campaignStage"],
            "flight_and_shooting": "passed", "webgl_renderer_active": state.get("webgl"),
            "gl_probe": gl, "browser_errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=None, help="real production or staging URL; if omitted, uses offline DOM injection")
    parser.add_argument("--headed", action="store_true", help="use a visible Chromium browser on the testing device")
    parser.add_argument("--require-webgl", action="store_true")
    parser.add_argument("--require-hardware", action="store_true", help="requires --url, real WebGL and disclosed non-software GPU")
    parser.add_argument("--chromium", default=None, help="optional Chromium executable path")
    args = parser.parse_args()
    if args.require_hardware and (not args.url or not args.headed):
        parser.error("--require-hardware requires --url and --headed on the intended physical device")
    outcomes = {}
    try:
        with sync_playwright() as play:
            kwargs = {"headless": not args.headed}
            if args.chromium:
                kwargs["executable_path"] = args.chromium
            browser = play.chromium.launch(**kwargs)
            for name, viewport in [("desktop_viewport", {"width": 1280, "height": 760}),
                                   ("mobile_viewport_emulated", {"width": 390, "height": 844})]:
                page = browser.new_page(viewport=viewport)
                try:
                    outcomes[name] = verify(page, args.url, args.require_webgl or args.require_hardware, args.require_hardware)
                finally:
                    page.close()
            browser.close()
        print(json.dumps({"status": "PASS", "note": "Mobile viewport is emulated, not a physical phone", "checks": outcomes}, indent=2))
    except Exception as error:
        print(json.dumps({"status": "FAIL", "reason": str(error), "completed_checks": outcomes}, indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())