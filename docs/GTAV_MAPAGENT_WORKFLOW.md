# First GTA V Map Agent experiment

This guide is for a small throwaway prop-placement scene. It does not create a full Dushanbe city map.

## 1. Confirm the local viewer

1. Start the editor from `gtav-mapagent/editor` with `npm start`.
2. Confirm that the embedded 3D world is visible.
3. Click inside the 3D viewport, then test WASD and mouse movement. Use the mouse wheel to adjust movement speed.
4. Record the GTA V game folder used by CodeWalker and whether it is Legacy or Enhanced. Do not assume an export is compatible with both editions.

## 2. Wait until the scene agent is available

The current local run confirmed viewer startup, but AI placement has not yet been verified because Claude Code could not reach Anthropic services. Until the chat agent can authenticate and respond, do not treat a typed prompt as a successful scene build.

Do not share Claude credentials, session tokens, or API keys in this repository.

## 3. Make a disposable test scene

After the agent is working:

1. Create a new project in the Projects panel so the experiment is separate from future city work.
2. Move the camera to a simple, open location in the existing world.
3. Ask for a compact prop arrangement within roughly 10–15 metres of the camera, using existing GTA V assets only. For example: a small plaza with benches, planters, and streetlights.
4. Inspect the placement from several angles. Undo the request if the scene is wrong; keep the test small.
5. Export a JSON copy first and inspect its prop names, positions, and rotations. Then export the format intended for the eventual target platform.

## 4. Verify export and keep sources separate

- Record the export format, game edition, tool versions, and test result.
- Only test an exported map in the relevant game edition and intended platform.
- Do not copy GTA V game files, extracted Rockstar assets, credentials, or third-party assets without redistribution permission into the Dushanbe-GTA repository.
- Do not paste the illustrative coordinates from `map-data/blocks/center_prototype.json` directly into GTA V placement coordinates. The project has not established a transform between those coordinate systems.

## 5. Understand the limits

GTA V Map Agent places existing GTA V props. It does not create new terrain, custom buildings, new interiors, or a complete replacement road network. Those parts of a Dushanbe recreation require a separate original 3D-asset pipeline and their own export and in-game tests.
