"""Every knob in one place. Override any of them in ~/StreamClips/settings.json."""

from pathlib import Path

from .common import DATA, Problem, read_json

DEFAULTS = {
    # finding streams
    "search_suffix": "stream",       # YouTube search = "<topic> <suffix>"; "" for any long video
    "search_when": "today",          # hour | today | week | month
    "max_age_hours": 48,             # watchlist videos older than this are skipped

    # listening
    "scan_model": "tiny",            # Whisper model for the whole stream (fast)
    "caption_model": "base",         # Whisper model for each clip's captions (accurate)
    "language": None,                # None = detect once per stream, or e.g. "en", "hi", "es"
    "block_minutes": 10,             # audio is processed and cached in blocks of this size
    "volume_jump_db": 7.0,           # this much louder than the surrounding minutes = a spike
    "chat_jump": 3.0,                # chat this many times its usual speed = a spike
    "chat_replay": True,             # read YouTube live-chat replays when there is one
    "chat_timeout": 360,

    # picking
    "clips": 3,                      # clips per stream
    "min_len": 15,
    "max_len": 59,                   # stays under the 60 s Shorts limit
    "part_minutes": 10,              # transcript window sent to the AI per call
    "part_overlap": 20,              # seconds shared by neighbouring windows
    "picks_per_part": 3,
    "brain_parallel": 3,             # AI calls at the same time
    "min_score": 40,                 # picks below this score are dropped

    # framing
    "width": 1080,
    "height": 1920,
    "layout": "auto",                # auto | stack | crop | blur | reel
    "cam_share": 0.40,               # stack layout: share of the height given to the facecam
    "big_face": 0.13,                # face wider than this share of the frame = talking head

    # title bar
    "title_font_file": None,         # None = a bold system font
    "title_size": 56,
    "title_bg": "FFFFFF",
    "title_fg": "111111",
    "title_top": 0.07,               # used when there is no facecam seam to sit on

    # captions
    "cap_font": "Arial Black",
    "cap_size": 86,
    "cap_words": 3,
    "cap_color": "FFFFFF",
    "cap_active": "FFD400",
    "cap_outline": 7,
    "cap_upper": True,
    "cap_y": 0.70,                   # vertical position of the caption line (0 top, 1 bottom)

    # watermark (a logo burned into every clip, under the title and captions)
    "watermark": None,               # path to a PNG with a transparent background; None = off
    "watermark_opacity": 0.30,       # 0 invisible, 1 solid
    "watermark_width": 0.36,         # share of the frame width (shrunk to fit the free space)
    "watermark_y": None,             # centre as a share of the height; None = the middle of
                                     # the free space between the title bar and the captions

    # the "reel" layout (layout: "reel"): the whole 16:9 gameplay in the middle of a branded
    # frame. Its art is in ~/StreamClips/brand/reel/ (see sc/reel.py)
    "reel_top_text": "LET'S GO!",    # the last word is orange, the rest white
    "reel_subscribe": False,         # the subscribe banner (play button, SUBSCRIBE, bell)
    "reel_cta": "SUBSCRIBE",         # the banner's text, when it's on
    "reel_orange": "FF7900",
    "reel_yellow": "FFB000",
    "reel_mascot": None,             # a PNG with transparency; None = the watermark logo
    "reel_font": None,               # a .ttf; None = Permanent Marker (downloaded once)

    # post text: one <clip>.txt per clip, next to the video
    "hashtags": 30,                  # how many, most important first. Platform caps: Instagram 5
                                     # (more blocks the post), YouTube 60 (more and all are
                                     # ignored), TikTok none (captions up to 4,000 characters)
    "credit_creator": True,          # a credit line with the creator's social media @handles
    "creator_socials": {},           # add or correct handles per creator, e.g.
                                     # {"ishowspeed": {"TikTok": "@name"}}; "" removes one

    # output
    "output_dir": None,              # where finished clips go, in date folders, with a
                                     # CLIPS.md index; None = ~/StreamClips
    "video_height": 1080,
    "crf": 21,
    "x264_preset": "fast",
    "loudness": -14,                 # LUFS; None to leave the audio as it is
    "audio_kbps": 192,
}


def load(cli=None):
    cfg = dict(DEFAULTS)
    user = DATA / "settings.json"
    if user.exists():
        data = read_json(user)
        if not isinstance(data, dict):
            raise Problem(f"{user} is not valid JSON")
        unknown = set(data) - set(DEFAULTS)
        if unknown:
            raise Problem(f"{user}: unknown setting(s) {', '.join(sorted(unknown))}")
        cfg.update(data)
    for key, value in (cli or {}).items():
        if value is not None:
            cfg[key] = value
    if cfg["watermark"]:
        mark = Path(str(cfg["watermark"])).expanduser()
        if not mark.is_file():
            raise Problem(f"watermark not found: {mark}. Fix the path in {user}, or set "
                          f"\"watermark\": null to make clips without it.")
        cfg["watermark"] = str(mark)
    cfg["output_dir"] = str(Path(str(cfg["output_dir"])).expanduser()) if cfg["output_dir"] else str(DATA)
    return cfg
