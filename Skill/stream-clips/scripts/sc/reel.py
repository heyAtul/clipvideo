"""The "reel" look: landscape gameplay kept whole (16:9, never cropped) in the middle of a
branded 9:16 canvas.

    top     the mascot, "LET'S GO!" and the facecam in a glowing frame
    middle  the full gameplay frame, 1080 x 608, with torn-paper edges
    bottom  brush strokes, claw marks and a faint oversized mascot; the subscribe banner
            (play button, SUBSCRIBE, bell) only with "reel_subscribe": true (off by default)

Every piece of art is its own PNG in ~/StreamClips/brand/reel/, generated from settings.json
the first time it's needed:

    texture.png     the dark grunge background
    top.png         brush strokes, the mascot, LET'S GO!
    bottom.png      brush strokes, claw marks, the faint mascot (+ the subscribe banner)
    frame.png       the facecam border
    edges.png       the torn-paper edges above and below the gameplay
    glow.png        the pulsing glow around the facecam (animated)
    bell.png        the bell (animated: it swings; only used with the subscribe banner)
    frame_fill.png  shown in the facecam frame when the stream has no facecam

A PNG edited by hand is kept as it is. Delete one to have it generated again."""

import hashlib
import json
import math
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .common import DATA, even, font_file, read_json, say, write_json

W, H = 1080, 1920
GAME_Y, GAME_H = 520, 608            # the gameplay band (16:9 at the full width)
FRAME = (684, 100, 372, 340)         # the facecam picture: x, y, w, h
BORDER = 9                           # facecam border thickness
GLOW_PAD = 56                        # room around the border for the glow
BELL = (788, 1312, 220, 220)         # the bell layer: x, y, w, h (it swings inside)
CAPTION_Y = 1222                     # the caption line, between the gameplay and the banner
VERSION = 2                          # bump to regenerate generated layers after code changes
FONT_URL = ("https://github.com/google/fonts/raw/main/apache/permanentmarker/"
            "PermanentMarker-Regular.ttf")
STATIC = ("texture", "bottom", "top", "frame", "edges")
LAYERS = STATIC + ("glow", "bell", "frame_fill")
WHITE = (255, 255, 255)


# ---------------------------------------------------------------- helpers

def _rgb(hex6):
    h = str(hex6).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


_font_path = None


def _font(cfg, size):
    """The graffiti font: reel_font, else Permanent Marker (downloaded once), else bold."""
    global _font_path
    if _font_path is None:
        wanted = cfg.get("reel_font")
        path = DATA / "brand" / "fonts" / "PermanentMarker-Regular.ttf"
        if wanted:
            path = wanted
        elif not path.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(FONT_URL, path)
            except Exception:  # noqa: BLE001 - no network: fall back to a system font
                path = None
        _font_path = str(path) if path else font_file("bold")
    try:
        return ImageFont.truetype(_font_path, size)
    except OSError:
        return ImageFont.truetype(font_file("bold"), size)


def _noise(rng, w, h, cell):
    small = rng.random((max(2, h // cell + 2), max(2, w // cell + 2)))
    img = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(img, np.float32) / 255


def _smooth(rng, n, k=7):
    a = rng.standard_normal(n + k)
    return np.convolve(a, np.ones(k) / k, mode="valid")[:n] * math.sqrt(k) * 0.5


def _path(points, n):
    pts = np.array(points, np.float32)
    t = np.linspace(0, 1, n)[:, None]
    if len(pts) == 2:
        return pts[0] * (1 - t) + pts[1] * t
    if len(pts) == 3:
        return (1 - t) ** 2 * pts[0] + 2 * (1 - t) * t * pts[1] + t ** 2 * pts[2]
    if len(pts) == 4:
        return ((1 - t) ** 3 * pts[0] + 3 * (1 - t) ** 2 * t * pts[1]
                + 3 * (1 - t) * t ** 2 * pts[2] + t ** 3 * pts[3])
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    s = np.linspace(0, cum[-1], n)
    return np.stack([np.interp(s, cum, pts[:, 0]), np.interp(s, cum, pts[:, 1])], 1)


def _paste(layer, piece, x, y):
    """alpha_composite that tolerates pieces hanging off the canvas."""
    x, y = int(round(x)), int(round(y))
    l, t = max(0, -x), max(0, -y)
    r, b = min(piece.width, layer.width - x), min(piece.height, layer.height - y)
    if r > l and b > t:
        layer.alpha_composite(piece.crop((l, t, r, b)), (x + l, y + t))


def stroke(layer, points, width, c0, c1, rng, rough=0.28, head=0.12, tail=0.4, glow=0.5,
           streaks=True):
    """A painted brush stroke along a line or curve: rough edges, dry-brush gaps, a colour
    fade from c0 to c1 and a soft glow."""
    n = 90
    p = _path(points, n)
    d = np.gradient(p, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-6
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    t = np.linspace(0, 1, n)
    prof = np.minimum(1, t / head) ** 0.6 * np.minimum(1, (1 - t) / tail) ** 0.8
    hw = width / 2 * prof
    up = p + nrm * (hw * (1 + rough * _smooth(rng, n)))[:, None]
    dn = p - nrm * (hw * (1 + rough * _smooth(rng, n)))[:, None]
    poly = [tuple(q) for q in up] + [tuple(q) for q in dn[::-1]]
    mask = Image.new("L", layer.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(poly, fill=255)
    if streaks:
        for _ in range(max(3, int(width / 3))):
            off = rng.uniform(-0.85, 0.85)
            t0 = rng.uniform(0.3, 0.95)
            t1 = min(1.0, t0 + rng.uniform(0.08, 0.45))
            i0, i1 = int(t0 * (n - 1)), int(t1 * (n - 1))
            seg = [tuple(p[i] + nrm[i] * hw[i] * off) for i in range(i0, i1 + 1)]
            if len(seg) > 1:
                draw.line(seg, fill=0, width=int(rng.integers(1, 4)))
    mask = mask.filter(ImageFilter.GaussianBlur(0.7))
    box = mask.getbbox()
    if not box:
        return
    pad = int(width * 1.4) + 4
    x0, y0 = max(0, box[0] - pad), max(0, box[1] - pad)
    x1, y1 = min(layer.width, box[2] + pad), min(layer.height, box[3] + pad)
    sub = mask.crop((x0, y0, x1, y1))
    a = np.asarray(sub, np.float32) / 255
    if glow:
        g = np.asarray(sub.filter(ImageFilter.GaussianBlur(width * 0.45 + 4)), np.float32) / 255
        a = np.maximum(a, g * glow)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    (sx, sy), (ex, ey) = p[0], p[-1]
    tt = np.clip(((xx - sx) * (ex - sx) + (yy - sy) * (ey - sy))
                 / ((ex - sx) ** 2 + (ey - sy) ** 2 + 1e-6), 0, 1)[..., None]
    col = np.array(c0, np.float32) * (1 - tt) + np.array(c1, np.float32) * tt
    rgba = np.dstack([col, a * 255]).clip(0, 255).astype(np.uint8)
    layer.alpha_composite(Image.fromarray(rgba, "RGBA"), (x0, y0))


def arc(center, r, a0, a1, n=40):
    return [(center[0] + r * math.cos(math.radians(a)), center[1] + r * math.sin(math.radians(a)))
            for a in np.linspace(a0, a1, n)]


def claws(layer, start, direction, rng, c0, c1, n=3, gap=40, length=230, width=24):
    """Claw marks: a few parallel, slightly curved scratches."""
    dx, dy = direction
    norm = math.hypot(dx, dy)
    dx, dy = dx / norm, dy / norm
    px, py = -dy, dx
    for i in range(n):
        ox, oy = start[0] + px * gap * i, start[1] + py * gap * i
        bend = rng.uniform(10, 22)
        pts = [(ox, oy), (ox + dx * length / 2 + px * bend, oy + dy * length / 2 + py * bend),
               (ox + dx * length, oy + dy * length)]
        stroke(layer, pts, width * rng.uniform(0.85, 1.1), c0, c1, rng, rough=0.2, head=0.08,
               tail=0.6, glow=0.55, streaks=False)


def text(layer, center, s, font, fill=WHITE, gradient=None, angle=0.0, shear=0.18,
         outline=7, glow=None, shadow=True):
    """Bold slanted text with a dark outline, an optional vertical gradient and glow."""
    box = font.getbbox(s, stroke_width=outline)
    m = 40
    tw, th = box[2] - box[0] + 2 * m, box[3] - box[1] + 2 * m
    at = (m - box[0], m - box[1])
    fill_mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(fill_mask).text(at, s, font=font, fill=255)
    out_mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(out_mask).text(at, s, font=font, fill=255, stroke_width=outline, stroke_fill=255)
    piece = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    if glow:
        g = out_mask.filter(ImageFilter.GaussianBlur(16))
        piece.alpha_composite(Image.merge("RGBA", [*(Image.new("L", (tw, th), v) for v in glow),
                                                   g.point(lambda v: int(v * 0.85))]))
    if shadow:
        s_mask = Image.new("L", (tw, th), 0)
        s_mask.paste(out_mask, (6, 9))
        s_mask = s_mask.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.8))
        piece.alpha_composite(Image.merge("RGBA", [*(Image.new("L", (tw, th), 0),) * 3, s_mask]))
    piece.alpha_composite(Image.merge("RGBA", [*(Image.new("L", (tw, th), 12),) * 3, out_mask]))
    if gradient:
        ys = np.linspace(0, 1, th)[:, None, None]
        col = (np.array(gradient[0]) * (1 - ys) + np.array(gradient[1]) * ys).repeat(tw, 1)
    else:
        col = np.broadcast_to(np.array(fill, np.float32), (th, tw, 3))
    rgba = np.dstack([col, np.asarray(fill_mask)]).astype(np.uint8)
    piece.alpha_composite(Image.fromarray(rgba, "RGBA"))
    if shear:
        extra = int(th * shear)
        piece = piece.transform((tw + extra, th), Image.AFFINE, (1, shear, -extra, 0, 1, 0),
                                resample=Image.BICUBIC)
    if angle:
        piece = piece.rotate(angle, resample=Image.BICUBIC, expand=True)
    _paste(layer, piece, center[0] - piece.width / 2, center[1] - piece.height / 2)


def _fit(img, width=None, height=None):
    r = min((width or 10 ** 9) / img.width, (height or 10 ** 9) / img.height)
    return img.resize((max(1, int(img.width * r)), max(1, int(img.height * r))), Image.LANCZOS)


def _shadow(layer, box, radius, blur=14, offset=(10, 14), strength=0.75):
    m = Image.new("L", layer.size, 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(m).rounded_rectangle((x0 + offset[0], y0 + offset[1], x1 + offset[0],
                                         y1 + offset[1]), radius=radius, fill=int(255 * strength))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(Image.merge("RGBA", [*(Image.new("L", layer.size, 0),) * 3, m]))


def _mascot(cfg):
    from pathlib import Path
    for key in ("reel_mascot", "watermark"):
        if cfg.get(key):
            p = Path(str(cfg[key])).expanduser()
            if p.is_file():
                return p
    return None


# ---------------------------------------------------------------- layers

def _texture(cfg, mascot, rng):
    v = 8 + 15 * _noise(rng, W, H, 240) + 9 * _noise(rng, W, H, 70) + 6 * rng.random((H, W))
    v[rng.random((H, W)) > 0.9986] += 26
    yy, xx = np.mgrid[0:H, 0:W]
    v *= 1 - 0.5 * (0.55 * ((xx - W / 2) / (W / 2)) ** 2 + 0.25 * ((yy - H / 2) / (H / 2)) ** 2)
    img = Image.fromarray(np.clip(np.stack([v * 1.03, v, v * 0.96], -1), 0, 255).astype(np.uint8))
    layer = img.convert("RGBA")
    draw = ImageDraw.Draw(layer)
    for _ in range(140):                                    # faint scratches
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        a = rng.uniform(0, math.pi)
        ln = rng.uniform(20, 120)
        g = int(rng.uniform(24, 40))
        draw.line([(x, y), (x + math.cos(a) * ln, y + math.sin(a) * ln)], fill=(g, g, g, 255), width=1)
    return layer


def _top(cfg, mascot, rng):
    o, y = _rgb(cfg["reel_orange"]), _rgb(cfg["reel_yellow"])
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stroke(layer, [(-60, 210), (40, 70), (210, -30)], 78, o, y, rng, glow=0.5)
    stroke(layer, arc((232, 282), 236, 118, 252), 30, y, o, rng, rough=0.3, glow=0.65, tail=0.3)
    stroke(layer, arc((232, 282), 262, 128, 200), 12, o, y, rng, rough=0.25, glow=0.5, streaks=False)
    stroke(layer, [(700, -40), (880, 10), (1130, 46)], 62, o, y, rng, glow=0.45)
    stroke(layer, [(900, 64), (1010, 44), (1120, 18)], 22, y, o, rng, glow=0.4)
    stroke(layer, [(-30, 505), (160, 470), (360, 492)], 26, o, y, rng, glow=0.4)
    if mascot:
        m = _fit(Image.open(mascot).convert("RGBA"), 432, 432)
        _paste(layer, m, 16, 52)
    x, yy, w, h = FRAME
    _shadow(layer, (x - BORDER, yy - BORDER, x + w + BORDER, yy + h + BORDER), 20)
    words = str(cfg["reel_top_text"]).split()
    first, last = (" ".join(words[:-1]), words[-1]) if len(words) > 1 else (words[0], "")
    text(layer, (528, 200), first, _font(cfg, 74), fill=WHITE, angle=9)
    if last:
        text(layer, (530, 318), last, _font(cfg, 128), gradient=(y, o), angle=9, glow=o)
    stroke(layer, [(418, 444), (530, 428), (652, 396)], 20, o, y, rng, glow=0.5, tail=0.5)
    return layer


def _play_button(layer, box):
    x, y, w, h = box
    k = 4
    big = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle((0, 0, w * k - 1, h * k - 1), radius=int(h * k * 0.3), fill=(255, 255, 255, 255))
    mask = big.getchannel("A")
    ys = np.linspace(0, 1, h * k)[:, None, None]
    col = (np.array([255, 38, 38]) * (1 - ys) + np.array([196, 0, 0]) * ys).repeat(w * k, 1)
    red = Image.fromarray(np.dstack([col, np.asarray(mask)]).astype(np.uint8), "RGBA")
    ImageDraw.Draw(red).polygon([(w * k * 0.39, h * k * 0.26), (w * k * 0.39, h * k * 0.74),
                                 (w * k * 0.70, h * k * 0.50)], fill=(255, 255, 255, 255))
    _shadow(layer, (x, y, x + w, y + h), int(h * 0.3), blur=10, offset=(6, 10))
    _paste(layer, red.resize((w, h), Image.LANCZOS), x, y)


def _bottom(cfg, mascot, rng):
    o, y = _rgb(cfg["reel_orange"]), _rgb(cfg["reel_yellow"])
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if mascot:
        m = _fit(Image.open(mascot).convert("RGBA"), 800, 800)
        arr = np.asarray(m, np.float32)
        arr[..., :3] *= 0.7
        arr[..., 3] *= 0.3
        _paste(layer, Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA"), 500, 1440)
    stroke(layer, [(930, 1205), (1020, 1180), (1130, 1150)], 52, o, y, rng, glow=0.45)
    stroke(layer, [(-70, 1915), (110, 1800), (330, 1712)], 92, o, y, rng, glow=0.5)
    stroke(layer, [(-40, 1840), (80, 1785), (230, 1745)], 26, y, o, rng, glow=0.4)
    stroke(layer, [(700, 1905), (900, 1840), (1130, 1800)], 54, o, y, rng, glow=0.4)
    claws(layer, (52, 1590), (0.55, 1), rng, o, y)
    if not cfg.get("reel_subscribe"):          # the subscribe banner is off unless asked for
        return layer
    _play_button(layer, (52, 1364, 168, 118))
    text(layer, (514, 1414), str(cfg["reel_cta"]), _font(cfg, 96), fill=WHITE, angle=4)
    stroke(layer, [(246, 1500), (500, 1494), (770, 1466)], 20, o, y, rng, glow=0.5, tail=0.5)
    cx, cy = BELL[0] + BELL[2] / 2, BELL[1] + BELL[3] / 2
    for a, ln in ((-62, 36), (-40, 44), (-18, 34)):            # the bell is ringing
        r0 = 104
        p0 = (cx + r0 * math.cos(math.radians(a)), cy + r0 * math.sin(math.radians(a)))
        p1 = (cx + (r0 + ln) * math.cos(math.radians(a)), cy + (r0 + ln) * math.sin(math.radians(a)))
        stroke(layer, [p0, p1], 11, o, y, rng, rough=0.1, head=0.2, tail=0.2, glow=0.5, streaks=False)
    return layer


def _frame(cfg, mascot, rng):
    o, y = _rgb(cfg["reel_orange"]), _rgb(cfg["reel_yellow"])
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x, yy, w, h = FRAME
    b = BORDER
    k = 3
    big = Image.new("L", ((w + 2 * b) * k, (h + 2 * b) * k), 0)
    d = ImageDraw.Draw(big)
    d.rounded_rectangle((0, 0, big.width - 1, big.height - 1), radius=20 * k, fill=255)
    d.rounded_rectangle((b * k, b * k, (w + b) * k - 1, (h + b) * k - 1), radius=8 * k, fill=0)
    ring = big.resize((w + 2 * b, h + 2 * b), Image.LANCZOS)
    gw, gh = ring.size
    yy_, xx_ = np.mgrid[0:gh, 0:gw]
    tt = ((xx_ / gw + yy_ / gh) / 2)[..., None]
    col = np.array(y, np.float32) * (1 - tt) + np.array(o, np.float32) * tt
    _paste(layer, Image.fromarray(np.dstack([col, np.asarray(ring)]).astype(np.uint8), "RGBA"),
           x - b, yy - b)
    cx, cy = x + w + b, yy - b                                  # accent marks, top-right corner
    for ang, r0, ln in ((-80, 22, 40), (-52, 20, 50), (-24, 22, 40)):
        p0 = (cx + r0 * math.cos(math.radians(ang)), cy + r0 * math.sin(math.radians(ang)))
        p1 = (cx + (r0 + ln) * math.cos(math.radians(ang)), cy + (r0 + ln) * math.sin(math.radians(ang)))
        stroke(layer, [p0, p1], 12, y, o, rng, rough=0.1, head=0.2, tail=0.2, glow=0.5, streaks=False)
    return layer


def _edges(cfg, mascot, rng):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for edge, sign in ((GAME_Y, -1), (GAME_Y + GAME_H, 1)):
        xs, x = [], -10.0
        while x < W + 20:
            xs.append(x)
            x += rng.uniform(5, 13)
        depth = 9 + 9 * _smooth(rng, len(xs), 9) + rng.uniform(0, 6, len(xs))
        depth = np.clip(depth, 4, 24)
        jag = [(xv, edge + sign * dv) for xv, dv in zip(xs, depth)]
        poly = [(-10, edge)] + jag + [(W + 20, edge)]
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).polygon(poly, fill=255)
        shadow = mask.filter(ImageFilter.GaussianBlur(6))
        sh = Image.new("L", (W, H), 0)
        sh.paste(shadow, (0, sign * 6))
        layer.alpha_composite(Image.merge("RGBA", [*(Image.new("L", (W, H), 0),) * 3,
                                                   sh.point(lambda v: int(v * 0.7))]))
        paper = (228 + 18 * rng.random((H, W))).astype(np.uint8)
        rgb = np.stack([paper, (paper * 0.985).astype(np.uint8), (paper * 0.96).astype(np.uint8)], -1)
        layer.alpha_composite(Image.fromarray(np.dstack([rgb, np.asarray(mask)]), "RGBA"))
    return layer


def _glow(cfg, mascot, rng):
    o = _rgb(cfg["reel_orange"])
    x, yy, w, h = FRAME
    b, p = BORDER, GLOW_PAD
    size = (w + 2 * (b + p), h + 2 * (b + p))
    ring = Image.new("L", size, 0)
    d = ImageDraw.Draw(ring)
    d.rounded_rectangle((p, p, size[0] - p - 1, size[1] - p - 1), radius=20, outline=255, width=b + 4)
    g = ring.filter(ImageFilter.GaussianBlur(16))
    hole = Image.new("L", size, 255)
    ImageDraw.Draw(hole).rounded_rectangle((p + b, p + b, size[0] - p - b - 1, size[1] - p - b - 1),
                                           radius=8, fill=0)
    a = (np.asarray(g, np.float32) * 1.6).clip(0, 255) * (np.asarray(hole, np.float32) / 255)
    return Image.fromarray(np.dstack([np.broadcast_to(np.array(o, np.uint8), (*a.shape, 3)),
                                      a.astype(np.uint8)]), "RGBA")


def _bell(cfg, mascot, rng):
    bw, bh = BELL[2], BELL[3]
    k = 4
    big = Image.new("RGBA", (bw * k, bh * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    s = bw * k / 220
    white, shade = (248, 248, 248, 255), (214, 214, 214, 255)

    def P(px, py):
        return (px * s, py * s)

    d.ellipse([*P(96, 34), *P(124, 62)], fill=white)                          # knob
    body = [P(110, 50)] + [P(110 + 48 * math.sin(a), 50 + 40 * (1 - math.cos(a)))
                           for a in np.linspace(0, math.pi / 2, 12)]
    body += [P(162, 100), P(166, 136), P(186, 158), P(34, 158), P(54, 136), P(58, 100)]
    body += [P(110 - 48 * math.sin(a), 50 + 40 * (1 - math.cos(a)))
             for a in np.linspace(math.pi / 2, 0, 12)]
    d.polygon(body, fill=white)
    d.rounded_rectangle([*P(26, 150), *P(194, 170)], radius=10 * s, fill=white)   # rim
    d.polygon([P(140, 70), P(158, 102), P(160, 140), P(176, 154), P(150, 154), P(146, 104)], fill=shade)
    d.ellipse([*P(94, 166), *P(126, 196)], fill=white)                        # clapper
    bell = big.resize((bw, bh), Image.LANCZOS)
    shadow = Image.new("L", (bw, bh), 0)
    shadow.paste(bell.getchannel("A"), (5, 8))
    out = Image.merge("RGBA", [*(Image.new("L", (bw, bh), 0),) * 3,
                               shadow.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.7))])
    out.alpha_composite(bell)
    return out


def _frame_fill(cfg, mascot, rng):
    x, yy, w, h = FRAME
    base = _texture(cfg, mascot, rng).crop((0, 0, w, h))
    if mascot:
        m = _fit(Image.open(mascot).convert("RGBA"), w - 40, h - 30)
        _paste(base, m, (w - m.width) / 2, (h - m.height) / 2)
    return base


BUILDERS = {"texture": _texture, "top": _top, "bottom": _bottom, "frame": _frame, "edges": _edges,
            "glow": _glow, "bell": _bell, "frame_fill": _frame_fill}


# ---------------------------------------------------------------- assets + filtergraph

def _sha(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def assets(cfg):
    """Make sure every layer PNG exists and is up to date, and compose the static ones into
    composed_bg.png. Returns {name: path}."""
    folder = DATA / "brand" / "reel"
    folder.mkdir(parents=True, exist_ok=True)
    manifest = read_json(folder / "layers.json", {}) or {}
    mascot = _mascot(cfg)
    keys = ("reel_top_text", "reel_cta", "reel_orange", "reel_yellow", "reel_font", "reel_subscribe")
    stamp = {k: cfg.get(k) for k in keys}
    stamp.update(version=VERSION, mascot=str(mascot), mtime=mascot.stat().st_mtime if mascot else 0)
    want = hashlib.sha1(json.dumps(stamp, sort_keys=True).encode()).hexdigest()[:12]
    paths = {}
    for i, name in enumerate(LAYERS):
        path = folder / f"{name}.png"
        rec = manifest.get(name) or {}
        edited = path.exists() and rec.get("sha") and _sha(path) != rec["sha"]
        if path.exists() and (edited or rec.get("inputs") == want):
            paths[name] = path
            continue
        say(f"  reel: drawing {name}.png", "step")
        BUILDERS[name](cfg, mascot, np.random.default_rng(1000 + i)).save(path)
        manifest[name] = {"inputs": want, "sha": _sha(path)}
        paths[name] = path
    bg = folder / "composed_bg.png"
    mix = hashlib.sha1("".join(_sha(paths[n]) for n in STATIC).encode()).hexdigest()
    if not bg.exists() or manifest.get("_bg") != mix:
        base = Image.open(paths["texture"]).convert("RGBA")
        for name in STATIC[1:]:
            base.alpha_composite(Image.open(paths[name]).convert("RGBA"))
        base.convert("RGB").save(bg)
        manifest["_bg"] = mix
    write_json(folder / "layers.json", manifest)
    paths["bg"] = bg
    return paths


def caption_cfg(cfg):
    """The settings with the caption line moved between the gameplay and the banner."""
    return dict(cfg, cap_y=CAPTION_Y / cfg["height"])


def _cover(cam, aim, sw, sh):
    """A crop of the facecam box with the frame's aspect ratio, centred, inside the frame."""
    x, y, w, h = cam
    cw, ch = (h * aim, h) if w / h > aim else (w, w / aim)
    cw, ch = min(cw, sw), min(ch, sh)
    cx = min(max(x + (w - cw) / 2, 0), sw - cw)
    cy = min(max(y + (h - ch) / 2, 0), sh - ch)
    return cx, cy, cw, ch


def graph(cfg, info, cam, length, fps, first, paths):
    """Filtergraph from [0:v] (the gameplay) plus image inputs numbered from `first`, ending
    in [framed]. Returns (filtergraph, extra ffmpeg input arguments)."""
    loop = ["-loop", "1", "-framerate", f"{fps:.3f}", "-t", f"{length:.3f}"]
    inputs, index = [], {}

    def add(name):                      # an image input, looped for the clip's length
        index[name] = first + len(index)
        inputs.extend([*loop, "-i", str(paths[name])])

    add("bg")
    add("glow")
    bell = bool(cfg.get("reel_subscribe"))
    if bell:
        add("bell")
    sw, sh = info["width"], info["height"]
    gh = min(even(W * sh / sw), GAME_H)
    gy = GAME_Y + (GAME_H - gh) // 2
    x, y, w, h = FRAME
    g = []
    if cam:
        cx, cy, cw, ch = _cover(cam, w / h, sw, sh)
        g += ["[0:v]split=2[gsrc][csrc]",
              f"[csrc]crop={even(cw)}:{even(ch)}:{even(cx)}:{even(cy)},"
              f"scale={w}:{h}:flags=lanczos,setsar=1[cam]",
              f"[gsrc]scale={W}:{gh}:flags=lanczos,setsar=1[game]"]
    else:
        add("frame_fill")
        g += [f"[{index['frame_fill']}:v]setsar=1[cam]",
              f"[0:v]scale={W}:{gh}:flags=lanczos,setsar=1[game]"]
    gx, gyy = x - BORDER - GLOW_PAD, y - BORDER - GLOW_PAD
    g += [f"[{index['bg']}:v][game]overlay=0:{gy}:shortest=1[l1]",
          f"[l1][cam]overlay={x}:{y}[l2]",
          f"[{index['glow']}:v]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
          f"a='alpha(X,Y)*(0.5+0.5*sin(2*PI*T/1.8))'[gl]"]
    if bell:
        g += [f"[l2][gl]overlay={gx}:{gyy}[l3]",
              f"[{index['bell']}:v]format=rgba,"
              f"rotate=a='0.22*sin(2*PI*t*3)*lt(mod(t,3),0.9)':c=none[bl]",
              f"[l3][bl]overlay={BELL[0]}:{BELL[1]},format=yuv420p[framed]"]
    else:
        g += [f"[l2][gl]overlay={gx}:{gyy},format=yuv420p[framed]"]
    return ";".join(g), inputs
