---
name: research-reproduction-planner
description: Build source-grounded, goal-mode research reproduction workflows for projects that start from papers, public benchmarks, official repositories, and a local dataset. Use when the user asks to research SOTA methods, reproduce a paper or leaderboard result, compare candidate repositories, migrate a public method to local data, create PRDs/NEXT_STEP/SOURCE_MAP docs for a long-running experiment, or continue a cross-session paper-to-local-data reproduction project.
---

# Research Reproduction Planner

## Core Rule

Turn paper reproduction work into an auditable project system before implementing models. Do not jump from a paper summary to training code. First establish the local data contract, public benchmark, candidate order, source map, goal-mode stages, and acceptance metrics.

Default to Chinese project documents unless the user requests otherwise. Keep file names, model names, metrics, CLI commands, paths, schema fields, and identifiers in English.

## Workflow

1. Inspect the current workspace before asking questions. Read existing docs, data folders, paper lists, configs, and previous `NEXT_STEP.md`/`SOURCE_MAP.md` if present.
2. Define the final local objective: input format, output format, required label system, background class, downstream deliverable, and acceptance criteria.
3. Inspect the local dataset without modifying raw data. Record sample counts, pairing rules, annotation schema, index rules, subsets, split facts, label meanings, and known irregularities.
4. Research 3-5 candidate methods with papers, official/credible repositories, public datasets, reported metrics, input/output formats, and reproducibility risk. Browse when sources, URLs, leaderboards, data availability, or repository status may have changed.
5. Download or index papers under `docs/papers` when the user wants local paper artifacts. For large datasets, first write the source, size, files, and validation plan; wait for explicit approval unless the user has already asked to download.
6. Create the project documents listed below. If documents already exist, update them without discarding user changes.
7. For each candidate, use the fixed stage template: Stage 1 official reproduction, Stage 2 local fine-tuning, Stage 3 local label/export alignment.
8. Before any Stage implementation, require a source-grounded audit from original papers, official repositories, official evaluation scripts, dataset pages, and credible loaders. Use a subagent for the audit when available.
9. Treat each Stage as a goal-mode workstream. Continue within the same Stage through audit, data prep, environment, training, evaluation, fixes, reruns, and artifact packaging until metrics pass, the user pauses/stops, or a real blocker appears.
10. Never auto-advance from one Stage to the next or from one Candidate to another. The user decides Stage pass/fail and candidate switching.

## Required Documents

Create or maintain these files in the project `docs` directory:

- `PROJECT.md`: final objective, local and public data contracts, label strategy, candidate order, metrics, directory conventions, and new-session reading order.
- `PRD_DATA_EVAL.md`: raw data rules, processed data rules, manifest fields, split strategy, label conversion, model input formats, unified evaluation output, metrics, and visualization acceptance.
- `PRD_REPRODUCTION.md`: candidate queue, Stage 1/2/3 definitions, acceptance metrics, source audit gate, experiment artifacts, and `NEXT_STEP.md` maintenance rules.
- `SOURCE_MAP.md`: source-of-truth index for papers, repositories, official pages, official evaluators, dataset pages, local clone paths, and required audit report paths.
- `NEXT_STEP.md`: cross-session status board with current candidate, current Stage, active goal, completed work, next executable action, source audit status, blockers, acceptance metric gap, and advancement rule.
- `docs/papers/README.md`: paper files, source URLs, repository URLs, priority order, and repository-discovery notes.

Use `references/reproduction_docs_template.md` when detailed section templates are needed.

## Source Audit Gate

For every Candidate and every Stage:

- Require source audit before implementation.
- Audit the paper, repository README, preprocessing code, training code, inference code, config files, official evaluator, dataset page, and any credible dataset loader.
- Write the audit under `docs/source_audits`, for example `candidate1_stage1_official_reproduction.md`.
- The audit must cite source files/sections and extract exact reproduction steps, commands, configs, data format, split contract, metrics, and unresolved implementation details.
- If the audit contradicts PRDs, update PRDs and `NEXT_STEP.md` before implementing.
- Do not implement from PRD summaries alone.

## Repository Rules

Record all candidate repositories in `SOURCE_MAP.md`.

- Clone repositories under `external_repos/{repository_name}`.
- If the repository exists, inspect it before pulling or modifying it. Do not overwrite local changes.
- If a candidate has no selected primary repository, perform repository discovery from the paper, official project page, author page, and current public code links. Do not invent a repository.
- Keep repository seeds for later candidates even if their full source maps are not expanded yet.

## Stage Template

Stage 1: official reproduction

- Reproduce the method on the paper/official benchmark dataset and split.
- Use official metrics and official evaluator when available.
- Record gap to paper or leaderboard results.
- Produce configs, splits, checkpoints, predictions, metrics, per-sample/per-label reports, visualizations, and `run_notes.md`.

Stage 2: local fine-tuning

- Transfer the Stage 1 code path, weights, and preprocessing knowledge to the local dataset.
- Preserve the local label system and background policy.
- Report full-data and important subset metrics with mean/std when using folds.
- Record distribution differences, overfitting signs, low-frequency class behavior, and local failure modes.

Stage 3: local label/export alignment

- Freeze or document class-id-to-local-label mapping.
- Export predictions in the local required label system.
- Verify unified evaluator compatibility.
- Produce visualizations and focused error analysis for missing, rare, ambiguous, or special labels.

## Goal-Mode State

When the user starts or resumes a Stage, make or continue a goal with the full Stage objective. `NEXT_STEP.md` must remain enough for a fresh session to resume accurately.

Do not stop because a normal subtask finished. Stop only when:

- acceptance metrics are met and artifacts are verified;
- the user pauses or stops;
- a real blocker requires user decision or external state.

At the end of each working session, update `NEXT_STEP.md` with completed work, next action, blocker state, and metric status.

## Defaults

- Use Chinese for project docs.
- Use source-grounded audits as mandatory.
- Use goal mode for each Stage.
- Browse by default for current papers, repositories, datasets, leaderboards, and public-code status.
- Download papers by default when requested; clone repositories only when their Candidate/Stage starts; request confirmation before large dataset downloads.
- Let the agent propose acceptance metrics from papers, leaderboards, local data size, and training constraints, but do not start a Stage without explicit metrics.
