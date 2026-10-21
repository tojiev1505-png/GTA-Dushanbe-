# Tooling research notes

## Purpose

This document records a cautious workflow for selecting tools for an original GTA: San Andreas map modification. The exact toolchain is **not selected yet**. Do not infer compatibility from the name of a tool alone.

## Candidate roles to research

1. **3D authoring:** Blender or another editor capable of producing original models and geometry.
2. **Game-format inspection/export:** a maintained GTA: San Andreas modding tool that explicitly supports the intended PC game edition and the file formats in use.
3. **Texture authoring:** an image editor that exports formats supported by the verified pipeline.
4. **Data and validation:** Python 3.10+ and the standard library for repeatable checks of project JSON.
5. **Source control/CI:** Git and GitHub Actions for text assets, scripts, documentation, and license-safe original sources.

## Verification checklist before choosing a game-specific tool

- Locate official documentation or a maintained upstream repository.
- Verify supported game edition, architecture, input/output formats, and known limitations.
- Read the tool's license and any bundled dependency licenses.
- Confirm the tool does not require redistribution of Rockstar binaries or extracted content.
- Prefer reproducible steps and small tests; scan downloads with the user's normal security tools.
- Record exact tool version, source URL, retrieval date, and test result after hands-on verification.

## Suggested first experiment

1. Create a tiny original road segment and one simple box building in a 3D editor.
2. Confirm scale units and transforms.
3. Export only after the game-specific format and tool are verified.
4. Inspect the exported result with the selected tool.
5. Do not describe the result as game-tested until it has been tested in the intended game environment.

## Status

- No game-specific exporter has been approved by this document.
- No game installation is assumed or required for the current data prototype.
- The current prototype is planning data only, not a game-ready asset.
- All candidate tool choices remain subject to current upstream documentation and license review.
