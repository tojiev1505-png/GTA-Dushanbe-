# First GTA V Map Agent experiment

This guide is for an incremental prop-placement prototype. It does not create a full Dushanbe city map.

## 1. Verified local setup

- The editor launches and the embedded CodeWalker world loads.
- The 3D camera is working.
- On 2026-10-22, the user confirmed that GTA V Map Agent, configured with Ollama's local API and `qwen3:4b`, successfully placed one existing GTA V streetlight.

The local-model environment used in the PowerShell session that launched the app:

```powershell
$env:ANTHROPIC_BASE_URL = "http://localhost:11434"
$env:ANTHROPIC_AUTH_TOKEN = "ollama"
$env:ANTHROPIC_API_KEY = ""
$env:MAP_EDITOR_MODEL = "qwen3:4b"
cd "$HOME\gtav-mapagent\editor"
npm start
```

For this local inference workflow, do not run `/login` as a fix for the Anthropic cloud timeout.

## 2. Next step: build the small square

Open the same project in the editor and send the request below. It intentionally says four streetlights total so the existing test lamp can be kept, rather than duplicated blindly.

> Build a small Dushanbe-inspired public square around the existing test streetlight. Keep that streetlight and place only the additional objects needed to reach four streetlights total. Add two benches facing each other and three planters around a simple central pedestrian space. Use only existing GTA V props returned by search_props, place the props in a folder named "Dushanbe Test Square", keep them on the ground, and avoid blocking roads or building entrances. Before placing an object, search for its exact model name. After placement, check every prop for collisions and ground contact; fix any problems and inspect the result from top view and at least two sides. Do not create custom models and do not export the map yet. Report the prop IDs and any validation issues.

If the agent starts asking what scene to build instead of acting, ask it to complete this explicit checklist using the map tools. Keep the existing test lamp unless it is in an unsafe position.

## 3. Inspect the result

- Verify the two benches visibly face each other.
- Count four streetlights total, including the existing one.
- Count three planters.
- Review the returned validation reports and any tool errors.
- Inspect the arrangement from multiple angles.
- Undo the last request if it causes a bad or oversized scene.

## 4. Export and game testing

After the prop arrangement looks right, save the project and export a JSON copy for review. Then decide whether the target is GTA V Legacy or Enhanced and whether the intended use is single-player or multiplayer. Export to the relevant format only after that decision, then test it in the selected game edition/platform.

Do not copy GTA V game files, extracted Rockstar assets, credentials, or third-party assets without redistribution permission into the Dushanbe-GTA repository. The illustrative coordinates from `map-data/blocks/center_prototype.json` are fictional local coordinates; they are not GTA V placement coordinates and cannot be pasted into the editor without a documented transform.

## 5. Understand the limits

GTA V Map Agent places existing GTA V props. It does not create new terrain, custom buildings, new interiors, or a complete replacement road network. Those parts of a Dushanbe recreation require a separate original 3D-asset pipeline and their own export and in-game tests.
