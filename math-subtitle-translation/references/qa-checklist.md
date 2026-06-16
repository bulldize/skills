# QA Checklist

## Automatic Checks

- SRT numbering is continuous from 1.
- Cue times are monotonic and non-overlapping.
- No empty subtitle blocks.
- No broken code tokens such as `deal.\nII`.
- No accidental lowercase code variables such as `fromcenter`.
- SRT and VTT parse as text with expected cue counts.

## Terminology Checks

- `cell` is `单元`, not `细胞`.
- `triangulation` is `三角剖分`.
- `annulus` is `环域`.
- `active cell` is `活动单元`.
- `boundary indicator` is `边界指示符`.
- `boundary description` is `边界描述`.
- `refinement` is `细化`.
- Code/API names are preserved.

## Human Spot Checks

- First minute: course context reads naturally.
- Main technical section: math and code terms are accurate.
- Complex reasoning section: no cue split changes meaning.
- Boundary/manifold section: new-vertex placement is clear.
- Ending: no orphan digits, music cues, or filler.

## Video Packaging Checks

- `ffprobe` shows video, audio, and subtitle streams.
- Subtitle stream language is `chi`.
- MP4 soft subtitles use MP4-safe code tokens.
- Roundtrip-extracted subtitle preserves `Point[2]`, `GeometryInfo[2]`, and other key tokens.

