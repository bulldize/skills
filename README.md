# Bulldize Codex Skills

这里存放个人常用的 Codex skills，用来沉淀可复用的工作流和项目方法。

## Skills 列表

| Skill | 用途 |
| --- | --- |
| `research-reproduction-planner` | 将论文复现、本地数据迁移、公开基准验证整理成可审计、可跨会话接续的 goal-mode 研究工程流程。 |
| `math-subtitle-translation` | 支持数学课程字幕翻译与打包流程。 |
| `repair-codex-plugins` | 修复 Codex 桌面端更新后本地插件配置丢失或不可用的问题。 |

## Research Reproduction Planner

当项目需要完成以下工作时，使用 `research-reproduction-planner`：

- 调研 SOTA 论文和可用代码仓库；
- 先在官方 benchmark 上复现论文或 leaderboard 结果；
- 再把复现方法迁移到本地数据集；
- 生成跨会话可接续的 PRD、`NEXT_STEP.md` 和 `SOURCE_MAP.md`；
- 在实现前强制进行 source-grounded audit；
- 将每个复现 Stage 作为 goal-mode 工作流持续推进。

默认触发 prompt：

```text
Use $research-reproduction-planner to turn this paper reproduction task into a source-grounded, goal-mode project workflow.
```

## 安装

把需要的 skill 目录复制到本机 Codex skills 目录，例如：

```powershell
Copy-Item -Recurse .\research-reproduction-planner $env:USERPROFILE\.codex\skills\
```

如有需要，重启 Codex 或重新加载 skills。
