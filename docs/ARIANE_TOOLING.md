# GTA V tooling research notes

## Purpose

This document tracks the tools and checks needed to build an original GTA V map project inspired by Dushanbe. A loaded viewer is only the first technical milestone; scene generation, export, game-edition compatibility, and in-game behavior still require separate verification.

## Current toolchain

### GTA V Map Agent + CodeWalker

- Upstream: https://github.com/cngil/gtav-mapagent
- Intended role: inspect the GTA V world, place existing GTA V props, validate placements, and export prop scenes.
- Local status on 2026-10-22: the Electron editor starts and the embedded CodeWalker world reaches the ready state.
- AI status: not verified. Claude Code could not reach Anthropic services from the current environment, so agent-driven prop placement is blocked until that connection/authentication issue is resolved or a supported alternative backend is implemented.
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
- Confirm the 3D camera and scene panel work.
- Confirm the AI can place a small number of existing props, if using the agent workflow.
- Export a tiny test scene and inspect the exported files.
- Test it in the intended game edition/platform; record the result, steps, and any limitations.
- Keep proprietary game files and extracted content out of this repository.

## Current first experiment

1. Check camera navigation in the loaded 3D view.
2. Resolve or replace the unavailable Claude agent connection before asking Map Agent to build a scene.
3. Create a disposable project with a very small prop arrangement near a known camera position.
4. Export a JSON copy for inspection; only then try the intended game format.
5. Keep the result separate from the illustrative planning JSON until a documented coordinate mapping exists.

## Status

- CodeWalker 3D world loading: verified locally on 2026-10-22, based on the user's run log and confirmation.
- Camera navigation: not yet reported.
- AI placement: blocked/not tested because the Claude Code connection to Anthropic timed out.
- Game export and in-game behavior: not tested.
- The planning prototype remains illustrative local-coordinate data, not a game-ready asset.
