# Shona Locative Morphology — Design (audit only, no implementation)

**Status:** Design/research artefact. Nothing below is implemented.
**Date:** 2026-09-07
**Scope:** `kuchikoro`, `mumba`, `mumusha`, `murwizi` — audited against the generic MSUNLI engine and the MSUNLI Shona pack, compared with the read-only shona-spacy reference (`shona_spacy/shona_spacy/data/shona_lexicon.json`, MIT).

This document does **not** modify the generic engine, the Shona pack, the lexicon, gold, or independent evaluation data. Its purpose is to determine (a) whether the generic engine already supports the required structure and (b) the smallest declarative changes needed, so implementation can be planned precisely later.

---

## 1. How the reference (shona-spacy) annotates locatives

`shona_component.py` runs JSON-first, then rules. For a token already in `shona_lexicon.json`, the hand-verified entry wins and no rules run. For the four tokens, the JSON entries are hand-annotated and say exactly:

| token | lemma | POS | category | morph_features | number | gloss |
|---|---|---|---|---|---|---|
| `Kuchikoro` | `chikoro` | NOUN | Mupanda 17 | `NounClass=17|Prefix=ku-|Locative|Directional|Educational` | to school |
| `Mumusha` | `musha` | NOUN | Mupanda 18 | `NounClass=18|Prefix=mu-|Locative|Internal|Home` | in the homestead/village |
| `Mumba` | `imba` | NOUN | Mupanda 18 | `NounClass=18|Prefix=mu-|Locative|Internal|Domestic` | inside the house |
| `Murwizi` | `rwizi` | NOUN | Mupanda 18 | `NounClass=18|Prefix=mu-|Locative|Internal|Natural` | in the river |

**Reference analysis model:** locative = one locative prefix (`ku-`/`mu-`/`pa-`) + the base word. The base word keeps its own form and lemma verbatim (`chikoro`, `musha`, `imba`, `rwizi`); the token-level noun class is **the locative class** (17/18); `number: Singular` reflects the (singular) base. The reference never decomposes the base word's own class prefix (`chi-` in `chikoro` is opaque to it), and it does **not** state the base noun's internal class for these tokens — so base classes cited below come from Fortune (1984) and standard reference grammar, not from shona-spacy.

Two quirks of the reference's own rule fallback (unused for these tokens because JSON first-matches) document its model's limits:

- `NOUN_CLASS_PREFIXES` is insertion-ordered (`1, 1a, 2, 3, …, 15, 16, 17, 18`) and the first matching prefix wins. Under the *rules*, `Mumusha` would strip class-1 `mu-` before class-18 is considered, and `Kuchikoro` would strip class-15 `ku-` before class-17 — i.e. the reference's **rule layer cannot distinguish locative `ku-`/`mu-` from the homophonous class-15/class-1 prefixes**. Only the hand-verified JSON gives the locative classes.
- For `Mumba`, stripping `mu-` leaves `mba`, but the lemma is `imba` — the reference silently treats `imba` as having an initial vowel that is not part of the prefixable stem. The base word `imba` therefore cannot be reconstructed by a plain prefix-strip; this is the only one of the four where the reference's own annotation already implies a vowel contraction.

---

## 2. Current MSUNLI state (what the engine + pack already have)

### Declared, generic-capable engine features

- **Morphotactic grammar is explicit sequential slots** — any number of prefix slots may precede the anchoring stem (`morphotactics.yaml:11-16`). The generic engine stacks N prefixes: proven generically by `tests/test_multi_prefix.py` (a fictional two-prefix pack analyses `kamutove` = `ka mu tove`) and in the Shona pack by the conjugated verb `ndaenda` = `nd- a- enda`.
- **Locative morphemes already exist** (`morphemes.yaml`): class 16 `pa`, class 17 `ku`, class 18 `mu` (carry `noun_class` 16/17/18, no number).
- **Three stacked nominal rules are already declared** (`morphotactics.yaml:83-88`): `locative-17-over-class-7` (`ku chi stem`), `locative-18-over-class-1` (`mu mu stem`), `diminutive-12-over-class-1`.
- **Restricting constraints already exist**: `noun-class-agreement` (each prefix class must agree with the stem class, incl. sg/pl partners), `verbal-infinitive-prefix` (verb stems take class 15 only), `verb-slot-stem-pos` (conjugated slots take verb stems only).

### Where each locative currently lands

Running the real pack, all four return `unknown_word` with zero analyses. Re-running with the pack's constraints **removed** shows exactly what the generator + unifier produce on their own:

| surface | with constraints (current) | generator + unifier only (constraints stripped) |
|---|---|---|
| `kuchikoro` | unknown_word | **analysed** `ku(17) chi(7) koro` — lemma `chikoro`, output features `noun_class=7` |
| `mumusha` | unknown_word | unknown_word (no matching rule/stem) |
| `mumba` | unknown_word | unknown_word (no matching rule/stem) |
| `murwizi` | unknown_word | unknown_word (no matching rule/stem) |
| `mumurume` (control for the 18-over-1 rule) | unknown_word | **analysed** `mu(18) mu(1) rume` — lemma `murume`, output `noun_class=1` |

Two engine-level facts are proven by this probe:

1. **The generator already produces stacked locative analyses** (`ku-chi-koro`, `mu-mu-rume`). They are rejected solely by the pack's `noun-class-agreement` constraint, which requires **every** affix class to agree with the stem class (`implementations.py::_noun_class_agreement`). An outer 17/18 can never agree with a class-7/1 stem via `noun_classes.yaml` pairings (16/17/18 have no sg/pl links; class 7 pairs only with 8, etc.). No declarative pairing change can express "outer locative class may differ" — pairing semantics are sing/pl-only.
2. **The feature unifier gives the *inner* prefix precedence** for `noun_class`/`number` (`DefaultFeatureUnifier._PREFIX_HEADED_FEATURES`: affixes merge later-wins, the stem yields). So even a permitted `ku-chi-koro` surfaces as **class 7**, not the reference's class 17.

---

## 3. Per-word findings

### 3.1 `kuchikoro` (to school)

| item | value |
|---|---|
| 1. Surface | `kuchikoro` |
| 2. Morpheme segmentation | MSUNLI: `ku`(17) `chi`(7) `koro`(stem). Reference: `ku-` + base `chikoro` (no inner split). |
| 3. Lemma convention | MSUNLI lemma comes from the anchoring stem entry → `chikoro` (stem `koro` already carries lemma `chikoro` in `lexicon.yaml:297-302`). Same lemma as the reference (`chikoro`). |
| 4. POS | noun |
| 5. noun class / locative class | locative class 17 (reference + expected output); base class 7 on the stem. |
| 6. number | singular (base `chikoro` singular; locative prefixes declare no number). |
| 7. underlying lexical noun class | 7 (`chikoro`; stem `koro` present in the lexicon). |
| 8. construction type | **stacked prefixes** — base class-7 prefix retained, outer locative class-17 prefix added: `ku- + chi- + stem`. |
| 9. required morphotactics | `locative-17-over-class-7` — **already declared** (`ku chi stem`). |
| 10. required constraints | agreement must exempt the **outermost** class-17 prefix; `affix_stem_pos` (class 15 on verb stems) is independent and must stay so `ku`(17) never attaches to verb stems; unifier must head `noun_class` from the outer prefix (today it would output 7). |
| 11. generic engine change necessary? | **Yes** — constraint semantics (allow an outer locative prefix) and unifier head-precedence (outer-prefix-headed `noun_class`/`number`). Neither is expressible in pack data today. Everything else for this word is already in place (rule + stem). |

### 3.2 `mumusha` (in the homestead/village)

| item | value |
|---|---|
| 1. Surface | `mumusha` |
| 2. Morpheme segmentation | MSUNLI decomposed: `mu`(18) `mu`(3) `sha`(stem). Reference: `mu-` + base `musha` (monolithic; its class-3 `mu-` is opaque to the reference). Independent gold (authored during Prompt-9 curation) chose the monolithic form: `mu`(18) `musha`(stem). |
| 3. Lemma convention | MSUNLI: `musha` (stem `sha` lemma `musha`, mirroring `koro`→`chikoro`). Reference: `musha`. Both agree on `musha`. |
| 4. POS | noun |
| 5. noun class / locative class | locative class 18; base class 3 on the stem. |
| 6. number | singular (base `musha` singular). |
| 7. underlying lexical noun class | 3 (`musha`). The stem `sha` is **not** in the lexicon — it requires a future lexicon addition (or the monolithic-stem representation). |
| 8. construction type | **stacked prefixes** (class-18 over class-3) under MSUNLI conventions; single prefix + whole base word under the reference. |
| 9. required morphotactics | `locative-18-over-class-3` (`mu mu stem`) — **not currently declared** (only 18-over-1, 17-over-7, 12-over-1 exist). |
| 10. required constraints | same outer-prefix agreement exemption. Note `mu` is an allomorph of classes 1, 3 **and** 18, so the exemption must apply to the OUTERMOST slot only — otherwise `mukadzi`-type words could gain spurious `mu(18) mu(1) X` analyses. |
| 11. generic engine change necessary? | **Yes** (same two changes as §3.1) **plus** a new declarative rule and a lexicon stem for `sha`. |

### 3.3 `mumba` (inside the house)

| item | value |
|---|---|
| 1. Surface | `mumba` |
| 2. Morpheme segmentation | No literal MSUNLI decomposition: class-18 `mu` + base `imba` → `muimba` ≠ `mumba` (requires initial-vowel elision `i-`→∅, i.e. morphophonology). The reference-signalled split `mu`(18) `mba`(stem) is literal (`mu`+`mba` = `mumba`) but contradicts the reference's own lemma `imba` — it implies base noun `imba` = initial vowel `i-` + stem `mba`, a structure MSUNLI has no declarative mechanism for (zero-prefix + stem would give `imba`; `mu`+`imba` gives `muimba`). |
| 3. Lemma convention | MSUNLI: `imba` (base word), matching reference `imba`. |
| 4. POS | noun |
| 5. noun class / locative class | locative class 18; base class 9 (`imba`). |
| 6. number | singular. |
| 7. underlying lexical noun class | 9 (`imba`); the prefixable stem `mba` / initial-vowel question is unresolved. |
| 8. construction type | **another structure** — base noun with a non-prefix initial vowel (initial-vowel + stem), under a locative prefix. Not a plain class-prefix stack and not a literal single-prefix + stem. |
| 9. required morphotactics | none satisfiable today: `locative-18-over-class-9` (`mu ∅ stem`) would produce `muimba`; the reference's `mu(18) + mba(stem)` needs a stem `mba` that cannot also yield the plain word `imba`. |
| 10. required constraints | vowel elision / initial-vowel handling — no constraint exists, and the generic engine has no morphophonology stage. |
| 11. generic engine change necessary? | **Yes, and more than the others** — a vowel-elision/initial-vowel mechanism (or an explicit lexicalization decision) is required. This is the true hard case and should be treated as a distinct design decision (see §6.3). |

### 3.4 `murwizi` (in the river)

| item | value |
|---|---|
| 1. Surface | `murwizi` |
| 2. Morpheme segmentation | MSUNLI decomposed: `mu`(18) over class-11 base, where the base `rwizi` itself = `rw`(11) `izi`(stem) — but class 11 declares only the alias `ru` (`morphemes.yaml:121`), so `rwizi` cannot be decomposed literally, and stem `izi` is not in the lexicon. Reference: `mu-` + base `rwizi` (monolithic). Independent gold used monolithic `mu`(18) `rwizi`(stem). |
| 3. Lemma convention | MSUNLI: `rwizi` (base word). Reference: `rwizi`. Agreed. |
| 4. POS | noun |
| 5. noun class / locative class | locative class 18; base class 11 (`rwizi`). |
| 6. number | singular. |
| 7. underlying lexical noun class | 11 (`rwizi`; class 11 pairs with class 10 for plural, per `noun_classes.yaml:178-189`). |
| 8. construction type | **stacked prefixes** in principle (class-18 over class-11), but the base cannot be formed with current data; the literal alternative is single prefix + monolithic stem `rwizi`. |
| 9. required morphotactics | `locative-18-over-class-11` (`mu ru stem`) or `locative-18-stem` over a monolithic `rwizi` stem — neither exists; additionally class 11 needs an `rw` allomorph (declarative data) and a stem `izi` (lexicon, future) for the decomposed route. |
| 10. required constraints | same outer-prefix agreement exemption (18 over 11 and 18 over monolithic stem). |
| 11. generic engine change necessary? | **Yes for the stack** (same two changes), but the decomposed route additionally needs class-11 `rw` alias + stem `izi` (declarative/lexicon, future); the reference-style monolithic route needs a lexicon entry `rwizi`. The glide (`ru`→`rw` before a vowel) is declarable as an alias — no engine morphophonology is strictly required for this word if the base is mono-stemmed. |

---

## 4. Reference vs MSUNLI convention — documented disagreements

1. **Flat vs fully decomposed.** The reference analyses a locative as one prefix + the whole base word (`ku-chikoro-like`), never splitting the base's own class prefix. MSUNLI's bare-stem convention decomposes fully (`ku-chi-koro`, `mu-mu-sha`, `mu-ru-izi`). These are the same construction described at two granularities; they are **not** interchangeable gold for lemmas/POS (those agree), but segmentation and `noun_class` features differ.
2. **Where the locative class lives.** Reference stamps the whole token with class 17/18. MSUNLI's natural output today would be the *inner* base class (7/1) because the unifier is inner-prefix-headed. The design must decide the whole-word class is the locative class (17/18) — matching the reference and standard Shona locative concord behaviour.
3. **`mumba`'s own internal contradiction.** The reference segmentation-implied stem (`mba`) is inconsistent with its lemma (`imba`). This is a genuine ambiguity in the source, not resolvable by faithful transcription.
4. **Rule-layer cannot disambiguate homophones.** `shona-spacy`'s rule fallback would mislabel class-15/1 homophones as the locatives (or the locatives as class 1/15); only its hand-verified JSON is reliable for these four, and MSUNLI's agreement + POS constraints exist precisely to avoid that same ambiguity declaratively.
5. **Independent gold mixed granularity (Prompt-9 authored, not source annotation).** The expected analyses in `evaluation/independent.yaml` use three different philosophies: `kuchikoro` fully decomposed (`ku chi koro`), `mumusha`/`murwizi` monolithic (`mu musha`, `mu rwizi`), `mumba` lattice (`mu mba`). This reflects curation decisions and subtle internal inconsistency, and will need re-authoring *at implementation time* (not now).

---

## 5. Proposed declarative representation (design only — NOT implemented)

Recommended target (when implementation is approved):

- **Morphotactics** — keep the existing `locative-17-over-class-7`; add stacked rules for the base classes actually attested: `locative-18-over-class-3` (`mu mu stem`), `locative-18-over-class-11` (`mu ru stem`), and, if the initial-vowel question is resolved, `locative-18-over-class-9` (`mu ∅ stem`). Extend the same pattern to class 16 `pa`. All rules stay plain sequential slots — no grammar extension needed.
- **Constraints** — extend the declarative agreement semantics so `noun_class_agreement` (or a sibling kind) accepts an **outer-prefix class set** (`params.outer_classes: ["16","17","18"]`): only the outermost prefix may carry an outer class, it is exempt from base-class agreement, and all *inner* prefixes must still agree with the stem class (incl. sg/pl pairing). This is small and generic; it also preserves the existing `affix_stem_pos` behaviour (`ku`(17) never on verb stems; `kufamba` stays class 15).
- **Feature semantics** — whole-word `noun_class`/`number` for a stacked nominal analysis must be headed by the outer (locative) prefix (class 17/18), matching the reference and Shona locative concord behaviour.
- **Data** — future lexicon additions for base-word stems (`sha` for `musha`, `izi` for `rwizi`), and a class-11 `rw` allomorph in `morphemes.yaml` if the decomposed `murwizi` route is chosen.
- **`mumba`** — requires an explicit decision (§6.3) rather than a mechanical data change.

### Declarative vs engine change summary

| needed piece | declarative pack data | generic engine change |
|---|---|---|
| stacked rules (17-over-7 exists; 18-over-3/11/9 new) | yes | no |
| `rw` allomorph for class 11 | yes (`morphemes.yaml`) | no |
| lexicon stems (`sha`, `izi`) | yes (future, via normal curation) | no |
| outer-prefix agreement exemption | **no** — not expressible today | **yes** (extend/parametrise agreement kind) |
| outer-prefix-headed `noun_class`/`number` | **no** | **yes** (unifier head/precedence semantics) |
| `mumba` vowel elision | **no** | **yes** (morphophonology stage) — or a lexicalization decision |

The honest bottom line: **a purely declarative change does not exist today.** Two small, generic engine changes (constraint semantics + unifier head-precedence) unlock `kuchikoro` immediately and `mumusha`/`murwizi` once their rules/stems are added; `mumba` additionally needs a morphophonology decision.

---

## 6. Ambiguities / conflicts discovered

### 6.1 Outer-slot-only exemption
`mu` and `ku` are homophonous across classes (15/17/18 `ku`; 1/3/18 `mu`). Any agreement relaxation must apply to the **outermost** prefix slot only, or spurious analyses appear (e.g. `mukadzi` as `mu(18) mu(1) X`). This is guarded by keeping the exemption inside the stacked rules' outer slot and by the unifier head decision.

### 6.2 Base-noun class sourcing
The reference locative entries never state the base noun's internal class (chikoro/musha/imba/rwizi). The class assignments used here (7/3/9/11) come from Fortune-based grammar, not from shona-spacy — a provenance gap to note for gold authorship.

### 6.3 `mumba` / the initial-vowel problem
`imba` behaves as `i-` + `mba` where the `i-` is not a class prefix. Declarative options for a future implementation: (a) a vowel-initial-stem mechanism (engine), (b) a lexical dual-entry (`imba`/`mba`) with a documented convention, or (c) accept `mumba` as a curated whole-word lexical entry. Each has different lemma/features trade-offs; this needs a separate decision.

### 6.4 Independent gold granularity
`independent.yaml` mixes decomposed and monolithic expected morphemes for these four (§4.5). Any future implementation must re-author these expectations consistently (single philosophy) and re-derive the `mumba` gold probe (`gold.yaml:1287` currently `unknown_word`) — all deferred, per this prompt's constraints.

### 6.5 `number` semantics
Locative prefixes declare no `number`; `number: Singular` on these tokens reflects the singular base. Full-decomposed analyses must not attach plurality of the base to the locative surface (and base-plural locatives such as `mumapako` are out of today's scope).

---

## 7. Out of scope (explicitly not done here)

- Generic engine code: **untouched** (constraint/unifier changes are recommendations only).
- Pack data (morphotactics, morphemes, lexicon, constraints, noun_classes): **untouched**.
- Gold and independent evaluation data: **untouched**; no score changes.
- Class 19/20/21, diminutives/augmentatives, corpus imports, ML: **untouched**.
- Tests: the existing suite already documents the required generic capability (`tests/test_multi_prefix.py`: fictional two-prefix analyses + Shona "declared-but-rejected" pins, e.g. `kuchikoro`/`kamukadzi`/`mumurume` → `unknown_word`); no new implementation tests were added for an unimplemented feature.

---

## 8. Files changed & quality checks

**Files changed:** `docs/SHONA_LOCATIVE_DESIGN.md` (created). Nothing else.

**Quality checks (msunli-morph-analyser):**
- `pytest` — 131 passed
- `ruff check .` — passed
- `mypy src` — passed

**Reference files read (read-only):** `shona-spacy/shona_spacy/data/shona_lexicon.json`, `shona-spacy/shona_spacy/shona_component.py`, `msunli-morph-analyser/docs/SHONA_RESOURCE_AUDIT.md`.