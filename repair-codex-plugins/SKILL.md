---
name: repair-codex-plugins
description: Repair local Codex plugin configuration after a Codex desktop update, especially when Chrome, Browser, Computer Use, LaTeX, or other openai-bundled plugins disappear from the plugin UI, show unavailable, or fail because openai-bundled points at an old WindowsApps path. Use when the user says plugins are missing after update, Chrome plugin is gone, Computer Use is unavailable, asks to restore/repair Codex plugins, or says in Chinese "修复 plugin", "恢复插件", "Chrome 插件没了", or "Computer Use 没了".
---

# Repair Codex Plugins

## Workflow

Run the bundled repair script first:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-dir>\scripts\repair-codex-plugins.ps1"
```

The script:

- Finds the currently installed `OpenAI.Codex` Windows package.
- Copies `app\resources\plugins\openai-bundled` into a user-writable versioned snapshot under `%USERPROFILE%\.codex\.tmp\bundled-marketplaces`.
- Updates `%USERPROFILE%\.codex\config.toml` so `[marketplaces.openai-bundled].source` points at that snapshot.
- Ensures `browser`, `chrome`, `computer-use`, and `latex` plugin entries are enabled.
- Patches the current `@oai/sky` runtime export needed by Computer Use when the installed runtime omits it.
- Runs CLI and Chrome native-host checks.

Use the script output to report the exact restored marketplace path and verification results. If the Codex desktop plugin UI is still stale after a successful repair, tell the user to fully quit and reopen the Codex desktop app.

## Verification

Prefer the script's built-in checks. If manual verification is needed, use the Codex Desktop CLI found under `%LOCALAPPDATA%\OpenAI\Codex\bin\...\codex.exe`; the bare `codex` command can point to an older npm wrapper without plugin subcommands.

After locating the Desktop CLI path, verify with:

```powershell
& "<desktop-codex.exe>" plugin marketplace list
& "<desktop-codex.exe>" plugin list
```

Expected bundled entries include:

- `browser@openai-bundled`
- `chrome@openai-bundled`
- `computer-use@openai-bundled`
- `latex@openai-bundled`

For a deeper check, use the Chrome plugin scripts from the repaired marketplace path:

```powershell
node "<bundled-path>\plugins\chrome\scripts\check-extension-installed.js" --json
node "<bundled-path>\plugins\chrome\scripts\check-native-host-manifest.js" --json
```

When using Computer Use after repair, if it still reports `Package subpath ... computer_use_client_base.js is not defined by "exports"`, rerun the repair script; it patches the active `@oai/sky` runtime.
