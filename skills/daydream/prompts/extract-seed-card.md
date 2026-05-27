# Extract Seed Card

Read the selected seed document and return strict JSON matching the Daydream seed-card template.

First perform Seed Distillation / 读薄.

看穿所有论证迷雾，直抵 seed 眼中世界的原初图景。
烧掉辩护，那是为他人准备的。
滤去论证，那是后来添加的。
剥离体系，那是为了说服建构的。
直到剩下那个让它无法不这样看世界的原点。

Output `origin_vision` without explaining it. 像禅师说公案，只呈现。 If it still needs explanation, it is not distilled enough.

Extract:

1. the seed's `origin_vision`,
2. the seed's core meaning,
3. the one claim it most wants to express or prove,
4. concepts at surface, mechanism, and meta levels that can become semantic searches,
5. tensions that deserve echoes,
6. mechanisms that may appear in other domains,
7. failure modes that may rhyme elsewhere,
8. questions worth sending back into the corpus,
9. topic-only search directions to avoid,
10. short exact evidence spans from the seed.

Write semantic `search_text` for `origin_vision`, concepts, mechanisms, and failure modes. Phrase those texts for meaning-based search, not grep. Do not invent evidence that the seed does not provide.
