# Steel City agent instructions

This repository is the existing Pittsburgh-inspired browser game, not a new graphics engine.

On approved visual art, image-to-game-code, cinematics, asset export, or screenshot-parity work, **read .agents/skills/cinematic-image-to-code/SKILL.md**. Implement the art in the actual renderer, capture gameplay, compare with reference, correct differences and verify via Playwright. Do not label key art as live 3D gameplay or a fallback as GPU proof.

Read live main HEAD, target branch HEAD and merge-base before changing anything. Preserve the seven-act game, missions, controls, joystick, audio, Sky Mode, approved imagery and Games Hub handoff. Make one reversible change; no new PR, merge, deployment, paid provider or public claims without fresh release proof.

Focused checks: `python scripts/export_graphics.py`, `python tests/verify_browser.py`, and `python tests/verify_joystick.py` on the graphics branch. Device WebGL and Meta-glasses compatibility need separate physical tests.

Report REALITY / FIX / PROOF / RISK / ROLLBACK / NEXT GATE with exact SHAs, files and screenshots.

## Portfolio cinematic composition standard (staged)

Preserve the approved Pittsburgh skyline, game world, seven-act structure, gameplay controls, art assets, and existing cinematic-image-to-code proof gate. One cohesive cinematic composition means in-renderer visual continuity, not key-art-only screenshots or invented performance claims.

Preserve product-specific approved original design references and local instructions; Figma mockups are scaffolding. Require exact-head desktop/mobile visual screenshots, interaction and keyboard, reduced-motion and performance checks before a PASS. Keep runtime adoption, source changes, merges, deployment, publication, and spending as independent evidence and approval gates. No changes to auth, payment, data, agent authority, privacy or working game controls without separate scope. Draft reference: `jussray/founder-control-room/skills/cinematic-composition/SKILL.md` on `feat/cinematic-composition-contract-20261104`.
