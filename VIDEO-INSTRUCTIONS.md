# Video instructions

Every instruction you've given about the videos, in one place, so none of them get lost. Each
rule shows your words, what's set up now, and where it's set. For how to use the skill, see
[README.md](README.md).

New instructions get added here with the date. Replaced ones stay, marked as replaced.

Last updated: 2026-11-24.

## Rules for every clip

### 1. Your logo on every clip

> "in every clip add the logo attached , make it opacity low and add it in between mid or
> anytwhere But edit such that nobody can crop the video and claim it the video to be his, and
> don't add where it might just interrupt with the content. And possibly add it in the middle,
> with a less opacity, but visible" (2026-11-23)

Then, the same evening:

| Your words | What changed |
|---|---|
| "make the logo smaller" | 370 px → 270 px wide |
| "small then smaller  and little more opacity" | 270 px → 184 px; 30% → 40% opacity |
| "little more opacity" | 40% → 50% |
| "place the logo in the top mid" | Middle of the gameplay → top centre |
| "that is good for now, mark them in md file" | Kept as it is, for now |

**Now:** top centre of the frame, about 23 px from the top edge, 184 px wide (17% of the
1080 px width), 50% opacity, drawn under the title bar and the captions.

**Set in** `~/StreamClips/settings.json`: `"watermark_y": 0.06`, `"watermark_width": 0.17`,
`"watermark_opacity": 0.50`. The logo file is `~/StreamClips/brand/logo_watermark.png`; the
original and a backup are in `Logo/`.

**Known trade-offs of the top centre** (accepted "for now"):
- It can overlap the streamer's head; it does on Speed's head in clips 2 and 3.
- It's easier to crop off than the middle: a strip of about 210 px.
- The most crop-proof spot is the middle of the gameplay. To use it, delete `"watermark_y"`.

The watermark applies to the stacked layout. The reel layout (rule 5) has no watermark, because
your brief says the mascot branding shouldn't cover the gameplay. Since the reel layout became
the default (2026-11-24), new clips show your logo as the reel branding (the mascot top left,
and faint in the bottom right) instead of this watermark.

### 2. One description per video, next to it, for a worldwide audience

> "also I want each video description to tackle the World wide audience  and I want full of
> hashtags until the instagram limit reach of description all related to that post, I want
> taht description of each video sepeate , next to the video" (2026-11-23)

> "dont wnat 3 description for insta youtube ticktok as all are same" (2026-11-23)

**Now:** `<clip>.txt` sits next to `<clip>.mp4` and holds only the text to paste: the
description, the credit line with the creator's @handles (rule 9), then the hashtags, separated
by blank lines. The same text goes on every platform.

Claude writes each description from what's said in that clip:
- simple, clear English for viewers who speak it as a second language
- no slang, in-jokes or local references
- line 1 is a hook; it says who the creator is; it ends with a question anyone, in any country,
  can answer in the comments
- 1–3 emojis, at most 400 characters

**Replaced:** three versions per file (Instagram, TikTok, YouTube) → one.

### 3. About 100 hashtags, all about the clip

> "not enought hashtag, give me like 100" (2026-11-23)

**Now:** `"hashtags": 100` in settings.json. The tags run from the most specific (the moment
itself) to the game and creator, the community, broad discovery tags, and popular tags in other
big languages. Every tag must relate to the clip. Filtered out automatically: platform tags
(#reels, #shorts, #tiktok, #fyp, #explore…), other streaming sites (like #twitchclips on a
YouTube stream) and spam tags (#followforfollow, #like4like).

When posting, keep as many as the platform allows (checked 2026-11-23):

| Platform | Keep |
|---|---|
| TikTok | All 100. No hashtag cap; captions up to 4,000 characters. |
| YouTube Shorts | The first 60. With more than 60, YouTube ignores all of them. |
| Instagram Reels | The first 5. Most sources say that's Instagram's cap since December 2025, and more can stop the post. |

**Replaced:** 5 / 30 / 15 per platform → 5 / 100 / 60 → one list of 100.

### 4. Everything in the Stream Clips Kit folder, sorted by date

> "make a folder in desktop of the skills and all the instruction about the logo" (2026-11-23)

> "and the videos should be there" (2026-11-23)

> "markdown that as well based on date make the video in the same folder only" (2026-11-23)

**Now:**
- Clips are made in `Clips/<date>/<topic>/<streamer>__<stream title>/`, in this folder and
  nowhere else (`"output_dir"` in settings.json).
- `Clips/CLIPS.md` lists every clip by date, newest first, with links to each video and its
  description. It's rebuilt after every run.
- The skill, the logo, the tools and the layout brief are in this folder too.
- **2026-11-24:** this folder was moved from `~/Desktop/Stream Clips Kit` to
  `~/Desktop/⾴/ATUL/clipvideo`. `"output_dir"` in settings.json and the path to this file in
  the installed skill's `SKILL.md` were updated to match, so clips still land here.

### 5. The landscape gameplay layout (reel), from your design brief

> "add this in the md file for the landscape gameplay video. I want the edited video like the
> one I will attach and describe" (2026-11-24)

The full brief, word for word, is in [Layout/REEL-LAYOUT-SPEC.md](Layout/REEL-LAYOUT-SPEC.md),
with your reference image ([Layout/reference-design.png](Layout/reference-design.png)). Its main
points:
- 1080 × 1920 (9:16), 30 or 60 fps, with important things inside Instagram's safe area.
- The gameplay keeps its 16:9 shape: never cropped, stretched, zoomed or distorted. It's
  1080 × 608, centred, with torn-paper edges or an orange border.
- Top (about 25%): the mascot on the left with glowing orange brush strokes and circular accents,
  graffiti "LET'S GO!", and the facecam top right in a glowing orange/yellow frame with subtle
  animated highlights. The face must be clearly visible.
- Bottom (about 43%): orange brush strokes, claw marks and a faint oversized mascot in the bottom
  right. The subscribe banner is off; see rule 6.
- Colours: black, orange #FF7900, golden yellow #FFB000, white text, dark grey textures. Neon
  glow, grunge, graffiti lettering, torn paper. Not cluttered or childish.
- Reusable: the gameplay and the facecam can be replaced, the logo is a separate asset, and the
  text, borders, background and graphics are editable. No black gaps.
- Match the reference composition; don't invent a different layout.

**Now:** built as the reel layout. Its art is in `~/StreamClips/brand/reel/`. A test is in
[Layout/reel-demo.jpg](Layout/reel-demo.jpg).

> "make reel the default layout." (2026-11-24)

**Default since 2026-11-24:** `"layout": "reel"` is in `~/StreamClips/settings.json`, so every
new clip uses it. For the old stacked look on one run, add `--layout auto` to the command.

### 6. No subscribe banner until you ask for it

> "do not add the scribe and bell icon only once i mention that" (2026-11-24)

**Now:** off (`"reel_subscribe"` isn't set, so it's false). The red YouTube play button is off
too, since it's part of the same banner. It goes on only when you say so. What it would look
like: [Layout/reel-demo-with-subscribe.jpg](Layout/reel-demo-with-subscribe.jpg).

### 7. Show a demo before changing all the clips

> "give me the screenshot demo it required then I will change" (2026-11-23)

> "before procceding show me the demo screenshot so that I will confirm the exact size of the
> logo" (2026-11-23)

> "i want to test" (2026-11-23)

**How it's done:** render short test versions (15 seconds), put frames side by side in one
screenshot, open it, and wait for your OK before re-rendering the real clips. The demo
screenshots are kept in `Logo/` and `Layout/`.

### 8. Keep every instruction in this file

> "I want you to create the md file in that "Stream Clips Kit" folder.I do not want any if the
> video instruction to lost" (2026-11-24)

**How it's done:** this file. The skill's own instructions tell Claude to read it before making
or changing clips, and to add each new instruction here.

> "have you markdown everytinh inthat "Stream Clips Kit" folder along with searching and finding
> the skill" (2026-11-24)

**How it's done:** the [README](README.md) covers finding streams (the search, its options and
the watchlist), where everything is, including the skill itself, and making clips. The searches
run so far are logged below, in [Searches run so far](#searches-run-so-far).

### 9. Credit the creator with their social media @handles

> "also add the youtuber social medial "@"" (2026-11-24)

**Now:** every description has a credit line between the description and the hashtags. For
Speed it reads:

```
🎥 Credit: IShowSpeed · YouTube @IShowSpeed · Instagram @ishowspeed · X @ishowspeedsui
```

The handles come from the creator's own channel: the handle of the platform the stream is on,
plus the social links the creator lists in the stream's description (the first one per
platform, so secondary channels are skipped). Speed's channel lists no TikTok account, so none is
added.

**Set in** `~/StreamClips/settings.json`: `"credit_creator"` (on unless set to `false`) and
`"creator_socials"`, which adds or corrects handles per creator, for example
`{"ishowspeed": {"TikTok": "@name"}}`. An empty value removes one.

**Note:** on Instagram and TikTok, any @name links to that app's account with that name. So
"@ishowspeedsui", Speed's X handle, points to whichever Instagram account has that name.

## What else every clip gets

These are the skill's defaults, which you've kept:
- 9:16 at 1080 × 1920; 15–59 seconds; 3 clips per stream.
- The reel layout (rule 5), the default since 2026-11-24. The old stacked layout (the facecam
  on top, the gameplay below, a title bar between them) is used only with `--layout auto`.
- Word-by-word captions, 3 words at a time, with the spoken word in yellow.
- Audio levelled to −14 LUFS.
- `POSTING.md` in each stream folder, with every clip's description, why it should work and
  where it is in the stream.

## Setup decisions

- **Where the skill came from:** `~/Downloads/stream-clips.zip` ("read this skill", then "yes
  install it and run setup", 2026-11-23). It's installed in `~/.claude/skills/stream-clips/`,
  where Claude Code finds it on its own; see [Where everything is](README.md#where-everything-is).
- **ffmpeg-full, not plain ffmpeg** ("yes update the skill to ffmpeg-full", 2026-11-23). Plain
  ffmpeg can't draw captions. If plain ffmpeg is installed, use `brew unlink ffmpeg`, never
  `brew uninstall`.
- The skill's Python environment uses Python 3.12, through `uv`.
- The installed skill has changes the original `stream-clips.zip` doesn't. Don't reinstall from
  Downloads; use `Skill/stream-clips-patched.zip`.

## Before posting a clip

- Watch it all the way through.
- Make sure the creator allows clipping.
- Skim the hashtags and delete any that don't fit (for example `#gta6leaks`, `#gta6release` and
  `#gta6online` on the alien clip).
- Keep only as many hashtags as the platform allows (the table in rule 3).

## Open items

- **Reel bottom section:** without the banner, there's an empty area between the captions and
  the faint mascot. Offered: move the captions down, or make the mascot bigger.
- **Reel mascot:** a transparent PNG of just the cat would match the reference more closely than
  the round badge.
- **Crop protection in the reel layout:** the gameplay band has no logo on it, so it can be
  cropped out (your brief says the branding shouldn't cover the gameplay).
- **Logo at top centre:** accepted "for now"; it overlaps Speed's head in clips 2 and 3.

## Searches run so far

### 2026-11-23: today's biggest GTA 6 streams

> `find --topic "GTA 6"` (your first test, right after setup)

Run as `find --topic "GTA 6" --keywords "gta 6,gta vi,gta6"` (YouTube, today's window, sorted by
views). Titles that were cut off in the results end with "…".

| # | Creator | Views | Length | Title | Link |
|---|---|---|---|---|---|
| 1 | IShowSpeed | 9,877,465 | 5h45m | 🔴EXPLORING VICE CITY - GTA 6 STREAM (EASTER EGGS) | [watch](https://www.youtube.com/watch?v=izXcd-bU72k) |
| 2 | Techno Gamerz | 4,034,672 | 1h29m | TREASURE HUNTING IN THE OCEAN GONE WRONG! \| GTA 6 GAMEPLAY #… | [watch](https://www.youtube.com/watch?v=Dz0naoD1QWo) |
| 3 | Gameplayrj | 2,316,929 | 10h11m | GTA 6 A 60 FPS É LINDO DEMAIS , VAMOS JOGAR O DIA TODO | [watch](https://www.youtube.com/watch?v=L5vMU26MPSQ) |
| 4 | Rubius Z | 2,195,534 | 0h29m | I Got 6 Stars in GTA 6 ⭐ | [watch](https://www.youtube.com/watch?v=NrNdw_Y6_bI) |
| 5 | TheBurntPeanut | 2,000,775 | 13h12m | 🔴LIVE \| GTA 6 \| DAY 4 \| BIGFOOT, ALIENS & BUGATTIS \| WE RIDE… | [watch](https://www.youtube.com/watch?v=1C2CBTT8XJU) |
| 6 | Thunder GOD Live | 1,442,125 | 2h01m | GTA 6 LIVE Gameplay Hindi \| Grand Theft Auto VI \| Exploring… | [watch](https://www.youtube.com/watch?v=JJTA_AKIgK4) |
| 7 | QuadMannGaming | 1,260,802 | 4h37m | NO HANDS \| GTA 6 LIVE 🔥 | [watch](https://www.youtube.com/watch?v=uPFxbJXmJuM) |
| 8 | NOT Eight Thoughts | 1,257,633 | 0h20m | GTA 6 is COLLAPSING (Rockstar is Panicking) | [watch](https://www.youtube.com/watch?v=YNkEYGgXT80) |

Notes:
- **Best for clipping:** #1, #5 and #7 are full streams with a facecam.
- **Not streams:** #4 and #8 are short edited videos; #8 is commentary rather than gameplay.
- **Picked:** #1 ("yes clip IShowSpeed's stream", 2026-11-23); see the next section.

### 2026-11-24: today's biggest GTA 6 streams

> "make more gta6 clips"

The same search as on 2026-11-23, one day later:

| # | Creator | Views | Length | Title | Link |
|---|---|---|---|---|---|
| 1 | IShowSpeed | 10,147,097 | 5h45m | 🔴EXPLORING VICE CITY - GTA 6 STREAM (EASTER EGGS) | [watch](https://www.youtube.com/watch?v=izXcd-bU72k) |
| 2 | Techno Gamerz | 6,519,908 | 1h29m | TREASURE HUNTING IN THE OCEAN GONE WRONG! \| GTA 6 GAMEPLAY #4 | [watch](https://www.youtube.com/watch?v=Dz0naoD1QWo) |
| 3 | Rubius Z | 2,738,072 | 0h29m | I Got 6 Stars in GTA 6 ⭐ | [watch](https://www.youtube.com/watch?v=NrNdw_Y6_bI) |
| 4 | Gameplayrj | 2,324,571 | 10h11m | GTA 6 A 60 FPS É LINDO DEMAIS , VAMOS JOGAR O DIA TODO | [watch](https://www.youtube.com/watch?v=L5vMU26MPSQ) |
| 5 | Live Insaan | 1,954,098 | 6h58m | GTA 6 🛑 We Back in Vice City Live (Day 2) | [watch](https://www.youtube.com/watch?v=VxChUHDOOqg) |
| 6 | Asmongold TV | 1,339,848 | 0h58m | GTA 6 just exposed every game critic.. | [watch](https://www.youtube.com/watch?v=2pKaKXIyDW0) |
| 7 | QuadMannGaming | 1,256,938 | 4h37m | NO HANDS \| GTA 6 LIVE 🔥 | [watch](https://www.youtube.com/watch?v=uPFxbJXmJuM) |
| 8 | CarryisLive | 1,095,689 | 3h38m | FINALLY GETTING THE GOLDEN LAMBO IN GTA VI \| NO PROMOTIONS | [watch](https://www.youtube.com/watch?v=ipZCIW7DNJo) |

Notes:
- **Not streams:** #2, #3 and #6 are edited videos; #6 is commentary rather than gameplay.
- **Not in English:** #4 (Portuguese), #5 and #8 (Hindi).
- **Picked by Claude, since no stream was named:** more moments from #1, which was already
  listened to, and #7, the biggest English stream with a facecam that hadn't been clipped.
- Other English facecam streams from the same search, not clipped: DashieGames (8h04m, 350,481
  views, [watch](https://www.youtube.com/watch?v=YQ-jPo61nMI)) and Kreek (3h27m, 274,535 views,
  "GTA 6 FINAL MISSION (BEST ENDING)", [watch](https://www.youtube.com/watch?v=8x0Mv137tMA)).

## Clips made so far

| Date | Stream | Layout | Clips |
|---|---|---|---|
| 2026-11-23 | IShowSpeed, "🔴EXPLORING VICE CITY - GTA 6 STREAM (EASTER EGGS)" | Stacked, logo top centre | Speed BEGS Chat To Stop LYING 😤 · SPEED FINDS AN ALIEN IN GTA 6 👽 · Speed FINDS BIGFOOT in GTA 6 👣 |
| 2026-11-24 | The same stream, recreated ("and now recreate the speed video") | Reel, no subscribe banner | The same 3 moments |

Both versions are kept, each in its own date folder. All 6 description files have the credit
line (rule 9).

Every clip, with links: [Clips/CLIPS.md](Clips/CLIPS.md).

## For Claude, in future sessions

- Read this file before making or changing any clip, and follow every rule in it.
- When the user gives a new instruction about the videos, add it here: their words, the date,
  what's set up and where it's set. Mark replaced instructions as replaced; never delete them.
- Show a demo screenshot and wait for the user's OK before applying a visual change to all
  clips (rule 7).
