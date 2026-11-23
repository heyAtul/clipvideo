"""Everything that happens to one stream, start to finish."""

import datetime
import hashlib
import os
import threading
from pathlib import Path

from . import describe, highlights, listen, media, produce
from .common import CACHE, Stopwatch, clock, human, parse_clock, probe, read_json, say, slug, tag, write_json

_index_lock = threading.Lock()


def work_dir(url):
    key = hashlib.sha1(url.strip().encode()).hexdigest()[:10]
    tail = slug(url.split("://")[-1], 40)
    path = CACHE / f"{tail}_{key}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def section_bounds(opts, total, work):
    lo, hi = 0.0, total
    if opts.section:
        a, _, b = opts.section.replace(" ", "").lstrip("*").partition("-")
        lo = parse_clock(a) if a else 0.0
        hi = min(parse_clock(b), total) if b else total
    elif opts.new_only:
        done = (read_json(work / "progress.json") or {}).get("done_until", 0.0)
        lo = max(0.0, done - 60)
    if hi - lo < 60:
        raise RuntimeError(f"nothing new to clip ({clock(lo)}-{clock(hi)} is under a minute)")
    return lo, hi


def process(url, opts, cfg):
    watch = Stopwatch()
    args = media.ytdlp_args(url, opts.cookies)
    work = work_dir(url)
    with watch.lap("look up"):
        meta = media.metadata(url, args, work)
    tag(meta["name"][:18])
    live = meta.get("live_status") == "is_live"
    if live:
        say("this stream is live: clipping what has been streamed so far", "warn")

    with watch.lap("download audio"):
        audio = media.audio(url, args, work, live=live)
    total = probe(audio)["duration"] or float(meta.get("duration") or 0)
    lo, hi = section_bounds(opts, total, work)
    say(f"{meta['title'][:70]}  ({human(total)}"
        + (f", clipping {clock(lo)}-{clock(hi)})" if (lo, hi) != (0.0, total) else ")"), "good")

    with watch.lap("listen"):
        heard = listen.scan(audio, total, lo, hi, work, cfg, live=live)
        spike_db = listen.spikes(heard["volume"])
        chat = listen.chat_speed(url, args, work, meta, cfg)

    video = {"title": meta["title"], "name": meta["name"], "url": url,
             "topic": opts.topic or "this video", "focus": opts.focus,
             "socials": describe.socials(meta, cfg)}
    with watch.lap("pick"):
        picks = highlights.pick(heard, spike_db, chat, lo, hi, work, cfg, video,
                                opts.brain_resolved, opts.model, redo=opts.repick)

    day = datetime.date.today().isoformat()
    root = Path(cfg["output_dir"])
    outdir = (root / day / slug(opts.topic or "clips", 30)
              / f"{slug(meta['name'], 24)}__{slug(meta['title'], 40)}")
    memory = read_json(work / "cam.json", {}) or {}
    ctx = {"url": url, "args": args, "audio": audio, "work": work, "outdir": outdir,
           "language": cfg["language"], "fast": opts.fast, "cam": opts.cam_box,
           "video": video, "brain": opts.brain_resolved, "model": opts.model}
    made = []
    with watch.lap("make clips"):
        for i, pick in enumerate(picks, 1):
            try:
                made.append(produce.make(i, pick, ctx, cfg, memory))
            except Exception as exc:  # noqa: BLE001 - one bad clip must not stop the rest
                say(f"clip {i} failed: {str(exc)[:300]}", "bad")
    write_json(work / "cam.json", memory)

    summary = (f"{human(hi - lo)} of stream -> {len(made)} clip(s) in {human(watch.total())} ("
               + ", ".join(f"{k} {human(v)}" for k, v in watch.parts.items()) + ")")
    if made:
        posting_sheet(outdir, video, made, summary, lo, hi)
        write_index(root)
        write_json(work / "progress.json", {"done_until": hi, "at": datetime.datetime.now().isoformat()})
        if not opts.keep_audio and not live:
            audio.unlink(missing_ok=True)
    say(summary, "good")
    tag("")
    return {"name": meta["name"], "title": meta["title"], "outdir": outdir, "clips": made,
            "summary": summary}


def posting_sheet(outdir, video, clips, summary, lo, hi):
    lines = [f"# {video['name']}: {video['title']}", "",
             f"Source: {video['url']}  ",
             f"Covered: {clock(lo)} to {clock(hi)}  ",
             summary, "",
             "Watch every clip before posting. Only clip creators who allow it "
             "(many run paid clipping programs).", ""]
    for c in clips:
        lines += [f"## {c['file']}", "",
                  f"**{c['title'] or ''}**  ",
                  f"{c['type']} · {c['seconds']:.0f}s · score {c['score']} · from {clock(c['start'])} "
                  f"· look: {c['look']}", "",
                  "Description to paste:", "", "```",
                  c["post"] if isinstance(c.get("post"), str)
                  else (c.get("caption") or "") + "\n" + " ".join(c.get("hashtags") or []), "```", ""]
        if c.get("post_text"):
            lines += [f"The same text is in [{c['post_text']}]({c['post_text']}), next to the video.", ""]
        lines += [f"_Why it should work: {c.get('why') or ''}_", "", "---", ""]
    (outdir / "POSTING.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(outdir / "clips.json", {"source": video, "covered": [lo, hi], "clips": clips})


def write_index(root):
    """CLIPS.md in the output folder: every clip made so far, by date, newest first.
    Rebuilt from each stream folder's clips.json, so it stays right if folders are deleted."""
    root = Path(root)

    def cell(text):
        return str(text or "").replace("|", "\\|").replace("\n", " ")

    with _index_lock:
        days = {}
        for sheet in sorted(root.glob("*/*/*/clips.json")):
            data = read_json(sheet)
            if not isinstance(data, dict) or not data.get("clips"):
                continue
            days.setdefault(sheet.parts[-4], []).append((sheet.parent, data))
        total = sum(len(d["clips"]) for streams in days.values() for _, d in streams)
        lines = ["# Clips", "",
                 f"{total} clip(s) from {sum(len(s) for s in days.values())} stream(s), newest first. "
                 "This file is rebuilt after every run. Each clip has a description file next to "
                 "it (the .txt): the description and hashtags, ready to paste.", ""]
        for day in sorted(days, reverse=True):
            lines += [f"## {day}", ""]
            for folder, data in days[day]:
                src = data.get("source") or {}
                rel = folder.relative_to(root).as_posix()
                lines += [f"### {cell(src.get('name'))}: {cell(src.get('title'))}", "",
                          f"Topic: {cell(src.get('topic'))} · [source video]({src.get('url', '')}) · "
                          f"[POSTING.md]({rel}/POSTING.md)", "",
                          "| Clip | Description | Title | Type | Length | Score | From |",
                          "|---|---|---|---|---|---|---|"]
                for c in data["clips"]:
                    desc = f"[{cell(c['post_text'])}]({rel}/{c['post_text']})" if c.get("post_text") else ""
                    lines.append(f"| [{cell(c.get('file'))}]({rel}/{c.get('file')}) | {desc} "
                                 f"| {cell(c.get('title'))} | {cell(c.get('type'))} "
                                 f"| {c.get('seconds', 0):.0f}s | {c.get('score', '')} "
                                 f"| {clock(c.get('start', 0))} |")
                lines.append("")
        tmp = root / "CLIPS.md.tmp"
        tmp.write_text("\n".join(lines), encoding="utf-8")
        os.replace(tmp, root / "CLIPS.md")
