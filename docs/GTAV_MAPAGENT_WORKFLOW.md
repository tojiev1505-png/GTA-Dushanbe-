# GTA V Map Agent: optional prop dressing

GTA V Map Agent is now a supporting tool for the Dushanbe map project, not the main tool for creating city geometry.

## Verified local setup

- Editor launches and the embedded CodeWalker world loads.
- The 3D camera is working.
- The user confirmed one existing GTA V streetlight was placed successfully with the local Ollama `qwen3:4b` configuration.

Launch from a PowerShell session configured for the local model:

```powershell
$env:ANTHROPIC_BASE_URL = "http://localhost:11434"
$env:ANTHROPIC_AUTH_TOKEN = "ollama"
$env:ANTHROPIC_API_KEY = ""
$env:MAP_EDITOR_MODEL = "qwen3:4b"
cd "$HOME\gtav-mapagent\editor"
npm start
```

## What to use it for

- Add existing game props after roads and building layout are defined.
- Place street furniture, planters, barriers, signs, and other placeable objects.
- Check ground contact and collisions for placements.
- Export a small prop arrangement for inspection.

## What not to expect from it

It does not generate custom city terrain, a complete street network, bespoke building facades or unique monuments. It also does not turn static car objects into fully functioning traffic. Use Blender + a verified GTA V asset pipeline for original geometry and separate game systems for live traffic behavior.

## Local agent prompt guidance

Qwen may print proposed tool calls instead of executing them. When that happens, ask for one concise action at a time and explicitly require the real tool to be called, then verify the resulting prop IDs/scene panel. Avoid making a long city scene depend on unverified calls.

## Project safety

- Work in a disposable project or separate project before mass placement.
- Do not export or install the result until target edition/platform is decided.
- Keep game files and exported proprietary assets out of the source repository unless redistribution is explicitly allowed.
