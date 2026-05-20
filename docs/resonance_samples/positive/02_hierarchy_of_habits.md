# 02 / 《习惯的层次》(Hierarchy of Habits) —— 摩尔斯电码与 Context 工程

* **在线链接**: [https://ambien.ai/blog/hierarchy-of-habits](https://ambien.ai/blog/hierarchy-of-habits)
* **来源类型 (Source Type)**: `human_reconstruction`
* **核心标签**: `chunking` · `skill-acquisition` · `context-engineering` · `working-memory` · `plateaus`
* **阅读时间/字数**: 9分钟 / ~2000字
---

---

## 1. 认识论配对 (Epistemological Pairing)

| 认识论层级 | 具体源文本 (Source Materials) | 核心概念/引文 |
| :--- | :--- | :--- |
| **Annotation (理论层)** | 1. Bryan & Harter (1899) *《电报语言研究：习惯层级的习得》*<br>2. George Miller (1956) *《神奇的数字 7±2》*<br>3. 2015 认知科学论文《认知与行为中组块序列的习得》 | **Bryan & Harter 电报平台期 (Plateau)**: 电报员在达到 15 单词/分钟时会遇到瓶颈。突破瓶颈不能靠更快地翻译字母（letter habits），而必须建立词组习惯（word habits）和句子习惯（sentence habits），用高层习惯压制低层动态。<br>**Miller**: 工作记忆的插槽是有限的（4-7个），但每个插槽内组块（chunk）的压缩率决定了真实信息吞吐量。 |
| **Discourse (行业层)** | 1. **Context Engineering** (Andrej Karpathy 2025/2026): “LLM 是 CPU，Context Window 是 RAM。上下文工程就是用恰到好处的高信号 Token 填满 RAM 的艺术。”<br>2. **Anthropic 长期 Agent Harness 研究** (2026): 披露了 Agent 在长程任务中的两种崩溃：在低层细节中迷失（Context 耗尽），或无法区分“任务已做”与“任务做对”（ perception 粒度错误）。 | **Novice Agent (初级代理)**: 把上下文塞满原始的 tool logs（相当于只听得见字母 dit-dah  tones 的电报新手）。<br>**Hierarchical Agent (层级代理)**: 通过持久化 Feature List、Scratchpad、Progress File、Git commit 规范来进行**“假肢组块化 (Prosthetic Chunking)”**，让 Agent 听懂“句子”。 |
| **Systemic (性能危机)** | **Agent 负载衰退** (2026年行业数据) | 当 Agent 上下文中并发任务增加时，由于内存干扰，任务完成率从 16.7% 断崖式下跌至 8.7%。这是“用字母级的感知，去解决句子级任务”的代价。 |

---

---

## 2. 同构结构共鸣 (Isomorphic Structural Resonance)

```
  [ 1899 电报员: 字母 -> 单词 -> 句子 (习惯分层) ]
                        │
                        ▼ (概念同构：工作记忆 slot 恒定，组块压缩率决定上限)
                        │
  [ 2026 编码 Agent: Tool Logs -> Scratchpad -> Milestone Plan ]
  (利用 Context Engineering 实现“假肢组块化”，突破上下文流失的平台期)
```

* **共鸣说明**：1899 年电报员听 Morse 电码遇到 15 wpm 平台期，是因为他们试图在意识中处理每一个字母音调（dit-dah）；现代 AI Agent 遭遇性能瓶颈或 context 溢出，是因为我们将每一步 tool outputs/logs 直接灌入 Context Window（在 Token/字母级别疲于奔命）。
* **突破口**：无论是人类还是 LLM，工作记忆的 slots 都是固定的物理限制（人类约 4 个，LLM 则是注意力退化曲线与有效 KV-cache 的软限制）。突破平台期的唯一路径是**“向上抽象 perceptual unit（感知单元）”**。在 Agent 中，外部的 Milestones Plan、Feature List、Progress file 本质上就是 Karpathy 所说的 “Context Engineering”，是人类为 Agent 编织的**“习惯层级假肢”**。

---

---

## 3. 结构映射验证模型 (Unified PairReport Model)

```python
pair_report = PairReport(
    source_type='human_reconstruction',
    seed_document=Document(
        id='bryan-harter-1899',
        title='Studies on the telegraphic language: the acquisition of a hierarchy of habits',
        layer='Annotation',
        summary='A foundational study showing that telegraphy mastery requires automating lower-level ',
        source_type='human_reconstruction'
    ),
    resonance_document=Document(
        id='anthropic-harness-2026',
        title='Effective harnesses for long-running agents',
        layer='Discourse',
        summary='Anthropic',
        source_type='human_reconstruction'
    ),
    isomorphism_score=0.92,
    resonance_verdict=Verdict.ACCEPTED,
    rejection_reason=None,
    rejection_tags=[],
    shared_structure={
        'fixed_working_memory_slots': '不管是人类的 4 个 Chunks 限制，还是 Agent 在高并发下的注意力衰减，工作记忆插槽都是物理瓶颈。',
        'hierarchical_annihilation': '高级习惯一旦稳定，会‘消灭’低级习惯的感知。优秀的 Agent 应该只读 Milestone，而不用重新感知每一行 bash 执行历史。'
    },
    vocabulary_gap_mapping={
        'letter habits (Bryan & Harter)': 'raw tool outputs / bash stdout / file read content',
        'sentence habits (Bryan & Harter)': 'feature specification / system milestone tracker',
        'telegraphic plateau (15 wpm)': 'context window saturation / task drift at 25%+ load',
        'word habits (Bryan & Harter)': 'scratchpad summary / function-level intent'
    },
    evidence_excerpts=[
        "Bryan & Harter (1899): 'There is a plateau in the acquisition of a habit, during which the learner seems to make no progress... One ceases to perceive the individual letters; he hears words, or even sentences.'",
        "George Miller (1956): 'The span of absolute judgment and the span of immediate memory of humans are in the neighborhood of seven chunks... The process of chunking is the most effective weapon we have to increase the capacity of our working memory.'",
        "Andrej Karpathy (2025): 'LLMs are CPUs; the context window is the RAM. Context engineering is the art of filling this RAM with the highest signal density tokens possible to avoid state saturation.'"
    ]
)
```

---

## 4. 原文证据 (Evidence Excerpts)

- *Bryan & Harter (1899): 'There is a plateau in the acquisition of a habit, during which the learner seems to make no progress... One ceases to perceive the individual letters; he hears words, or even sentences.'*
- *George Miller (1956): 'The span of absolute judgment and the span of immediate memory of humans are in the neighborhood of seven chunks... The process of chunking is the most effective weapon we have to increase the capacity of our working memory.'*
- *Andrej Karpathy (2025): 'LLMs are CPUs; the context window is the RAM. Context engineering is the art of filling this RAM with the highest signal density tokens possible to avoid state saturation.'*
