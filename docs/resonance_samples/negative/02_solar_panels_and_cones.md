# 02 / 太阳能电池与人眼视网膜 (Solar Panels and Cones)

* **来源类型 (Source Type)**: `synthetic_negative`
* **案例分类 (Verdict Class)**: `REJECTED (Far-Miss)`
* **指标得分 (Metrics)**: 表面相似度 `0.85` | 结构同构度 `0.20` | 跨领域跨度 `0.95`

---

## 1. 认识论配对 (Epistemological Pairing)

* **Seed (理论层/原始数据)**: 生物物理学关于人眼视网膜光感受器（Retinal Phototransduction）的超极化反应与重置速率。
* **Candidate (行业层/匹配候选)**: 2026 年实验室钙钛矿（Perovskite）薄膜太阳能电池的光电激子转移效率。

---

## 2. 反向评估剖析 (Rejection Rationale)

表面上，两者都是关于“吸收光子并转化为电信号（光电转换）”的跨领域物理与生物机制对比，具有强烈的欺骗性。但在工程设计和控制目标上完全相左：太阳能电池的核心目标是**“最大化电能的收集、转化效率与持续平稳输出（高吞吐量能量收集）”**；而视网膜视锥细胞则是**“以极其灵敏的单光子响应进行信息探测，并通过极速的酶促反应对信号进行重置和退激活（低延迟高频信息传导）”**。因此，这是一场将“能量收集”与“信息探测”生硬拉扯在一起的伪科学类比，属于“差例子”（Far-Miss）。

---

## 3. 结构映射验证模型 (Unified PairReport Model)

```python
pair_report = PairReport(
    source_type='synthetic_negative',
    seed_document=Document(
        id='biological-phototransduction',
        title='The biophysics of retinal phototransduction',
        layer='Annotation',
        summary='Seed summary.',
        source_type='synthetic_negative'
    ),
    resonance_document=Document(
        id='perovskite-solar-efficiency-2026',
        title='Efficiency leaps in Perovskite photovoltaic cells',
        layer='Discourse',
        summary='Resonance summary.',
        source_type='synthetic_negative'
    ),
    isomorphism_score=0.20,
    resonance_verdict=Verdict.REJECTED,
    rejection_reason="Structural misfit: ['forced_scientific_comparison', 'incompatible_engineering_bottlenecks']",
    rejection_tags=['forced_scientific_comparison', 'incompatible_engineering_bottlenecks'],
    shared_structure={},
    vocabulary_gap_mapping={},
    evidence_excerpts=[
        "Retinal Biophysics: 'Retinal phototransduction operates via a rapid G-protein cascade that drives hyperpolarization within milliseconds, followed by immediate enzymatic reset to maintain sensitivity.'",
        "Perovskite Photovoltaics (2026): 'Perovskite photovoltaic cells achieve high power conversion efficiency by maximizing the absorption cross-section and maintaining long diffusion lengths for photo-excited charges.'"
    ]
)
```

---

## 4. 原文证据 (Evidence Excerpts)

- *Retinal Biophysics: 'Retinal phototransduction operates via a rapid G-protein cascade that drives hyperpolarization within milliseconds, followed by immediate enzymatic reset to maintain sensitivity.'*
- *Perovskite Photovoltaics (2026): 'Perovskite photovoltaic cells achieve high power conversion efficiency by maximizing the absorption cross-section and maintaining long diffusion lengths for photo-excited charges.'*
