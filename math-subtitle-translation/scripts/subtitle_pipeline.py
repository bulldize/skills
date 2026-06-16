#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_API_BASE = "https://token-plan-cn.xiaomimimo.com/v1"


@dataclass
class Word:
  text: str
  start_ms: int


@dataclass
class Cue:
  index: int
  start_ms: int
  end_ms: int
  en: str
  zh: str = ""


DEFAULT_GLOSSARY = {
  "deal.II": "deal.II",
  "triangulation": "三角剖分",
  "Triangulation<2>": "Triangulation<2>",
  "cell": "单元",
  "active cell": "活动单元",
  "iterator": "迭代器",
  "quadrilateral": "四边形",
  "vertex/vertices": "顶点",
  "mesh": "网格",
  "annulus": "环域",
  "GridGenerator::hyper_shell": "GridGenerator::hyper_shell",
  "hyper_shell": "hyper_shell",
  "boundary indicator": "边界指示符",
  "boundary description": "边界描述",
  "manifold": "流形",
  "adaptive refinement": "自适应细化",
  "execute_coarsening_and_refinement": "execute_coarsening_and_refinement()",
  "active_cell_iterator": "active_cell_iterator",
}


def normalize_en(text: str) -> str:
  text = re.sub(r"\s+", " ", text).strip()
  replacements = {
    "deal 2": "deal.II",
    "deal two": "deal.II",
    "conon conon": "::",
    "invalent it": "invalid iterator",
    "annual": "annulus",
    "anulus": "annulus",
    "hypershell": "hyper_shell",
    "hypers shell": "hyper_shell",
    "hyper shell": "hyper_shell",
    "four Loop": "for loop",
    "execute execute cooning": "execute_coarsening_and_refinement",
    "execute cooning": "execute_coarsening_and_refinement",
  }
  for old, new in replacements.items():
    text = re.sub(rf"\b{re.escape(old)}\b", new, text, flags=re.IGNORECASE)
  text = re.sub(
    r"\btriangulation 2\s*::\s*active cell iterator\b",
    "Triangulation<2>::active_cell_iterator",
    text,
    flags=re.IGNORECASE,
  )
  text = re.sub(r"\bPoint 2\b", "Point<2>", text, flags=re.IGNORECASE)
  return text


def load_words(json3_path: Path) -> list[Word]:
  data = json.loads(json3_path.read_text(encoding="utf-8"))
  words: list[Word] = []
  for event in data.get("events", []):
    start = event.get("tStartMs")
    segs = event.get("segs")
    if start is None or not segs:
      continue
    text = "".join(str(seg.get("utf8", "")) for seg in segs).strip()
    if not text or text == "[Music]" or text == "\\n":
      continue
    for seg in segs:
      token = str(seg.get("utf8", "")).strip()
      if not token or token == "[Music]":
        continue
      words.append(Word(token, int(start) + int(seg.get("tOffsetMs", 0))))
  words.sort(key=lambda word: word.start_ms)
  return words


def build_cues(words: list[Word], duration_ms: int) -> list[Cue]:
  cues: list[Cue] = []
  current: list[Word] = []
  break_words = {"so", "okay", "right", "then", "but", "and", "because", "whereas"}

  def flush(next_start: int | None = None) -> None:
    nonlocal current
    if not current:
      return
    start = current[0].start_ms
    last = current[-1].start_ms
    end = min(duration_ms, max(last + 1300, start + 1500))
    if next_start is not None:
      end = min(end, max(start + 1200, next_start - 80))
    en = normalize_en(" ".join(word.text for word in current))
    if en:
      cues.append(Cue(len(cues) + 1, start, end, en))
    current = []

  for i, word in enumerate(words):
    if current:
      gap = word.start_ms - current[-1].start_ms
      text_len = len(" ".join(w.text for w in current))
      elapsed = word.start_ms - current[0].start_ms
      lower = word.text.lower().strip(",.?!")
      if gap > 1600 or elapsed > 7200 or text_len > 92 or (
        elapsed > 3600 and text_len > 58 and lower in break_words
      ):
        flush(word.start_ms)
    current.append(word)
    if len(current) >= 19:
      next_start = words[i + 1].start_ms if i + 1 < len(words) else None
      flush(next_start)
  flush(None)

  for cue, next_cue in zip(cues, cues[1:]):
    if cue.end_ms > next_cue.start_ms - 80:
      cue.end_ms = max(cue.start_ms + 1000, next_cue.start_ms - 80)
  return cues


def ms_to_srt_time(ms: int) -> str:
  hours, rem = divmod(ms, 3_600_000)
  minutes, rem = divmod(rem, 60_000)
  seconds, millis = divmod(rem, 1000)
  return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def ms_to_vtt_time(ms: int) -> str:
  return ms_to_srt_time(ms).replace(",", ".")


def display_width(text: str) -> int:
  return sum(1 if ord(char) < 128 else 2 for char in text)


def is_ascii_token_char(char: str) -> bool:
  return bool(re.match(r"[A-Za-z0-9_:.<>()=+\-/*\[\]]", char))


def is_cjk(char: str) -> bool:
  return "\u4e00" <= char <= "\u9fff"


def needs_space(left: str, right: str) -> bool:
  return (
    is_ascii_token_char(left) and is_ascii_token_char(right)
  ) or (
    is_ascii_token_char(left) and is_cjk(right)
  ) or (
    is_cjk(left) and is_ascii_token_char(right)
  )


def join_tokens(tokens: list[str]) -> str:
  text = ""
  for token in tokens:
    if not text:
      text = token
    else:
      text += (" " if needs_space(text[-1], token[0]) else "") + token
  return text


def wrap_zh(text: str, width: int = 38) -> str:
  text = re.sub(r"\s+", " ", text).strip()
  if display_width(text) <= width:
    return text
  tokens = re.findall(r"[A-Za-z0-9_:.<>()=+\-/*\[\]]+|[^\s]", text)
  if len(tokens) < 2:
    return text
  total = display_width(join_tokens(tokens))
  target = total / 2
  best_split = 1
  best_score = float("inf")
  for split in range(1, len(tokens)):
    left = join_tokens(tokens[:split])
    right = join_tokens(tokens[split:])
    overflow = max(0, display_width(left) - width) + max(0, display_width(right) - width)
    penalty = 6 if tokens[split] in "，。；：、？！)]}" else 0
    score = overflow * 20 + abs(display_width(left) - target) + penalty
    if score < best_score:
      best_score = score
      best_split = split
  return f"{join_tokens(tokens[:best_split])}\n{join_tokens(tokens[best_split:])}"


def save_cues(cues: list[Cue], path: Path) -> None:
  path.write_text(json.dumps([cue.__dict__ for cue in cues], ensure_ascii=False, indent=2), encoding="utf-8")


def load_cues(path: Path) -> list[Cue]:
  return [Cue(**item) for item in json.loads(path.read_text(encoding="utf-8"))]


def write_srt(cues: list[Cue], path: Path, field: str) -> None:
  lines: list[str] = []
  out_index = 1
  for cue in cues:
    text = getattr(cue, field).strip()
    if not text:
      continue
    lines.append(str(out_index))
    lines.append(f"{ms_to_srt_time(cue.start_ms)} --> {ms_to_srt_time(cue.end_ms)}")
    lines.extend(wrap_zh(text).splitlines() if field == "zh" else [text])
    lines.append("")
    out_index += 1
  path.write_text("\n".join(lines), encoding="utf-8")


def write_vtt(cues: list[Cue], path: Path) -> None:
  lines = ["WEBVTT", ""]
  for cue in cues:
    if not cue.zh.strip():
      continue
    lines.append(f"{ms_to_vtt_time(cue.start_ms)} --> {ms_to_vtt_time(cue.end_ms)}")
    lines.extend(wrap_zh(cue.zh).splitlines())
    lines.append("")
  path.write_text("\n".join(lines), encoding="utf-8")


def extract_json_object(text: str) -> dict[str, Any]:
  text = text.strip()
  if text.startswith("```"):
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
  try:
    return json.loads(text)
  except json.JSONDecodeError:
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
      return json.loads(text[start:end + 1])
    raise


def translate_batch(cues: list[Cue], api_key: str, api_base: str, model: str, glossary: dict[str, str]) -> dict[int, str]:
  system = (
    "你是数学、科学计算和编程课程的专业中文字幕译者。"
    "输出自然、简洁、适合屏幕阅读的中文技术字幕。"
    "保留代码/API 名称和数字，不逐字翻译口头填充词。"
  )
  user = {
    "task": "translate_subtitle_batch",
    "requirements": [
      "返回严格 JSON，不要 Markdown。",
      "JSON 形如 {\"items\":[{\"id\":1,\"zh\":\"...\"}]}。",
      "每个 id 必须出现一次，顺序不变。",
      "中文应专业、简洁，避免解释性扩写。",
      "按术语表修正明显 ASR 错误。",
    ],
    "glossary": glossary,
    "items": [{"id": cue.index, "en": cue.en} for cue in cues],
  }
  body = {
    "model": model,
    "messages": [
      {"role": "system", "content": system},
      {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
    ],
    "temperature": 0.1,
  }
  req = urllib.request.Request(
    api_base.rstrip("/") + "/chat/completions",
    data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    method="POST",
  )
  for attempt in range(4):
    try:
      with urllib.request.urlopen(req, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
      parsed = extract_json_object(payload["choices"][0]["message"]["content"])
      return {int(item["id"]): str(item["zh"]).strip() for item in parsed["items"]}
    except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError) as exc:
      if attempt == 3:
        first = cues[0].index if cues else "?"
        last = cues[-1].index if cues else "?"
        raise RuntimeError(f"translation failed for ids {first}-{last}: {exc}") from exc
      time.sleep(2 ** attempt)
  raise AssertionError("unreachable")


def cmd_cues(args: argparse.Namespace) -> int:
  words = load_words(args.json3)
  cues = build_cues(words, args.duration_ms)
  args.out_dir.mkdir(parents=True, exist_ok=True)
  save_cues(cues, args.out_dir / f"{args.video_id}.cues.en.json")
  write_srt(cues, args.out_dir / f"{args.video_id}.en.cleaned.srt", "en")
  print(f"Wrote {len(cues)} cues.")
  return 0


def cmd_translate(args: argparse.Namespace) -> int:
  api_key = os.environ.get(args.api_key_env)
  if not api_key:
    print(f"{args.api_key_env} is required", file=sys.stderr)
    return 2
  cues = load_cues(args.cues)
  checkpoint = args.out_dir / f"{args.video_id}.cues.zh-CN.checkpoint.json"
  if checkpoint.exists():
    saved = {int(item["index"]): str(item.get("zh", "")).strip() for item in json.loads(checkpoint.read_text(encoding="utf-8"))}
    for cue in cues:
      cue.zh = saved.get(cue.index, "")
  glossary = DEFAULT_GLOSSARY.copy()
  if args.glossary_json:
    glossary.update(json.loads(args.glossary_json.read_text(encoding="utf-8")))
  for start in range(0, len(cues), args.batch_size):
    batch = cues[start:start + args.batch_size]
    todo = [cue for cue in batch if not cue.zh.strip()]
    if not todo:
      print(f"Skipping cues {batch[0].index}-{batch[-1].index} from checkpoint.")
      continue
    print(f"Translating cues {todo[0].index}-{todo[-1].index}...")
    translated = translate_batch(todo, api_key, args.api_base, args.model, glossary)
    for cue in todo:
      cue.zh = translated[cue.index]
    save_cues(cues, checkpoint)
  save_cues(cues, args.out_dir / f"{args.video_id}.cues.zh-CN.json")
  write_srt(cues, args.out_dir / f"{args.video_id}.zh-CN.srt", "zh")
  write_vtt(cues, args.out_dir / f"{args.video_id}.zh-CN.vtt")
  return 0


def cmd_export(args: argparse.Namespace) -> int:
  cues = load_cues(args.cues)
  args.out_dir.mkdir(parents=True, exist_ok=True)
  write_srt(cues, args.out_dir / f"{args.video_id}.zh-CN.srt", "zh")
  write_vtt(cues, args.out_dir / f"{args.video_id}.zh-CN.vtt")
  return 0


def cmd_mp4_safe(args: argparse.Namespace) -> int:
  text = args.srt.read_text(encoding="utf-8")
  for old, new in {
    "Point<2>": "Point[2]",
    "GeometryInfo<2>": "GeometryInfo[2]",
    "GeometryInfo<3>": "GeometryInfo[3]",
    "Triangulation<2>": "Triangulation[2]",
  }.items():
    text = text.replace(old, new)
  args.output.write_text(text, encoding="utf-8")
  return 0


def cmd_qa(args: argparse.Namespace) -> int:
  text = args.srt.read_text(encoding="utf-8")
  blocks = [block for block in text.strip().split("\n\n") if block.strip()]
  nums = [int(block.splitlines()[0]) for block in blocks if block.splitlines()[0].isdigit()]
  failures: list[str] = []
  if nums != list(range(1, len(nums) + 1)):
    failures.append("SRT numbering is not continuous")
  times = []
  for block in blocks:
    lines = block.splitlines()
    if len(lines) >= 2 and "-->" in lines[1]:
      times.append(lines[1])
  if len(times) != len(blocks):
    failures.append("Some blocks lack timing lines")
  for bad in ["deal.\nII", "fromcenter", "第7讲", "今天step"]:
    if bad in text:
      failures.append(f"Found suspicious text: {bad!r}")
  print(json.dumps({"blocks": len(blocks), "failures": failures}, ensure_ascii=False, indent=2))
  return 1 if failures else 0


def main() -> int:
  parser = argparse.ArgumentParser()
  sub = parser.add_subparsers(dest="command", required=True)

  p = sub.add_parser("cues")
  p.add_argument("--json3", required=True, type=Path)
  p.add_argument("--out-dir", required=True, type=Path)
  p.add_argument("--video-id", required=True)
  p.add_argument("--duration-ms", type=int, default=1_489_815)
  p.set_defaults(func=cmd_cues)

  p = sub.add_parser("translate")
  p.add_argument("--cues", required=True, type=Path)
  p.add_argument("--out-dir", required=True, type=Path)
  p.add_argument("--video-id", required=True)
  p.add_argument("--api-key-env", default="XIAOMI_API_KEY")
  p.add_argument("--api-base", default=DEFAULT_API_BASE)
  p.add_argument("--model", default="mimo-v2.5-pro")
  p.add_argument("--batch-size", type=int, default=10)
  p.add_argument("--glossary-json", type=Path)
  p.set_defaults(func=cmd_translate)

  p = sub.add_parser("export")
  p.add_argument("--cues", required=True, type=Path)
  p.add_argument("--out-dir", required=True, type=Path)
  p.add_argument("--video-id", required=True)
  p.set_defaults(func=cmd_export)

  p = sub.add_parser("mp4-safe")
  p.add_argument("--srt", required=True, type=Path)
  p.add_argument("--output", required=True, type=Path)
  p.set_defaults(func=cmd_mp4_safe)

  p = sub.add_parser("qa")
  p.add_argument("--srt", required=True, type=Path)
  p.set_defaults(func=cmd_qa)

  args = parser.parse_args()
  return args.func(args)


if __name__ == "__main__":
  raise SystemExit(main())
