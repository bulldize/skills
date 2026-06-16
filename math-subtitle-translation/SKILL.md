---
name: math-subtitle-translation
description: Professional Chinese subtitle workflow for mathematical, scientific, programming, and technical lecture videos. Use when asked to add Chinese subtitles, translate lecture subtitles, batch-translate YouTube/local videos, produce SRT/VTT/soft-subtitle MP4 files, preserve math/code terminology, or build QA-able subtitle pipelines.
---

# Math Subtitle Translation

## Workflow

1. Inspect the source video and available subtitles. Prefer YouTube `json3` auto subtitles over YouTube SRT when available because SRT is often a rolling caption window with overlapping repeated text.
2. Normalize cue timing before translation. Build sentence-level cues from word/segment events; avoid translating overlapping rolling SRT cues directly.
3. Translate with a glossary and checkpoint every batch. Use small batches, usually 10-18 cues, and require strict JSON output.
4. Polish after translation. Fix ASR errors, remove filler-only cues, preserve code/API names, and export clean SRT/VTT from structured cue JSON.
5. QA before delivery. Check numbering, monotonic timing, empty cues, terminology, code tokens, and soft-subtitle roundtrip.
6. Package video only after subtitle QA. Download the highest available quality with `bv*+ba/best`; do not use low-quality convenience formats such as `-f 18` for final video.
7. For MP4 `mov_text`, create an MP4-safe SRT that replaces code angle brackets such as `Point<2>` with `Point[2]`.
8. Put final videos in `/Users/bulldize/Desktop/有限元方法/Dealii教程中` and use only the normal viewing filename `Lecture <N> - <Chinese summary title>.zh-CN.softsub.mp4`. Treat `<video-id>.zh-CN.softsub.mp4` as a temporary/debug artifact, not final delivery.

## Resources

- Read `references/pitfalls.md` before running a new pipeline or debugging subtitle output.
- Read `references/glossary.md` for math/FEM/deal.II terminology and common ASR corrections.
- Read `references/qa-checklist.md` before final delivery.
- Use `scripts/subtitle_pipeline.py` for reusable cue generation, translation, export, highest-quality download, MP4-safe conversion, soft-subtitle packaging, final naming, and QA checks.

## Commands

Set API credentials through environment variables only:

```bash
export XIAOMI_API_KEY="..."
```

Generate sentence-level cues from YouTube `json3`:

```bash
python /Users/bulldize/.codex/skills/math-subtitle-translation/scripts/subtitle_pipeline.py cues \
  --json3 subtitles/<video-id>/<video-id>.en.json3 \
  --out-dir subtitles/<video-id> \
  --video-id <video-id>
```

Translate with checkpointing:

```bash
python /Users/bulldize/.codex/skills/math-subtitle-translation/scripts/subtitle_pipeline.py translate \
  --cues subtitles/<video-id>/<video-id>.cues.en.json \
  --out-dir subtitles/<video-id> \
  --video-id <video-id> \
  --api-key-env XIAOMI_API_KEY \
  --model mimo-v2.5-pro \
  --batch-size 10
```

Export SRT/VTT from polished or translated cue JSON:

```bash
python /Users/bulldize/.codex/skills/math-subtitle-translation/scripts/subtitle_pipeline.py export \
  --cues subtitles/<video-id>/<video-id>.cues.zh-CN.polished.json \
  --out-dir subtitles/<video-id> \
  --video-id <video-id>
```

Download the highest-quality source video:

```bash
python /Users/bulldize/.codex/skills/math-subtitle-translation/scripts/subtitle_pipeline.py download \
  --url '<youtube-url>' \
  --out-dir subtitles/<video-id> \
  --video-id <video-id> \
  --merge-output-format mp4
```

Create an MP4-safe subtitle file:

```bash
python /Users/bulldize/.codex/skills/math-subtitle-translation/scripts/subtitle_pipeline.py mp4-safe \
  --srt subtitles/<video-id>/<video-id>.zh-CN.srt \
  --output subtitles/<video-id>/<video-id>.zh-CN.mp4-safe.srt
```

Package soft subtitles:

```bash
python /Users/bulldize/.codex/skills/math-subtitle-translation/scripts/subtitle_pipeline.py softsub \
  --video subtitles/<video-id>/<video-id>.video.highest.mp4 \
  --subtitle subtitles/<video-id>/<video-id>.zh-CN.mp4-safe.srt \
  --lecture <N> \
  --summary-title '<Chinese summary title>'
```

Run QA checks:

```bash
python /Users/bulldize/.codex/skills/math-subtitle-translation/scripts/subtitle_pipeline.py qa \
  --srt subtitles/<video-id>/<video-id>.zh-CN.srt
```

## Delivery

Deliver at least:

- `*.zh-CN.srt`
- `*.zh-CN.vtt`
- `*.cues.zh-CN.polished.json` or `*.cues.zh-CN.json`

When video packaging is requested, also deliver:

- `*.video.highest.<ext>`
- `*.zh-CN.mp4-safe.srt`
- `/Users/bulldize/Desktop/有限元方法/Dealii教程中/Lecture <N> - <Chinese summary title>.zh-CN.softsub.mp4`
- `embedded.zh-CN.roundtrip.srt` for verification
