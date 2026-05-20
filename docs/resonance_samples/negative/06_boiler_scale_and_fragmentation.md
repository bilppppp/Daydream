# 06 / 锅炉水垢与磁盘碎片化 (Boiler Scale & Database Fragmentation)

* **来源类型 (Source Type)**: `synthetic_negative`
* **案例分类 (Verdict Class)**: `REJECTED (Far-Miss)`
* **指标得分 (Metrics)**: 表面相似度 `0.72` | 结构同构度 `0.18` | 跨领域跨度 `0.85`

---

## 1. 认识论配对 (Epistemological Pairing)

* **Seed (理论层/原始数据)**: 19 世纪工业蒸汽机史关于锅炉内壁钙镁矿物质结垢（Boiler Scale）层阻碍热传导效率并最终引发物理爆炸的研究。
* **Candidate (行业层/匹配候选)**: 2026 年数据库磁盘物理存储层由于频繁随机增删导致 B+ 树叶分裂、数据页无序碎片化，进而引发磁盘 IOPS 饱和与查询超时。

---

## 2. 反向评估剖析 (Rejection Rationale)

很容易被写成“关于系统累积沉淀导致吞吐阻力增加”的平庸类比。水垢的结晶是一个**“受温度、相变、矿物质饱和度控制的化学析出物理过程”**。磁盘碎片化是一个**“受数据结构设计、存储单元分配算法和随机写入频率影响的逻辑拓扑失序”**。除了“东西堆积了导致变慢”的肤浅感受外，两者并没有像“Ashby 局部调节模型”那样深刻的控制论同构。

---

## 3. 结构映射验证模型 (Unified PairReport Model)

```python
pair_report = PairReport(
    source_type='synthetic_negative',
    seed_document=Document(
        id='steam-boiler-incrustation',
        title='Mineral deposition rates in pressure boilers',
        layer='Annotation',
        summary='Seed summary.',
        source_type='synthetic_negative'
    ),
    resonance_document=Document(
        id='btree-fragmentation-latency',
        title='B+ Tree page fragmentation under randomized delete loads',
        layer='Discourse',
        summary='Resonance summary.',
        source_type='synthetic_negative'
    ),
    isomorphism_score=0.18,
    resonance_verdict=Verdict.REJECTED,
    rejection_reason="Structural misfit: ['chemical_deposition_vs_logical_ordering', 'naive_bottleneck_association']",
    rejection_tags=['chemical_deposition_vs_logical_ordering', 'naive_bottleneck_association'],
    shared_structure={},
    vocabulary_gap_mapping={},
    evidence_excerpts=[
        "Boiler Scaling Analysis (1890): 'Mineral deposition inside steam boilers forms a calcium carbonate scale layer that severely impedes heat transfer, causing localized pressure hazards.'",
        "B+ Tree Storage Mechanics (2026): 'Random database inserts and deletes cause B+ Tree page splits, resulting in physical database page fragmentation and increased random disk I/O latency.'"
    ]
)
```

---

## 4. 原文证据 (Evidence Excerpts)

- *Boiler Scaling Analysis (1890): 'Mineral deposition inside steam boilers forms a calcium carbonate scale layer that severely impedes heat transfer, causing localized pressure hazards.'*
- *B+ Tree Storage Mechanics (2026): 'Random database inserts and deletes cause B+ Tree page splits, resulting in physical database page fragmentation and increased random disk I/O latency.'*
