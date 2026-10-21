# gta4l notes (handoff)

Samsung Galaxy Tab A7 10.4 2020, `gta4l`, SM-T500 (3 GB) / SM-T505, SM6115 "Bengal".
Branch: `topaz` of `NoNameBuilder/ios-topaz` (fork of MakrSas/ios-topaz).

## Hardware facts (verified from live DT / firmware)

- RAM: `0x8A000000` is the first address above every fixed carve-out.
  TzApps at `0x61800000` (0x63900000 end), `rmtfs-mem` at `0x89B01000`.
  3 GB model: `0x8A000000` + `0x76000000` → `0x100000000`.
  4 GB model: `0x8A000000` + `0xB6000000` → `0x140000000`.
- GIC: GICD `0x0F200000` (64 KiB), GICR `0x0F300000` (1 MiB, 8 frames × 0x20000).
  Gold CPU 0 (MPIDR `0x100`) redistributor = `0x0F380000`.
- Generic timer: 19.2 MHz, virtual timer INTID 19.
- APSS watchdog: `0x0F017000` (`+8` = enable/status word).
- GENI UART: `0x04A90000`, IRQ 363.
- Display: panel 1200×2000, framebuffer region `0x5C000000` (16 MiB reserved in
  `MemoryMapLib.c` as "Display Reserved"), stride 4800, a8r8g8b8.
- Storage: eMMC 5.1 at `0x04744000` (SDHCI). UFS block `0x04800000` is unclocked —
  any MMIO read there bus-faults/reboots. No UFS node in the gta4l ADT.
- Boot CPU is a Silver A53 (no 16K granule); shim wakes Gold `0x100` via
  `PSCI_CPU_ON_64` and parks Silver.
- ABL DTB requirements: `qcom,msm-id = <0x1bc 0x10000>`,
  `qcom,board-id = <0x1000b 0x00>`; boot header v2, page 4096.

## Build / flash

```sh
gh workflow run xnu.yml -R NoNameBuilder/ios-topaz --ref topaz
gh run download <RUN_ID> -R NoNameBuilder/ios-topaz -n xnu-kernel -D xnu/out
tools/build_gta4l.sh xnu/out/kernel.development.sweet
heimdall flash --BOOT out/xnu-gta4l.img
```

`tools/build_gta4l.sh` uses the repo shim (`shim/build.sh`, cross gcc), the repo
`tools/mkpayload.py` (resolves `LC_DYLD_CHAINED_FIXUPS`), the repo `tools/mkadt.py`
with `GTA4L=1 PHYSBASE=0x8a000000 MEMSIZE=0x76000000 --native`, then
`tools/mkboot_gta4l.py` (header v2, page 4096, proven offsets).

## Observations

- Verified boot (run 39494952947 kernel): shim bars + XNU console on panel.
  Panic: `SWEET CPU: invalid topology cpu=1 mpidr=0x101 count=4`.
  Cause: patch `0060` was edited (hunk context) → `0080` (topaz CPU topology) was
  skipped by the apply script → `0078`'s check `(phys_id & 0xff) != 0` rejected
  Gold cores `0x101..0x103`.
- Fix: keep `xnu/patches` pristine; only move `0113`–`0130` (modem/Wi-Fi) to
  `xnu/patches_disabled_gta4l/`. Rebuild pending.
- `gta4l-xnu-boot-kit.zip`: its shim and packer are usable for reference, but its
  `mkpayload.py` does not resolve chained fixups → the kernel crashes immediately.
  Do not use it; build from the repo.
- ABL drops to download mode on a generic vendor DTB (4.4 MB blob) — always pack the
  board DTB (71,295 B, md5 `7ccb50243221e8f8d4805837c33c2e6a`).

## Next

1. Verify the rebuilt kernel passes the CPU topology (4 Gold cores) and reaches
   root-mount panic.
2. Build a minimal HFS+ ramdisk for `rd=md0` (or an eMMC/SDHCI root driver).
3. Retarget SweetSurface/AppleCLCD to 1200×2000 (and `sweet-fbcon` already is).
4. Then touch (SPI novatek/himax) and keys, then userland.
