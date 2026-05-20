# 03 / 飞轮储能与计算机主频 (Flywheel Energy & CPU Clock Rate)

* **来源类型 (Source Type)**: `synthetic_negative`
* **案例分类 (Verdict Class)**: `REJECTED (Far-Miss)`
* **指标得分 (Metrics)**: 表面相似度 `0.70` | 结构同构度 `0.10` | 跨领域跨度 `0.85`

---

## 1. 认识论配对 (Epistemological Pairing)

* **Seed (理论层/原始数据)**: 工业机械史关于飞轮（Flywheel）通过大质量物理旋转角动量守恒来稳定蒸汽机动力输出的研究。
* **Candidate (行业层/匹配候选)**: 2026 年芯片超频（Overclocking）与时钟周期发生器（Clock signal generator）的高频逻辑状态切换。

---

## 2. 反向评估剖析 (Rejection Rationale)

表面上，两者都讨论“旋转/频率/周期/能量储存”以维持系统的稳定运转。但在控制论图谱上，飞轮依靠**“物理质量的动能惯性”**平滑物理波动，这属于连续的机械阻尼；而 CPU 时钟周期则是**“通过压电效应产生极其纯净的方波，驱动数十亿硅晶体管进行离散的逻辑状态翻转”**。这根本不需要物理惯性，反而要极力消除任何物理漂移。两者因果逻辑全无映射，属于生拉硬扯。

---

## 3. 结构映射验证模型 (Unified PairReport Model)

```python
pair_report = PairReport(
    source_type='synthetic_negative',
    seed_document=Document(
        id='steam-flywheel-1850',
        title='Kinetic stabilization of mechanical flywheels',
        layer='Annotation',
        summary='Seed summary.',
        source_type='synthetic_negative'
    ),
    resonance_document=Document(
        id='cpu-overclock-clock-2026',
        title='Latching stability in high-frequency CPU clocking',
        layer='Discourse',
        summary='Resonance summary.',
        source_type='synthetic_negative'
    ),
    isomorphism_score=0.10,
    resonance_verdict=Verdict.REJECTED,
    rejection_reason="Structural misfit: ['mechanical_vs_discrete_logic', 'lexical_spin_clash']",
    rejection_tags=['mechanical_vs_discrete_logic', 'lexical_spin_clash'],
    shared_structure={},
    vocabulary_gap_mapping={},
    evidence_excerpts=[
        "Steam Engine Flywheel (1850): 'The large physical mass of the steam engine\\'s flywheel stores kinetic energy to smooth out the continuous rotational velocity variations.'",
        "CPU Microarchitecture (2026): 'The quartz crystal oscillator generates a stable, high-frequency square wave to synchronize discrete transistor state switching inside digital microprocessors.'"
    ]
)
```

---

## 4. 原文证据 (Evidence Excerpts)

- *Steam Engine Flywheel (1850): 'The large physical mass of the steam engine\'s flywheel stores kinetic energy to smooth out the continuous rotational velocity variations.'*
- *CPU Microarchitecture (2026): 'The quartz crystal oscillator generates a stable, high-frequency square wave to synchronize discrete transistor state switching inside digital microprocessors.'*
