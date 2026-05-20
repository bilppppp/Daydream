# 11 / 双数据库雪崩 (The Two Outages)

* **来源类型 (Source Type)**: `synthetic_negative`
* **案例分类 (Verdict Class)**: `BORDERLINE (Near-Miss)`
* **指标得分 (Metrics)**: 表面相似度 `0.75` | 结构同构度 `0.95` | 跨领域跨度 `0.05`

---

## 1. 认识论配对 (Epistemological Pairing)

* **Seed (理论层/原始数据)**: Stripe 2026 年 3 月大规模并发导致的 Redis 锁死与雪崩事件。
* **Candidate (行业层/匹配候选)**: Supabase 2026 年 4 月由于短时流量冲击导致 Postgres 连接池插槽饱和与请求挂死事故。

---

## 2. 反向评估剖析 (Rejection Rationale)

这属于因果拓扑高度一致但认识论跨度极窄的 Near-Miss 边界案例。两者的底层逻辑完全同构：都在高并发负载下，由于临界共享资源（Redis 锁 / PG 连接池）饱和引发连锁堵塞，进而导致外部 API 网关超时崩溃。然而，由于两件事情**完全发生在现代互联网后端系统工程这同一个狭窄的技术领域内部**（甚至同属于 Hacker News 上的技术故障复盘），这直接违反了 Daydream 寻找“跨领域远距类比与顿悟感”的初心，写出的文章只会退化为平庸平淡的“技术故障对比综述”。

---

## 3. 结构映射验证模型 (Unified PairReport Model)

```python
pair_report = PairReport(
    source_type='synthetic_negative',
    seed_document=Document(
        id='stripe-redis-outage',
        title='Post-mortem on Redis Lock Saturation',
        layer='Discourse',
        summary='Seed summary.',
        source_type='synthetic_negative'
    ),
    resonance_document=Document(
        id='supabase-pg-pool-exhaustion',
        title='Database pool starvation at Supabase',
        layer='Discourse',
        summary='Resonance summary.',
        source_type='synthetic_negative'
    ),
    isomorphism_score=0.95,
    resonance_verdict=Verdict.REJECTED,
    rejection_reason="Structural misfit: ['flat_domain_overlap', 'missing_epistemological_span']",
    rejection_tags=['flat_domain_overlap', 'missing_epistemological_span'],
    shared_structure={},
    vocabulary_gap_mapping={},
    evidence_excerpts=[
        "Stripe Post-Mortem (2026): 'Stripe\\'s post-mortem details how high concurrency led to Redis lock saturation, locking worker threads and causing cascading API gateway timeouts.'",
        "Supabase Post-Mortem (2026): 'Supabase experienced database pool starvation under high transient load, exhausting PostgreSQL connection slots and locking down query routing.'"
    ]
)
```

---

## 4. 原文证据 (Evidence Excerpts)

- *Stripe Post-Mortem (2026): 'Stripe\'s post-mortem details how high concurrency led to Redis lock saturation, locking worker threads and causing cascading API gateway timeouts.'*
- *Supabase Post-Mortem (2026): 'Supabase experienced database pool starvation under high transient load, exhausting PostgreSQL connection slots and locking down query routing.'*
