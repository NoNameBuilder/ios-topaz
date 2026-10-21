#!/bin/bash
# Build a gta4l (Galaxy Tab A7 10.4) XNU boot.img: shim + fixup-resolved payload
# + ADT, packed as Samsung header v2 with the device DTB.
#
#   tools/build_gta4l.sh kernel.development.sweet [ramdisk.img]
set -euo pipefail
cd "$(dirname "$0")/.."
KERNEL=${1:?usage: tools/build_gta4l.sh kernel.development.sweet [ramdisk.img]}
RAMDISK=${2:-}
OUT=${OUT:-out}
mkdir -p "$OUT"
[ -f "$OUT/ramdisk.bin" ] || printf '\0\0\0\0\0' > "$OUT/ramdisk.bin"

GTA4L=1 PHYSBASE=0x8a000000 MEMSIZE=0x76000000 \
    python3 tools/mkadt.py "$OUT/gta4l.adt" --native

CMD="debug=0xc serial=3 cpus=${CPUS:-4} keepsyms=1 -noprogress rd=md0 sweettouch=0 sweethw=0 sweetfb_noconsole=0 sweetfb_hz=30"
python3 tools/mkpayload.py "$KERNEL" "$OUT/gta4l.adt" "$OUT/payload.bin" \
    --cmdline "$CMD" ${RAMDISK:+--ramdisk "$RAMDISK"}

MKBOOTIMG=/bin/true shim/build.sh >/dev/null 2>&1 || true
cp shim/out/Image "$OUT/shim.bin"
size=$(stat -c%s "$OUT/shim.bin")
truncate -s $(( (size + 4095) / 4096 * 4096 )) "$OUT/shim.bin"
cat "$OUT/shim.bin" "$OUT/payload.bin" > "$OUT/Image"
gzip -9 -f -k "$OUT/Image"

python3 tools/mkboot_gta4l.py \
    --kernel "$OUT/Image.gz" \
    --dtb tools/gta4l/sm6115-samsung-gta4l.dtb \
    --ramdisk "$OUT/ramdisk.bin" \
    --cmdline "$CMD" \
    -o "$OUT/xnu-gta4l.img"

ls -l "$OUT/xnu-gta4l.img"
echo "flash: heimdall flash --BOOT $PWD/$OUT/xnu-gta4l.img"
