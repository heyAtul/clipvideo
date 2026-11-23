---
name: stream-clips
description: Turns long livestreams and videos into ready-to-post vertical clips (TikTok, Reels, YouTube Shorts) on any topic or game (GTA 6, Valorant, Fortnite, Minecraft, chess, podcasts...). Finds the biggest recent streams for a topic, listens to the whole stream locally (Whisper), marks where the streamer got loud and where chat exploded, has an AI pick the moments that will go viral, then cuts 9:16 clips with the facecam on top and gameplay below, a title bar, word-by-word captions, and a POSTING.md with a caption and hashtags per clip. Free and local, no API keys; works on macOS and Windows from Claude Code, Codex, Gemini CLI or OpenCode. Use when someone wants to clip streams or streamers, make Shorts/TikToks from a VOD or long video, run a clipping side hustle or clipping campaign, or says "clip this stream", "find the best moments", "make clips of <streamer>'s <game> stream".
---

# Stream Clips

Long streams in, vertical clips out. **You run everything; the user only gives a topic or links.**

**This user's standing instructions:** before making or changing clips, read `~/Desktop/Stream Clips Kit/VIDEO-INSTRUCTIONS.md` and follow every rule in it. When the user gives a new instruction about the videos, add it to that file: their words, the date, and the setting that does it. Mark replaced instructions as replaced; never delete them.

`SKILL_DIR` = the folder this file is in. Every command is:

- macOS / Linux: `python3 "SKILL_DIR/scripts/streamclips.py" <command> ...`
- Windows: `python "SKILL_DIR\scripts\streamclips.py" <command> ...` (or `py` if `python` is missing)

Below, `streamclips` is short for that.

Clips are saved in `<output>/<date>/<topic>/<creator>__<title>/`. `<output>` is the `output_dir` setting if it is set (check `~/StreamClips/settings.json`), otherwise `~/StreamClips` (Windows: `C:\Users\<name>\StreamClips`). After every run, `<output>/CLIPS.md` is rebuilt: it lists every clip by date, newest first. The cache, settings.json and the watchlist always stay in `~/StreamClips`.

## 0. First time on a computer

1. Run `streamclips setup` and wait for **READY**. It checks for ffmpeg (and that it can draw captions), a JavaScript runtime (deno or node; YouTube downloads need one) and disk space. It then builds a private Python environment in `~/.streamclips`, installs Whisper, OpenCV, Pillow and yt-dlp, and downloads two Whisper models (~220 MB) and a face model (0.2 MB).
2. If something is MISSING, install it the official way, then open a new terminal and run setup again. Ask the user before anything that needs an admin password.
   - macOS: `brew install ffmpeg-full deno`, then `brew link --force ffmpeg-full` (Homebrew doesn't put it on the PATH by itself).
     Don't use the plain `ffmpeg` formula: it's built without libass, so every clip fails at the caption step. If plain `ffmpeg` is already installed, run `brew unlink ffmpeg` before linking. Don't `brew uninstall` it: Homebrew then also removes other packages it thinks are unused.
   - Windows: `winget install Gyan.FFmpeg` and `winget install DenoLand.Deno`
3. `streamclips doctor` checks the install at any time.

## 1. What happens to each stream

1. **Audio only.** The stream's full audio is downloaded (a 4-hour stream is about 250 MB). The video isn't downloaded yet.
2. **Listen (local, free).**
   - Whisper `tiny` transcribes everything, in 10-minute blocks that are cached.
   - The volume of every second is measured. Shouting and laughing show up as spikes.
   - On YouTube replays, the chat replay shows how fast chat was moving.
3. **Pick.** The transcript is split into 10-minute parts and each part is marked with `<<VOLUME +N dB>>` and `<<CHAT Nx>>`. An AI reads every part and returns the strongest moments: `reaction`, `skill`, `funny`, `reveal`, `take`, `tip` and `story`. Each comes with a title bar, a caption, hashtags and a 1-100 score. The cut points are snapped to clean word boundaries, and the best N per stream are kept.
4. **Make each clip.**
   - Only that clip's video is downloaded (up to 1080p).
   - It's synced to the stream audio by matching the sound.
   - Captions are re-transcribed with Whisper `base` and shown word by word.
   - The frame becomes 9:16, with the look chosen automatically:
     - **stack**: facecam on top, gameplay below (a small face in a corner)
     - **crop**: follows the face (podcast, just chatting, IRL)
     - **blur**: the whole frame over a blurred copy of itself (no face)
     - **reel** (with `--layout reel`, or `"layout": "reel"` in settings.json; this user has it as the default since 2026-11-24, and `--layout auto` gives the stacked look for one run): the whole 16:9 gameplay, never cropped, in the middle of a branded frame. The top has the mascot, "LET'S GO!" and the facecam in a glowing frame; the bottom has brush strokes, claw marks and a faint mascot. Captions go just under the gameplay. The subscribe banner (play button, SUBSCRIBE, bell) appears only with `"reel_subscribe": true`. Leave it off unless the user asks for it. This look has no title bar and no watermark. Its art is separate PNG layers in `~/StreamClips/brand/reel/`, generated from the `reel_*` settings; a layer edited by hand is kept, and deleting one regenerates it. The code is in `scripts/sc/reel.py`.
   - The title bar is added (not in the reel look) and the audio is levelled to -14 LUFS.
5. **Files written:**
   - `<clip>.txt` next to each video: the text to paste and nothing else. It holds one description written for a worldwide audience, a credit line with the creator's social media @handles, then `hashtags` hashtags (default 30), most important first, separated by blank lines. The handles come from the stream's metadata (the platform's own handle) and the social links in its description; `creator_socials` in settings adds or corrects them, and `credit_creator: false` drops the line. The same text is used on every platform. Platform caps to tell the user about: Instagram 5 (more blocks the post), YouTube 60 (more and all of them are ignored), TikTok none (captions up to 4,000 characters). Every tag must relate to the clip, since misleading hashtags can get a video removed. The brain writes it from the clip's transcript, with one call per clip, cached. With `--brain agent`, or if that call fails, it falls back to the picker's short caption and hashtags.
   - `POSTING.md`: every clip's description, why each clip should work, and where it is in the stream
   - `clips.json`
   - `checks/<clip>.jpg`: 3 frames from each clip, for a quick look

## 2. Who picks the moments (`--brain`)

The default `--brain auto` uses the AI CLI that is running this skill, falling back to any one installed. It runs on the user's own subscription; there are no API keys.

| You are running in | Use |
|---|---|
| Claude Code | `--brain claude` (calls `claude -p`) |
| Codex (ChatGPT) | `--brain codex` (calls `codex exec`) |
| Gemini CLI | `--brain gemini` (calls `gemini -p`) |
| OpenCode | `--brain opencode` (calls `opencode run`) |
| Anything else, or a nested call fails | `--brain agent`: you pick the moments yourself |

Add `--model <name>` to choose a model for that CLI, for example `--model sonnet` on Claude Code to use less of the subscription.

**Agent mode** (`--brain agent`). The command stops with exit code 3 after listening, and prints a list of `part_XXXXXX.prompt.txt` files, each with its `.answer.json` path.

1. Read each prompt file and follow its instructions.
2. Write only the JSON array to the matching answer file. `[]` is a valid answer.
3. Run the exact same command again. It continues from where it stopped and makes the clips.

If there are many parts, answer them in batches and re-run. Parts that already have answers are skipped.

## 3. Run it

Run long jobs in the background. Tell the user in plain words what is happening: downloading, listening, picking, making clips.

```
streamclips find --topic "Valorant"                              # biggest Valorant streams today
streamclips find --topic "GTA 6" --keywords "gta 6,gta vi,gta6"  # better title matching
streamclips clip URL --topic "GTA 6"                             # one stream, 3 clips
streamclips clip URL URL URL --topic "Fortnite" --clips 4        # several streams, 2 at a time
streamclips clip --find --topic "GTA 6" --count 7                # find + clip (~21 clips)
streamclips clip URL --topic "chess" --section "1:00:00-2:30:00" # only part of a long stream
streamclips clip URL --topic "GTA 6" --new-only                  # live stream: only what's new
```

**Always pass `--topic`.** It steers both the search and the picking.

- **Keywords:** choose `--keywords` with the spellings people really use in titles. For example GTA 6 → `gta 6,gta vi,gta6`, and League of Legends → `league,lol`.
- **Focus:** use `--focus "..."` for extra direction, for example `--focus "clutch 1v5s and rage moments"` or `--focus "tips beginners can use"`.

| flag | what it does |
|---|---|
| `--clips N` | clips per stream (default 3) |
| `--count N` | with `--find`: how many streams |
| `--when hour/today/week/month` | search window (default today) |
| `--search "words"` | exact YouTube search instead of "<topic> stream" |
| `--parallel N` | streams processed at the same time (default 2) |
| `--section A-B` | only that part, `h:mm:ss-h:mm:ss` |
| `--new-only` | continue from where the last run on this stream ended |
| `--cookies chrome` | use the browser login: age-restricted YouTube, Kick, sub-only Twitch VODs |
| `--layout stack/crop/blur` | force one look (default auto) |
| `--cam x,y,w,h` | facecam box as fractions of the frame, if auto framing gets it wrong |
| `--min / --max` | clip length limits in seconds (default 15-59) |
| `--language en` | skip language detection |
| `--fast` | hardware video encoding (Apple, NVIDIA, Intel or AMD) when available |
| `--repick` | pick moments again; keeps the downloads |
| `--keep-audio` | keep the stream audio afterwards (it's deleted by default) |

Re-running the same command resumes. Finished steps are cached in `~/StreamClips/.cache/`.

**Language.** By default, the language is detected separately for each 10-minute block and
each clip, so streamers who switch languages are handled.

- **Hinglish** (Hindi mixed with English): add `--language en`. Captions then come out in Roman letters, the way Indian Shorts are usually captioned. Pure Hindi in Devanagari: `--language hi`.
- **Garbled transcript:** if the transcript in a prompt file looks garbled, the scan model is too small for that language. Set `"scan_model": "base"` in settings.json. It's about 2× slower but much more accurate for non-English speech.

## 4. Finding streams

`find` uses no keys and checks two sources:

- **YouTube search:** long videos for "<topic> stream" from the chosen window, sorted by views.
- **The watchlist** (`~/StreamClips/watchlist.txt`): lines like `twitch:<login>`, `youtube:@handle` or `kick:<name>`, optionally `| <topic>`. Each creator's newest video with a matching title, from the last 48 hours, is used.

Help the user fill the watchlist with the creators they clip for. That's how Twitch and Kick streams get in.

## 5. After the clips are made: check them

Before you report back, look at `checks/*.jpg` for each clip if you can view images. Otherwise, extract a frame with ffmpeg. Confirm:

- the face is visible in the top panel (stack look) or in the facecam frame (reel look)
- the title is readable and names the right person (stack look; the reel look has no title bar)
- reel look: the whole gameplay is in the middle band, with nothing cropped
- the captions are inside the frame
- if a watermark is set: it is visible, and it doesn't cover the title, the captions or the face

If a facecam crop is wrong, re-run with `--cam x,y,w,h` (fractions of the 16:9 frame; e.g. a top-right cam ≈ `0.72,0.0,0.28,0.3`). Tell the user which clips look strongest, using the scores and the `why` lines.

**Never post for the user.** They post. `POSTING.md` has the caption for each clip. Remind them to:

- watch each clip before posting
- only clip creators who allow it (many big streamers run paid clipping programs)
- post fast, since a clip gets most of its views in its first hours

Settings live in `~/StreamClips/settings.json`, using any key from `scripts/sc/settings.py`, for example `{"cap_active": "00E5FF", "cam_share": 0.45, "clips": 4}`.

**Watermark (the user's logo on every clip).** Set `"watermark": "<path to a PNG>"` in settings.json. The logo is drawn under the title and captions, centred across the frame and centred in the free space between the title bar and the captions. It can't be cropped off without cutting into the clip, and it never covers the title or captions. Tune it with `watermark_opacity` (default 0.30), `watermark_width` (share of the frame width, default 0.36; it shrinks to fit) and `watermark_y` (the centre as a share of the height, to place it yourself).

- The PNG needs a transparent background. If the user's logo sits on a solid colour (a JPG on black, for example), cut the background out first, or it shows as a faint box.
- To add the watermark to clips that were already made, run the same `clip` command again. The picks are cached, so only the clips are made again.

## 6. Problems

- **"YouTube needs a login" / "not a bot" / Kick 403 / sub-only VOD** → add `--cookies chrome` (or the browser the user is signed into).
- **Every clip fails with `No option name near '….ass'`**, or setup says ffmpeg **can't draw captions** → that ffmpeg has no libass. macOS: `brew install ffmpeg-full`, `brew unlink ffmpeg`, `brew link --force ffmpeg-full`. Then run the same command again: the picks are cached, so only the clips are made again.
- **"weak sound match"** on a clip → it may be ~1 s off. Check that clip, or `--repick`.
- **The picker CLI fails inside another agent's sandbox** (common in Codex) → `--brain agent`.
- **"nothing strong enough"** → a low-energy stream. Try another stream, a `--focus`, or `"min_score": 25` in settings.json.
- **Slow listening** → about 1-3 minutes per stream hour, depending on the CPU. Use `--section` for long streams.
- **Disk** → about 0.1 GB per stream hour while working. The audio is deleted after the clips are made.
