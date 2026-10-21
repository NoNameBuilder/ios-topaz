#!/usr/bin/env python3
"""Pack a Samsung gta4l boot image (header v2, 4096-byte pages) - stdlib only.

Geometry is the one the SM-T500/SM-T505 ABL accepts:
  kernel @0x00008000, ramdisk @0x20000000, tags @0x1e00000, dtb @0x1f00000
The DTB must carry gta4l's qcom,msm-id/board-id or ABL drops to download mode.

  mkboot_gta4l.py --kernel Image.gz --dtb sm6115-samsung-gta4l.dtb \
      [--ramdisk rd] [--cmdline "..."] -o boot.img

Header v2 has no cmdline field that ABL honours; the string is stored only so
the image is self-describing for humans/tools.
"""
import argparse
import struct
import sys

PAGE = 4096
KERNEL_ADDR = 0x00008000
RAMDISK_ADDR = 0x20000000
TAGS_ADDR = 0x1E00000
DTB_ADDR = 0x1F00000
HEADER_SIZE = 1660


def pad(data, page=PAGE):
    return data + b"\0" * (-len(data) % page)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", required=True)
    ap.add_argument("--dtb", required=True)
    ap.add_argument("--ramdisk")
    ap.add_argument("--cmdline", default="")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    kernel = open(a.kernel, "rb").read()
    dtb = open(a.dtb, "rb").read()
    ramdisk = open(a.ramdisk, "rb").read() if a.ramdisk else b""

    if dtb[:4] != b"\xd0\x0d\xfe\xed":
        sys.exit(f"{a.dtb}: not a flattened device tree")
    if b"qcom,msm-id" not in dtb or b"qcom,board-id" not in dtb:
        sys.exit(f"{a.dtb}: missing qcom,msm-id/qcom,board-id; ABL will reject it")

    name = b"gta4l-xnu"[:16].ljust(16, b"\0")
    cmd = a.cmdline.encode()[:511].ljust(512, b"\0")
    hdr = bytearray(HEADER_SIZE)
    hdr[0:8] = b"ANDROID!"
    struct.pack_into("<10I", hdr, 8, len(kernel), KERNEL_ADDR, len(ramdisk),
                     RAMDISK_ADDR, 0, 0, TAGS_ADDR, PAGE, 2, 0)
    hdr[48:64] = name
    hdr[64:576] = cmd
    struct.pack_into("<I", hdr, 1644, HEADER_SIZE)
    struct.pack_into("<I", hdr, 1648, len(dtb))
    struct.pack_into("<Q", hdr, 1652, DTB_ADDR)

    img = pad(bytes(hdr)) + pad(kernel) + pad(ramdisk) + pad(dtb)
    open(a.out, "wb").write(img)
    print(f"PACKED {a.out} ({len(img)} B): kernel {len(kernel)} @{KERNEL_ADDR:#x}, "
          f"ramdisk {len(ramdisk)} @{RAMDISK_ADDR:#x}, dtb {len(dtb)} @{DTB_ADDR:#x}")


if __name__ == "__main__":
    main()
