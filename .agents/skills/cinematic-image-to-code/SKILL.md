---
name: cinematic-image-to-code
description: "Implement approved original cinematic imagery into the existing Juss & Co image, video and game pipeline; render, compare, correct and verify with source-linked receipts."
---

# Cinematic image-to-code: source → implementation → proof

Use for /image2code, /makeskill, visual-to-production, new graphic assets, screenshot parity or cinematic game/video upgrades. This skill routes into THIS repository's existing production modules; **never** spin up a replacement studio, video engine, game, or control room.

## Fixed contract

1. Observe **current main HEAD**, working branch exact head and merge-base; name source asset, owner, rights/approval, route and existing tests. Reject stale evidence.
2. **Generate/reference → inspect → implement → render → compare → correct → verify.** Build in the existing renderer. Preserve the actual gameplay, scene timing, source work and approved visual fingerprint.
3. Keep **reference art**, **local generated composite**, **motion video**, **live software screenshot**, and **hardware 3D evidence** separate; do not mislabel a poster/background as GPU-rendered gameplay or a video as a recorded product demo.
4. Produce SHA-256/provenance/continuity evidence where the current pipeline supports it. Byte matching proves matching bytes, **not** copyright permission, a trusted creator, live motion, GPU performance, or publishing authority.
5. Verify the focused tests first; for interactive surfaces, run real desktop + mobile Playwright, inspect uncaught JS/console errors, asset loading, readable controls and a gameplay/shot flow. If hardware WebGL is unavailable, mark it BLOCKED and identify fallback proof independently.
6. Never silently merge/deploy/publish, incur paid model charges, override approved graphics, invent current performance or create duplicate PRs. Existing approvals do not replace fresh exact-head release gates.

## Reality/provenance receipt

Return **REALITY / FIX / PROOF / RISK / ROLLBACK / NEXT GATE** with main SHA, branch SHA, changed paths, asset hashes, actual screenshots and unresolved release gates. Source image ≠ runtime evidence.

## This repository: GAME renderer

- Canonical existing game: `index.html`, seven-act Pittsburgh-inspired world, browser controls, Sky Mode, gameplay HUD, software fallback and WebGL path. Preserve missions, NPCs, joystick and approved artwork.
- Existing graphic export `scripts/export_graphics.py` matches the embedded approved skyline to `assets/pittsburgh-night-skyline.jpg`. Run it read-only first; `--write` intentionally updates only that derived file.
- Generated art may be a reference, title screen, skybox, cutscene or decal. Character mesh, textures, physics, camera, movement and combat must exist as game code/assets separately. Compare title **and active gameplay** to reference screenshots; never advertise the illustrated reference as live gameplay.
- Focused browser proof: `python tests/verify_browser.py`; in the existing graphics/joystick branch also `python tests/verify_joystick.py`. For real device proof, run the documented deployed-route/hardware gate. Source screenshots and emulator output alone cannot verify hardware WebGL or Meta glasses.
- Keep art export SHA, Playwright screenshots and exact-head CI separate. Do not alter main, Games Hub deployment or Cloudflare route without release approval.

## Two mutually aware graphics lanes (Steel City)

- Art lane: approved embedded JPEG and exported skyline, checked for byte identity. It declares the runtime revision expected.
- Playable lane: existing WebGL renderer, geometry and desktop/mobile Playwright screenshots. It declares the approved art asset expected.
- Both lanes use the same graphics/shot-contract.json shot ID, acknowledge their peer, and produce linked hashes/screenshots through scripts/verify_graphics_lanes.py. Run it after export and WebGL capture, and review proof/steel-city/graphics-comparison.html.
- Passing synchronization proves source bytes and recorded software-rendered gameplay; it does not prove pixel similarity to complete concept art. Human frame review, physical GPU and live-domain gates remain separate.
