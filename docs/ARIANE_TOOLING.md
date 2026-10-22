# GTA V tooling research notes

## Purpose

This document tracks the tools and checks needed to build an original GTA V map project inspired by Dushanbe. A loaded viewer and one placed object are early milestones; complex scenes, exports, game-edition compatibility, and in-game behavior still require separate verification.

## Current toolchain

### GTA V Map Agent + CodeWalker

- Upstream: https://github.com/cngil/gtav-mapagent
- Intended role: inspect the GTA V world, place existing GTA V props, validate placements, and export prop scenes.
- Local status on 2026-10-22: the Electron editor starts, the embedded CodeWalker world reaches the ready state, and the user confirms camera navigation works.
- AI status: the user confirmed that after configuring Ollama's local Anthropic-compatible API and selecting `qwen3:4b`, Map Agent successfully placed one existing streetlight prop. This verifies the basic path from the local model to a map tool call.
- Anthropic cloud: Claude Code timed out connecting to `api.anthropic.com`; the user's current location is Russia. Do not keep retrying cloud login as the path to local inference.
- Still unverified: larger multi-object scene construction, tool-call reliability across a longer request, the independent critic/review loop, and map export/game testing.
- Important limitation: this tool does not author new terrain, custom building models, interiors, or a full road network. It is suitable for a prop-scene prototype, not by itself for replacing a real city or producing all of Dushanbe from scratch.
- Outputs described upstream include JSON and YMAP, plus platform-specific exports such as Menyoo and FiveM. Test the selected output in the intended edition/platform before relying on it.

### Additional authoring work that may be needed

1. **Original 3D geometry:** Blender or another 3D editor for project-authored buildings, road pieces, terrain, and unique landmarks.
2. **GTA V asset pipeline:** select and verify a maintained exporter/importer that supports the target game edition and required formats. Do not assume a tool built for Legacy supports Enhanced, or the reverse.
3. **Texture authoring:** an image editor whose exported formats are supported by the selected pipeline.
4. **Data and validation:** Python 3.10+ and the standard library for repeatable checks of project JSON.
5. **Source control/CI:** Git and GitHub Actions for text assets, scripts, documentation, and license-safe original sources.

## Verification checklist

Before a map slice is called complete:

- Record the GTA V edition (Legacy or Enhanced), installation used by CodeWalker, and intended export format.
- Record tool versions, upstream URLs, licenses, and retrieval/test dates.
- Confirm the 3D camera and scene/project controls work.
- Confirm the AI can place a small number of existing props.
- Inspect every placement from multiple angles and review any validation report.
- Export a tiny test scene and inspect the exported files.
- Test it in the intended game edition/platform; record the result, steps, and any limitations.
- Keep proprietary game files and extracted content out of this repository.

## Current next experiment

1. Keep the existing test streetlight; do not rebuild it.
2. In a disposable project, ask the local agent for a small square with two facing benches, four streetlights in total, and three planters. Specify the placement/checking process in the prompt, and ask the agent not to create custom models.
3. Inspect the result from several angles and correct any collision/floating issues reported by validation.
4. Save the project and export JSON first so the placements can be reviewed.
5. Only test a game-specific format after deciding whether the target is Legacy or Enhanced and whether the intended usage is single-player or multiplayer.
6. Keep the result separate from the illustrative planning JSON until a documented coordinate mapping exists.

## Status

- CodeWalker world loading: verified locally on 2026-10-22.
- Camera navigation: verified by user on 2026-10-22.
- Local model and first prop placement: confirmed by user on 2026-10-22 with Ollama `qwen3:4b`.
- Longer scene generation and critic/review: not yet verified.
- Game export and in-game behavior: not tested.
- The planning prototype remains illustrative local-coordinate data, not a game-ready asset.
