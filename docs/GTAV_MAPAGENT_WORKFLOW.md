# First GTA V Map Agent experiment

This guide is for a small throwaway prop-placement scene. It does not create a full Dushanbe city map.

## 1. Confirm the local viewer

1. Start the editor from `gtav-mapagent/editor` with `npm start`.
2. Confirm that the embedded 3D world is visible.
3. Click inside the 3D viewport and test WASD and mouse movement. Use the mouse wheel to adjust movement speed. This step has been confirmed by the user on 2026-10-22.
4. Record the GTA V game folder used by CodeWalker and whether it is Legacy or Enhanced. Do not assume an export is compatible with both editions.

## 2. Test whether the scene agent can respond

The editor and camera are working, but the chat agent has not yet been verified because Claude Code previously could not reach Anthropic services. Try one small request in the editor. If it succeeds, continue below. If it reports a sign-in or connectivity error, stop and send the exact error text; do not keep retrying or reinstalling the working viewer.

Suggested first prompt:

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
