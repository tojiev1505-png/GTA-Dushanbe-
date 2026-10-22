# GTA V tooling research notes

## Purpose

This document tracks the tools and checks needed to build an original GTA V map project inspired by Dushanbe. A loaded viewer is only the first technical milestone; scene generation, export, game-edition compatibility, and in-game behavior still require separate verification.

## Current toolchain

### GTA V Map Agent + CodeWalker

- Upstream: https://github.com/cngil/gtav-mapagent
- Intended role: inspect the GTA V world, place existing GTA V props, validate placements, and export prop scenes.
- Local status on 2026-10-22: the Electron editor starts, the embedded CodeWalker world reaches the ready state, and the user confirms camera navigation works.
- AI status: blocked. On 2026-10-22, running `claude` produced `Unable to connect to Anthropic services` with a 10-second timeout for `api.anthropic.com`; the editor displays `Not logged in · Please run /login`. An earlier direct TCP test on port 443 also failed. The login command cannot succeed until the service is reachable and the location/account is eligible.
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
2. Do not keep retrying `/login` while `api.anthropic.com` times out.
3. If the user's current physical region is supported by Anthropic, test one other ordinary network and check firewall/proxy configuration. If it remains unreachable, collect `Test-NetConnection api.anthropic.com -Port 443` and `curl.exe -I --connect-timeout 10 https://api.anthropic.com` results.
4. If Anthropic is unavailable in the user's region, plan a code change to a supported model provider rather than trying to bypass the regional restriction. The current app uses Claude Agent SDK, so changing provider is an implementation task, not a settings toggle.
5. After an agent can respond, create a disposable project with a small prop arrangement, inspect it, and export JSON before trying a game-specific format.
6. Keep the result separate from the illustrative planning JSON until a documented coordinate mapping exists.

## Status

- CodeWalker world loading: verified locally on 2026-10-22.
- Camera navigation: verified by user on 2026-10-22.
- Claude Code login / AI placement: blocked by repeated API connection timeout; not tested successfully.
- Game export and in-game behavior: not tested.
- The planning prototype remains illustrative local-coordinate data, not a game-ready asset.
