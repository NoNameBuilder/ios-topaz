# ios-topaz / gta4l

Apple's open-source XNU (xnu-8796, iOS 16 era) running on the Samsung Galaxy Tab A7
10.4 (2020) — `gta4l`, SM-T500 / SM-T505, Qualcomm **SM6115 "Bengal"** (Snapdragon 662).

This is a fork of [MakrSas/ios-topaz](https://github.com/MakrSas/ios-topaz) — itself a port of
[dipa-studio/ios-sweet](https://github.com/dipa-studio/ios-sweet) — retargeted from the Redmi
Note 12 4G (`topaz`, SM6225) to `gta4l`.

> Experimental bring-up. It boots the XNU kernel and draws its console, then panics because
> there is no root device yet. Nothing is installed on internal storage.

## State (2026-10-21)

| Area | State |
| --- | --- |
| Boot | Unlocked Samsung ABL → `heimdall flash --BOOT` of a header-v2 image → shim → XNU |
| Console | Works: shim bars (blue/yellow/green), then the XNU kernel log on the 1200×2000 panel |
| CPU | Four Gold Cortex-A73 (MPIDR `0x100`–`0x103`), 16K pages, GICv3, generic timer. Silver A53 parked (no 16K granule) |
| Memory | `0x8A000000` upward, above TzApps and `rmtfs-mem`; 3 GB model: `0x76000000` bytes, 4 GB: `0xB6000000` |
| Storage | **None.** eMMC 5.1 (`0x04744000`); the UFS driver (`0x04804000`) is not usable and its ADT node is omitted |
| Root | Needs `rd=md0` + an HFS+ ramdisk; the current build has no ramdisk image, so XNU panics at root mount |
| Touch / keys | Not ported (topaz uses FocalTech FT5452 on QUP0 SE2; gta4l uses SPI touch) |
| Display backend | Kernel console only; the topaz SweetSurface/AppleCLCD constants are still 1080×2400 |
| Modem / Wi-Fi | Not ported, patches disabled (no `modem_a` on SM-T500) |

Last verified boot: kernel log through `SWEET AMFI`, panic `SWEET CPU: invalid topology`
(then fixed by keeping the pristine patch chain — rebuild pending).

## How it differs from topaz

| | topaz (SM6225) | gta4l (SM6115) |
| --- | --- | --- |
| SoC | khaje | bengal |
| RAM window | `0x140000000` | `0x8A000000` (3 GB) / up to `0x140000000` (4 GB) |
| Display | 1080×2400, stride 4320, FB `0x5C000000` | 1200×2000, stride 4800, FB `0x5C000000` |
| Storage | UFS 3.0 `0x04804000` | eMMC `0x04744000` (no driver) |
| Bootloader | Xiaomi fastboot, boot image v4 | Samsung ABL, boot image **v2**, DTB in header |
| Flash | `fastboot boot` | `heimdall flash --BOOT` |

Same on both: GICD `0x0F200000`, GICR `0x0F300000`, APSS watchdog `0x0F017000`,
GENI UART `0x04A90000`, boot CPU is a Silver A53 → Gold `0x100` must be woken with PSCI.

## ABL requirements

The image must be header v2 with 4096-byte pages and the board DTB:

```
qcom,msm-id  = <0x1bc 0x10000>
qcom,board-id = <0x1000b 0x00>
```

Wrong DTB (or a generic vendor blob) drops the tablet into download mode.
`tools/mkboot_gta4l.py` packs exactly this geometry and refuses a DTB without those IDs.
The DTB lives in `tools/gta4l/sm6115-samsung-gta4l.dtb` (71,295 B).

## Build

Kernel (needs macOS / GitHub Actions):

```sh
gh workflow run xnu.yml -R YOU/ios-topaz --ref topaz \
    -f kernel_config=DEVELOPMENT -f machine_config=SWEET
gh run download <RUN_ID> -R YOU/ios-topaz -n xnu-kernel -D xnu/out
```

Boot image (Linux, Python 3 + aarch64-linux-gnu-gcc for the shim):

```sh
tools/build_gta4l.sh xnu/out/kernel.development.sweet
```

Outputs `out/xnu-gta4l.img` and the exact `heimdall` command.

## Flash / recover

```sh
heimdall flash --BOOT out/xnu-gta4l.img
```

Download mode: hold **Vol+ and Vol−** and plug USB. The flash writes only the `BOOT`
partition, so recovery is flashing any working image back to `BOOT` (stock, Mu-Silicium,
or the previous build). See `RECOVERY.md`.

## Next

1. Pack a minimal HFS+ ramdisk (`rd=md0`) so XNU reaches a root device.
2. Port the display path to 1200×2000 and, ideally, 1200×2000 canvas.
3. eMMC/SDHCI root driver, then touch/keys.
4. Only then: userland (needs the iPhone X root and shared cache, as on topaz).

## Credits

- dipa-studio/ios-sweet — original XNU-on-Snapdragon work.
- MakrSas/ios-topaz — SM6225 port, shim, patch set, iOS 16 userland bring-up.
- Project Silicium / Mu-Silicium — gta4l DTB/DTBO and firmware reference used to derive
  the memory map and display addresses.
