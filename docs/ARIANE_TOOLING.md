# GTA V tooling research notes

## Purpose

This document tracks the tools and checks needed to build an original GTA V map project inspired by Dushanbe. A loaded viewer is only the first technical milestone; scene generation, export, game-edition compatibility, and in-game behavior still require separate verification.

## Current toolchain

### GTA V Map Agent + CodeWalker

- Upstream: https://github.com/cngil/gtav-mapagent
- Intended role: inspect the GTA V world, place existing GTA V props, validate placements, and export prop scenes.
- Local status on 2026-10-22: the Electron editor starts, the embedded CodeWalker world reaches the ready state, and the user confirms camera navigation works.
- AI status with Anthropic cloud: blocked. On 2026-10-22, running `claude` produced a 10-second timeout connecting to `api.anthropic.com`; the user says they are in Russia. Repeating login is not the solution. A local Ollama model with its Anthropic-compatible Messages API is the proposed experiment; it does not depend on Anthropic cloud access, but app compatibility is not yet verified.
- Recovery check: if the user is physically in a region officially supported by Anthropic, test another ordinary network (for example, a phone hotspot) and check local firewall/proxy settings. If the user is in an unsupported region, do not attempt to bypass regional availability rules; use a model/provider available to them and port the app's agent integration instead.
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
- Confirm the AI can place a small number of existing props, if using the agent workflow.
- Export a tiny test scene and inspect the exported files.
- Test it in the intended game edition/platform; record the result, steps, and any limitations.
- Keep proprietary game files and extracted content out of this repository.

## Current first experiment

1. The CodeWalker world and camera controls have been verified.
2. Use the local Ollama compatibility experiment before making code changes. Install Ollama for Windows from https://ollama.com/download/windows and pull `qwen3:4b` (`ollama pull qwen3:4b`).
3. In the same PowerShell session, set `$env:ANTHROPIC_BASE_URL = "http://localhost:11434"`, `$env:ANTHROPIC_AUTH_TOKEN = "ollama"`, `$env:ANTHROPIC_API_KEY = ""`, and `$env:MAP_EDITOR_MODEL = "qwen3:4b"`. Test with `claude --model qwen3:4b` and a simple prompt. These are proposed settings, not a confirmed working configuration for this app.
4. If the simple CLI test succeeds, close any running Map Agent window and start `npm start` from the same PowerShell session so the app inherits those environment variables. If the app still fails, capture the exact error: Claude Agent SDK may use features the local compatibility endpoint does not fully implement. Do not publish API keys or tokens.
5. After an agent can respond, create a disposable project with a small prop arrangement, inspect it, and export JSON before trying a game-specific format.
6. Keep the result separate from the illustrative planning JSON until a documented coordinate mapping exists.

## Status

- CodeWalker world loading: verified locally on 2026-10-22.
- Camera navigation: verified by user on 2026-10-22.
- Claude Code login / Anthropic cloud: blocked by repeated API connection timeout. Local Ollama model route: proposed, not yet tested.
- Game export and in-game behavior: not tested.
- The planning prototype remains illustrative local-coordinate data, not a game-ready asset.
