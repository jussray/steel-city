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
    assert state["hillsideWalkMinZ"] == -83, (label, mode, state)

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

    approach = None
    if label == "desktop":
        # Exercise the REAL input path, starting from the normal spawn.
        # No teleport, mocked hero state or fake renderer success.
        def drive(key, js_condition, timeout):
            page.keyboard.down(key)
            try:
                page.wait_for_function(js_condition, timeout=timeout)
            except Exception as exc:
                raise AssertionError(
                    f"{mode} movement blocked on {key}: "
                    f"{page.evaluate('window.__steelCityDebug()')}") from exc
            finally:
                page.keyboard.up(key)

        page.keyboard.down("ShiftLeft")
        try:
            # Capture the existing real-input route at two distinct viewpoints.
            # These frames are WebGL/fallback captures, not the approved key art.
            drive("KeyW", "window.__steelCityDebug().z < -26", 90000)
            bridge_entrance = page.evaluate("window.__steelCityDebug()")
            assert -31.5 < bridge_entrance["z"] < -26, (mode, bridge_entrance)
            assert abs(bridge_entrance["x"]) < 1.5, (mode, bridge_entrance)
            entrance_image = PROOF / f"bridge-entrance-desktop-{mode}.png"
            page.screenshot(path=str(entrance_image))

            drive("KeyW", "window.__steelCityDebug().z < -45", 90000)
            bridge_midspan = page.evaluate("window.__steelCityDebug()")
            assert -51 < bridge_midspan["z"] < -45, (mode, bridge_midspan)
            assert abs(bridge_midspan["x"]) < 1.5, (mode, bridge_midspan)
            midspan_image = PROOF / f"bridge-midspan-desktop-{mode}.png"
            page.screenshot(path=str(midspan_image))

            drive("KeyW", "window.__steelCityDebug().z < -65", 90000)
            crossed = page.evaluate("window.__steelCityDebug()")
            assert "MOUNT WASHINGTON" in page.locator("#place").inner_text(), (
                mode, crossed)
            drive("KeyA", "window.__steelCityDebug().x < -29.8", 60000)
            # At x ~= -30, the house sits at z=-75.5. Its closest
            # collision face is about -73.25; continuing to press W
            # must NOT take the player through its foundation.
            page.keyboard.down("KeyW")
            try:
                page.wait_for_function(
                    "window.__steelCityDebug().z < -72.6", timeout=30000)
                before_block = page.evaluate("window.__steelCityDebug()")
                page.wait_for_timeout(1400)
                after_block = page.evaluate("window.__steelCityDebug()")
            finally:
                page.keyboard.up("KeyW")
            assert -73.6 < after_block["z"] < -72.4, (
                mode, "home collision missing", before_block, after_block)
            assert abs(after_block["z"] - before_block["z"]) < .6, (
                mode, "walked through home", before_block, after_block)
            assert -32 < after_block["x"] < -28, (
                mode, "wrong house route", after_block)
            approach_image = PROOF / f"hillside-approach-{mode}.png"
            page.screenshot(path=str(approach_image))
            approach = {
                "bridgeEntrance": {
                    "x": bridge_entrance["x"], "z": bridge_entrance["z"],
                    "screenshot": str(entrance_image.relative_to(ROOT)),
                    "input": "ShiftLeft + KeyW"
                },
                "bridgeMidspan": {
                    "x": bridge_midspan["x"], "z": bridge_midspan["z"],
                    "screenshot": str(midspan_image.relative_to(ROOT)),
                    "input": "ShiftLeft + KeyW"
                },
                "bridgeCrossedAtZ": crossed["z"],
                "collisionAt": {
                    "x": after_block["x"], "z": after_block["z"],
                    "y": after_block["y"]},
                "screenshot": str(approach_image.relative_to(ROOT)),
                "realKeyboardTraversal": True,
            }

            # From the real hillside approach, attempt to walk back into the
            # river outside the bridge. This used to traverse the water.
            assert not page.evaluate(
                "window.__steelHillsideContract.canTraverseGround(-30,-50)"
            ), "Off-bridge river incorrectly marked walkable"
            assert page.evaluate(
                "window.__steelHillsideContract.canTraverseGround(0,-50)"
            ), "Central bridge incorrectly blocked"

            page.keyboard.down("KeyS")
            try:
                page.wait_for_function(
                    "window.__steelCityDebug().z > -64.8", timeout=35000)
                # Allow the last legal 0.6-unit movement step to complete.
                # Then sample twice while S remains held to prove the bank blocks it.
                page.wait_for_timeout(1000)
                water_edge = page.evaluate("window.__steelCityDebug()")
                page.wait_for_timeout(700)
                water_block = page.evaluate("window.__steelCityDebug()")
            finally:
                page.keyboard.up("KeyS")
            assert -64.8 < water_block["z"] <= -64.0, (
                mode, "Walked into the river off-bridge", water_edge, water_block)
            assert abs(water_block["z"] - water_edge["z"]) < .6, (
                mode, "Character continued into water", water_edge, water_block)
            assert -32 < water_block["x"] < -28, (mode, water_block)
            river_image = PROOF / f"river-bank-ground-{mode}.png"
            page.screenshot(path=str(river_image))

            # Flying across open water is intentionally supported, but LAND
            # may only succeed on solid shore or the bridge, never mid-river.
            page.keyboard.press("f")
            assert page.evaluate("window.__steelCityDebug().skyMode") is True
            drive("KeyS", "window.__steelCityDebug().z > -59", 35000)
            airborne = page.evaluate("window.__steelCityDebug()")
            assert -64 < airborne["z"] < -36 and airborne["skyMode"], airborne
            page.keyboard.press("f")
            assert page.evaluate("window.__steelCityDebug().skyMode") is True, (
                mode, "Landed on open water")
            sky_image = PROOF / f"river-sky-landing-refused-{mode}.png"
            page.screenshot(path=str(sky_image))
            drive("KeyW", "window.__steelCityDebug().z < -64.8", 35000)
            page.keyboard.press("f")
            assert page.evaluate("window.__steelCityDebug().skyMode") is False, (
                mode, "Cannot land on the shore")

            approach["riverBoundary"] = {
                "blockedOffBridge": True,
                "groundStoppedAtZ": water_block["z"],
                "skyCrossingAllowed": True,
                "unsafeLandingRefused": True,
                "shoreLandingAllowed": True,
                "groundScreenshot": str(river_image.relative_to(ROOT)),
                "flightScreenshot": str(sky_image.relative_to(ROOT)),
                "input": "real keyboard from normal spawn",
            }
        finally:
            page.keyboard.up("ShiftLeft")

    assert not errors, (label, mode, errors)
    page.close()
    return {
        "viewport": label, "mode": mode, "webgl": not force_fallback,
        "count": state["hillsideHomeCount"], "solids": state["hillsideSolidCount"],
        "bridgeDetail": state["bridgeDetail"],
        "bridgeTrussSegments": state["bridgeTrussSegments"],
        "approach": approach, "footprints": homes, "minimapPixel": [201, 159, 107],
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
    if label == "desktop":
        assert pair[0]["approach"] and pair[1]["approach"], "Bridge approach evidence absent"
        for view in ("bridgeEntrance", "bridgeMidspan"):
            for renderer in pair:
                point = renderer["approach"][view]
                assert Path(ROOT / point["screenshot"]).is_file(), point
                assert point["input"] == "ShiftLeft + KeyW", point
        for renderer in pair:
            assert renderer["approach"]["bridgeEntrance"]["z"] > -31.5
            assert renderer["approach"]["bridgeMidspan"]["z"] < -45
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
    "groundRoute": "bridge crossing and elevated-home foundation collision",
    "realDeviceOrProduction": "not verified",
}, indent=2))
