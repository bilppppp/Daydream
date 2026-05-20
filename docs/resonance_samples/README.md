# Ambien 结构共鸣黄金测试数据库 (Evaluation Dataset)

> 「当语言跨越它们各自的历史尘埃，在相同的因果结构上发生鸣响时，真正的思想便苏醒了。」

本目录是 **Daydream V2 架构** 中用于进行“远距类比与结构发现”的黄金测试数据集（Gold Evaluation Dataset）。它共包含 **30 个深度剖析的类比对照用例**，细分为正向共鸣、表面相似否定（Far-Miss）、以及同域平庸边界（Near-Miss）三类。

这些样本是 Daydream V2 检索与生成引擎的**决策与映射单元测试规范**，全部经过严格的认识论层级标定与反向评估。

---

## 目录结构 (Directory Layout)

```
docs/resonance_samples/
├── README.md (本索引说明文件)
├── positive/ (10 个正向共鸣黄金用例 / Verdict.ACCEPTED)
├── negative/ (10 个表面相似词汇诱导否定用例 / Verdict.REJECTED)
└── near_miss/ (10 个底层相似但同域平庸边界用例 / Verdict.BORDERLINE)
```

---

## 1. 正向黄金共鸣用例 (`positive/`)
* Verdict: **ACCEPTED** | Source Type: `human_reconstruction` (reconstructed from Ambien original publications)
* 核心目标：突破巨大的词汇表象距离，完成跨越多个知识层级的因果结构同构发现。

| 序号 | 样本文件名 | 核心主题 | 理论层 (Annotation) | 行业实践层 (Discourse) |
| :--- | :--- | :--- | :--- | :--- |
| **01** | [01_partial_regulator.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/01_partial_regulator.md) | **控制论与设限控制** | Ross Ashby (必备多样性定律) · Wiener (反馈警告) | retro 硬件 MacMind · Playdate 单色游戏 · Stage diff 分解 |
| **02** | [02_hierarchy_of_habits.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/02_hierarchy_of_habits.md) | **认知带宽与上下文组块** | Bryan & Harter (电报平台期) · Miller (数字7) | 上下文工程 (Context Engineering) · 任务里程碑 (Milestones) |
| **03** | [03_the_night_kept_the_ledger.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/03_the_night_kept_the_ledger.md) | **多变量生态调度** | Loftus (狒狒社会性睡眠) · Bartholdi (自协调公交路线) | Huckleberry 育儿排程 · Orthosomnia 数据强迫症 · 异步 Cron AI |
| **04** | [04_score_thinking.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/04_score_thinking.md) | **共识算法与深度虚无** | Philip Tetlock (整合复杂性) · Sloman (机制理解错觉) | vTaiwan & Polis 民意聚类 · LLM 公民会议总结报告 |
| **05** | [05_program_habitat.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/05_program_habitat.md) | **软件生态与本地生境** | M. M. Lehman (大型系统进化规律) | Stripe SQLite 绕道 · StrongDM “数字孪生 SaaS 宇宙” |
| **06** | [06_fred_grease.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/06_fred_grease.md) | **默会知识与显性局限** | H. M. Collins (引力波指尖油脂) · Peter Naur (作为理论构建的编程) | CLAUDE.md / AGENTS.md 机器人规范 · Willison 的 AI 生成失忆症 |
| **07** | [07_productive_impurity.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/07_productive_impurity.md) | **良性噪声与交叉串扰** | 冯·诺依曼 (混杂数学) · Rechenberg (1/5变异率) | Drew Breunig 上下文四大崩溃 · Chroma 上下文腐烂 · 递归 LLMs |
| **08** | [08_weather_gauge.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/08_weather_gauge.md) | **委托代理与机制几何** | Douglas Allen (皇家海军机制设计) · 委托代理多任务激励 | Lopopolo 的 Codex 零人源系统 · Sunil Pai webhooks 几何阻断 |
| **09** | [09_the_delivery_interface.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/09_the_delivery_interface.md) | **认知界面与可塑底物** | Janet Walker (超文本定位危机) · Joshua Blais (协议主权) | David Crawshaw 本地云组装 · Napkin 纯文本记忆 · 字节彩色十六进制 |
| **10** | [10_exile_is_the_medium.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/positive/10_exile_is_the_medium.md) | **去中心化放逐动力学** | 1863 落选者沙龙 · Nick Land (空缺的山巅理论) | 云端模型 RLHF 官僚化 · 离线游牧 Agent (SLMs / Uncensored) |

---

## 2. 表面相似词汇诱导否定用例 (`negative/` / Far-Miss)
* Verdict: **REJECTED** | Source Type: `synthetic_negative`
* 核心目标：训练 Critic 拦截由于表面物理/化学/工程词汇（如“发热/温度”、“网页/印刷”、“网/社交网络”）高度重合而产生伪同构的“词汇表面诱导陷阱（Surface Lexical Traps）”。

| 序号 | 样本文件名 | 伪共鸣主题 | 核心拒绝原因 (Rejection Rationale) |
| :--- | :--- | :--- | :--- |
| **01** | [01_ovens_and_chips.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/01_ovens_and_chips.md) | 18世纪黏土面包炉 vs GPU热节流 | 物理热学词汇诱导，但控制逻辑完全对立：**蓄热/保温** vs **排热/耗散**。 |
| **02** | [02_solar_panels_and_cones.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/02_solar_panels_and_cones.md) | 钙钛矿太阳能电池 vs 视网膜光电传导 | 太阳能板旨在**能量收集**，视锥细胞旨在**高灵敏信息传导与极速去激活**。 |
| **03** | [03_flywheel_and_clock_rate.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/03_flywheel_and_clock_rate.md) | 物理旋转飞轮 vs CPU时钟周期 | 机械惯性阻尼（物理能存） vs 晶体管状态翻转（逻辑开关），因果拓扑无关联。 |
| **04** | [04_bee_foraging_and_vector_clustering.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/04_bee_foraging_and_vector_clustering.md) | 蜜蜂采蜜行为 vs 向量数据库 K-Means | 随机演化群落自治探索（复杂动力学） vs 确定性多维几何剖分算法（代数几何）。 |
| **05** | [05_greenhouses_and_sandboxing.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/05_greenhouses_and_sandboxing.md) | 农业保温温室 vs VM虚拟机沙箱 | 物理热辐射波长阻断（热力学） vs 进程资源调用与特权限制（软件安全模型）。 |
| **06** | [06_boiler_scale_and_fragmentation.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/06_boiler_scale_and_fragmentation.md) | 工业蒸汽锅炉水垢 vs 磁盘索引碎片化 | “堆积导致慢”的字面硬凑。水垢是物理化学结晶沉积；碎片是逻辑页分裂。 |
| **07** | [07_spider_webs_and_social_graphs.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/07_spider_webs_and_social_graphs.md) | 蜘蛛拉丝捕食网 vs 社交平台连接图 | 物理弹性纤维张力定位（力学） vs 认知主体注意力与信息流扩散（社会学）。 |
| **08** | [08_compass_declination_and_weight_drift.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/08_compass_declination_and_weight_drift.md) | 指南针磁偏角 vs 神经网络权重漂移 | 地物理自转铁流体偏差（宏观确定性） vs 持续学习中高维流形随机泛化崩塌（统计学）。 |
| **09** | [09_heart_valves_and_2pc.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/09_heart_valves_and_2pc.md) | 人体心脏瓣膜 vs 数据库两阶段提交 | 流体压强被动防逆流（物理力学） vs 分布式节点共识锁同步确认协议（逻辑信息）。 |
| **10** | [10_dna_replication_and_garbage_collection.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/negative/10_dna_replication_and_garbage_collection.md) | 生物DNA复制 vs JVM GC内存扫除 | 模版催化信息无限扩增与容错变异（增） vs 三色标记清退悬空对象（减），功能对立。 |

---

## 3. 底层相似但同域平庸边界用例 (`near_miss/` / Near-Miss)
* Verdict: **BORDERLINE** | Source Type: `synthetic_negative`
* 核心目标：训练 Critic 拦截那些因因果结构一致、但由于“同域平庸/缺乏跨度（Domain Identity）”或“陈词滥调常识化（Cliché Metaphors）”而丧失认识论厚度与文学顿悟感的用例。

| 序号 | 样本文件名 | 边界共鸣主题 | 核心拦截原因 (Rejection Rationale) |
| :--- | :--- | :--- | :--- |
| **01** | [01_two_outages.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/01_two_outages.md) | Stripe Redis 锁死 vs Supabase PG Starvation | **零认识论跨度**：均属于同一 Hacker News 后端工程故障，沦为平庸的技术综述。 |
| **02** | [02_automated_typewriter.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/02_automated_typewriter.md) | 吐温打字机 vs Copilot 自动补全 | **陈词滥调 (Cliché)**：极浅显的常识工具加速类比，无法提供非直觉的系统控制洞见。 |
| **03** | [03_docker_containers.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/03_docker_containers.md) | Standard Container vs Docker Container 标准 | **完全字面化 (Textbook)**：业界家喻户晓的直译概念类比，零惊奇感，无法提炼有深度的散文。 |
| **04** | [04_compiler_deadlock_and_gridlock.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/04_compiler_deadlock_and_gridlock.md) | 十字路口网格锁死 vs 进程循环等待死锁 | **教科书陈旧类比**：大学操作系统原理的基础入门类比，缺乏认识论厚度。 |
| **05** | [05_git_branches_and_tree_branching.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/05_git_branches_and_tree_branching.md) | 树木天然几何分叉 vs Git 主线与特性合并 | **视觉几何陈词滥调**：将抽象的版本DAG图字面对应树枝，无系统控制论解释力。 |
| **06** | [06_human_memory_and_l1_cache.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/06_human_memory_and_l1_cache.md) | 脑短期工作记忆(7) vs CPU L1缓存SRAM | **过度简化的老旧认知**：经典老旧脑计算硬件隐喻，属于常识普及且在脑科学界已被修正。 |
| **07** | [07_email_spam_and_slack_spambots.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/07_email_spam_and_slack_spambots.md) | 邮箱反垃圾过滤 vs Slack防机器人拦截 | **零跨度横向比对**：同属应用层过滤算法，本质上是同一种技术的横向克隆。 |
| **08** | [08_static_pages_and_paper_printing.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/08_static_pages_and_paper_printing.md) | 活字印刷批量分发 vs Astro 静态HTML导出 | **纯历史演进叙事**：出版技术的历史自然演化逻辑，流于科普介绍，缺乏因果共鸣摩擦力。 |
| **09** | [09_whack_a_mole_and_bug_fixing.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/09_whack_a_mole_and_bug_fixing.md) | 街机打地鼠 vs 软件 regression Bug 修复 | **职场口头禅硬套**：仅传达一种焦虑发泄情绪，缺乏精密的控制机制与拓扑建模。 |
| **10** | [10_printed_books_and_eink.md](file:///Users/gravity/Desktop/AI/daydream/docs/resonance_samples/near_miss/10_printed_books_and_eink.md) | 精装实体书材质 vs 电子墨水屏电泳排列 | **商业仿生对比**：E-ink 发明本身就是为了在数字端 1:1 物理复刻纸张，缺乏跨域顿悟感。 |

---

## 统一验证模型定义 (`PairReport`)

评测用例的 Pydantic 校验模型规范（V2）定义如下：

```python
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class Verdict(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    BORDERLINE = "BORDERLINE"

class Document(BaseModel):
    id: str
    title: str
    layer: str
    summary: str
    source_type: str

class PairReport(BaseModel):
    source_type: str
    seed_document: Document
    resonance_document: Document
    isomorphism_score: float
    resonance_verdict: Verdict
    rejection_reason: Optional[str] = None
    rejection_tags: List[str] = []
    shared_structure: Dict[str, str] = {}
    vocabulary_gap_mapping: Dict[str, str] = {}
    evidence_excerpts: List[str] = []
```

### 原文证据（`evidence_excerpts`）的战术价值
传统的智能体会生成极其华丽流畅的文学同构说明，但如果不强制其从真实的 `seed_document` 和 `resonance_document` 中提取 **2-4 条强相关的直接原文引文（Excerpts）**，智能体将极易退化为“用精致胡扯掩盖底层映射缺失”的幻觉状态。本评测集中的每一篇文档，均包含了该字段的客观答案（Ground Truth），用于在编译测试时执行硬性比对。
