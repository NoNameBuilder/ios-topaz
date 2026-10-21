# gta4l: flash / recovery runbook

Samsung Galaxy Tab A7 10.4 2020 (`gta4l`, SM-T500 / SM-T505, SM6115).
Bootloader is unlocked; there is no fastboot. Use **heimdall** in download mode.

## Download mode

Power off. Hold **Vol+ and Vol−** together, then plug USB. Heimdall prints
`Failed to detect compatible download-mode device` if the combo was missed.

## Flash the XNU image

```sh
heimdall flash --BOOT ~/gta4l/ios-topaz/out/xnu-gta4l.img
```

Only `BOOT` is written. `userdata`, `bootloader`, `tz`, `hyp`, `modem` are untouched,
so the tablet always comes back by flashing a working `BOOT`.

## Recover

Any of these can be written to `BOOT`:

| What | Path |
| --- | --- |
| Mu-Silicium UEFI (known working) | `~/gta4l/uefi-build/gta4l-silicium-acpi-v8-dt.img` |
| Stock boot (firmware dump) | `~/restkfwgta4l/partitions/boot/live-device/boot.img` |
| iOS shim (if a working build exists) | `~/gta4l/ios-topaz/out/xnu-gta4l.img` |

```sh
heimdall flash --BOOT <image>
```

If the tablet shows the "download mode" screen instead of booting, it means ABL rejected
the image (usually a DTB without `qcom,msm-id`/`qcom,board-id`, or wrong page size).
Re-flash a known-good image; no EDL or Odin is needed.

## Build checks before flashing

```sh
python3 tools/mkboot_gta4l.py --help
```

`mkboot_gta4l.py` refuses DTBs without `qcom,msm-id`/`qcom,board-id` and always packs
page 4096, header v2, `kernel @0x8000`, `ramdisk @0x20000000`, `tags @0x1e00000`,
`dtb @0x1f00000`.

## Notes

- `heimdall` may need a replug after a failed detect; the device re-enumerates as
  `05c6:9008` only while the download-mode screen is up.
- Do not flash `xbl`, `tz`, `hyp`, or `abl`: they are OEM-signed and PBL checks them.
- No Mac is needed for the boot image; only the kernel build needs macOS/CI.
