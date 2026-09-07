# Shona Resource Audit

**Status:** Resource survey only — no imports, no engine changes, no lexicon expansion, no gold-data generation.
**Date:** 2026-09-07
**Scope:** `shona-spacy` (rule-based spaCy NLP pipeline) and `shona_moph` (WebIK/hybrid neural+rule analyser) reviewed as READ-ONLY references for eventual import into MSUNLI (`msunli-morph-analyser`).

This document does **not** modify the MSUNLI engine. It is a planning artefact summarising what each reference project offers, licensing, areas of conflict/uncertainty, and what should (and should not) be copied.

---

## 1. What `shona-spacy` offers

`shona-spacy` is a rule-based Shona NLP pipeline for spaCy (v0.1.0) by Happymore Masoka, **MIT licensed**. It does JSON-first lexicon lookup, then closed-class matching, then rule-based morphological parsing.

### Useful lexical resources

- **`shona_spacy/data/shona_lexicon.json`** (2,583 lines) — a **hand-annotated** lexicon of ~130+ Shona tokens. Each entry carries:
  - `token`, `lemma`, `pos` (NOUN, VERB, PRON, ADJ, ADV, NUM, IDEOPH)
  - `category_detail` — noun-class label (`Mupanda 1`…`20`, Diminutive, Augmentative, Independent, Possessive, ObjectPrefix, Reflexive, Demonstrative, Relative)
  - `morph_features`, `tense`, `aspect`, `mood`, `person`, `number`, `gender`, `clitic_type`, `dependency_relation`, `gloss` (English translation), `comments`
  - Many entries marked **`Verified manually`**

### Noun-class information

- `shona_component.py:31-40` — `NOUN_CLASS_PREFIXES` mapping classes 1, 1a, 2–10, 15–18 to surface prefixes.
- `mipanda.ipynb` — the most complete noun-class reference in the repo: **24 classes** with human-readable labels including nuances: 1a (null, proper nouns), 2a (Manyika a/va mismatch), 2b (Zezuru a-), 19 (sv-/svi- Karanga), 21 (zi- augmentative), 12/13 (ka-/tu- diminutive), 15/16/17/18 (ku-/pa-/ku-/mu- locatives + infinitive).

### POS / features

- POS inventory: NOUN, VERB, PRON, DET, ADV, CCONJ, ADJ, NUM, IDEOPH, X.
- Feature strings like `NounClass=1|Rule=True`, `Person=1|Number=Singular|Independent=True`, plus `Locative`, `ProperNoun`, `Reduplicated` markers.

### Manually verified annotations

- The JSON lexicon is the core manually verified resource — entries explicitly commented `Verified manually`.
- `shona_tokens_with_classes.csv` (178,765 lines) — a **large automatically annotated** corpus (social-media/chat dataset) with token, normalised form, matched prefix, numeric class, and human-readable class label. This is rule-generated, not hand-verified.

### Closed-class vocabulary

- `shona_component.py:48-53` — `CLOSED_CLASS` word lists: ADV (`mangwanani`, `mangwana`, `zvishoma`, `zvikuru`, `chaizvo`), PRON (`ini`, `iwe`, `iye`, `isu`, `imi`, `ivo`), DET (`uyu`, `uyo`, `ichi`, `icho`, `izi`, `izo`), CCONJ (`kana`, `asi`, `nekuti`, `uye`).
- The lexicon also contains full pronoun sets: independent, possessive, object prefixes, reflexives, demonstratives, relatives (sentence_ids 1500–1547).

### Useful corpus resources

- `shona_tokens_with_classes.csv` — raw token-frequency/prefix-labelling corpus (noisy, code-mixed, rule-labelled).
- `Untitled113.ipynb` / `map101 (2).ipynb` — notebooks encoding inflectional-prefix and derivational-suffix lists, a seed lemma dictionary, and root lexicons (famb, gar, tuk, bik, sung, dy, etc.).

---

## 2. What `shona_moph` offers

`shona_moph` is a Streamlit app performing **hybrid neural + rule-based** Shona morphology analysis. **No LICENSE file present.** Dependencies (tensorflow, streamlit, etc.) via `requirements.txt` (unpinned).

### Noun-class knowledge

- `fortune_grammar.py` / `app.py` — `SHONA_CLASS_MAP` based explicitly on **George Fortune's "Shona Grammatical Constructions"**. Encodes classes 1, 2, 2a, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21 with **meaning, number, and singular/plural pairing** (e.g. `mu`→[Cl.1 person, Cl.3 tree, Cl.18 locative]; `ku`→[Cl.15 infinitive, Cl.17 locative]).
- Adds `svi`→Cl.19 and `zi`→Cl.21 beyond the base Fortune table, each with a `priority` ranking for disambiguation.
- `app.py:162-165` — a `select_best_class()` heuristic with **stem category lists** used to disambiguate ambiguous `mu-`:
  - `PERSON_STEMS`: nhu, ntu, kuru, rume, fazi, ana, komana, sikana
  - `LOCATIVE_STEMS`: munda, minda, musha, rodhi, gomo, dziva
  - `TREE_STEMS`: ti, tondo, pani, ndo, sasa, tsamvu, nzviro
  - `BODY_PART_STEMS`: soro, romo, mhuno, dzira

### Morphological rules / useful stem categories

- Noun-class prefix → class mapping (prefix-stem segmentation) with **singular↔plural prefix swaps** for lemma generation (e.g. `zvi-bage`→`chi-bage`).
- The four semantic stem categories above (person / locative / tree / body-part) are the most directly reusable *conceptual* resource for noun-class disambiguation.

### Verb morphology

- **Not covered.** The system is noun-morphology-only; verbs are touched only via `ku`→Cl.15 (infinitive). No subject concords, tense markers, or verb-stem lists exist here.

### What the ML model actually does

- `shona_morphology_final.keras` + `tokenizer.pickle` implement **character-level prefix–stem boundary detection**. For an input word it predicts, per character position, whether the split boundary falls there (probability > 0.5 = split point). Output: `prefix` / `stem`.
- It is a **segmentation regressor**, *not* a full POS tagger or grammar model. The `.keras` tagger variant (`shona_morphology_tagger.keras`) is present but not wired up.
- Boundary detection feeds the rule-based class map; the neural part only guesses where to split. **No training scripts** are shipped — only pre-trained artifacts.

---

## 3. Comparison table

| Resource | Source        | What it provides | MSUNLI action |
| -------- | ------------- | ---------------- | ------------- |
| `shona_lexicon.json` (hand-annotated tokens, lemmas, POS, noun class, glosses, `Verified manually`) | shona-spacy | Verified lexical/annotation inventory across 20+ noun classes + pronoun/locative/diminutive/augmentative sets | **reference** — great validation source for existing gold; candidate stem/lemma+class pairs to *manually* curate into `languages/shona/lexicon.yaml` later (not now) |
| `CLOSED_CLASS` word lists (ADV/PRON/DET/CCONJ) | shona-spacy | Small verified closed-class vocabulary | **reference** — candidate future closed-class entries; requires lexicon-format conversion and review |
| `noun-class-prefix` mapping + `mipanda` 24-class table (incl. 1a/2a/2b, Ka-/Tu-, SV-/SVI-, zi-) | shona-spacy | Broad noun-class inventory incl. dialectal/lexical nuances | **reference** — cross-check against MSUNLI `noun_classes.yaml`; good for spotting missing/allomorphic prefixes |
| `VERB_*` rules (subject concords, tense markers, verb roots, derivational suffixes) | shona-spacy | Verb/concord + tense vocabulary and derivational suffix inventory | **reference** — conceptual; do **not** copy Python lists; may inform future `morphemes.yaml`/`morphotactics.yaml` verb expansions |
| `SHONA_CLASS_MAP` (Fortune) incl. meaning + number + singular/plural pairing | shona-moph | Fortune-based noun-class semantics and pairing + priority ranking | **reference** — validate MSUNLI `noun_classes.yaml` (already Fortune-derived); largely redundant but a useful cross-check |
| Semantic stem categories (PERSON/LOCATIVE/TREE/BODY-PART) for `mu-` disambiguation | shona-moph | Reusable stem lists for disambiguating ambiguous prefixes | **reference** — candidate curated stem lists for future constraint/disambiguation logic |
| `shona_tokens_with_classes.csv` (178K line token corpus) | shona-spacy | Large raw token + prefix-labelled corpus (rule-generated, code-mixed) | **review** — noisy/auto-labelled; possible future frequency/candidate-lexicon mining only |
| `select_best_class()` heuristic | shona-moph | Priority/overlap disambiguation strategy for ambiguous prefixes | **reference** — conceptual approach; MSUNLI already ranks candidates generically |
| `shona_morphology_final.keras` + `tokenizer.pickle` | shona-moph | Neural character-level prefix–stem boundary detection | **do not import** — MSUNLI explicitly excludes the Keras model (V1 scope) |
| `app.py` / `shona_component.py` rule logic | both | Python/rule-engine implementation | **do not copy** — architecture-minded reference only; porting rule *lists* into YAML data is a separate decision |

---

## 4. Licensing

| Project | License | Notes |
| ------- | ------- | ----- |
| `shona-spacy` | **MIT** (`pyproject.toml`) | Freely reusable/re-referenceable; attribution to author expected. No separate LICENSE file — declared in `pyproject.toml` (has a stray PowerShell here-string wrapper artifact). |
| `shona_moph` | **None declared** | **No LICENSE/README present.** Treat as unlicensed/unknown — do **not** directly copy code or data into MSUNLI without permission/clarification. The Fortune noun-class knowledge itself is derived from a published grammar (see conflicts). |
| MSUNLI (`morph-analyser`) | **MIT** (code), language pack **CC-BY-4.0** | MSUNLI's Shona pack is already Fortune-derived and CC-BY-4.0. |

**Import risk:** Anything copied from `shona_moph` (which has no licence) would be an unlicensed import — avoid copying directly. `shona-spacy` (MIT) is safe to reference and, with attribution, to reuse.

---

## 5. Conflicting / uncertain information

- **Class 2b (Zezuru `vana-`/`a-`), 19 (sv-/svi-), 21 (zi-)**: MSUNLI marks these `disputed`; the reference projects encode them as normal classes (`shona-spacy` lists Mupanda 19/20 for `pf-`/`ku-` forms; `shona_moph` adds sv-/zi-). Dialectal classification varies.
- **Class-20 handling**: `shona-spacy` labels Mupanda 20 as nominalized/infinitive forms (`kufamba`, `kudzidza`) — which MSUNLI treats as **class 15 infinitive / verb**, not a distinct noun class 20. Terminology mismatch to reconcile.
- **Prefix `m-` allomorph**: shared by classes 1/3 in both MSUNLI and references, but segmentation of forms like `musikana`/`Mwana` (`Mwana`→stem `ana` in shona-spacy vs MSUNLI's `nhu`-style segmentation) may differ on nasal-compression edge cases.
- **Class 9 modelling**: MSUNLI models 9/1a as zero-prefix; shona-spacy lists class 9 prefixes `n/m/`` separately (nasal classes), creating potential double-count vs class 1/3 `m-`. Needs a decision on how nasal-prefix nouns are segmented.
- **Lemma convention**: shona-spacy lexicons largely store *prefixed full-word* lemmas (e.g. `murume`) with `lemma` such as `rume`; MSUNLI stores bare stems with `lemma: murume`. Conversion required if lemmas were imported.
- **Corpus noise**: the 178K-line CSV mixes Shona, English, and code-mixed tokens with rule-generated (not hand-verified) labels — low confidence, use with care.

---

## 6. Resources that should NOT be copied

- **The Keras model** (`shona_morphology_final.keras`, `shona_morphology_tagger.keras`) and `tokenizer.pickle` — MSUNLI V1 scope explicitly excludes ML models; also unclear provenance/training.
- **`shona_moph` code** (`app.py`, `fortune_grammar.py`) and **closed-class Python rule tables** from `shona-spacy` (`shona_component.py`, `mipanda.ipynb`, `Untitled113.ipynb`, `map101.ipynb`) — no Python logic should be ported into MSUNLI (which uses declarative YAML); and `shona_moph` is unlicensed.
- **`shona_tokens_with_classes.csv`** as raw gold/evaluation data — it is auto-labelled and not verified; should not be treated as gold. Comments/dependency-relation fields would require full re-annotation.
- **Google Sheets integration code** / Streamlit UI (`test_sheets*.py`, `app.py` UI) — irrelevant to the engine.

---

## 7. Single most valuable resource from each project

- **`shona-spacy` → `shona_spacy/data/shona_lexicon.json`.** The manually verified, hand-annotated lexicon (token ↔ lemma ↔ POS ↔ noun class ↔ English gloss) is the highest-quality reusable lexical asset. It is MIT-licensed, spaCy-independent (pure JSON), and can be mined as a **validated cross-check for MSUNLI's gold set** and a curated source for future lexicon expansion — without any dependency on spaCy.

- **`shona_moph` → The Fortune-based `SHONA_CLASS_MAP` with singular/plural pairing and the semantic stem categories (person/locative/tree/body-part) used for `mu-` disambiguation.** This is the cleanest, most authoritative noun-class + disambiguation knowledge in the repo. MSUNLI's `noun_classes.yaml` already covers much of it, so the practical value is as a **cross-validation of pairing/priority and as a stem-category model for future ambiguity handling** — not as a data import (unlicensed).

---

## 8. Verification

The requested checks could **not be executed**: the shell tool failed to spawn PowerShell with `EPERM: operation not permitted, uv_spawn ... powershell.EXE` on every invocation in this environment. The commands to be run (unchanged, in `msunli-morph-analyser/`) are:

```bash
pytest --tb=short -q
ruff check .
mypy src
```

**Recommendation:** re-run these locally; the repo's existing quality gates (per README/pyproject) are `pytest`, `ruff`, and `mypy --strict`. No MSUNLI source or test was modified by this audit.

---

*Prepared for MSUNLI language-pack roadmap. Nothing in this document implements imports or changes the morphology engine; those are follow-on tasks.*
