#!/usr/bin/env python3
"""Cross-check two Steel City graphics lanes against one shot ID.

Run AFTER the existing art export and Playwright WebGL gates.
A PASS does not establish visual image parity, physical GPU or deployment.
"""
import hashlib
import json
import struct
from html import escape
from pathlib import Path
from export_graphics import source_bytes

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "proof" / "steel-city"

def require(ok, why):
    if not ok:
        raise SystemExit("BLOCKED: " + why)

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def main():
    doc = json.loads((ROOT / "graphics/shot-contract.json").read_text(encoding="utf-8"))
    art, runtime = doc["lanes"]["art"], doc["lanes"]["runtime"]
    shot_id = doc["shot_id"]
    require(doc["schema"] == "steel-city.graphics-lanes.v1" and bool(shot_id), "unknown graphics contract")
    require(art["id"] == "art" and runtime["id"] == "runtime", "lane identities diverged")
    require(art["peer_lane"] == runtime["id"] and runtime["peer_lane"] == art["id"],
            "graphics lanes do not acknowledge each other")
    require(art["requires_runtime_graphics_revision"] == runtime["graphics_revision"],
            "art lane targets a different rendering revision")
    require(runtime["requires_art_asset"] == art["asset"], "renderer targets a different art asset")
    require(art["asset"] == "assets/pittsburgh-night-skyline.jpg", "unexpected art path")
    approved = source_bytes()
    asset_path = ROOT / art["asset"]
    require(asset_path.is_file() and asset_path.read_bytes() == approved,
            "exported and embedded approved art differ")
    art_sha = sha256(approved)

    game = (ROOT / "index.html").read_text(encoding="utf-8")
    require("graphicsRevision:'" + runtime["graphics_revision"] + "'" in game, "renderer revision drift")
    require("neighborhoodDetail:'" + runtime["neighborhood_detail"] + "'" in game, "scene detail drift")
    receipt_path = ROOT / runtime["receipt"]
    require(receipt_path.is_file(), "WebGL Playwright receipt absent")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(receipt.get("status") == "PASS", "WebGL verification did not pass")
    require(receipt.get("rendering") == "software swiftshader only", "unexpected renderer classification")
    require(receipt.get("physicalGpuVerified") is False and receipt.get("productionVerified") is False,
            "software proof mislabeled physical/production")
    checks = {item["viewport"]: item for item in receipt.get("checks", [])}
    images = {}
    for label, relative in runtime["screenshots"].items():
        check = checks.get(label)
        require(check is not None, "missing gameplay viewport: " + label)
        require(check.get("webgl") is True and check.get("graphicsRevision") == runtime["graphics_revision"],
                "gameplay renderer version drift: " + label)
        require(check.get("GL", {}).get("context") is True and not check.get("browserErrors"),
                "gameplay WebGL or JavaScript error: " + label)
        path = ROOT / relative
        require(path.is_file(), "gameplay screenshot missing: " + relative)
        data = path.read_bytes()
        require(len(data) > 4096 and data[:8] == b"\x89PNG\r\n\x1a\n", "invalid screenshot PNG: " + relative)
        width, height = struct.unpack(">II", data[16:24])
        require(width >= 350 and height >= 600, "undersized gameplay screenshot: " + relative)
        images[label] = {"path": relative, "sha256": sha256(data), "width": width, "height": height}

    proof = {
        "status": "PASS_LANE_SYNC_ONLY", "shotId": shot_id, "goal": doc["goal"],
        "art": {"id": "art", "peerLane": "runtime", "shotId": shot_id,
                "asset": art["asset"], "assetSha256": art_sha,
                "exactlyMatchesEmbeddedArt": True,
                "expectedRuntimeRevision": runtime["graphics_revision"]},
        "runtime": {"id": "runtime", "peerLane": "art", "shotId": shot_id,
                    "graphicsRevision": runtime["graphics_revision"],
                    "expectedArtSha256": art_sha,
                    "softwareWebglScreenshots": images, "softwareWebglVerified": True},
        "releaseGates": {"visualSimilarityToApprovedFullFrame": "UNKNOWN",
                         "physicalGPU": "UNKNOWN", "productionRoute": "UNKNOWN"}
    }
    PROOF.mkdir(parents=True, exist_ok=True)
    (PROOF / "approved-reference.jpg").write_bytes(approved)
    (PROOF / "graphics-lanes-receipt.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    cards = [("Art lane · approved 2D skyline", "approved-reference.jpg"),
             ("Runtime lane · desktop software WebGL", Path(images["desktop"]["path"]).name),
             ("Runtime lane · mobile-emulated software WebGL", Path(images["mobile_emulated"]["path"]).name)]
    figures = "\n".join('<figure><img src="' + escape(path, quote=True) + '" alt="' +
                        escape(label, quote=True) + '"><figcaption>' + escape(label) +
                        '</figcaption></figure>' for label, path in cards)
    gallery = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" '
               'content="width=device-width,initial-scale=1"><title>Steel City graphics lane comparison</title>'
               '<style>body{font-family:system-ui;background:#0b1220;color:#f4f5fb;margin:2rem}'
               '.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}'
               'figure{margin:0}img{width:100%;border:1px solid #69748d;border-radius:10px}'
               'figcaption{padding:.6rem}p{max-width:65ch}</style>'
               '<h1>Steel City · two lanes, one shot</h1><p>Shot: ' + escape(shot_id) +
               '. The image is approved 2D key art. Gameplay images are software-WebGL captures.'
               ' Visual similarity, physical GPU and production remain unverified.</p>'
               '<div class="grid">' + figures + '</div></html>')
    (PROOF / "graphics-comparison.html").write_text(gallery, encoding="utf-8")
    print(json.dumps({"status": proof["status"], "shotId": shot_id,
                      "artSha256": art_sha, "softwareScreenshots": images,
                      "gallery": "proof/steel-city/graphics-comparison.html",
                      "visualParity": "UNKNOWN"}, indent=2))

if __name__ == "__main__":
    main()
