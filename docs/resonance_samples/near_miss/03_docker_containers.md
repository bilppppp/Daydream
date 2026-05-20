# 13 / Docker 容器与航运集装箱 (Docker Containers and Shipping Containers)

* **来源类型 (Source Type)**: `synthetic_negative`
* **案例分类 (Verdict Class)**: `BORDERLINE (Near-Miss)`
* **指标得分 (Metrics)**: 表面相似度 `0.62` | 结构同构度 `0.92` | 跨领域跨度 `0.40`

---

## 1. 认识论配对 (Epistemological Pairing)

* **Seed (理论层/原始数据)**: 20 世纪海运物流史关于标准集装箱（Standard Shipping Container）发明对全球码头装卸、堆叠、联运效率的工业革命化改观研究。
* **Candidate (行业层/匹配候选)**: 2026 年现代云计算架构中 Docker 容器镜像封装、资源命名空间（Namespace）隔离以及运行时统一交付的标准。

---

## 2. 反向评估剖析 (Rejection Rationale)

这不仅是教科书式的经典隐喻，更是 Docker 名字的直译来源。集装箱标准化对全球航运的“统一接口、消除非标拼箱损耗”与 Docker 镜像对应用程序的“统一封装、消除环境不一致损耗”在底层完全同构。**但因为这个类比过于家喻户晓（零惊喜度/零心智冲突）**，如果把它作为 Daydream 写作引擎的配对，写出来的文章没有任何文学张力或先锋思想启发，纯属普及 IT 常识的软文，应当果断拒绝。

---

## 3. 结构映射验证模型 (Unified PairReport Model)

```python
pair_report = PairReport(
    source_type='synthetic_negative',
    seed_document=Document(
        id='shipping-container-standardization',
        title='Malcom McLean and the containerization of global logistics',
        layer='Annotation',
        summary='Seed summary.',
        source_type='synthetic_negative'
    ),
    resonance_document=Document(
        id='docker-image-specifications',
        title='OCI standard specifications for container runtimes',
        layer='Discourse',
        summary='Resonance summary.',
        source_type='synthetic_negative'
    ),
    isomorphism_score=0.92,
    resonance_verdict=Verdict.REJECTED,
    rejection_reason="Structural misfit: ['literal_textbook_metaphor', 'zero_conceptual_surprise']",
    rejection_tags=['literal_textbook_metaphor', 'zero_conceptual_surprise'],
    shared_structure={},
    vocabulary_gap_mapping={},
    evidence_excerpts=[
        "Maritime Logistics History: 'The standard shipping container revolutionized global logistics by establishing a unified physical interface that eliminated manual break-bulk cargo handling.'",
        "OCI Container Runtime Specifications (2026): 'The Open Container Initiative specifies a standardized virtualization format that bundles application binaries with their runtime namespaces to run uniformly.'"
    ]
)
```

---

## 4. 原文证据 (Evidence Excerpts)

- *Maritime Logistics History: 'The standard shipping container revolutionized global logistics by establishing a unified physical interface that eliminated manual break-bulk cargo handling.'*
- *OCI Container Runtime Specifications (2026): 'The Open Container Initiative specifies a standardized virtualization format that bundles application binaries with their runtime namespaces to run uniformly.'*
