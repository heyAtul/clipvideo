"""Post text for each clip: one description written for a worldwide audience, a credit line with
the creator's social media @handles, then hashtags (most important first). Saved as <clip>.txt
next to the video, ready to paste."""

import json
import re

from . import brains
from .common import Problem, read_json, say, write_json

PROMPT = """You write the post text for a short vertical video clip (Instagram Reels, TikTok, \
YouTube Shorts). The audience is worldwide: many viewers speak English as a second language and \
have never heard of the creator.

Clip title: "<<TITLE>>"
Moment type: <<TYPE>>
From: "<<VIDEO>>" by <<CREATOR>>, streamed on <<SOURCE>>
Topic: <<TOPIC>>
Why it should work: <<WHY>>
What is said in the clip (automatic transcript, may contain mistakes):
<<TRANSCRIPT>>

Write two things.

description: 2-4 short lines in simple, clear English that anyone in the world understands. No \
slang, no in-jokes, no local references. Line 1 is a hook that makes a stranger stop scrolling. \
Say who the creator is in a few words. End with a question anyone, in any country, can answer in \
the comments. Use 1-3 emojis. No hashtags in the description. At most 400 characters.

hashtags: exactly <<N>> different hashtags, ordered from most to least important. Start with \
the ones about this exact clip (what happens, what is found, the type of moment), then the game \
or subject and the creator, then the wider community around them, then broad discovery tags used \
worldwide, and popular tags in other big languages (Spanish, Portuguese, Hindi in Latin letters, \
Arabic, Indonesian...). Every tag must still relate to this clip: no unrelated trending tags, \
because platforms remove videos for misleading hashtags. The same list is used on every platform, so no platform tags (#reels, #shorts, #tiktok, \
#fyp) and no streaming site other than <<SOURCE>>. No spam tags (#followforfollow, #like4like, \
#f4f). No spaces inside a tag.

Reply with only a JSON object, no prose, no markdown fence:
{"description": "...", "hashtags": ["#...", "#..."]}
"""

MAX_CHARS = 4000   # TikTok's caption limit, the longest of the short-video apps


def _fill(**values):
    text = PROMPT
    for key, value in values.items():
        text = text.replace(f"<<{key}>>", str(value))
    return text


def _parse(raw):
    text = (raw or "").strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1).strip()
    a, b = text.find("{"), text.rfind("}")
    if a < 0 or b <= a:
        return None
    try:
        data = json.loads(text[a:b + 1])
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def extra(want):
    """Spare tags to ask for, so the lists stay full after filtering out duplicates and
    platform tags."""
    return max(5, want // 10)

# Platform tags look wrong when one list goes on every platform.
PLATFORM_TAG = re.compile(r"^(reels?|shorts?|youtubeshorts|tiktok\w*|fyp\w*|foryou\w*|"
                          r"explore\w*|insta\w*|reelsinstagram|instareels)$")
SITES = {"YouTube": re.compile(r"youtube|^yt"), "Twitch": re.compile(r"twitch"),
         "Kick": re.compile(r"^kick(stream|clips|live|com)")}


def source_of(url):
    url = str(url or "").lower()
    return next((name for key, name in (("youtu", "YouTube"), ("twitch", "Twitch"), ("kick", "Kick"))
                 if key in url), "a streaming site")


def tags(raw, limit, source=None):
    """Clean hashtags: letters, digits and _ in any script; no duplicates; no platform tags and
    no streaming site other than `source`; at most `limit`."""
    out, seen = [], set()
    for t in raw or []:
        t = re.sub(r"\W", "", str(t))
        low = t.lower()
        if not t or low in seen or PLATFORM_TAG.match(low):
            continue
        if any(rx.search(low) for name, rx in SITES.items() if name != source):
            continue
        seen.add(low)
        out.append("#" + t)
    return out[:limit]


def generate(pick, words, ctx, cfg, cache):
    """{"description", "hashtags"} for one clip: written by the brain, cached in `cache`.
    Falls back to the picker's short caption and hashtags if the brain can't be used."""
    want = int(cfg["hashtags"])
    video = ctx.get("video") or {}
    source = source_of(video.get("url"))
    key = {"title": pick.get("title"), "start": pick.get("start"), "want": want}
    cached = read_json(cache) or {}
    if cached.get("key") == key and cached.get("description"):
        cached["hashtags"] = tags(cached.get("hashtags"), want, source)
        return cached
    fallback = {"key": key, "description": str(pick.get("caption") or "").strip(),
                "hashtags": tags(pick.get("hashtags"), want, source)}
    brain = ctx.get("brain")
    if not brain or brain == "agent":
        return fallback
    prompt = _fill(TITLE=pick.get("title") or "", TYPE=pick.get("type") or "moment", SOURCE=source,
                   VIDEO=video.get("title") or "", CREATOR=video.get("name") or "the creator",
                   TOPIC=video.get("topic") or "", WHY=pick.get("why") or "",
                   TRANSCRIPT=" ".join(w["w"] for w in words)[:1500] or "(no speech)",
                   N=want + extra(want))
    try:
        data = _parse(brains.ask(brain, prompt, ctx.get("model"), cache.parent))
    except Problem as exc:
        say(f"  description: {str(exc)[:120]}; using the short caption instead", "warn")
        return fallback
    if not data or not str(data.get("description") or "").strip():
        say("  description: no usable answer; using the short caption instead", "warn")
        return fallback
    out = {"key": key, "description": str(data["description"]).strip(),
           "hashtags": tags(data.get("hashtags"), want, source) or fallback["hashtags"]}
    write_json(cache, out)
    return out


# Social links the creator lists in the stream's description: (platform, pattern, not a handle)
SOCIAL_LINKS = (
    ("Instagram", r"instagram\.com/([A-Za-z0-9_.]+)",
     {"p", "reel", "reels", "stories", "explore", "accounts", "tv", "share"}),
    ("TikTok", r"tiktok\.com/@([A-Za-z0-9_.]+)", set()),
    ("X", r"(?:twitter|x)\.com/([A-Za-z0-9_]+)", {"intent", "i", "home", "share", "hashtag", "search"}),
    ("Twitch", r"twitch\.tv/([A-Za-z0-9_]+)", {"videos", "directory", "p", "subs"}),
    ("Kick", r"kick\.com/([A-Za-z0-9_]+)", {"video", "videos", "categories"}),
    ("Threads", r"threads\.net/@([A-Za-z0-9_.]+)", set()),
    ("YouTube", r"youtube\.com/@([A-Za-z0-9_.-]+)", set()),
)
ORDER = ("YouTube", "Instagram", "TikTok", "X", "Twitch", "Kick", "Threads")


def socials(meta, cfg):
    """The creator's social media @handles, as [[platform, "@handle"], ...]. The platform the
    stream is on comes from its metadata; the others from links in the stream's description
    (the first one per platform, so secondary channels further down are skipped). Settings
    "creator_socials" adds or corrects handles: {"<creator name>": {"TikTok": "@name"}}, and
    an empty value removes one."""
    found = {}
    url = str(meta.get("webpage_url") or "").lower()
    uid = str(meta.get("uploader_id") or "")
    if "youtu" in url and uid.startswith("@"):
        found["YouTube"] = uid
    elif "twitch.tv" in url and uid:
        found["Twitch"] = "@" + uid.lstrip("@")
    elif "kick.com" in url:
        m = re.search(r"kick\.com/([a-z0-9_]+)", url)
        if m and m.group(1) not in ("video", "videos"):
            found["Kick"] = "@" + m.group(1)
    text = str(meta.get("description") or "")
    for platform, pattern, skip in SOCIAL_LINKS:
        if platform in found:
            continue
        for m in re.finditer(pattern, text, re.I):
            handle = m.group(1).rstrip(".")
            if handle and handle.lower() not in skip:
                found[platform] = "@" + handle
                break
    name = str(meta.get("name") or meta.get("channel") or meta.get("uploader") or "").lower()
    for platform, handle in ((cfg.get("creator_socials") or {}).get(name) or {}).items():
        if handle:
            found[platform] = "@" + str(handle).lstrip("@")
        else:
            found.pop(platform, None)
    return [[p, found[p]] for p in ORDER if p in found] + \
           [[p, h] for p, h in found.items() if p not in ORDER]


def credit(video, cfg):
    """One line crediting the creator, with their @handles. Empty when there are none or
    "credit_creator" is off."""
    handles = (video or {}).get("socials") or []
    if not cfg.get("credit_creator", True) or not handles:
        return ""
    return f"🎥 Credit: {video.get('name') or 'the creator'} · " + " · ".join(
        f"{platform} {handle}" for platform, handle in handles)


def write(path, record, cfg, video=None):
    """Write <clip>.txt: the description, the credit line with the creator's @handles, then
    the hashtags (most important first), separated by blank lines. Nothing else, so the
    whole file can be pasted as is. Returns the text."""
    head = "\n\n".join(part for part in (record["description"], credit(video, cfg)) if part)
    chosen = record["hashtags_all"][:int(cfg["hashtags"])]
    body = (head + "\n\n" + " ".join(chosen)).strip()
    while len(body) > MAX_CHARS and chosen:
        chosen = chosen[:-1]
        body = (head + "\n\n" + " ".join(chosen)).strip()
    path.write_text(body + "\n", encoding="utf-8")
    return body
