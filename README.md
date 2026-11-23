# Stream Clips Kit

Everything for making vertical clips with your logo on them: the finished clips, the clipping
skill, your logo and layout, and how it all works.

Start here:
- [VIDEO-INSTRUCTIONS.md](VIDEO-INSTRUCTIONS.md): every instruction you've given about the
  videos, in your words, plus the searches run and the clips made so far.
- This README: how to find streams, make clips, find the skill, and change things.
- [Clips/CLIPS.md](Clips/CLIPS.md): every clip by date, with links.
- [Layout/REEL-LAYOUT-SPEC.md](Layout/REEL-LAYOUT-SPEC.md): your design brief for the reel layout.

## What's in this folder

| Folder / file | What it is |
|---|---|
| `README.md` | This guide. |
| `VIDEO-INSTRUCTIONS.md` | Every instruction you've given about the videos, in your words, with what's set up and where. |
| `Clips/` | Your finished clips, in date folders: `Clips/<date>/<topic>/<streamer>__<stream title>/`. New clips are saved here automatically. |
| `Clips/CLIPS.md` | Every clip by date, newest first, with links to the videos and descriptions. It's rebuilt after every run. |
| `Logo/logo_original.jpg` | Your logo, as you supplied it. |
| `Logo/logo_watermark.png` | The same logo with the black background removed. The watermark and the reel layout use this version. |
| `Logo/opacity-comparison-20-30-40.jpg` | One frame at 20%, 30% and 40% opacity, for comparison. |
| `Logo/watermark-demo-270px-30pct.jpg`, `Logo/watermark-demo-184px-40pct.jpg` | Earlier logo-size demos, in the middle position. |
| `Logo/watermark-test-top-centre.jpg` | The test of the current logo position, top centre. |
| `Layout/REEL-LAYOUT-SPEC.md` | Your design brief for the landscape gameplay layout, with the reference image. |
| `Layout/reference-design.png` | The reference design. |
| `Layout/reel-demo.jpg` | A test of the layout on two of the clips. |
| `Layout/reel-demo-with-subscribe.jpg` | The same test with the subscribe banner on (it's off for now). |
| `Skill/stream-clips/` | A copy of the clipping skill, with every change made for this setup. |
| `Skill/stream-clips-patched.zip` | The same skill as a zip, for installing it again or on another computer. |
| `Skill/changes.patch` | Every change made to the original skill, line by line. |
| `Skill/settings.json` | A backup copy of your settings. |
| `Tools/make_watermark.py` | Cuts the background out of a logo. |

Each stream folder inside `Clips/` holds:
- the `.mp4` clips
- one `.txt` per clip, with the same name as the video: the description and hashtags to paste
  (see [Descriptions and hashtags](#descriptions-and-hashtags))
- `POSTING.md`, with every clip's description in one place
- `clips.json`, the same details in a machine-readable form
- `checks/`, with 3 frames from each clip for a quick look

## Where everything is

Some of what the skill uses lives outside this folder:

| What | Where |
|---|---|
| The skill Claude Code uses | `~/.claude/skills/stream-clips/` |
| A copy of it, with all the changes | `Skill/` in this folder |
| The original download | `~/Downloads/stream-clips.zip`. It doesn't have this setup's changes, so don't reinstall from it. |
| Your settings | `~/StreamClips/settings.json` |
| Your watchlist of creators | `~/StreamClips/watchlist.txt` (empty so far) |
| The logo in use | `~/StreamClips/brand/logo_watermark.png` |
| The reel layout's art layers | `~/StreamClips/brand/reel/` |
| The graffiti font | `~/StreamClips/brand/fonts/PermanentMarker-Regular.ttf` |
| Working files (audio, transcripts, picked moments) | `~/StreamClips/.cache/`, a hidden folder. The stream audio is deleted after each run. |
| The skill's Python and speech models | `~/.streamclips/` (Python 3.12, the Whisper models and a face model) |
| ffmpeg | Homebrew's `ffmpeg-full` |

### Finding the skill

Claude Code loads skills from `~/.claude/skills/` on its own; this one is called
`stream-clips`. You don't open it: ask in plain words, and Claude Code uses it whenever the
request is about clipping streams. For example:
- "Find today's biggest GTA 6 streams"
- "Clip this stream: <link>"
- "Make 3 clips from the last 2 hours of this live stream: <link>"
- "Find the best moments in <streamer>'s <game> stream"

To check that it's installed and working, run:

```
python3 ~/.claude/skills/stream-clips/scripts/streamclips.py doctor
```

Every line should say ok. If the skill is missing, install it again from
`Skill/stream-clips-patched.zip` (see [Setting up on another Mac](#setting-up-on-another-mac)).

## Finding streams to clip

Ask Claude Code, for example "Find today's biggest GTA 6 streams", or run:

```
python3 ~/.claude/skills/stream-clips/scripts/streamclips.py find --topic "GTA 6" --keywords "gta 6,gta vi,gta6"
```

The search uses no accounts or API keys. It looks in two places:
1. **YouTube:** a search for "<topic> stream", limited to videos over 20 minutes long from the
   chosen time window, sorted by views.
2. **Your watchlist** (`~/StreamClips/watchlist.txt`): each creator's newest video from the last
   48 hours whose title matches the topic. This is how Twitch and Kick streams get in.

It lists the biggest streams first, at most one per creator, and only those whose title contains
the topic or one of the keywords.

| Option | What it does |
|---|---|
| `--topic "GTA 6"` | What to look for. Always set it. |
| `--keywords "gta 6,gta vi,gta6"` | The spellings a title can contain (default: just the topic). |
| `--when hour`, `today`, `week` or `month` | The search window (default: today). |
| `--count 8` | How many streams to list (default: 8). |
| `--search "words"` | Exact YouTube search words, instead of "<topic> stream". |
| `--cookies chrome` | Uses your browser's login, for age-restricted YouTube videos, Kick and subscriber-only Twitch videos. |

**The watchlist** has one creator per line. Add `| topic` to check a creator only for that topic:

```
twitch:tarik
youtube:@IShowSpeed | gta 6
kick:<name>
```

**Find and clip in one go:** `clip --find --topic "GTA 6" --count 3` finds the 3 biggest streams
and makes 3 clips from each.

The searches run so far, with their results, are in
[VIDEO-INSTRUCTIONS.md](VIDEO-INSTRUCTIONS.md#searches-run-so-far).

## Making clips

Ask Claude Code, for example "Clip this stream: <link>", or run:

```
python3 ~/.claude/skills/stream-clips/scripts/streamclips.py clip <link> --topic "GTA 6" --clips 3
```

Every clip is made in the reel layout (your default), with its own description file, and is
saved in `Clips/` under today's date.

| Option | What it does |
|---|---|
| `--clips 3` | Clips per stream (default: 3). |
| `--focus "funniest moments"` | Extra direction for picking the moments. |
| `--section 1:00:00-2:30:00` | Only that part of the stream; faster for long streams. |
| `--new-only` | For a live stream: only what's new since the last run. |
| `--layout auto` | The old stacked look for this run, instead of the reel layout. |
| `--language en` | Skips language detection; good for English streams. |

Before posting:
- Watch each clip all the way through.
- Make sure the creator allows clipping.
- Post soon: clips get most of their views in the first hours.

## The logo watermark

### Where it goes

**Current setting (chosen on 2026-11-23): top centre, 184 px, 50% opacity.**

This watermark is for the stacked layout. The reel layout, your default since 2026-11-24, shows
your mascot as part of its branding instead, so it doesn't add this watermark.

```
┌──────────────────────────┐
│         ( LOGO )         │  <- top centre, 50% opacity
│      facecam (top 40%)   │
│                          │
├─────[  TITLE BAR  ]──────┤
│                          │
│       CAPTION TEXT       │  <- captions sit at 70% of the height
│                          │
│         gameplay         │
└──────────────────────────┘
```

| | Value | Setting |
|---|---|---|
| Position | Top centre of the frame, about 23 px from the top edge | `"watermark_y": 0.06` |
| Size | 184 px wide, 17% of the 1080 px frame width | `"watermark_width": 0.17` |
| Opacity | 50% | `"watermark_opacity": 0.50` |
| Layering | Drawn under the title and the captions, so it never covers them | (always) |

Things to know about the top-centre spot:
- **It can overlap the streamer's head.** Where it lands depends on how high the streamer sits in
  the camera. In the test, it cleared Speed's head in clip 1 and covered the top of his hair in
  clip 2.
- **It's easier to crop off.** Someone could cut a strip of about 210 px off the top to remove it,
  losing only the top of the facecam.

If either becomes a problem, there are two alternatives:

| Option | Change in settings.json | Result |
|---|---|---|
| Middle of the gameplay (the most crop-proof) | delete the `watermark_y` line | Centred between the title bar and the captions. Never covers the face, and cropping it out ruins the clip. |
| Top centre, smaller | `"watermark_width": 0.12` | About 130 px. Overlaps the streamer's head less, but it's small. |

The test images are in `Logo/`: `watermark-test-top-centre.jpg` (the current position), plus
`watermark-demo-184px-40pct.jpg` and `watermark-demo-270px-30pct.jpg` (earlier tries, in the
middle position).

### Changing it

Your settings are in `~/StreamClips/settings.json`. Edit that file, not the backup in `Skill/`:

```json
{
  "layout": "reel",
  "watermark": "~/StreamClips/brand/logo_watermark.png",
  "watermark_opacity": 0.50,
  "watermark_width": 0.17,
  "watermark_y": 0.06,
  "hashtags": 100,
  "output_dir": "~/Desktop/Stream Clips Kit/Clips"
}
```

| Setting | Default | What it does |
|---|---|---|
| `layout` | `auto` (yours: `reel`) | The look of every clip. `auto` is the stacked look (facecam on top, cropped gameplay below). |
| `watermark` | off | The path to the logo PNG. Set it to `null` to turn the watermark off. |
| `watermark_opacity` | `0.30` (yours: `0.50`) | 0 is invisible and 1 is solid. Try 0.2 for subtle or 0.5 for strong. |
| `watermark_width` | `0.36` (yours: `0.17`) | The size, as a share of the frame width. The logo shrinks automatically if it would touch the title or the captions. |
| `watermark_y` | automatic (yours: `0.06`, top centre) | The vertical centre, as a share of the height (`0.5` is the exact middle). Leave it out to place the logo automatically in the middle of the gameplay. |
| `output_dir` | `~/StreamClips` | Where finished clips are saved. |
| `hashtags` | `30` (yours: `100`) | How many hashtags go in each clip's description, most important first. |
| `credit_creator` | `true` | Adds a credit line with the creator's social media @handles. |
| `creator_socials` | none | Adds or corrects a creator's handles, for example `{"ishowspeed": {"TikTok": "@name"}}`. An empty value removes one. |

To apply a change to clips you've already made, run the same `clip` command again. The picked
moments are cached, so only the videos are made again (about 5 minutes for 3 clips). The new
versions replace the old ones.

The logo the skill actually uses is `~/StreamClips/brand/logo_watermark.png`. The copy in `Logo/`
is a backup.

### Using a different logo

1. **If it's a PNG with a transparent background:** copy it to `~/StreamClips/brand/` and point
   `"watermark"` at it.
2. **If it's on a solid background** (like the original JPG on black): cut the background out
   first with the tool, then point `"watermark"` at the new PNG.

   ```
   ~/.streamclips/venv/bin/python ~/Desktop/"Stream Clips Kit"/Tools/make_watermark.py new-logo.jpg ~/StreamClips/brand/new-logo-watermark.png
   ```

   The tool is made for round badge logos with an orange ring on black, like yours. Everything
   inside the ring stays solid, and outside the ring only the bright parts stay. For any other
   logo, it removes the dark background by brightness, which also makes dark parts of the logo
   see-through. For those, a background-remover app or a transparent PNG from the designer gives
   a better result.
3. **Check it:** open the PNG in Preview. There should be no box around the logo.

## Landscape gameplay layout (reel)

The design brief is in [Layout/REEL-LAYOUT-SPEC.md](Layout/REEL-LAYOUT-SPEC.md), with the
reference image. The gameplay stays whole, in landscape, in the middle of a branded 9:16 frame.
A test on two of the clips is in [Layout/reel-demo.jpg](Layout/reel-demo.jpg).

| Section | Pixels (of 1080 × 1920) | What's in it |
|---|---|---|
| Top | 0–520 (27%) | Your mascot with orange brush arcs; "LET'S GO!"; the facecam in a glowing orange frame (top right) |
| Middle | 520–1128 (32%) | The full gameplay frame, 1080 × 608, never cropped, stretched or zoomed, with torn-paper edges |
| Bottom | 1128–1920 (41%) | The word-by-word captions; brush strokes, claw marks and a faint oversized mascot |

Motion: the glow around the facecam frame pulses.

**The subscribe banner is off.** That's the red play button, SUBSCRIBE and the bell from the
brief. To turn it on, add `"reel_subscribe": true` to `~/StreamClips/settings.json`; the bell
then swings every 3 seconds. To see how it looks, open
[Layout/reel-demo-with-subscribe.jpg](Layout/reel-demo-with-subscribe.jpg).

### Using it

**The reel layout is your default** (since 2026-11-24): `"layout": "reel"` is in
`~/StreamClips/settings.json`, so every new clip uses it.
- For the old stacked look on one run, add `--layout auto` to the `clip` command.
- To make the stacked look the default again, remove the `"layout"` line from settings.json.

The reel look has no title bar and no watermark, because the branding takes their place.

### Editing it

Every graphic is its own PNG in `~/StreamClips/brand/reel/`:

| Layer | What it is |
|---|---|
| `texture.png` | The dark grunge background |
| `top.png` | Brush strokes, the mascot, LET'S GO! |
| `bottom.png` | Brush strokes, claw marks, the faint mascot (and the subscribe banner, when it's on) |
| `frame.png` | The facecam border |
| `edges.png` | The torn-paper edges above and below the gameplay |
| `glow.png` | The pulsing glow around the facecam |
| `bell.png` | The bell (only used when the subscribe banner is on) |
| `frame_fill.png` | Shown in the facecam frame when a stream has no facecam |

- **To change a graphic,** edit its PNG in any image editor. The skill keeps your edited
  version. Delete a PNG to have it drawn again from your settings.
- **To change the text, colours, mascot or font,** set any of these in `settings.json`:
  `"reel_top_text"` (default `"LET'S GO!"`; the last word is orange), `"reel_subscribe"`
  (`false`), `"reel_cta"` (the banner's text, `"SUBSCRIBE"`), `"reel_orange"` (`"FF7900"`), `"reel_yellow"` (`"FFB000"`), `"reel_mascot"`
  (a transparent PNG; by default, your watermark logo) and `"reel_font"` (a `.ttf`; by default,
  Permanent Marker). Layers you haven't edited are redrawn automatically.

### How it differs from the reference

- **No subscribe banner** (play button, SUBSCRIBE, bell) until you ask for it; see above.
- **The mascot is your round badge logo,** because that's the logo file you have. The reference
  shows the cat on its own. For that look, save a transparent PNG of just the cat and set
  `"reel_mascot"` to it.
- **The facecam comes from the stream itself.** The skill finds the streamer's camera
  automatically; to set the camera area yourself, add `--cam x,y,w,h`. Using a separately
  recorded facecam file isn't supported yet.
- **The stream's own overlays stay visible** in the gameplay (its facecam box, chat and counters),
  because the gameplay is never cropped.
- **The gameplay band is easy to crop out,** because there's no logo on the gameplay itself. The
  branding is all around it.

## Descriptions and hashtags

Every clip gets its own description file, next to the video, with the same name:

```
01_speed-begs-chat-to-stop-lying.mp4
01_speed-begs-chat-to-stop-lying.txt   <- open it, select all, copy, paste
```

The file holds only the text to paste, in three parts separated by blank lines: the
description, a credit line with the creator's social media @handles, and 100 hashtags. You can
paste the whole thing, and the same text works on every platform.

```
🎥 Credit: IShowSpeed · YouTube @IShowSpeed · Instagram @ishowspeed · X @ishowspeedsui
```

The handles come from the creator's own channel: the platform the stream is on, plus the social
links they list in the stream's description. To add or correct one, set `"creator_socials"` in
settings.json, for example `{"ishowspeed": {"TikTok": "@name"}}`. To leave the credit line out,
set `"credit_creator": false`.

Claude writes each description from what's actually said in that clip:
- **Language:** simple, clear English that viewers anywhere can follow, with no slang or in-jokes.
- **Shape:** a hook on line 1, a few words on who the creator is, and a closing question anyone in
  any country can answer in the comments.
- **Hashtags:** all about that clip (the game, the creator, what happens, the type of moment,
  broad discovery tags), plus a few popular tags in other big languages where they fit. The most
  important tags come first.

Each platform has its own hashtag limit. The tags are ordered most important first, so where a
platform allows fewer, keep the ones at the start:

| Platform | Hashtags it allows | What to do |
|---|---|---|
| TikTok | no cap (captions up to 4,000 characters) | Paste all 100. The full text is about 1,500 characters. |
| YouTube Shorts | 60; with more, it ignores all of them | Delete the hashtags after the 60th. |
| Instagram Reels | 5 since December 2025; with more, the post is blocked | Keep only the first 5. Tags in comments count too. |

Two things to know:
- **Every tag must relate to the clip.** YouTube says irrelevant or misleading hashtags can get a
  video removed. Skim the list and delete any that don't fit (for example `#gta6leaks` on a clip
  that isn't a leak).
- **To change the number,** set `"hashtags"` in `~/StreamClips/settings.json`. Yours is 100.

## Setting up on another Mac

1. Install the tools: `brew install ffmpeg-full deno uv`, then `brew link --force ffmpeg-full`.
   - Use `ffmpeg-full`, not `ffmpeg`. The plain version can't draw captions, so every clip fails.
   - If the plain `ffmpeg` is already installed, run `brew unlink ffmpeg` first. Don't run
     `brew uninstall ffmpeg`: Homebrew then also removes other packages it thinks are unused.
   - `uv` gives the skill Python 3.12. With macOS's built-in Python 3.9, the video downloader is
     too old for YouTube.
2. Unzip `Skill/stream-clips-patched.zip` into `~/.claude/skills/`, so you end up with
   `~/.claude/skills/stream-clips/`.
3. Run `python3 ~/.claude/skills/stream-clips/scripts/streamclips.py setup` and wait for
   **READY**. It downloads about 220 MB of speech models.
4. Run `mkdir -p ~/StreamClips/brand`. Copy `Logo/logo_watermark.png` into that folder, and copy
   `Skill/settings.json` to `~/StreamClips/settings.json`.
5. Run `python3 ~/.claude/skills/stream-clips/scripts/streamclips.py doctor`. Every line should
   say ok.

Or ask Claude Code: *"Install the stream-clips skill from Stream Clips Kit on my Desktop,
following its README."*

**Don't reinstall from the original `stream-clips.zip` in Downloads.** It doesn't have this
setup's changes: the caption check, the watermark, the Desktop output folder and the `CLIPS.md`
index.

## Troubleshooting

| Problem | Fix |
|---|---|
| `watermark not found: …` | The path in `~/StreamClips/settings.json` is wrong, or the PNG was moved. |
| A faint box around the logo | The PNG has no transparent background. Make it again with the tool. |
| The logo covers something important | Lower `watermark_opacity` or `watermark_width`, or move it with `watermark_y`. |
| Every clip fails with `No option name near '….ass'` | ffmpeg can't draw captions. Install `ffmpeg-full` (see step 1 of setup). The `doctor` command checks for this. |
| Clips appear in a new, empty `Stream Clips Kit` folder | This folder was renamed or moved. Update `output_dir` in `~/StreamClips/settings.json`. |
| You want new clips saved back in `~/StreamClips` | Remove the `output_dir` line from `~/StreamClips/settings.json`. |
