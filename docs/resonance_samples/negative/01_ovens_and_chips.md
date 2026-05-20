# 01 / 烤面包炉与芯片发热 (The Ovens and the Chips)

* **来源类型 (Source Type)**: `synthetic_negative`
* **案例分类 (Verdict Class)**: `REJECTED (Far-Miss)`
* **指标得分 (Metrics)**: 表面相似度 `0.89` | 结构同构度 `0.15` | 跨领域跨度 `0.90`

---

## 1. 认识论配对 (Epistemological Pairing)

* **Seed (理论层/原始数据)**: 1780 年巴黎面包房黏土烤炉的物理储热保温性能研究。
* **Candidate (行业层/匹配候选)**: 2026 年超高密度芯片的 GPU 铜热管耗散与热节流限制。

---

## 2. 反向评估剖析 (Rejection Rationale)

表面上，两者都讨论了关于“温度、热传导、热量保持”等物理词汇，诱导系统建立两者的相似性。然而，两者的物理控制逻辑完全对立：黏土烤炉的核心工程目标是**“利用高比热容材料进行热量保持与闭环蓄热”**，以维持稳定的烘烤温度；而 GPU 散热系统则是**“通过高导热铜介质将多余的热量极速消散，属于开环的温度排斥与耗散”**。这属于表面词汇完全重合但因果拓扑完全冲突的“差例子”（Far-Miss）。

---

## 3. 结构映射验证模型 (Unified PairReport Model)

```python
pair_report = PairReport(
    source_type='synthetic_negative',
    seed_document=Document(
        id='paris-ovens-1780',
        title='Clay ovens of 18th century Paris',
        layer='Annotation',
        summary='Seed summary.',
        source_type='synthetic_negative'
    ),
    resonance_document=Document(
        id='gpu-throttling-2026',
        title='GPU Thermal Throttling in High Density Clusters',
        layer='Discourse',
        summary='Resonance summary.',
        source_type='synthetic_negative'
    ),
    isomorphism_score=0.15,
    resonance_verdict=Verdict.REJECTED,
    rejection_reason="Structural misfit: ['surface_lexical_trap', 'contradictory_causality']",
    rejection_tags=['surface_lexical_trap', 'contradictory_causality'],
    shared_structure={},
    vocabulary_gap_mapping={},
    evidence_excerpts=[
        "Clay Oven Study (1780): 'La construction des fours à pain à Paris en 1780 reposait sur l\\'utilisation de briques d\\'argile épaisse pour retenir la chaleur pendant plusieurs heures.'",
        "GPU Thermal Management (2026): 'Modern high-density GPU nodes rely on copper vapor chambers and high-flow liquid cooling loops to dissipate thermal energy away from the silicon die, triggering hardware throttles if junction temperatures exceed 105C.'"
    ]
)
```

---

## 4. 原文证据 (Evidence Excerpts)

- *Clay Oven Study (1780): 'La construction des fours à pain à Paris en 1780 reposait sur l\'utilisation de briques d\'argile épaisse pour retenir la chaleur pendant plusieurs heures.'*
- *GPU Thermal Management (2026): 'Modern high-density GPU nodes rely on copper vapor chambers and high-flow liquid cooling loops to dissipate thermal energy away from the silicon die, triggering hardware throttles if junction temperatures exceed 105C.'*
