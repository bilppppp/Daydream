# Ambien Resonance (Daydream) 项目需求与技术设计文档 (V2)

## 0. 文档定位与更新说明

本文档为 **V2 版本**，针对本地 macOS 上开发基于 **Hermes Agent** / **OpenClaw** 的离线第一、定时运行“白日梦共鸣系统”进行最终技术指导。

### V2 核心架构演进：
> 💡 **“脑手彻底解耦”原则**：
> * **脑 (Hermes Brain)**：作为智能中枢，负责所有认知层任务（抽象卡片抽取、结构共鸣比较、Critic 严格盲审、Essay 综合写作）。Hermes 直接调用其当前激活的驱动模型（无论是自部署的 Ollama、官方订阅 Auth 还是云端 API），**Python CLI 内部不包含任何一行 LLM 调用代码**。
> * **手脚与账本 (Python CLI & qmd)**：作为工具与文件存储层，负责本地目录初始化、Pydantic 结构校验、`qmd` 检索封装、中间状态落盘、策略平衡以及防内卷过滤。

---

## 1. 系统总体架构

系统的运行完全依托于 **Hermes Skill (脑)** 与 **本地 CLI (手脚)** 的协同管道。

```text
       ┌────────────────────────────────────────────────────────┐
       │                 Hermes Agent / Cron                    │  (脑：智能驱动)
       │  ┌──────────────────────────────────────────────────┐  │
       │  │                 ambien-resonance                 │  │
       │  │                    SKILL.md                      │  │
       │  └──────┬─────────────────▲─────────────────┬───────┘  │
       └─────────┼─────────────────┼─────────────────┼──────────┘
                 │ 1. 触发/初始化   │ 3. 提取候选卡片   │ 5. 校验并落盘 Cards/Reports/Drafts
                 ▼                 │                 ▼
       ┌───────────────────────────┴────────────────────────────┐
       │                   Python CLI Tool                      │  (手脚：数据与账本)
       │            (ambien-resonance cli wrapper)              │
       └─────────┬───────────────────────────▲──────────────────┘
                 │ 2. 检索请求                │ 4. 返回片段 JSON
                 ▼                           │
       ┌─────────────────────────────────────┴──────────────────┐
       │                   qmd (Local RAG)                      │  (检索底层)
       │    ├─ qmd://corpus (原始高品味知识库，排除 drafts/)     │
       │    └─ qmd://cards  (已生成的结构卡索引)                 │
       └────────────────────────────────────────────────────────┘
```

### 三层职责划分

| 层级 | 组件 | 核心职责 | 特点 |
| :--- | :--- | :--- | :--- |
| **智能层 (脑)** | **Hermes 当前模型** | 1. 依策略生成 Seed Query<br/>2. 抽取 Structure Card JSON<br/>3. 比对结构共鸣并输出 Alignment JSON<br/>4. G-Eval 严格 Critic 盲审打分<br/>5. 撰写高品味 Synthesis Essay | **零硬编码 API Key**，完全使用当前 Agent 激活的模型（本地或云端）。 |
| **检索层 (根)** | **qmd** | 1. 本地 Markdown 索引与管理<br/>2. Qwen3-Embedding 本地向量化<br/>3. BM25 + Vector 混合检索与 Rerank | **纯本地化**，无外部调用，速度极快。 |
| **工具层 (手)** | **Python CLI** | 1. 初始化标准目录与 `qmd.yml`<br/>2. 提供 `start-run` 决定当前 Daydream 策略<br/>3. 封装 `qmd` 检索并返回 JSON 给 Hermes<br/>4. 使用 Pydantic 严格校验所有入参 JSON 结构<br/>5. 状态落盘（`runs/`、`cards/`、`drafts/`） | **无 LLM 依赖**，高稳定性，秒级响应。 |

---

## 2. 核心规避原则 (防内卷/防污染)

> [!IMPORTANT]
> **防生态自我污染 (Anti-Echo Contamination)**：
> 自动生成的 `drafts/` 目录**必须在 `qmd.yml` 索引中被硬性排除**。系统在 Daydream 时只能检索 `corpus/`（用户手工输入的高品味初级语料）与 `cards/`（已经过的抽象卡片），绝对不能召回自己生成的草稿。否则，系统将在数次做梦后进入“LLM 生成内容的自我回授”，导致严重的“幻觉堆叠与模型崩溃”。

---

## 3. 核心概念：结构共鸣 (Structural Resonance)

结构共鸣并非“语义相似”，亦非“主题重合”。它指代的是：**表面话题风马牛不相及，但底层的角色关系、约束条件、张力机制、失败模式或解决路径高度一致。**

### CJK 多语言对齐机制 (Multilingual Bridge)
由于用户的个人语料库大概率存在中英混合、甚至多语言碎片的情况。为保证结构映射的精确性，系统在 Skill Prompts 中要求：
* **原始属性**（如 `surface_topic`, `evidence_spans`）保留原始语言。
* **高阶抽象**（如 `abstractions.l3_functional_roles`, `abstractions.l4_meta_patterns`, `central_tension`）**强制统一使用规范的英文术语/模式名称**进行抽取。
* 这样可确保在 `qmd://cards` 检索和角色二部图匹配时，中英文卡片能够在相同的“高阶逻辑维度”上产生交叉碰撞。

---

## 4. 本地 CLI 命令设计

CLI (`ambien-resonance`) 的职责是做完美的账本与手脚，提供高可用的 Shell 交互接口。

### 4.1 核心命令列表

```bash
# 1. 环境医生：检查 macOS 环境、npm、qmd 安装及本地 Embedding 状态
ambien-resonance doctor

# 2. 目录初始化：在当前 workspace 创建标准文件结构，并自动写入 qmd.yml (配置好 drafts 排除规则)
ambien-resonance init

# 3. 开启做梦轮次：读取 runs/ 历史，基于“策略平衡器”选择本次最少运行的 strategy，返回 run_id
# 策略包括: random-collision (随机碰撞) | tag-bridge (标签桥接) | temporal-bridge (时间跨度桥梁)
ambien-resonance start-run --strategy auto

# 4. qmd 混合检索封装：执行 hybrid search 并直接输出标准化的 JSON 字符串供 Hermes 脑部读取
ambien-resonance qmd-query --collection corpus --limit 12 "Seed Query"

# 5. 校验并落盘 Structure Card：接收 JSON，通过 Pydantic 严格校验，保存为 cards/by_doc/<doc_id>.md 并更新 cards.jsonl
ambien-resonance save-card --run <run_id> --doc <doc_id> --input '<json_string>'

# 6. 校验并落盘共鸣配对报告：保存角色映射与共鸣得分
ambien-resonance save-pair-report --run <run_id> --input '<json_string>'

# 7. 校验并落盘 Critic 盲审报告：保存 G-Eval 盲审结论
ambien-resonance save-critic-report --run <run_id> --input '<json_string>'

# 8. 落盘 Essay 草稿：固化生成的 Synthesis Essay 至 drafts/ 目录，更新 latest run 指针
ambien-resonance save-draft --run <run_id> --title "Title" --input '<markdown_content>'
```

---

## 5. 项目目录结构

项目推荐命名为 `ambien-resonance`，文件结构严谨且扁平：

```text
ambien-resonance/
├─ README.md
├─ pyproject.toml              # 使用 uv / poetry 管理 CLI 的依赖 (pydantic, typer 等)
├─ qmd.yml                     # 自动生成的 qmd 索引配置，硬排除 drafts/ 目录
├─ corpus/                     # 用户的高品味原始语料库 (按专题分类)
│  ├─ hermes/
│  ├─ vibe-coding/
│  └─ essays/
├─ cards/                      # 结构抽象卡
│  ├─ cards.jsonl              # 机器快速读取的索引镜像
│  └─ by_doc/                  # 易于 Git diff 和人眼审阅的结构卡文件
│     └─ doc_001.md            # 包含 YAML frontmatter (Card 结构) + 原文摘要
├─ runs/                       # 做梦运行历史 (全生命周期审计)
│  ├─ latest -> 2026-05-20_113000/
│  └─ 2026-05-20_113000/
│     ├─ manifest.json         # 本次运行元数据 (run_id, strategy, timestamp, status)
│     ├─ qmd_results.json      # 原始检索召回的候选文本
│     ├─ cards.jsonl           # 本次抽取的临时卡片
│     ├─ pair_report.json      # 共鸣配对得分报告
│     ├─ critic_report.json    # G-Eval 盲审打分报告
│     └─ draft.md              # 生成的文章草稿 (若通过)
├─ drafts/                     # 最终生成的草稿集散地 (人眼审阅/修改出口)
│  └─ 2026-05-20-resonance-title.md
├─ src/
│  └─ ambien_resonance/
│     ├─ __init__.py
│     ├─ cli.py                # Typer 命令行分发
│     ├─ schemas.py            # Pydantic 强类型声明
│     ├─ store.py              # 文件读写与状态转移逻辑
│     └─ qmd_wrapper.py        # qmd subprocess 管道封装
└─ skill/                      # 分发给 Hermes / OpenClaw 安装 of Skill 文件夹
   └─ ambien-resonance/
      ├─ SKILL.md              # 智能调度说明书与 Pipeline 编排
      └─ scripts/
         └─ run_loop.sh        # Cron 定时唤醒的自循环 Shell
```

---

## 6. 数据结构 Schema 设计 (Pydantic)

CLI 在保存各个步骤的输入时，通过强类型定义确保“脑”输出的数据质量。

### 6.1 Structure Card Schema

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Role(BaseModel):
    id: str = Field(description="角色ID，例如 R1, R2")
    label: str = Field(description="表层名称")
    function: str = Field(description="深层功能/职责描述，例如 'Buffer stabilizer'")

class Relation(BaseModel):
    src: str = Field(description="源角色ID")
    rel: Literal["causes", "enables", "blocks", "depends_on", "reverses", "contains", "contrasts_with"]
    dst: str = Field(description="目标角色ID")

class AbstractionLevels(BaseModel):
    l1_concrete_events: List[str] = Field(description="具体事件记录")
    l2_generalized_actions: List[str] = Field(description="通用动作抽象")
    l3_functional_roles: List[str] = Field(description="功能角色抽象 (强制英文术语)")
    l4_meta_patterns: List[str] = Field(description="元模式/系统拓扑结构 (强制英文术语)")

class StructureCard(BaseModel):
    card_id: str
    doc_id: str
    title: str
    source_layer: Literal["hermes", "vibe-coding", "essays", "other"]
    surface_topic: str
    central_tension: str = Field(description="核心张力矛盾")
    mechanism: str = Field(description="动作发生机制")
    failure_mode: Optional[str] = Field(None, description="系统崩溃/失败模式")
    solution_pattern: Optional[str] = Field(None, description="解决或平衡机制")
    roles: List[Role]
    relations: List[Relation]
    abstractions: AbstractionLevels
    evidence_spans: List[str] = Field(description="原文引用的精确语句，用于防幻觉审计")
```

### 6.2 Resonance Pair Report Schema

```python
class RoleAlignment(BaseModel):
    src_role_id: str
    dst_role_id: str
    alignment_justification: str

class PairReport(BaseModel):
    run_id: str
    seed_doc_id: str
    candidate_doc_id: str
    shared_structure: str = Field(description="一句话概括的共同底层结构")
    role_alignments: List[RoleAlignment]
    surface_distance: float = Field(description="表面主题距离，0.0 (相同主题) 到 1.0 (完全跨领域)")
    structural_alignment_score: float = Field(description="结构对齐吻合度评分 0.0 ~ 1.0")
    novelty_score: float = Field(description="类比新颖度评分 0.0 ~ 1.0")
```

### 6.3 Critic Report Schema

G-Eval 打分指标，平均分 $\ge 4.0$ 且无一票否决项方可通过：

```python
class CriticReport(BaseModel):
    run_id: str
    scores: dict = Field(
        description="包含: grounded_evidence (1-5), role_alignment (1-5), non_triviality (1-5), surface_independence (1-5)"
    )
    mismatch_notes: str = Field(description="记录该类比不成立、不完美的地方（强制要求，防硬凑）")
    verdict: Literal["accept", "reject", "near_miss"]
    rationale: str
```

---

## 7. Hermes Skill 设计 (SKILL.md)

Skill 是面向 Hermes Agent 的程序蓝图，定义了“脑”如何像编舞一样调用 CLI 和思考。

```markdown
---
name: ambien-resonance
description: 定时或主动在本地知识库寻找结构共鸣，并起草高品味 Synthesis Essay。
version: 0.2.0
platforms: [macos, linux]
metadata:
  hermes:
    category: research
    tags: [analogy, writing, local-rag, synthesis]
    requires_toolsets: [terminal]
    config:
      - key: ambien.project_root
        description: Ambien Resonance 项目根路径
        default: "~/Desktop/AI/daydream"
---

# Ambien Resonance 流程编排

当用户想要发现跨领域笔记的深层相似性，或者触发 Daydream 循环自动写选题草稿时，调用本 Skill。

## 标准执行程序 (Procedural Loop)

1. **进入做梦轮次**：
   * 运行 `ambien-resonance start-run --strategy auto`。
   * 获取 CLI 返回的 `run_id` 和当前执行策略（例如 `temporal-bridge`）。

2. **种子选择与检索**：
   * 脑部思考：根据推荐策略，随机或选择一篇最近的高品味笔记作为 Seed。
   * 脑部思考：为 Seed 提取抽象关键词或反义 Bottleneck 检索词。
   * 运行终端命令：`ambien-resonance qmd-query --collection corpus "<检索词>"` 获取候选片段列表。

3. **结构卡提取 (Structure Card Extraction)**：
   * 针对选中的 Seed 笔记和候选笔记，使用脑部驱动模型抽取 `StructureCard`。
   * **多语言对齐规则**：`abstractions.l3` 和 `l4` 必须翻译并归一化为规范英文概念（如 "Feedback Loops", "Rate Limiter"）。
   * 运行终端命令保存卡片：`ambien-resonance save-card --run <run_id> --doc <doc_id> --input '<JSON>'`。

4. **共鸣比对 (Resonance Comparison)**：
   * 比对两份 Card 的 `abstractions`、`roles` 与 `relations`。
   * 生成 `PairReport` JSON，运行终端命令保存：`ambien-resonance save-pair-report --run <run_id> --input '<JSON>'`。

5. **G-Eval 严格盲审 (Critic)**：
   * 审阅 `PairReport`，进行自我 Critic。必须明确指出该类比的“失效点/硬凑处罚点 (mismatch_notes)”。
   * 评分要求：G-Eval 均分需 $\ge 4.0$。
   * 运行终端命令保存评判：`ambien-resonance save-critic-report --run <run_id> --input '<JSON>'`。

6. **写作或放弃 (Draft or Bail-out)**：
   * **Bail-out 分支**：若被 Critic 拒绝，结束本次做梦，生成 `rejection_report.md`。
   * **Draft 分支**：若通过，调用最强写作脑，撰写 Synthesis Essay（要求：标题、核心 Thesis、三段论、以及专门的一节用于论述“该类比在何处失效”）。
   * 运行终端命令落盘：`ambien-resonance save-draft --run <run_id> --title "<Title>" --input '<MD内容>'`。
   * 向用户/系统推送本日简报。
```

---

## 8. 自动化与调度配置 (Hermes Cron)

通过配置 Hermes 守护进程的 `cron` 调度，系统在无需人眼盯盘时自我运行，静默生产：

```bash
# 每日清晨 6 点，在后台悄悄开启白日梦共鸣流程，并将优秀草稿保存到 drafts 目录
/cron add "0 6 * * *" "运行 ambien-resonance 发现本日结构共鸣并撰写草稿" --skill ambien-resonance --deliver local
```

系统会把最新的运行快照（latest run）保存在 `runs/latest` 软链接中，用户醒来后只需执行：
```bash
# 查看本日“做梦”审计轨迹
ambien-resonance inspect --run latest
```
即可优雅地阅读、审计、修改本日新鲜出炉的洞察文章。
