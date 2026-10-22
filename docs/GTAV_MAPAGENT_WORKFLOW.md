# First GTA V Map Agent experiment

This guide is for a small throwaway prop-placement scene. It does not create a full Dushanbe city map.

## 1. Confirm the local viewer

1. Start the editor from `gtav-mapagent/editor` with `npm start`.
2. Confirm that the embedded 3D world is visible.
3. Click inside the 3D viewport and test WASD and mouse movement. Use the mouse wheel to adjust movement speed. This step was confirmed by the user on 2026-10-22.
4. Record the GTA V game folder used by CodeWalker and whether it is Legacy or Enhanced. Do not assume an export is compatible with both editions.

## 2. Test a local model through Ollama

The editor and camera work, but Claude Code cannot reach `api.anthropic.com` from the user's current region. Do not keep retrying `/login`. A proposed alternative is Ollama's local Anthropic-compatible API. It routes model inference to the user's own computer rather than Anthropic cloud. This approach is documented by Ollama, but has not yet been tested end-to-end in this Map Agent build.

1. Install Ollama for Windows from https://ollama.com/download/windows.
2. Open PowerShell and run `ollama --version`, then `ollama pull qwen3:4b`. Ollama lists Qwen3 model variants with tool-calling support; the 4B package is approximately 2.5 GB and is a sensible initial test for a PC with a 6 GB GPU, though actual speed and memory use vary.
3. In the same PowerShell window, configure this local API and model:

   ```powershell
   $env:ANTHROPIC_BASE_URL = "http://localhost:11434"
   $env:ANTHROPIC_AUTH_TOKEN = "ollama"
   $env:ANTHROPIC_API_KEY = ""
   $env:MAP_EDITOR_MODEL = "qwen3:4b"
   ```

4. First test the bridge with `claude --model qwen3:4b`. Ask it to reply exactly `OK`. This is intended to confirm the local Messages API is answering without an Anthropic login.
5. If the CLI test succeeds, exit it, close any existing Map Agent instance, and run `npm start` from the same PowerShell session. The editor inherits these environment variables and uses `MAP_EDITOR_MODEL` for the builder and (unless manually overridden) the critic.
6. Try one small prop placement. If the editor reports an unsupported endpoint or another SDK error, capture the exact message; the compatibility API may not support every advanced Claude Agent SDK operation. Do not continue to assume the agent works until this succeeds.

Once the agent works, use this first test prompt:

> At the current camera position, build a small Dushanbe-inspired public square using only existing GTA V props: place two benches facing each other, four streetlights around them, and three planters. Keep everything on the ground, avoid blocking roads or buildings, and inspect the placement from multiple angles. Do not create custom models.

This is a small test of placement and validation, not a real reconstruction of Dushanbe architecture.

Do not share Claude credentials, session tokens, or API keys in the repository.

## 3. Inspect and export the test scene

1. Review each placed item from several angles. Undo the request if the arrangement is wrong.
2. Export a JSON copy first and inspect its prop names, positions, and rotations.
3. Only then export the format intended for the eventual target platform.

## 4. Verify export and keep sources separate

- Record the export format, game edition, tool versions, and test result.
- Only test an exported map in the relevant game edition and intended platform.
- Do not copy GTA V game files, extracted Rockstar assets, credentials, or third-party assets without redistribution permission into the Dushanbe-GTA repository.
- Do not paste the illustrative coordinates from `map-data/blocks/center_prototype.json` directly into GTA V placement coordinates. The project has not established a transform between those coordinate systems.

## 5. Understand the limits

GTA V Map Agent places existing GTA V props. It does not create new terrain, custom buildings, new interiors, or a complete replacement road network. Those parts of a Dushanbe recreation require a separate original 3D-asset pipeline and their own export and in-game tests.
