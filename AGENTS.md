# Working on ios-topaz / gta4l

- Read `NOTES-gta4l.md` before starting: hardware facts, addresses, what has been
  tried, artifacts and next action. Update it after each milestone and before stopping.
- Record commits, CI run IDs, exact build/flash results, and distinguish observations
  from guesses.
- Kernel builds run on GitHub Actions (`gh workflow run xnu.yml --ref topaz`).
  `tools/build_gta4l.sh` builds the boot image locally (Linux, Python 3 +
  `aarch64-linux-gnu-gcc` for the shim).
- Flashing is **heimdall**, download mode (Vol+ and Vol−, then USB). Only the `BOOT`
  partition is written; never flash `xbl`, `abl`, `tz`, `hyp`, or `modem`.
- Do not fix a failing patch by editing patch files: the set is a dependent chain
  (`0060` → `0080` → display/touch). Editing hunk context silently skips later
  patches and produces a kernel that panics on CPU topology.
- Keep device dumps, serial numbers and Apple artifacts out of git.
