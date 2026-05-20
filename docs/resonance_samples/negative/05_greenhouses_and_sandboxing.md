# 05 / 温室大棚与沙箱隔离 (Greenhouses & VM Sandboxing)

* **来源类型 (Source Type)**: `synthetic_negative`
* **案例分类 (Verdict Class)**: `REJECTED (Far-Miss)`
* **指标得分 (Metrics)**: 表面相似度 `0.65` | 结构同构度 `0.08` | 跨领域跨度 `0.92`

---

## 1. 认识论配对 (Epistemological Pairing)

* **Seed (理论层/原始数据)**: 农业史关于温室大棚（Greenhouse）利用玻璃对不同波长辐射的透过率（短波透光，长波阻断）来捕获太阳能并锁住室内空气温度的机理研究。
* **Candidate (行业层/匹配候选)**: 2026 年现代操作系统中沙箱隔离技术（VM Sandboxing / Linux Seccomp）限制流氓软件恶意调用特权内核的执行模型。

---

## 2. 反向评估剖析 (Rejection Rationale)

“隔离”一词是两者的表象交点。温室大棚是一个**“基于热力学波长反射和空气对流切断的物理屏障系统”**，其隔离目的是维持内部的能量高态。沙箱隔离则是一个**“基于软件定义特权级、内核调用白名单审查以及进程地址空间映射切断的虚拟安全系统”**，其目的是防止有害指令向外逃逸。除了字面意思“关起来”，两者的机制几何和运行机理毫无关联。

---

## 3. 结构映射验证模型 (Unified PairReport Model)

```python
pair_report = PairReport(
    source_type='synthetic_negative',
    seed_document=Document(
        id='greenhouse-thermodynamics-1900',
        title='Solar trapping in glasshouse structures',
        layer='Annotation',
        summary='Seed summary.',
        source_type='synthetic_negative'
    ),
    resonance_document=Document(
        id='seccomp-process-isolation',
        title='Restricting process namespaces via seccomp filters',
        layer='Discourse',
        summary='Resonance summary.',
        source_type='synthetic_negative'
    ),
    isomorphism_score=0.08,
    resonance_verdict=Verdict.REJECTED,
    rejection_reason="Structural misfit: ['thermodynamic_vs_security_privilege', 'literal_containment_trap']",
    rejection_tags=['thermodynamic_vs_security_privilege', 'literal_containment_trap'],
    shared_structure={},
    vocabulary_gap_mapping={},
    evidence_excerpts=[
        "Greenhouse Thermodynamics (1900): 'Glass greenhouses act as selective radiation filters, transmitting shortwave solar light while blocking outgoing longwave infrared radiation.'",
        "Container Isolation (2026): 'OS process isolation utilizes namespace mapping and kernel privilege level checks (such as seccomp filters) to restrict user-space code execution.'"
    ]
)
```

---

## 4. 原文证据 (Evidence Excerpts)

- *Greenhouse Thermodynamics (1900): 'Glass greenhouses act as selective radiation filters, transmitting shortwave solar light while blocking outgoing longwave infrared radiation.'*
- *Container Isolation (2026): 'OS process isolation utilizes namespace mapping and kernel privilege level checks (such as seccomp filters) to restrict user-space code execution.'*
