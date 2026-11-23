"""Cut the black square background out of the logo and save a transparent PNG.

Inside the orange ring everything is kept (so the cat's black jacket and the gun stay solid).
Outside the ring, opacity follows brightness: the crown, brush strokes and glow stay, and the
pure black background becomes fully transparent.

usage (it needs Pillow and numpy, which the stream-clips environment has):
    ~/.streamclips/venv/bin/python make_watermark.py <logo.jpg> <out.png>
"""

import sys

import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
rgb = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
h, w, _ = rgb.shape
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]

# The ring is the bright orange/yellow pixels. Find its edges along the middle row and the
# middle column (from below: the crown sits above the ring at the top).
ring = (r > 200) & (g > 110) & (b < 120)
cy, cx = h // 2, w // 2


def first(line):
    idx = np.flatnonzero(line)
    return int(idx[0]) if len(idx) else None


edges = (first(ring[cy, :]), first(ring[cy, ::-1]), first(ring[::-1, cx]))
if None in edges:
    # No orange ring: just key out the dark background. Dark parts inside the logo turn
    # see-through too, so a PNG with a transparent background is the better choice here.
    print("no orange ring found: removing the dark background by brightness only")
    inside = np.zeros((h, w), np.float32)
else:
    left, right, bottom = edges[0], w - 1 - edges[1], h - 1 - edges[2]
    center_x = (left + right) / 2
    radius = (right - left) / 2
    center_y = bottom - radius
    print(f"ring: center=({center_x:.0f},{center_y:.0f}) radius={radius:.0f} "
          f"(left={left} right={right} bottom={bottom})")
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.hypot(xx - center_x, yy - center_y)
    inside = np.clip((radius + 6 - dist) / 6, 0, 1)        # 1 inside the ring, 6 px soft edge

brightness = rgb.max(axis=2)
outside = np.clip((brightness - 8) / 70, 0, 1) ** 0.8      # black -> 0, bright strokes -> 1

alpha = np.maximum(inside, outside)
alpha_img = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))

out = Image.fromarray(rgb.astype(np.uint8)).convert("RGBA")
out.putalpha(alpha_img)
bbox = out.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()  # trim empty edges
out = out.crop(bbox)
out.save(dst)
print(f"saved {dst}  {out.width}x{out.height}  (trimmed to {bbox})")
