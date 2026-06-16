# Pitfalls

## YouTube SRT Is Usually a Rolling Window

Do not translate YouTube auto SRT cue-by-cue when `json3` is available. Auto SRT often repeats previous words and overlaps heavily. Prefer `json3`, reconstruct word-level events, then generate sentence-level cues.

## Common ASR Errors

- `deal 2`, `deal two` -> `deal.II`
- `annual`, `anulus` -> `annulus`
- `hypershell`, `hyper shell` -> `hyper_shell`
- `conon conon` -> `::`
- `invalent it` -> `invalid iterator`
- `four Loop` -> `for loop`
- `execute execute cooning` -> `execute_coarsening_and_refinement`
- `Z Z` in boundary context -> `zero`

## Model Calls Need Checkpoints

Batch translation can time out. Write a checkpoint after every successful batch and skip already translated cues on rerun. Use small batches, typically 10-18 cues.

## JSON Output Is Not Guaranteed

Even when prompted, models may return fenced JSON or extra prose. Require strict JSON and parse defensively by extracting the JSON object if needed.

## Filler Words Hurt Chinese Subtitles

Do not translate every `um`, `you know`, repeated `so`, or filler fragment. Remove filler-only cues during polishing.

## Code/API Tokens Must Survive

Preserve names like `deal.II`, `Point<2>`, `GeometryInfo<2>::vertices_per_cell`, `active_cell_iterator`, `cell->vertex(2)`, `set_refine_flag()`, and `execute_coarsening_and_refinement()`.

## Line Wrapping Can Break Meaning

Do not wrap by raw character count. Keep ASCII code tokens intact, preserve order, and add spaces between Chinese and code tokens.

## SRT Numbering Must Be Rebuilt

If empty/filler cues are removed, re-number output SRT blocks from 1. Do not reuse internal cue ids as SRT numbers.

## MP4 mov_text Eats Angle Brackets

MP4 `mov_text` treats `<...>` as tags. Original SRT/VTT may keep `Point<2>`, but MP4-safe SRT should use `Point[2]`, `GeometryInfo[2]`, etc. Always roundtrip-extract the embedded subtitle and check key tokens.

## Do Not Use `-f 18` for Final Video

`yt-dlp -f 18` is a convenient low-quality MP4, commonly 360p. Final packaged lecture videos should use the highest available quality:

```bash
yt-dlp -f 'bv*+ba/best' --merge-output-format mp4 -o '<video-id>.video.highest.%(ext)s' '<url>'
```

If the highest streams are not MP4-compatible, preserve quality with MKV rather than falling back to a low-resolution MP4.

## Friendly Final Filenames Matter

Keep the machine-readable `*.zh-CN.softsub.mp4`, but also create a viewing-friendly copy named `Lecture <N> - <Chinese summary title>.zh-CN.softsub.mp4`. Get the lecture number from the source title, metadata, or manifest. Summarize the Chinese title from the actual lecture content.

## ffmpeg May Lack Hard-Subtitle Filters

Homebrew `ffmpeg` may not include `subtitles` / `ass` filters. Default to soft subtitles unless a libass-capable build is available.

## ASR Endpoint Compatibility Is Uncertain

A model list may include ASR models without exposing an OpenAI-compatible `/audio/transcriptions` endpoint. Probe with a short sample; if it fails, continue with YouTube `json3` timing instead of blocking.
