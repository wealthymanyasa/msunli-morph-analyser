# Language Packs

Language packs are **declarative data only** — they contain **zero executable
Python**. All linguistic knowledge lives in the pack; the generic engine
(`src/morph/engine/`) interprets it. This is the core invariant of the
platform.

This document explains the pack structure, the Shona resource layout, and how
to add a new language.

## Pack contract

Each pack is a directory of YAML files under `languages/<code>/`:

```
languages/<code>/
├── manifest.yaml        # required — metadata
├── normalization.yaml   # optional
├── lexicon.yaml         # optional   (stem inventory)
├── closed_class.yaml    # optional   (whole-word unsegmentable lexical items)
├── morphemes.yaml       # optional   (affix/stem morphemes)
├── morphotactics.yaml   # optional   (valid morpheme sequences)
├── paradigms.yaml       # optional   (reserved)
├── constraints.yaml     # optional   (declarative constraints)
├── ranking.yaml         # optional   (deterministic ranking config)
├── noun_classes.yaml    # optional   (mipanda / noun-class resource)
├── resources.yaml       # optional   (per-resource provenance)
└── tests/
    └── analyses.yaml    # language-specific expectations (data)
```

`manifest.yaml` must include `metadata` with:

```yaml
metadata:
  code: sn                # ISO 639-1 (or canonical) code
  name: chiShona (Shona)
  version: "0.1.0"        # semantic version
  engine_compatibility: "1.x"   # semver-style; major must match the engine
  license: CC-BY-4.0
  provenance: "free-text source/attribution"
  author: Optional author
```

The pack is validated by `LanguagePackValidator` (required metadata, a valid
semantic `version`, matching `engine_compatibility`, schema validity, and
resource integrity) before it can be loaded by the engine. Invalid or
incompatible packs are rejected with clear, structured errors.

## Loading

```python
from morph.loading import load_language_pack

pack = load_language_pack("languages/shona")   # validated LanguagePack
```

or via the application service:

```python
from morph.service.analysis import create_service

service = create_service()
service.load_language_directory("languages/shona")
result = service.analyze("murume", "sn")
```

## Shona resource structure

The Shona pack lives in `languages/shona/`.

### Mipanda / noun classes (`noun_classes.yaml`)

Noun classes are **structured**, not a flat `prefix -> class` map. Each class
records:

- `identifier` (e.g. `1`, `7`, `2a`)
- `label`, optional `subclass`
- `prefixes` (underlying morphemes) and `surface_allomorphs`
- `has_zero_prefix` (e.g. class 1a, class 9)
- `singular_of` / `plural_of` pairings
- `semantic_tendencies`, `agreement`
- `examples`
- `provenance` and `status` (`attested` / `draft` / `disputed`)

**Shared / allomorphic surface forms are represented explicitly as data, not
collapsed into unique classes.** For example:

- `mu-`, `mw-`, `m-` are allomorphs shared by class 1 and class 3. They are
  NOT distinct classes.
- `ku-` is shared by class 15, class 17 (locative) and the verbal infinitive.
- Class 1a and class 9 are modelled with a zero/null prefix.

This distinction is declared in `morphemes.yaml` (same `aliases` under multiple
morpheme ids) and `noun_classes.yaml` (`surface_allomorphs`,
`has_zero_prefix`). The engine interprets these as data; it does not hard-code
them.

### Lexicon (`lexicon.yaml`)

Lexicon entries are bare **stems** (the part after a noun-class/verbal prefix).
Each entry may declare:

- `surface` — the stem (matched by the anchoring `stem` morpheme)
- `lemma` — the dictionary form (e.g. the prefixed full word for nouns)
- `pos` — `noun` / `verb`, etc.
- `features` — grammatical features, e.g. `noun_class`, `number`
- `provenance` — optional per-entry source (e.g. `shona-spacy
  (shona_lexicon.json)`); resource-level provenance lives in `resources.yaml`

```yaml
- surface: koma
  lemma: mukoma
  pos: noun
  features:
    noun_class: "1"
    number: singular
  provenance: "shona-spacy (shona_lexicon.json)"
```

### Closed-class words (`closed_class.yaml`)

Closed-class items (pronouns, conjunctions, adverbs, determiners, …) have **no
prefix/stem segmentation**: the surface form IS the whole word. They are
declared as whole-word lexical entries (same `LexicalEntry` schema as the
lexicon: `surface` / `lemma` / `pos` / optional `features` / optional
`provenance`), and the generic engine analyses any input that matches a
closed-class surface exactly as a single whole-word `closed_class` morpheme —
no affixal segmentation is attempted for that word.

```yaml
closed_class:
  - surface: kana
    lemma: kana
    pos: cconj
    provenance: "shona-spacy (shona_lexicon.json)"
```

Because matching is an exact, whole-surface lookup, closed-class entries never
interfere with noun/verb segmentation or with unrelated unknown words. This
mechanism is language-independent — any language pack may ship a
`closed_class.yaml` with no engine changes.

### Morphemes (`morphemes.yaml`)

Each morpheme declares:

- `id` — unique identifier (referenced by morphotactics)
- `aliases` — surface realizations (an empty string `""` = zero/null prefix);
  the same alias may appear under multiple morpheme ids
- `sources_lexicon` — `true` for the anchoring stem morpheme (matched against
  lexicon surfaces), `false` for affixes (matched against aliases)
- `features` — grammatical features contributed when the morpheme is present

### Morphotactics (`morphotactics.yaml`)

Morphotactics are first-class data expressing valid morpheme orderings, e.g.:

```yaml
morphotactics:
  - id: noun-class-1-stem
    sequence: "noun-class-1 stem"     # prefix → nominal stem
  - id: noun-class-15-verb-stem
    sequence: "noun-class-15 stem"    # infinitive ku- → verb stem
  - id: sagr-tam-stem
    sequence: "sagr-1sg tam-perfect? stem"   # subject agr → (TAM) → stem
  - id: locative-17-over-class-7
    sequence: "noun-class-17 noun-class-7 stem"   # ku- → chi- → stem (two prefixes)
```

Token grammar: space-separated morpheme ids; a trailing `?` marks optional.
Rules are **explicit sequential slots** — a rule may carry any number of prefix
slots before the anchoring stem (e.g. `prefix1 prefix2 stem`), and the engine
stacks them generically in surface order. There is no grammar framework, no
grouping and no operator beyond the optional `?`. The Shona pack ships three
stacked nominal-prefix rules as demonstrations (see `morphotactics.yaml`); the
generic engine interprets these sequences.

### Features

Used features include `pos`, `number`, `noun_class`, `person`, `tense`,
`aspect`, `role`. Only features supported by V1 resources are populated.

### Constraints (`constraints.yaml`)

Constraints are declarative `kind` declarations interpreted by the generic
validator:

```yaml
constraints:
  - id: noun-class-agreement
    kind: noun_class_agreement
    params: {}
```

`noun_class_agreement` requires the noun-class of a prefix and its stem to
agree (equal, or via the declared `singular_of`/`plural_of` pairings). This
rejects spurious allomorph/shared-prefix readings (e.g. `mukadzi` analysed as
class 3 instead of class 1) without any Shona logic in the engine.

### Ranking (`ranking.yaml`)

Deterministic, lower score preferred. `prefer_lemmas` and named `penalties`
(`no_lemma`, `longer_segmentation`). Ranking output is fully reproducible.

### Provenance (`resources.yaml`)

Each resource records its `source` and `notes`, so pack data can be traced.
Disagreements between sources are documented (e.g. classes `2b`, `19`, `21`
marked `status: disputed`) rather than silently resolved.

## Known limitations

- No complete morphophonology (nasal assimilation, tone, etc.).
- No derivational morphology.
- No paradigms implemented yet (schema reserved).
- Representative V1 lexicon; not complete Shona coverage.
- Locative classes (16/17/18) and class 9's general surface prefix are
  modelled conservatively.

## Adding another language

Adding a language requires **only**:

1. a new pack directory `languages/<code>/` (manifest + resources), and
2. a `tests/analyses.yaml` expectations file.

**No modification of the generic engine or domain is required.** The generic
expectation harness (`morph.testing.run_expectations`) runs any language pack's
expectations. See `tests/test_testing.py` for a demonstration with a fictional
second language.
