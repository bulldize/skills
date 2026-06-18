# Bulldize Codex Skills

Personal Codex skills used for repeatable project workflows.

## Skills

| Skill | Purpose |
| --- | --- |
| `research-reproduction-planner` | Builds source-grounded, goal-mode paper reproduction workflows from papers, public benchmarks, repositories, and local datasets. |
| `math-subtitle-translation` | Supports math lecture subtitle translation workflows. |
| `repair-codex-plugins` | Repairs local Codex plugin configuration after desktop/plugin updates. |

## Research Reproduction Planner

Use `research-reproduction-planner` when a project needs to:

- research SOTA papers and available repositories;
- reproduce a paper or leaderboard result on the official benchmark first;
- migrate the reproduced method to a local dataset;
- create cross-session PRDs, `NEXT_STEP.md`, and `SOURCE_MAP.md`;
- require source-grounded audits before implementation;
- run each reproduction stage as a goal-mode workstream.

Default prompt:

```text
Use $research-reproduction-planner to turn this paper reproduction task into a source-grounded, goal-mode project workflow.
```

## Install

Copy a skill directory into your Codex skills folder, for example:

```powershell
Copy-Item -Recurse .\research-reproduction-planner $env:USERPROFILE\.codex\skills\
```

Restart Codex or reload skills if needed.
