# Steel City agent instructions

This repository is the existing Pittsburgh-inspired browser game, not a new graphics engine.

On approved visual art, image-to-game-code, cinematics, asset export, or screenshot-parity work, **read .agents/skills/cinematic-image-to-code/SKILL.md**. Implement the art in the actual renderer, capture gameplay, compare with reference, correct differences and verify via Playwright. Do not label key art as live 3D gameplay or a fallback as GPU proof.

Read live main HEAD, target branch HEAD and merge-base before changing anything. Preserve the seven-act game, missions, controls, joystick, audio, Sky Mode, approved imagery and Games Hub handoff. Make one reversible change; no new PR, merge, deployment, paid provider or public claims without fresh release proof.

Focused checks: `python scripts/export_graphics.py`, `python tests/verify_browser.py`, and `python tests/verify_joystick.py` on the graphics branch. Device WebGL and Meta-glasses compatibility need separate physical tests.

Report REALITY / FIX / PROOF / RISK / ROLLBACK / NEXT GATE with exact SHAs, files and screenshots.