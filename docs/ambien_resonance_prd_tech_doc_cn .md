# Ambien Resonance Skill 项目需求文档与技术设计文档

## 0. 文档定位

本文档用于指导在本地 macOS 上开发一个 Ambien-like 项目，并最终以 Hermes Skill 的形态部署使用。

项目目标不是开发一个完整 WebApp，也不是开发一个独立 AI 写作 SaaS，而是复现 Ambien 黑客松项目的核心能力：

> 在一个有限、本地、个人化的资料库中，让 Agent 通过检索、抽象、比较和写作，主动发现不同材料之间的“结构共振”，并生成可继续修改的 synthesis essay 草稿。

后续修正后的关键原则是：

> **Hermes 负责 LLM 判断与写作；qmd 负责 embedding 与检索；本地 CLI 负责工具化、落盘、审计和流程固定。**

也就是说，MVP 阶段不要把项目做成一个独立调用 OpenAI / Ollama / 其他 LLM API 的 Python 应用。LLM 的调用默认由 Hermes 当前配置的驱动模型完成。

---

## 1. 项目背景

Ambien 公开展示的是一个 daydreaming agent。它在一个小型、本地、经过人工选择的资料库中游走，寻找不同材料之间的 structural resonance，并在发现有价值的连接后写成文章。

这个项目最值得复现的不是“自动写博客”，而是：

1. 有边界的本地语料库。
2. 不是等用户提问，而是主动做 daydream loop。
3. 不只找语义相似，而是找“表面不同、底层结构相似”的材料组合。
4. 输出不是问答，而是 synthesis essay。
5. 生成结果会反过来进入系统，影响下一次选题和反重复判断。

因此，本项目的核心价值是：

> 把个人资料库变成一个可以自动产生选题、洞察和草稿的 Hermes Skill。

---

## 2. 产品目标

### 2.1 一句话定义

**Ambien Resonance Skill 是一个运行在 Hermes 中的本地资料库“做梦”Skill。它通过 qmd 检索本地资料，由 Hermes 当前模型完成结构抽象、结构共振判断和文章生成，并把运行过程保存为可审计的本地文件。**

### 2.2 核心目标

MVP 要做到：

1. 在本地 macOS 上开发和运行。
2. 以 Hermes Skill 作为主要使用入口。
3. 使用 qmd 管理本地资料库检索和 embedding。
4. 不在 Python CLI 中直接调用 LLM API。
5. 由 Hermes 当前驱动模型完成：
   - seed 解释
   - structure card 抽取
   - 结构共振比较
   - critic 判断
   - 文章草稿写作
6. CLI 只负责：
   - 初始化目录
   - 调用 qmd
   - 读取候选材料
   - 保存 Hermes 生成的 JSON / Markdown
   - 管理 runs/、drafts/、cards/ 等文件
   - 提供 inspect / export / review 等命令
7. 输出一篇 Markdown 草稿，并保存完整运行记录。

### 2.3 不做什么

MVP 阶段明确不做：

1. 不做 Web 前端。
2. 不做用户系统。
3. 不做在线编辑器。
4. 不做完整后端数据库服务。
5. 不做多用户部署。
6. 不自己实现 embedding。
7. 不直接集成 Chroma / FAISS / LanceDB。
8. 不强制接入 Ollama。
9. 不让 CLI 自己调用 OpenAI-compatible API。
10. 不做博客发布系统。

这些都可以作为 v2/v3 后续扩展，但不是第一阶段目标。

---

## 3. 产品形态选择

### 3.1 为什么选择 Skill-first

本项目最适合的形态是：

```text
Hermes Skill
  + 本地 CLI 工具层
  + qmd 本地检索层
  + 文件型状态与运行记录
```

而不是：

```text
完整 WebApp
  + 前端
  + 后端 API
  + 数据库
  + 用户系统
```

原因是：

1. 项目核心是 agent loop，不是资料管理 UI。
2. Ambien 原项目的精神更接近 Skill / Agent pipeline，而不是 WebApp。
3. 你已经有 Hermes 环境，Skill 是最自然的使用入口。
4. WebApp 会把开发重心拖向界面、数据库、鉴权和部署，而不是“结构共振”。
5. 你真正需要的是一个可被 Hermes 调用、可被 cron 定时运行、可写入本地文件的能力模块。

### 3.2 为什么不能只是一个 SKILL.md

纯 `SKILL.md` 太薄，不适合承载：

1. qmd 调用封装。
2. 运行记录管理。
3. JSON schema 校验。
4. 文件读写。
5. cards / runs / drafts 目录维护。
6. gold cases 测试集。
7. inspect / review 命令。

所以更合理的结构是：

```text
Skill = 使用说明 + 操作流程 + 调用入口
CLI = 工具执行层 + 文件落盘层 + 可审计流程层
qmd = 检索与 embedding 层
Hermes 当前模型 = 智能判断与写作层
```

---

## 4. 系统总体架构

### 4.1 修正后的核心架构

```text
用户 / QQ / Hermes TUI
        ↓
Hermes Skill: ambien-resonance
        ↓
调用本地 CLI 工具
        ↓
CLI 调用 qmd 检索本地 corpus
        ↓
Hermes 读取候选材料
        ↓
Hermes 当前驱动模型抽取 structure card
        ↓
Hermes 当前驱动模型比较结构共振
        ↓
Hermes 当前驱动模型进行 critic 判断
        ↓
Hermes 当前驱动模型生成 Markdown 草稿
        ↓
CLI 保存 cards / runs / drafts / manifest
```

### 4.2 三层职责

| 层级 | 组件 | 职责 |
|---|---|---|
| 智能层 | Hermes 当前驱动模型 | 理解、抽象、比较、判断、写作 |
| 检索层 | qmd | 管理本地资料库、embedding、关键词检索、语义检索、hybrid query |
| 工具层 | Python CLI | 初始化、调用 qmd、读写文件、保存 JSON、维护运行记录 |

### 4.3 模型职责修正版

| 能力 | MVP 默认负责者 | 说明 |
|---|---|---|
| 文档索引 | qmd | 不自己实现 |
| embedding | qmd | 不引入 Ollama embedding |
| 候选材料检索 | qmd | 用 `qmd query` |
| seed 选择 | Hermes + 少量规则 | Skill 中规定策略，Hermes 执行判断 |
| structure card 抽取 | Hermes 当前模型 | 不由 CLI 调 API |
| 结构共振比较 | Hermes 当前模型 | LLM 判断为主，CLI 只保存结果 |
| critic 评分 | Hermes 当前模型 | 判断是否硬凑、重复、证据不足 |
| 文章写作 | Hermes 当前模型 | 使用当前配置的最强模型 |
| 运行记录 | CLI | 固定落盘，便于审计 |

### 4.4 Ollama 的位置

MVP 阶段：**不需要 Ollama。**

只有在以下情况下才考虑 Ollama：

1. 你希望 Hermes 当前驱动模型就是本地 Ollama 模型。
2. 你希望后续完全离线运行。
3. 你想在 v2 里让 CLI 支持独立 LLM provider。
4. qmd 的 embedding 或召回表现不够，需要额外结构卡 embedding。

但这不是 MVP 的必要条件。

---

## 5. 核心概念：结构共振

### 5.1 定义

结构共振不是语义相似，也不是主题相似。

它指的是：

> 两份材料表面话题不同，但背后的问题结构、角色关系、失败模式、解决机制或时间结构相似。

例如：

```text
材料 A：Hermes 初学者不能一开始装太多 skill。
材料 B：vibe coding 多轮迭代后会出现上下文污染和重复实现。
材料 C：NotebookLM 不能直接塞整个 repo，需要结构化输入。
```

普通语义相似会说：

```text
它们都和 AI 工具有关。
```

结构共振应该说：

```text
复杂 AI 工具的问题不是能力不足，而是边界管理不足。越强的工具，越需要小场景、小循环、小反馈来驯化。
```

这就是本项目要实现的核心能力。

### 5.2 好的结构共振标准

一个好的结构共振通常满足：

1. 表面话题有一定距离。
2. 底层问题结构相似。
3. 有明确的共同机制。
4. 有足够证据支撑。
5. 能形成一篇有张力的文章。
6. 不是把任何东西都硬说成“复杂系统”“反馈循环”“信息流动”。

### 5.3 坏的结构共振

以下都应被 critic 拒绝：

1. 只是主题相似。
2. 只是都提到 AI。
3. 只是都涉及“系统”“复杂性”“反馈”等泛词。
4. 只能总结成一句漂亮但空泛的话。
5. 不能展开为具体文章。
6. 和近期草稿高度重复。
7. 缺少原文证据。

---

## 6. 核心运行流程

### 6.1 一次 daydream cycle

```text
1. Hermes Skill 被用户触发
2. Skill 调用 CLI 检查项目状态
3. CLI 返回 corpus、qmd index、recent runs 状态
4. Hermes 选择本次策略：random collision / tag bridge / temporal bridge
5. Hermes 生成 seed query
6. CLI 调用 qmd query 获取候选材料
7. Hermes 阅读候选材料片段
8. Hermes 抽取 structure cards
9. CLI 保存 cards
10. Hermes 比较 cards，寻找结构共振
11. Hermes 运行 critic
12. 如果通过，Hermes 写 essay draft
13. CLI 保存 draft、manifest、pair report
14. Hermes 返回摘要给用户
```

### 6.2 失败时的行为

如果没有找到好的结构共振，不应该硬写文章。

系统应该保存一次 failed run：

```text
runs/<run_id>/
  manifest.json
  candidates.json
  cards.jsonl
  rejection_report.md
```

并返回：

```text
本次没有找到足够强的结构共振。
最接近的组合是 A / B，但问题是：只是主题相似，缺少共同机制。
建议下一次切换到 temporal-bridge 策略。
```

这很重要。真正的 Ambien-like 系统应该允许“没有梦到有价值的东西”。

---

## 7. 项目目录结构

建议项目名：`ambien-resonance`

```text
ambien-resonance/
├─ README.md
├─ pyproject.toml
├─ qmd.yml
├─ .env.example
├─ .gitignore
│
├─ corpus/
│  ├─ hermes/
│  ├─ openclaw/
│  ├─ vibe-coding/
│  ├─ notebooklm/
│  ├─ home-server/
│  └─ essays/
│
├─ cards/
│  ├─ cards.jsonl
│  └─ by_doc/
│
├─ runs/
│  ├─ latest -> 2026-xx-xx_xxxxxx/
│  └─ 2026-xx-xx_xxxxxx/
│     ├─ manifest.json
│     ├─ seed.json
│     ├─ qmd_results.json
│     ├─ cards.jsonl
│     ├─ pair_report.json
│     ├─ critic_report.json
│     ├─ draft.md
│     └─ report.md
│
├─ drafts/
│  └─ 2026-xx-xx-title.md
│
├─ prompts/
│  ├─ extract_structure.md
│  ├─ compare_cards.md
│  ├─ critic.md
│  ├─ draft_essay.md
│  └─ anti_repetition.md
│
├─ src/
│  └─ ambien_resonance/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ config.py
│     ├─ qmd.py
│     ├─ fs.py
│     ├─ schemas.py
│     ├─ runs.py
│     ├─ cards.py
│     ├─ reports.py
│     └─ utils.py
│
├─ skill/
│  ├─ SKILL.md
│  ├─ scripts/
│  │  ├─ run_once.sh
│  │  ├─ qmd_query.sh
│  │  ├─ save_card.py
│  │  ├─ save_run.py
│  │  ├─ save_draft.py
│  │  └─ inspect_latest.py
│  └─ references/
│     ├─ method.md
│     ├─ scoring-rubric.md
│     ├─ output-format.md
│     └─ examples.md
│
└─ tests/
   ├─ fixtures/
   │  ├─ gold_cases/
   │  └─ bad_cases/
   ├─ test_schemas.py
   ├─ test_runs.py
   └─ test_qmd_wrapper.py
```

---

## 8. CLI 设计

### 8.1 CLI 的定位

CLI 不是智能中枢。

CLI 的职责是：

1. 管理目录结构。
2. 检查依赖。
3. 调用 qmd。
4. 保存 Hermes 生成的中间产物。
5. 维护 latest run。
6. 提供 inspect / validate。
7. 为 Hermes Skill 提供稳定工具接口。

### 8.2 MVP 命令

```bash
ambien-resonance init
ambien-resonance doctor
ambien-resonance index
ambien-resonance qmd-query "关键词或查询"
ambien-resonance start-run --strategy auto
ambien-resonance save-card --run <run_id> --input card.json
ambien-resonance save-pair-report --run <run_id> --input pair_report.json
ambien-resonance save-critic-report --run <run_id> --input critic_report.json
ambien-resonance save-draft --run <run_id> --input draft.md
ambien-resonance inspect --run latest
ambien-resonance validate --run latest
```

### 8.3 暂不实现的命令

MVP 阶段不要实现：

```bash
ambien-resonance llm-call
ambien-resonance embed
ambien-resonance openai
ambien-resonance ollama
ambien-resonance webapp
```

这些命令会把项目方向带偏。

---

## 9. qmd 集成设计

### 9.1 qmd 的职责

qmd 负责：

1. 索引本地 Markdown。
2. embedding。
3. 关键词检索。
4. 语义检索。
5. hybrid query。
6. 返回候选材料。

项目不要重复实现这些能力。

### 9.2 qmd 配置示例

```yaml
collections:
  hermes:
    path: ./corpus/hermes
    pattern: "**/*.md"
  openclaw:
    path: ./corpus/openclaw
    pattern: "**/*.md"
  vibe_coding:
    path: ./corpus/vibe-coding
    pattern: "**/*.md"
  notebooklm:
    path: ./corpus/notebooklm
    pattern: "**/*.md"
  home_server:
    path: ./corpus/home-server
    pattern: "**/*.md"
  essays:
    path: ./corpus/essays
    pattern: "**/*.md"
```

### 9.3 qmd 调用封装

CLI 中只需要封装：

```bash
qmd embed
qmd query --json "..."
```

Python 封装示例：

```python
import json
import subprocess
from pathlib import Path


def qmd_query(query: str, limit: int = 12, cwd: Path | None = None) -> list[dict]:
    cmd = ["qmd", "query", "--json", "-n", str(limit), query]
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)
```

### 9.4 不做自定义 embedding

MVP 不引入：

```text
sentence-transformers
FAISS
Chroma
LanceDB
Ollama /v1/embeddings
```

后续只有当 qmd 召回不够时，才考虑做“structure card embedding”。

---

## 10. Hermes Skill 设计

### 10.1 Skill 的定位

Skill 是用户入口和操作说明书。

Skill 负责告诉 Hermes：

1. 什么时候使用本 Skill。
2. 如何调用 CLI。
3. 如何分步骤完成 daydream cycle。
4. 如何生成和保存 structure card。
5. 如何判断结构共振。
6. 如何生成草稿。
7. 如何返回结果摘要。

### 10.2 SKILL.md 草案

```markdown
---
name: ambien-resonance
description: 在本地资料库中寻找结构共振，并生成 synthesis essay 草稿。
version: 0.1.0
platforms: [macos, linux]
tags: [writing, research, qmd, resonance, local-corpus]
---

# Ambien Resonance

当用户想要从本地资料库中寻找跨材料的深层结构关系、自动生成选题、写 synthesis essay 草稿时，使用本 Skill。

## 核心原则

- 不要把它当成普通 RAG 问答工具。
- 不要只找主题相似。
- 目标是寻找“表面不同但底层结构相似”的材料组合。
- qmd 负责检索和 embedding。
- Hermes 当前驱动模型负责结构抽象、结构比较、critic 和写作。
- CLI 只负责工具调用、文件读写和运行记录。
- 如果没有找到足够强的结构共振，不要硬写文章。

## 标准流程

1. 运行 `ambien-resonance doctor` 检查环境。
2. 运行 `ambien-resonance start-run --strategy auto` 创建 run。
3. 根据本次策略生成 seed query。
4. 调用 `ambien-resonance qmd-query "<query>"` 获取候选材料。
5. 阅读候选材料，抽取 structure card。
6. 调用 `ambien-resonance save-card` 保存 structure card。
7. 比较 cards，判断是否存在结构共振。
8. 运行 critic，拒绝硬凑、重复、证据不足的组合。
9. 如果通过，写一篇 Markdown 草稿。
10. 调用 `ambien-resonance save-draft` 保存草稿。
11. 调用 `ambien-resonance inspect --run latest` 检查结果。
12. 向用户返回简短摘要：材料 A、材料 B、共同结构、草稿路径。

## 返回格式

向用户返回：

- 本次策略
- 选中的材料
- 共同结构一句话
- critic 结论
- 草稿路径
- 如果失败，说明失败原因和下次建议
```

---

## 11. Structure Card 设计

### 11.1 为什么需要 Structure Card

结构共振不能直接在原文上比较。

必须先把每个材料抽象成一个结构卡：

```text
原始材料
  ↓
Hermes 当前模型抽取
  ↓
Structure Card
  ↓
结构比较
```

Structure Card 的目的不是总结文章，而是提取：

1. 主体是谁。
2. 面对什么约束。
3. 核心张力是什么。
4. 发生了什么机制。
5. 如何失败。
6. 如何解决。
7. 能抽象成什么模式。
8. 有哪些原文证据。

### 11.2 Structure Card JSON

```json
{
  "doc_id": "string",
  "chunk_id": "string",
  "title": "string",
  "source_layer": "hermes | openclaw | vibe-coding | notebooklm | home-server | essay | other",
  "surface_topic": "string",
  "entities": ["string"],
  "roles": [
    {
      "entity": "string",
      "role": "string",
      "salience": 0.0
    }
  ],
  "central_tension": "string",
  "mechanism": "string",
  "failure_mode": "string",
  "solution_pattern": "string",
  "boundary_conditions": ["string"],
  "relations": [
    {
      "subject": "string",
      "predicate": "string",
      "object": "string"
    }
  ],
  "abstractions": {
    "surface": "string",
    "schema": "string",
    "meta": "string"
  },
  "evidence_spans": ["string"],
  "weak_structure": false,
  "confidence": 0.0
}
```

### 11.3 抽取提示词

```text
你要从下面的资料片段中抽取 Structure Card。

注意：
你不是在总结文章。
你是在提取它背后的问题结构。

请输出 JSON，不要输出解释文字。

需要包含：
1. 表面主题 surface_topic
2. 主要实体 entities
3. 角色 roles
4. 核心张力 central_tension
5. 机制 mechanism
6. 失败模式 failure_mode
7. 解决模式 solution_pattern
8. 边界条件 boundary_conditions
9. 关系 relations
10. 抽象层 abstractions
11. 原文证据 evidence_spans
12. weak_structure
13. confidence

如果这段材料缺少明确结构，请设置 weak_structure=true。

资料片段：
{{chunk_text}}
```

---

## 12. 结构共振比较设计

### 12.1 比较目标

比较两个 Structure Card 时，不问：

```text
它们是不是同一个话题？
```

而是问：

```text
它们的问题形状是否类似？
它们是否有相似的张力、机制、失败模式或解决模式？
这种相似是否足够非显然？
```

### 12.2 比较提示词

```text
你是结构共振判断器。

你的任务不是判断两份材料是否主题相似。
你的任务是判断它们是否存在“表面不同但底层结构相似”的关系。

请比较 Structure Card A 和 Structure Card B。

重点判断：
1. 核心张力是否相似。
2. 机制是否相似。
3. 失败模式是否相似。
4. 解决模式是否相似。
5. 表面话题是否有足够距离。
6. 是否有足够证据。
7. 是否能写成一篇有价值的文章。
8. 是否只是硬凑。

请输出 JSON：
{
  "verdict": "reject | weak | strong",
  "shared_structure": "一句话说明共同结构",
  "aligned_roles": [],
  "aligned_mechanisms": [],
  "surface_distance": 0.0,
  "structural_alignment": 0.0,
  "evidence_strength": 0.0,
  "novelty": 0.0,
  "essay_potential": 0.0,
  "forced_analogy_penalty": 0.0,
  "final_score": 0.0,
  "rationale": "简短说明"
}
```

### 12.3 评分公式

```text
final_score =
  0.30 * structural_alignment
+ 0.20 * mechanism_similarity
+ 0.15 * surface_distance
+ 0.15 * evidence_strength
+ 0.10 * novelty
+ 0.10 * essay_potential
- forced_analogy_penalty
- repetition_penalty
```

通过门槛：

```text
final_score >= 0.72
verdict == strong
forced_analogy_penalty <= 0.25
```

MVP 中这个分数可以由 Hermes 直接生成，不需要 CLI 自己计算。CLI 只负责保存结果。

---

## 13. Critic 设计

### 13.1 Critic 的作用

Critic 是防止系统胡扯的关键。

它要拒绝：

1. 硬凑类比。
2. 主题相似冒充结构相似。
3. 证据不足。
4. 文章不可展开。
5. 和近期文章重复。
6. 只有漂亮话，没有机制。

### 13.2 Critic 提示词

```text
你是结构共振 critic。

请审查下面的 pair report。
你的任务是尽可能严格地判断它是否值得写成文章。

拒绝以下情况：
- 只是主题相似
- 只是都和 AI / 工具 / 系统有关
- 共同结构过于空泛
- 缺少原文证据
- 不能展开成具体文章
- 与最近草稿重复
- 只是为了写而写

请输出 JSON：
{
  "publishable": true,
  "main_reason": "string",
  "risks": ["string"],
  "required_revisions": ["string"],
  "should_resample": false
}
```

---

## 14. 草稿生成设计

### 14.1 草稿不是最终文章

MVP 输出的是 Markdown 草稿，不是最终成文。

草稿应包括：

1. 标题。
2. 核心论点。
3. 开头。
4. 2-4 个主体部分。
5. 反向解释或限制条件。
6. 结尾。
7. frontmatter。

### 14.2 草稿 frontmatter

```markdown
---
run_id: "2026-05-20-xxxx"
strategy: "random-collision"
source_docs:
  - "corpus/hermes/xxx.md"
  - "corpus/vibe-coding/yyy.md"
shared_structure: "复杂 AI 工具的问题不是能力不足，而是边界管理不足"
critic_score: 0.82
publish_gate: "draft"
created_at: "2026-05-20"
---
```

### 14.3 写作提示词

```text
请基于下面的结构共振报告写一篇中文 synthesis essay 草稿。

要求：
1. 不要暴露 pipeline。
2. 不要说“材料 A / 材料 B”。
3. 不要写成研究报告。
4. 要像一篇可发表的中文经验随笔。
5. 从具体场景开头。
6. 中间揭示共同结构。
7. 结尾回到现实行动建议。
8. 保留一点不确定性，不要过度拔高。

结构共振报告：
{{pair_report}}

相关原文证据：
{{evidence_spans}}
```

---

## 15. 数据与文件格式

### 15.1 Run manifest

```json
{
  "run_id": "2026-05-20-103000-random-collision",
  "created_at": "2026-05-20T10:30:00+09:00",
  "strategy": "random-collision",
  "status": "drafted",
  "seed_query": "复杂工具 小场景 驯化 上下文污染",
  "qmd_results_path": "runs/.../qmd_results.json",
  "cards_path": "runs/.../cards.jsonl",
  "pair_report_path": "runs/.../pair_report.json",
  "critic_report_path": "runs/.../critic_report.json",
  "draft_path": "runs/.../draft.md",
  "exported_draft_path": "drafts/2026-05-20-ai-tools-need-small-scenes.md"
}
```

### 15.2 Pair report

```json
{
  "pair_id": "pair-001",
  "card_a": "card-id-a",
  "card_b": "card-id-b",
  "shared_structure": "string",
  "verdict": "strong",
  "scores": {
    "structural_alignment": 0.83,
    "mechanism_similarity": 0.78,
    "surface_distance": 0.66,
    "evidence_strength": 0.81,
    "novelty": 0.74,
    "essay_potential": 0.86,
    "forced_analogy_penalty": 0.12,
    "final_score": 0.79
  },
  "rationale": "string",
  "evidence": ["string"]
}
```

---

## 16. MVP 开发路线

### 16.1 第 0 步：准备工作

准备：

1. 20-50 篇 Markdown 语料。
2. 5 个好结构共振样本。
3. 5 个坏结构共振样本。
4. qmd 安装完成。
5. Hermes 本地可运行。
6. Codex 可以访问项目目录。

### 16.2 第 1 步：项目骨架

Codex 第一轮只做骨架：

1. `pyproject.toml`
2. `src/ambien_resonance/`
3. Typer CLI
4. 目录初始化
5. qmd wrapper
6. runs 管理
7. JSON schema
8. skill/SKILL.md
9. tests 基础测试

先跑通：

```bash
ambien-resonance init
ambien-resonance doctor
ambien-resonance start-run
ambien-resonance inspect --run latest
```

### 16.3 第 2 步：qmd 检索

实现：

```bash
ambien-resonance index
ambien-resonance qmd-query "复杂工具 小场景 驯化"
```

输出保存到：

```text
runs/latest/qmd_results.json
```

### 16.4 第 3 步：Hermes Skill 流程

让 Skill 能按步骤执行：

1. 创建 run。
2. 生成 query。
3. 调 qmd。
4. 抽卡。
5. 保存卡片。
6. 比较。
7. 保存报告。
8. 写 draft。
9. 保存 draft。

### 16.5 第 4 步：人工测试

用 5 个 gold cases 验证：

1. 是否能召回材料。
2. 是否能抽出合理 structure card。
3. 是否能拒绝坏 case。
4. 是否能写出不空泛的草稿。

---

## 17. 给 Codex 的初始开发提示词

下面这段可以直接给 Codex 作为第一轮开发任务：

```text
请创建一个 Python CLI + Hermes Skill 项目，项目名为 ambien-resonance。

项目目标：
做一个 Hermes Skill-first 的本地资料库结构共振工具。它通过 qmd 检索本地 Markdown 资料，由 Hermes 当前驱动模型完成 structure card 抽取、结构共振比较、critic 判断和 Markdown 草稿生成。Python CLI 不直接调用任何 LLM API。

重要约束：
1. MVP 阶段不要实现独立 LLM client。
2. 不要在 Python 中调用 OpenAI、Ollama、Anthropic、OpenRouter 或任何 OpenAI-compatible API。
3. embedding 不要自己实现，完全交给 qmd。
4. 不要引入 Chroma、FAISS、LanceDB、sentence-transformers。
5. 不要做 WebApp。
6. 不要做数据库服务。
7. CLI 只负责目录管理、qmd wrapper、文件读写、JSON schema 校验、runs 管理和 inspect。
8. Hermes Skill 负责指导 Hermes 当前模型完成所有 LLM 判断和写作。

请实现：
- pyproject.toml
- src/ambien_resonance/cli.py
- src/ambien_resonance/config.py
- src/ambien_resonance/qmd.py
- src/ambien_resonance/runs.py
- src/ambien_resonance/schemas.py
- src/ambien_resonance/fs.py
- skill/SKILL.md
- skill/scripts/run_once.sh
- skill/scripts/inspect_latest.py
- prompts/extract_structure.md
- prompts/compare_cards.md
- prompts/critic.md
- prompts/draft_essay.md
- tests/test_schemas.py
- tests/test_runs.py

CLI 命令：
- ambien-resonance init
- ambien-resonance doctor
- ambien-resonance index
- ambien-resonance qmd-query "..."
- ambien-resonance start-run --strategy auto
- ambien-resonance save-card --run <run_id> --input <json_file>
- ambien-resonance save-pair-report --run <run_id> --input <json_file>
- ambien-resonance save-critic-report --run <run_id> --input <json_file>
- ambien-resonance save-draft --run <run_id> --input <markdown_file>
- ambien-resonance inspect --run latest
- ambien-resonance validate --run latest

项目目录：
- corpus/
- cards/
- runs/
- drafts/
- prompts/
- skill/
- tests/

验收标准：
1. `ambien-resonance init` 可以创建标准目录。
2. `ambien-resonance doctor` 可以检查 qmd 是否安装。
3. `ambien-resonance qmd-query` 可以调用 qmd 并输出 JSON。
4. `ambien-resonance start-run` 可以创建 runs/<run_id>/ 并维护 runs/latest。
5. save-* 命令可以保存 Hermes 生成的 JSON / Markdown。
6. inspect 可以读取 latest run 并输出摘要。
7. 所有中间结果都必须落盘，便于审计。
8. 不允许隐藏式调用 LLM。
```

---

## 18. 风险分析

### 18.1 风险：项目变成普通 RAG

表现：

```text
找几篇相似文章，然后总结一下。
```

应对：

1. 强制 structure card。
2. 强制比较机制和失败模式。
3. critic 拒绝主题相似。
4. 准备 bad cases。

### 18.2 风险：项目变成 WebApp 工程

表现：

```text
开始做前端、后端、数据库、登录、页面管理。
```

应对：

1. MVP 不做 WebApp。
2. 所有输出先用 Markdown。
3. 所有状态先用本地文件。
4. UI 只作为 v2 review dashboard。

### 18.3 风险：CLI 变成独立 AI App

表现：

```text
Python 里开始写 OpenAI client / Ollama client。
```

应对：

1. MVP 禁止 CLI 直接调用 LLM。
2. LLM 判断由 Hermes 当前模型完成。
3. CLI 只做工具层。
4. 后续再预留 provider interface。

### 18.4 风险：qmd 召回不够好

表现：

```text
总是找到同主题材料，找不到远距离结构共振。
```

应对：

1. 改进 seed query。
2. 让 Hermes 生成抽象查询。
3. 使用 tag bridge / temporal bridge。
4. v2 再考虑 structure card embedding。

### 18.5 风险：输出文章空泛

表现：

```text
文章里全是“系统、反馈、复杂性、边界”。
```

应对：

1. 写作前必须有原文 evidence spans。
2. critic 检查是否有具体场景。
3. 要求从具体案例开头。
4. 要求保留反向解释。

---

## 19. 版本路线图

### MVP：跑通一次结构共振循环

目标：

```text
Hermes 调用 Skill，qmd 检索资料，Hermes 判断结构共振，生成草稿并落盘。
```

交付：

1. CLI 工具。
2. qmd wrapper。
3. SKILL.md。
4. runs/ 运行记录。
5. drafts/ 草稿。
6. 5 个 gold cases。

### v1：可审计、可复盘

新增：

1. critic 更严格。
2. anti-repetition。
3. inspect report 更清晰。
4. review 命令。
5. 本地评测集。
6. cron 初步支持。

### v2：更接近 Ambien

新增：

1. random collision。
2. tag bridge。
3. temporal bridge。
4. strategy balancing。
5. failed topology logging。
6. current mode。
7. 可选本地模型 fallback。

### v3：120% 复现

新增：

1. 多跳结构共振。
2. structure card embedding。
3. 简单 review dashboard。
4. 静态博客导出。
5. 更完整 gold set。
6. 自动定时 daydream。

---

## 20. 最终验收标准

### 20.1 100% 复现标准

满足：

1. 有本地 bounded corpus。
2. 使用 qmd 检索。
3. 通过 Hermes Skill 触发。
4. 能主动寻找结构共振。
5. 能生成 synthesis essay 草稿。
6. 能保存运行记录。
7. 能用 frontmatter / runs 影响下一次反重复。
8. 能通过 cron 或手动命令周期运行。

### 20.2 120% 复现标准

额外满足：

1. 每次判断都有 structure card。
2. 每次结构共振都有 pair report。
3. 每次拒绝都有 rejection report。
4. 有 gold cases 和 bad cases。
5. 有 inspect / validate。
6. 有 anti-repetition。
7. 有 failed topology logging。
8. 能稳定在你自己的 Hermes 中部署。
9. 能接入你的 QQ bot 或后续家庭服务器工作流。

---

## 21. 一句话总结

这个项目最正确的形态是：

> **一个 Hermes Skill-first 的本地结构共振系统。Hermes 当前模型负责思考和写作，qmd 负责 embedding 与检索，Python CLI 负责工具化和落盘。MVP 不做 WebApp，不自己调用 LLM，不自己管理 embedding。**

只要这个边界守住，项目就不会跑偏。

