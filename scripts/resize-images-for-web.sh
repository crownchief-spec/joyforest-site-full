#!/usr/bin/env bash
# Resize images for web: max 1600px on longest edge, JPEG quality 85%
set -e
cd "$(dirname "$0")/.."
MAX=1600
JPEG_QUALITY=85

for f in $(find assets/images -type f \( -name "*.jpg" -o -name "*.jpeg" \) ! -path "*/logo*" ! -name "logo.png"); do
  w=$(sips -g pixelWidth "$f" 2>/dev/null | awk '/pixelWidth/{print $2}')
  h=$(sips -g pixelHeight "$f" 2>/dev/null | awk '/pixelHeight/{print $2}')
  if [ -z "$w" ] || [ -z "$h" ]; then continue; fi
  if [ "$w" -le "$MAX" ] && [ "$h" -le "$MAX" ]; then
    tmp=$(mktemp).jpg
    sips -s format jpeg -s formatOptions "$JPEG_QUALITY" "$f" --out "$tmp" 2>/dev/null && mv "$tmp" "$f"
    continue
  fi
  tmp=$(mktemp).jpg
  sips -Z "$MAX" -s format jpeg -s formatOptions "$JPEG_QUALITY" "$f" --out "$tmp" 2>/dev/null && mv "$tmp" "$f"
  echo "Resized: $f"
done

for f in $(find assets/images -type f -name "*.png" ! -path "*/logo*" ! -name "logo.png"); do
  w=$(sips -g pixelWidth "$f" 2>/dev/null | awk '/pixelWidth/{print $2}')
  h=$(sips -g pixelHeight "$f" 2>/dev/null | awk '/pixelHeight/{print $2}')
  if [ -z "$w" ] || [ -z "$h" ]; then continue; fi
  if [ "$w" -le "$MAX" ] && [ "$h" -le "$MAX" ]; then continue; fi
  sips -Z "$MAX" "$f" 2>/dev/null
  echo "Resized: $f"
done

echo "Done."
