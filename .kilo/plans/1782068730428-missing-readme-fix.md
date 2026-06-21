# Fix: Missing README.md causing `pip install -r requirements_vocal_fixed.txt` to fail

## Problem

`setup.py` reads `README.md` on line 5 (`open("README.md", ...)`) as the `long_description` for the package. However, **no `README.md` file exists** in the project root. This causes `pip install -e .` (triggered by `-e .` on line 96 of `requirements_vocal_fixed.txt`) to fail with `FileNotFoundError: [Errno 2] No such file or directory: 'README.md'`.

## Solution

Create a `README.md` file in the project root (`C:\Users\toufik.guettari\.gemini\antigravity-ide\scratch\vr_scenario_lib\README.md`) with appropriate project documentation content.

The existing markdown files (QUICKSTART.md, ARCHITECTURE_DOCUMENTATION.md, GUIDE_COMMANDES.md, QUICKSTART_WINDOWS.md, QUICKSTART_RGPC.md) can serve as reference for the content.

## Steps

1. Create `README.md` in the project root with:
   - Project title and description
   - Overview of what vr-scenario-lib does (VR training scenario generator for the gas sector)
   - Links/references to the other documentation files
   - Basic installation instructions
   - Requirements (Python >= 3.10)

2. Verify the fix by running `pip install -r requirements_vocal_fixed.txt` or at least `pip install -e .` successfully.

## Notes

- Only the file `README.md` needs to be created. No other files need modification.
- The content should be in French to match the project's existing language conventions (based on setup.py description being in French).
- Alternatively, if a README is not desired, `setup.py` could be modified to gracefully handle a missing README (e.g., use a fallback description), but creating the README is the cleaner fix.
