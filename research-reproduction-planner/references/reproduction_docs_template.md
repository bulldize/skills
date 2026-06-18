# Reproduction Project Document Templates

Use these templates when creating or repairing a source-grounded paper reproduction project. Keep documents concise but decision-complete enough for a fresh session to resume the project.

## Directory Skeleton

```text
docs/
  PROJECT.md
  NEXT_STEP.md
  PRD_DATA_EVAL.md
  PRD_REPRODUCTION.md
  SOURCE_MAP.md
  source_audits/
  papers/
    README.md
data/
  downloads/
  external/
  raw/
  processed/
external_repos/
experiments/
src/
```

## PROJECT.md

Required sections:

- Project Goal: final local deliverable, input format, output format, label system, background class, and downstream use.
- Current Status: current Candidate, current Stage, `NEXT_STEP.md` path, and source audit state.
- Local Data Contract: raw path, sample counts, file pairing, annotation schema, label/index rules, subsets, and read-only policy.
- Public Benchmark Data Contract: dataset name, source URLs, size, format, annotation schema, splits, download status, and validation status.
- Label Strategy: canonical labels, model-internal labels, mapping back to local labels, and background policy.
- Candidate Order: ranked methods and why the first candidate is first.
- Metrics Contract: common metrics and subset reporting.
- Directory Convention: where downloads, external data, processed data, external repos, experiments, and source audits live.
- New Session Entry: exact reading order for `NEXT_STEP.md`, `SOURCE_MAP.md`, project docs, and paper index.

## PRD_DATA_EVAL.md

Required sections:

- Summary: data/evaluation layer purpose.
- Raw Data Inputs: each dataset format and annotation contract.
- Processed Data Outputs: manifest, split files, normalized labels, model-specific formats.
- Manifest Fields: sample id, paths, source dataset, split/fold, jaw/subset fields, label availability, checksums if useful.
- Split Strategy: official splits for public data; local folds or train/val/test rules for local data.
- Label Conversion: source labels to canonical labels, background, instances, missing labels, local mapping.
- Model Input Adapters: per candidate/model intermediate formats.
- Unified Evaluation Format: ground truth/prediction fields and path convention.
- Metrics: accuracy, IoU, Dice/DSC, task-specific metrics, subset metrics.
- Visualization: required GT vs prediction samples and coverage.
- Acceptance: conversion checks, sample-count checks, label-distribution checks, evaluator smoke tests.

## PRD_REPRODUCTION.md

Required sections:

- Summary: candidate-method workflow, not a paper list.
- Source Audit Gate: mandatory audit, audit file path, required audit contents, and rule to update PRDs if sources contradict assumptions.
- Candidate Queue: 3-5 candidates with repository availability and reproducibility rationale.
- Stage 1 Official Reproduction: benchmark dataset, official split, metrics, acceptance thresholds, artifacts.
- Stage 2 Local Fine-Tuning: local dataset adaptation, folds/subsets, metrics, acceptance thresholds, artifacts.
- Stage 3 Local Label/Export Alignment: label mapping, export format, evaluator compatibility, visualization, error analysis, artifacts.
- Experiment Artifacts: config, split, metrics, per-sample/per-label reports, checkpoint, predictions, visualizations, `run_notes.md`.
- NEXT_STEP Maintenance: active goal, done, pending, next action, blockers, metric gap, source audit state, advancement rule.

Do not include automatic fallback or automatic candidate switching unless the user explicitly requests it. The user decides Stage pass/fail and candidate switching.

## SOURCE_MAP.md

Required sections:

- Source Audit Rule: audit before implementation; use subagent when available; do not implement from summaries.
- Repository Location Rules: clone under `external_repos`, inspect existing checkouts, do not overwrite local changes.
- Current Repository Locations: remote URL, expected local path, status.
- Future Candidate Repository Seeds: repository seeds and discovery notes for later candidates.
- Candidate N / Stage M Sources: paper PDF, official repo README, preprocessing code, training code, inference code, configs, official evaluator, dataset page, dataset loader.
- Known Facts To Re-check: important facts that were already found but must be verified during audit.
- Audit Report Requirements: exact content the audit must include.

## NEXT_STEP.md

Required sections:

- Current Candidate.
- Current Stage.
- Active Stage Goal: full goal-mode objective and stop conditions.
- Current Data/Repository Status.
- Stage Progress: Done and Pending items.
- Immediate Next Action: one executable next action.
- Acceptance Targets: metric thresholds and required artifacts.
- Required First/Next Deliverable.
- Current Blockers: write `None` when there is no blocker.
- Advancement Rule: do not move to the next Stage/Candidate until the user explicitly decides.

## docs/papers/README.md

Required sections:

- Project Documents: links to `NEXT_STEP.md`, `SOURCE_MAP.md`, `PROJECT.md`, PRDs.
- Reproduction Order: Candidate list.
- Public Dataset Notes: official benchmark facts and source URLs.
- Downloaded Papers: table with priority, file, paper title, paper source URL, repository URL, notes.
- Verification: file size/signature or other paper-integrity checks.

## Source Audit Report

Required sections:

- Scope: Candidate, Stage, objective, sources read.
- Source Inventory: paper, repo commits/branches if known, evaluator files, dataset pages, loaders.
- Data Contract: official data format, labels, instances, background, split.
- Preprocessing: exact inputs, outputs, commands, generated files, assumptions.
- Training: order, configs, commands, dependencies, checkpoints, expected runtime constraints.
- Inference: commands, inputs, outputs, postprocessing.
- Evaluation: official metrics, scripts, expected prediction format, known leaderboard numbers.
- Source-vs-PRD Mismatches: corrections needed before implementation.
- Open Questions: only questions not answerable from sources.
- Next Implementation Actions: concrete steps for the main session.

## Experiment Run Notes

Each formal run should have a `run_notes.md` with:

- Run id, date, candidate, stage.
- Code commit or repository state.
- Dataset version and split.
- Config and command.
- Hardware/environment notes.
- Metrics summary and acceptance status.
- Gap to paper/leaderboard.
- Error modes and representative samples.
- Next action.
