#!/usr/bin/env bash
# Dung lai bo slide tu bo slide goc.
#   ./build.sh <slide_goc.pptx> [thu_muc_tam]
# Can: python3 (python-pptx, matplotlib, pillow, lxml), node (react-icons, react, react-dom, sharp).
set -euo pipefail
SRC="$1"
WORK="${2:-./_work}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$WORK/img" "$WORK/charts" "$WORK/icons"
python3 "$HERE/prep_assets.py" "$SRC" "$WORK/img"
python3 "$HERE/charts.py" "$WORK/charts"
(cd "$HERE" && node icons.js icons.json "$WORK/icons")
python3 "$HERE/build_deck.py" "$SRC" "$WORK" "$HERE/../Slide_Bao_ve_DATN_Gimbal_NuttX.pptx"
python3 "$HERE/check_anim.py" "$HERE/../Slide_Bao_ve_DATN_Gimbal_NuttX.pptx" | tail -1
python3 "$HERE/export_script.py" "$HERE/../Slide_Bao_ve_DATN_Gimbal_NuttX.pptx" "$HERE/../KICH_BAN_THUYET_TRINH.md"
