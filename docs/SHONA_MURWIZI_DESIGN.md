# Shona Class-11 Locative `murwizi` — Design (audit only, no implementation)

**Status:** Design/research artefact. Nothing below is implemented.
**Date:** 2026-09-07
**Scope:** `murwizi` only. Audited against the MSUNLI Shona pack, `docs/SHONA_LOCATIVE_DESIGN.md`, and the read-only shona-spacy reference (`shona_spacy/shona_spacy/data/shona_lexicon.json`, MIT).

This document does **not** modify engine code, the pack (lexicon/morphemes/morphotactics/noun_classes/constraints), gold, or independent evaluation data.

---

## Reference annotation (shona-spacy, hand-verified JSON)

Single entry for `Murwizi` (sentence 1235):

| token | lemma | POS | category | morph_features | number | gloss |
|---|---|---|---|---|---|---|
| `Murwizi` | `rwizi` | NOUN | Mupanda 18 | `NounClass=18|Prefix=mu-|Locative|Internal|Natural` | in the river |

Reference model: one locative prefix (`mu-`) + the whole base word `rwizi`. The base's own class prefix is opaque to the reference (it never decomposes `rwizi` into `rw- + izi`, and it does not state the base noun's internal class — the class-11 assignment below comes from Fortune (1984)/standard grammar, not shona-spacy). The token-level noun class is the **locative class 18**; `number: Singular` reflects the singular base.

---

## Findings

### 1. Correct linguistic structure
`murwizi` = "in the river": class-18 locative `mu-` over the class-11 base noun `rwizi` (river). The base itself is `rw- (class 11 prefix) + izi (root)`. In Shona the class-11 prefix is `ru-`, which surfaces as `rw-` (glide before a vowel-initial root). Correct structure:

    mu(18) + rw(11) + izi(stem)

### 2. Base noun class
**11.** `rwizi` is a class-11 noun (ru-/rw- class; pairs with class 10 for the plural — `nzizi`, per `noun_classes.yaml:178-189`, class "11" declares `plural_of: "10"`).

### 3. Correct MSUNLI morpheme decomposition
Fully decomposed, matching the pack's bare-stem convention (cf. `mu-ru-izi`, like `ku-chi-koro`, `mu-mu-sha`):

    mu  → noun-class-18   (outer locative)
    rw  → noun-class-11   (inner base-class prefix, `rw` allomorph)
    izi → stem            (class-11 root; lemma `rwizi`)

Expected output features: `{noun_class: "18", number: singular}` (locative class heads the surface, singular base).

The literal monolithic split `mu(18) + rwizi(stem)` is the *reference* granularity, not the MSUNLI convention — and it is not combinable with the current engine anyway (§8).

### 4. Lemma convention
MSUNLI lemma is inherited from the anchoring stem entry → `rwizi` (stem `izi` lemma `rwizi`, mirroring `koro`→`chikoro`, `sha`→`musha`). Reference lemma: `rwizi`. **Agreed.**

### 5. POS
**noun** (both MSUNLI and reference).

### 6. Surface noun class
**18** — the locative class, headed by the outermost prefix (matching the reference's `NounClass=18` and standard Shona locative concord).

### 7. Required class-11 representation/allomorph
The class-11 morpheme must expose the **`rw` allomorph**. Today (`morphemes.yaml:119-125`) class 11 declares only `aliases: ["ru"]`. The `ru→rw` change before vowel-initial roots is declarable statically as an extra alias (`aliases: ["ru", "rw"]`). For descriptive consistency, `noun_classes.yaml:183` (`surface_allomorphs: ["ru"]` for class "11") should also list `rw` — but that field is documentation/descriptive; the operational change is the morpheme alias.

### 8. Existing generic outer-locative mechanism (Prompt 12) sufficiency
**Yes — sufficient for the decomposed route, as-is.**

With the three declarative pieces of §9 present:
- **Agreement:** outer `mu(18)` is in `constraints.yaml` `outer_classes: ["16","17","18"]`, and there are ≥2 affixes, so the outermost slot is exempt; the inner `ru(11)` must still agree with stem `izi` (class 11) → self-agreement passes.
- **Unifier:** outermost prefix heads `noun_class`/`number` → output class **18** (not the inner 11, not the stem's).

No engine change is needed.

**Caveat (why the monolithic route is not an option today):** the Prompt-12 exemption deliberately applies only when **>1 affix** is present; a single `mu(18)` over a class-11 stem (whole-word `rwizi` stem) is rejected by agreement. That is intended behaviour (prevents spurious analyses) and means the decomposed route is the only consistent target.

### 9. Missing capability
For the decomposed route, everything missing is **declarative data** — no engine behaviour, no morphophonology:

| missing piece | kind | status |
|---|---|---|
| stem `izi` (class 11, lemma `rwizi`, POS noun, singular) in `lexicon.yaml` | **lexical resource** | absent (not in lexicon) |
| `locative-18-over-class-11` rule (`noun-class-18 noun-class-11 stem`) in `morphotactics.yaml` | **morphotactic rule** | absent (18-over-1 and 18-over-3 exist) |
| `rw` alias on the class-11 morpheme in `morphemes.yaml` | **allomorph representation** | absent (only `ru`) |

- **Morphophonology:** NOT required. The `ru→rw` glide is a static, declarable allomorph (an alias), not a computed phonological rule; the engine has no morphophonology stage and none is needed for this word.
- **Generic engine behavior:** NOT required — the Prompt-12 outer-locative mechanism covers both the agreement exemption and the outer-headed class.

### 10. Reference annotation vs MSUNLI representation — conflict?
**No conflict on the surface-level facts.** The reference's lemma (`rwizi`), POS (NOUN), surface class (18), and number (Singular) all agree with the MSUNLI decomposed representation. The only difference is **segmentational granularity**: the reference is flat (`mu-` + opaque base `rwizi`), MSUNLI is fully decomposed (`mu + rw + izi`) — the same documented convention gap as `kuchikoro`/`mumusha` (`docs/SHONA_LOCATIVE_DESIGN.md` §4.1). `source_annotation` is never scored; it is surfaced verbatim in failure reports.

**Data-vs-convention note (not authoritative):** the Prompt-9-authored `independent.yaml` record for `murwizi` (lines 559-580) uses the monolithic expected morphemes `mu(18) + rwizi(stem)` while `kuchikoro` uses the decomposed `ku(18) chi(7) koro` — a known mixed-granularity inconsistency across the locative records (§4.5 of the design doc). Per this prompt's constraints, `independent.yaml` is untouched; any future implementation would re-author these expectations consistently.

---

## What a future implementation would add (design only — NOT implemented)

- `lexicon.yaml`: stem `izi` → lemma `rwizi`, POS noun, `{noun_class: "11", number: singular}`, with provenance citing shona-spacy + Fortune (base class 11).
- `morphotactics.yaml`: `locative-18-over-class-11` → `"noun-class-18 noun-class-11 stem"`, extending the existing stacked-locative pattern.
- `morphemes.yaml`: class-11 `aliases: ["ru", "rw"]` (and, for documentation, `noun_classes.yaml` class-11 `surface_allomorphs`).
- Verify the generic mechanism reproduces: `murwizi` → `analysed`, lemma `rwizi`, POS `noun`, morphemes `mu(18) rw(11) izi(stem)`, features `{noun_class: "18", number: singular}`.

No engine code, no morphophonology, no ML, no new classes.

---

## Files changed & quality checks

**Files changed:** `docs/SHONA_MURWIZI_DESIGN.md` (created). Nothing else.

**Quality checks (msunli-morph-analyser):** run to confirm the audit introduced no changes.
- `pytest` — 137 passed
- `ruff check .` — passed
- `mypy src` — passed

**Reference files read (read-only):** `shona-spacy/shona_spacy/data/shona_lexicon.json` (entry for `Murwizi`, sentence 1235), `msunli-morph-analyser/docs/SHONA_LOCATIVE_DESIGN.md`, current Shona pack (`lexicon.yaml`, `morphemes.yaml`, `morphotactics.yaml`, `noun_classes.yaml`, `constraints.yaml`), `languages/shona/evaluation/independent.yaml` (murwizi record), `languages/shona/evaluation/gold.yaml` (no murwizi probe).