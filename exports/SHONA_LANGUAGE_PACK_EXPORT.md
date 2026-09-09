# ============================================================
# SHONA (chiShona) LANGUAGE PACK — FULL EXPORT FOR EXPERT REVIEW
# ============================================================
#
# MSUNLI Morphological Analyser Project
# Version: 0.2.0
# License: CC-BY-4.0
# Primary Source: Fortune, G. (1984) "An Analytical Grammar of Shona"
#
# PURPOSE OF THIS DOCUMENT
# -------------------------
# This file contains the COMPLETE Shona language pack data for review
# by a Shona language expert/researcher. Every linguistic data file
# from the pack is included below in full.
#
# The expert is invited to:
#   1. REVIEW all noun class assignments, stems, lemmas, and morpheme analyses
#   2. CORRECT any errors in linguistic data
#   3. ADD new vocabulary, noun classes, verbal morphology, etc.
#   4. EDIT or REPLACE any section as needed
#   5. ANNOTATE sections with comments for discussion
#
# HOW TO EDIT
# -----------
# Each section below corresponds to one YAML file in the language pack.
# The expert can:
#   - Edit the YAML data directly in this file and return it
#   - Or edit the individual .yaml files in languages/shona/ directly
#   - Or provide annotations/comments in a separate document
#
# DATA FORMAT NOTES
# -----------------
# - "surface" = the actual written form (or stem portion)
# - "lemma" = the citation form of the word
# - "pos" = part of speech (noun, verb, pron, adv, cconj, det)
# - "noun_class" = Bantu noun class number (1-21 for Shona)
# - "morphemes" = the breakdown of a word into prefix + stem
#
# ============================================================


# ============================================================
# SECTION 1: MANIFEST (manifest.yaml)
# Language metadata and provenance
# ============================================================

metadata:
  code: sn
  name: chiShona (Shona)
  version: "0.2.0"
  engine_compatibility: "1.x"
  license: CC-BY-4.0
  author: "V1 morph-analyser project"
  provenance: >
    Representative V1 inventory based on Fortune (1984) An Analytical
    Grammar of Shona, standard chiShona pedagogical references, and
    widely attested lexical items from Shona language courses.
    This is a starter pack, not a complete grammar.


# ============================================================
# SECTION 2: NOUN CLASSES (noun_classes.yaml)
# All 22 Bantu noun classes used in Shona
#
# REVIEW CHECKLIST:
# - Are all prefixes and allomorphs correct?
# - Are the singular/plural pairings correct?
# - Are the agreement concords accurate?
# - Are the semantic tendencies correct?
# - Are disputed classes (2b, 19, 21) classified correctly?
# - Are examples representative?
# ============================================================

noun_classes:
  # CLASS 1 — Human beings (singular)
  - identifier: "1"
    label: "mu-/va-"
    prefixes: ["mu-"]
    surface_allomorphs: ["mu", "mw", "m"]
    has_zero_prefix: false
    plural_of: "2"
    semantic_tendencies: ["human beings"]
    agreement: ["a-", "u-", "wa-", "o-"]
    examples: ["murume (man)", "mukadzi (woman)", "mukomana (boy)"]
    provenance: "Fortune (1984); standard pedagogical references"
    status: attested

  # CLASS 1a — Zero prefix (names, kinship)
  - identifier: "1a"
    label: "∅- (zero)"
    prefixes: ["∅"]
    surface_allomorphs: [""]
    has_zero_prefix: true
    plural_of: "2a"
    semantic_tendencies: ["names", "kinship terms"]
    agreement: ["a-"]
    examples: ["Tatenda (name)", "mai (mother)", "baba (father)"]
    provenance: "Fortune (1984); standard pedagogical references"
    status: attested

  # CLASS 2 — Plural of class 1
  - identifier: "2"
    label: "va-"
    prefixes: ["va-"]
    surface_allomorphs: ["va", "v"]
    has_zero_prefix: false
    singular_of: "1"
    semantic_tendencies: ["plural of class 1 (humans)"]
    agreement: ["va-"]
    examples: ["varume (men)", "vakadzi (women)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 2a — Plural of class 1a
  - identifier: "2a"
    label: "va-"
    prefixes: ["va-"]
    surface_allomorphs: ["va"]
    has_zero_prefix: false
    singular_of: "1a"
    semantic_tendencies: ["plural of class 1a (names/kinship)"]
    agreement: ["va-"]
    examples: ["vaTatenda", "vanababa (fathers)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 2b — Variants (DISPUTED)
  - identifier: "2b"
    label: "(variants under va-)"
    prefixes: []
    surface_allomorphs: ["vana-"]
    has_zero_prefix: false
    semantic_tendencies: ["emphatic/communal people, e.g. vanhu"]
    agreement: ["va-"]
    examples: ["vanhu (people)"]
    provenance: "Fortune (1984); note disagreements on classification"
    status: disputed

  # CLASS 3 — Inanimate singular (trees, plants, objects, body parts)
  - identifier: "3"
    label: "mu-/mi-"
    prefixes: ["mu-"]
    surface_allomorphs: ["mu", "mw", "m"]
    has_zero_prefix: false
    plural_of: "4"
    semantic_tendencies: ["trees, plants, inanimate objects", "body parts"]
    agreement: ["u-", "wa-", "wo-"]
    examples: ["muti (tree)", "mupata (valley)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 4 — Plural of class 3
  - identifier: "4"
    label: "mi-"
    prefixes: ["mi-"]
    surface_allomorphs: ["mi", "m"]
    has_zero_prefix: false
    singular_of: "3"
    semantic_tendencies: ["plural of class 3"]
    agreement: ["i-", "ya-"]
    examples: ["miti (trees)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 5 — Miscellaneous singular
  - identifier: "5"
    label: "ri-/ma-"
    prefixes: ["ri-"]
    surface_allomorphs: ["ri", "r"]
    has_zero_prefix: false
    plural_of: "6"
    semantic_tendencies: ["miscellaneous singular items", "natural phenomena"]
    agreement: ["ri-", "iro-"]
    examples: ["zai (egg)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 6 — Plural of class 5
  - identifier: "6"
    label: "ma-"
    prefixes: ["ma-"]
    surface_allomorphs: ["ma"]
    has_zero_prefix: false
    singular_of: "5"
    semantic_tendencies: ["plural of class 5", "mass/abstract plurals"]
    agreement: ["a-"]
    examples: ["mazai (eggs)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 7 — Objects, languages, manner/abstraction
  - identifier: "7"
    label: "chi-/zvi-"
    prefixes: ["chi-"]
    surface_allomorphs: ["chi", "ch"]
    has_zero_prefix: false
    plural_of: "8"
    semantic_tendencies: ["objects, languages, manner/abstraction"]
    agreement: ["chi-", "cha-"]
    examples: ["chikoro (school)", "chiShona (the Shona language)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 8 — Plural of class 7
  - identifier: "8"
    label: "zvi-"
    prefixes: ["zvi-"]
    surface_allomorphs: ["zvi", "zv"]
    has_zero_prefix: false
    singular_of: "7"
    semantic_tendencies: ["plural of class 7"]
    agreement: ["zvi-"]
    examples: ["zvikoro (schools)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 9 — Animals, inanimate objects (often zero/nasal prefix)
  - identifier: "9"
    label: "∅-/nasal-"
    prefixes: ["∅", "n-", "m-", "ny-"]
    surface_allomorphs: [""]
    has_zero_prefix: true
    plural_of: "10"
    semantic_tendencies: ["animals", "inanimate objects"]
    agreement: ["i-", "yi-"]
    examples: []
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 10 — Plural of class 9
  - identifier: "10"
    label: "dz- (pl of 9)"
    prefixes: ["dz-"]
    surface_allomorphs: ["dz", "d"]
    has_zero_prefix: false
    singular_of: "9"
    semantic_tendencies: ["plural of class 9"]
    agreement: ["dzi-"]
    examples: []
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 11 — Long/thin objects, abstract nouns
  - identifier: "11"
    label: "ru-"
    prefixes: ["ru-"]
    surface_allomorphs: ["ru", "rw"]
    has_zero_prefix: false
    plural_of: "10"
    semantic_tendencies: ["long/thin objects", "abstract nouns"]
    agreement: ["ru-"]
    examples: []
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 12 — Diminutive singular
  - identifier: "12"
    label: "ka-/tu-"
    prefixes: ["ka-"]
    surface_allomorphs: ["ka"]
    has_zero_prefix: false
    plural_of: "13"
    semantic_tendencies: ["diminutive singular"]
    agreement: ["ka-"]
    examples: ["kavana (little child)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 13 — Plural of class 12 (diminutive)
  - identifier: "13"
    label: "tu-"
    prefixes: ["tu-"]
    surface_allomorphs: ["tu"]
    has_zero_prefix: false
    singular_of: "12"
    semantic_tendencies: ["plural of class 12 (diminutive)"]
    agreement: ["tu-"]
    examples: []
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 14 — Abstract, quality nouns
  - identifier: "14"
    label: "u-"
    prefixes: ["u-"]
    surface_allomorphs: ["u", "w"]
    has_zero_prefix: false
    semantic_tendencies: ["abstract nouns", "quality nouns"]
    agreement: ["u-", "hwa-"]
    examples: ["uhama (kinship)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 15 — Infinitive/gerund
  - identifier: "15"
    label: "ku-"
    prefixes: ["ku-"]
    surface_allomorphs: ["ku", "kw"]
    has_zero_prefix: false
    semantic_tendencies: ["infinitive/gerund"]
    agreement: ["ku-"]
    examples: ["kuenda (to go)"]
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 16 — Locative: at/near specific place
  - identifier: "16"
    label: "pa- (locative)"
    prefixes: ["pa-"]
    surface_allomorphs: ["pa"]
    has_zero_prefix: false
    semantic_tendencies: ["locative: at/near specific place"]
    agreement: ["pa-"]
    examples: []
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 17 — Locative: at/general location, direction
  - identifier: "17"
    label: "ku- (locative)"
    prefixes: ["ku-"]
    surface_allomorphs: ["ku"]
    has_zero_prefix: false
    semantic_tendencies: ["locative: at/general location", "direction"]
    agreement: ["ku-"]
    examples: []
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 18 — Locative: inside/within
  - identifier: "18"
    label: "mu- (locative)"
    prefixes: ["mu-"]
    surface_allomorphs: ["mu"]
    has_zero_prefix: false
    semantic_tendencies: ["locative: inside/within"]
    agreement: ["mu-"]
    examples: []
    provenance: "Fortune (1984)"
    status: attested

  # CLASS 19 — Diminutive, dialectal (DISPUTED)
  - identifier: "19"
    label: "svi- (diminutive, dialectal)"
    prefixes: ["svi-"]
    surface_allomorphs: ["svi"]
    has_zero_prefix: false
    semantic_tendencies: ["diminutive (in some dialects)"]
    agreement: []
    examples: []
    provenance: "Dialectal; classification varies"
    status: disputed

  # CLASS 21 — Augmentative (DISPUTED)
  - identifier: "21"
    label: "zi- (augmentative)"
    prefixes: ["zi-"]
    surface_allomorphs: ["zi"]
    has_zero_prefix: false
    semantic_tendencies: ["augmentative"]
    agreement: []
    examples: []
    provenance: "Fortune (1984); status varies"
    status: disputed


# ============================================================
# SECTION 3: MORPHEMES (morphemes.yaml)
# Full morpheme inventory — prefixes, allomorphs, verbal morphology
#
# REVIEW CHECKLIST:
# - Are all allomorph aliases correct?
# - Are there missing noun class prefixes?
# - Are the verbal morphology morphemes complete?
# - Should additional tense/aspect/subject-agreement forms be added?
# ============================================================

morphemes:
  # --- Anchoring stems ---
  - id: stem
    sources_lexicon: true
    aliases: []

  # --- Noun class prefixes (mipanda) ---

  # Class 1 (sg, humans). Allomorphs: mu-/mw-/m-.
  - id: noun-class-1
    aliases: ["mu", "mw", "m"]
    sources_lexicon: false
    features:
      noun_class: "1"
      number: singular

  # Class 1a (zero prefix: names, kinship).
  - id: noun-class-1a
    aliases: [""]
    sources_lexicon: false
    features:
      noun_class: "1a"
      number: singular

  # Class 2 (pl of class 1).
  - id: noun-class-2
    aliases: ["va", "v"]
    sources_lexicon: false
    features:
      noun_class: "2"
      number: plural

  # Class 2a (pl of class 1a).
  - id: noun-class-2a
    aliases: ["va"]
    sources_lexicon: false
    features:
      noun_class: "2a"
      number: plural

  # Class 3 (sg, inanimate). Allomorphs: mu-/mw-/m- (SHARED with class 1).
  - id: noun-class-3
    aliases: ["mu", "mw", "m"]
    sources_lexicon: false
    features:
      noun_class: "3"
      number: singular

  # Class 4 (pl of class 3).
  - id: noun-class-4
    aliases: ["mi", "m"]
    sources_lexicon: false
    features:
      noun_class: "4"
      number: plural

  # Class 5 (sg).
  - id: noun-class-5
    aliases: ["ri", "r"]
    sources_lexicon: false
    features:
      noun_class: "5"
      number: singular

  # Class 6 (pl of class 5).
  - id: noun-class-6
    aliases: ["ma"]
    sources_lexicon: false
    features:
      noun_class: "6"
      number: plural

  # Class 7 (sg).
  - id: noun-class-7
    aliases: ["chi", "ch"]
    sources_lexicon: false
    features:
      noun_class: "7"
      number: singular

  # Class 8 (pl of class 7).
  - id: noun-class-8
    aliases: ["zvi", "zv"]
    sources_lexicon: false
    features:
      noun_class: "8"
      number: plural

  # Class 9 (sg, often zero/nasal prefix).
  - id: noun-class-9
    aliases: [""]
    sources_lexicon: false
    features:
      noun_class: "9"
      number: singular

  # Class 10 (pl of class 9).
  - id: noun-class-10
    aliases: ["dz", "d"]
    sources_lexicon: false
    features:
      noun_class: "10"
      number: plural

  # Class 11 (sg). Allomorphs: ru-/rw-.
  - id: noun-class-11
    aliases: ["ru", "rw"]
    sources_lexicon: false
    features:
      noun_class: "11"
      number: singular

  # Class 12 (sg, diminutive).
  - id: noun-class-12
    aliases: ["ka"]
    sources_lexicon: false
    features:
      noun_class: "12"
      number: singular

  # Class 13 (pl of class 12).
  - id: noun-class-13
    aliases: ["tu"]
    sources_lexicon: false
    features:
      noun_class: "13"
      number: plural

  # Class 14 (sg, abstract).
  - id: noun-class-14
    aliases: ["u", "w"]
    sources_lexicon: false
    features:
      noun_class: "14"
      number: singular

  # Class 15 (infinitive/gerund prefix).
  - id: noun-class-15
    aliases: ["ku", "kw"]
    sources_lexicon: false
    features:
      noun_class: "15"
      number: singular
      pos: verbal_infinitive

  # Class 16 (locative near speaker).
  - id: noun-class-16
    aliases: ["pa"]
    sources_lexicon: false
    features:
      noun_class: "16"

  # Class 17 (locative).
  - id: noun-class-17
    aliases: ["ku"]
    sources_lexicon: false
    features:
      noun_class: "17"

  # Class 18 (locative inside).
  - id: noun-class-18
    aliases: ["mu"]
    sources_lexicon: false
    features:
      noun_class: "18"

  # --- Verbal morphology (representative) ---

  # Subject agreement (SA) — 1st person singular.
  - id: sagr-1sg
    aliases: ["nd"]
    sources_lexicon: false
    features:
      person: "1"
      number: singular
      role: subject

  # Tense/aspect marker — perfect/anterior.
  - id: tam-perfect
    aliases: ["a"]
    sources_lexicon: false
    features:
      tense: perfect
      aspect: anterior


# ============================================================
# SECTION 4: LEXICON (lexicon.yaml)
# Stem inventory (~45 entries) organized by noun class
#
# REVIEW CHECKLIST:
# - Are stem-to-lemma mappings correct?
# - Are noun class assignments accurate?
# - Are there missing common Shona words?
# - Should more verb stems be added?
# - Are the provenance notes accurate?
# ============================================================

lexicon:
  # --- Class 1/2 (human) — base set ---
  - surface: rume
    lemma: murume
    pos: noun
    features:
      noun_class: "1"
      number: singular

  - surface: kadzi
    lemma: mukadzi
    pos: noun
    features:
      noun_class: "1"
      number: singular

  - surface: komana
    lemma: mukomana
    pos: noun
    features:
      noun_class: "1"
      number: singular

  - surface: nhu
    lemma: munhu
    pos: noun
    features:
      noun_class: "1"
      number: singular

  - surface: sikana
    lemma: musikana
    pos: noun
    features:
      noun_class: "1"
      number: singular

  - surface: kuru
    lemma: mukuru
    pos: noun
    features:
      noun_class: "1"
      number: singular

  # --- Class 1/2 (human) — curated from shona-spacy ---
  - surface: kwasha
    lemma: mukuwasha
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: rora
    lemma: murora
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: koma
    lemma: mukoma
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: pfumi
    lemma: mupfumi
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: rwere
    lemma: murwere
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: purisa
    lemma: mupurisa
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: porofita
    lemma: muporofita
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: fundisi
    lemma: mufundisi
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: bereki
    lemma: mubereki
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: zukuru
    lemma: muzukuru
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: dzimai
    lemma: mudzimai
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: dzimu
    lemma: mudzimu
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: penza
    lemma: mupenzi
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: roya
    lemma: muroyi
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: nyepa
    lemma: munyepi
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: shavi
    lemma: mushavi
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  # --- Class 1/2 (human) — independent-evaluation resolutions ---
  - surface: ana
    lemma: mwana
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: rimi
    lemma: murimi
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: "nin'ina"
    lemma: "munin'ina"
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json); reference lemma cited as n'ina"

  - surface: dzidzisi
    lemma: mudzidzisi
    pos: noun
    features:
      noun_class: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  # --- Class 1a (zero-prefix kinship) ---
  - surface: mai
    lemma: mai
    pos: noun
    features:
      noun_class: "1a"
      number: singular

  - surface: baba
    lemma: baba
    pos: noun
    features:
      noun_class: "1a"
      number: singular

  # --- Class 3/4 (inanimate) ---
  - surface: ti
    lemma: muti
    pos: noun
    features:
      noun_class: "3"
      number: singular

  - surface: pata
    lemma: mupata
    pos: noun
    features:
      noun_class: "3"
      number: singular

  - surface: sha
    lemma: musha
    pos: noun
    features:
      noun_class: "3"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json); decomposed stem sha (base musha)"

  # --- Class 5/6 ---
  - surface: zai
    lemma: zai
    pos: noun
    features:
      noun_class: "5"
      number: singular

  - surface: banga
    lemma: banga
    pos: noun
    features:
      noun_class: "5"
      number: singular

  - surface: zita
    lemma: zita
    pos: noun
    features:
      noun_class: "5"
      number: singular

  - surface: doro
    lemma: doro
    pos: noun
    features:
      noun_class: "5"
      number: singular

  # --- Class 7/8 (objects/languages) ---
  - surface: koro
    lemma: chikoro
    pos: noun
    features:
      noun_class: "7"
      number: singular

  - surface: shona
    lemma: chiShona
    pos: noun
    features:
      noun_class: "7"

  - surface: garo
    lemma: chigaro
    pos: noun
    features:
      noun_class: "7"
      number: singular

  - surface: pfeko
    lemma: chipfeko
    pos: noun
    features:
      noun_class: "7"
      number: singular

  - surface: rungu
    lemma: chiRungu
    pos: noun
    features:
      noun_class: "7"

  # --- Class 11 (ru-/rw-) ---
  - surface: izi
    lemma: rwizi
    pos: noun
    features:
      noun_class: "11"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json); decomposed stem izi (base rwizi)"

  # --- Class 12/13 (diminutive) ---
  - surface: vana
    lemma: kavana
    pos: noun
    features:
      noun_class: "12"
      number: singular

  # --- Class 14 (abstract) ---
  - surface: hama
    lemma: uhama
    pos: noun
    features:
      noun_class: "14"
      number: singular

  - surface: she
    lemma: ushe
    pos: noun
    features:
      noun_class: "14"
      number: singular

  # --- Verbal stems (representative) ---
  - surface: enda
    lemma: enda
    pos: verb
    features: {}

  - surface: uya
    lemma: uya
    pos: verb
    features: {}

  - surface: bika
    lemma: bika
    pos: verb
    features: {}

  - surface: taura
    lemma: taura
    pos: verb
    features: {}

  - surface: famba
    lemma: famba
    pos: verb
    features: {}

  - surface: verenga
    lemma: verenga
    pos: verb
    features: {}

  - surface: rara
    lemma: rara
    pos: verb
    features: {}

  - surface: shanda
    lemma: shanda
    pos: verb
    features: {}

  - surface: ita
    lemma: ita
    pos: verb
    features: {}

  - surface: nwa
    lemma: nwa
    pos: verb
    features: {}


# ============================================================
# SECTION 5: CLOSED CLASS (closed_class.yaml)
# Whole-word lexical units (no prefix/stem segmentation)
#
# REVIEW CHECKLIST:
# - Are POS tags correct?
# - Are person/number features correct for pronouns?
# - Are noun_class/proximity features correct for determiners?
# - Are there missing common closed-class words?
# ============================================================

closed_class:
  # --- Pronouns (5) ---
  - surface: ini
    lemma: ini
    pos: pron
    features:
      person: "1"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: iwe
    lemma: iwe
    pos: pron
    features:
      person: "2"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: ivo
    lemma: ivo
    pos: pron
    features:
      person: "3"
      number: plural
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: iye
    lemma: iye
    pos: pron
    features:
      person: "3"
      number: singular
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: isu
    lemma: isu
    pos: pron
    features:
      person: "1"
      number: plural
    provenance: "shona-spacy (shona_lexicon.json)"

  # --- Conjunctions (3) ---
  - surface: kana
    lemma: kana
    pos: cconj
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: asi
    lemma: asi
    pos: cconj
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: uye
    lemma: uye
    pos: cconj
    provenance: "shona-spacy (shona_lexicon.json)"

  # --- Adverbs (3) ---
  - surface: mangwanani
    lemma: mangwanani
    pos: adv
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: zvishoma
    lemma: zvishoma
    pos: adv
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: zvikuru
    lemma: zvikuru
    pos: adv
    provenance: "shona-spacy (shona_lexicon.json)"

  # --- Determiners (3) ---
  - surface: uyu
    lemma: uyu
    pos: det
    features:
      noun_class: "1"
      proximity: near
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: uyo
    lemma: uyo
    pos: det
    features:
      noun_class: "1"
      proximity: far
    provenance: "shona-spacy (shona_lexicon.json)"

  - surface: ichi
    lemma: ichi
    pos: det
    features:
      noun_class: "7"
      proximity: near
    provenance: "shona-spacy (shona_lexicon.json)"


# ============================================================
# SECTION 6: MORPHOTACTICS (morphotactics.yaml)
# Valid morpheme sequences (word formation rules)
#
# REVIEW CHECKLIST:
# - Are all valid prefix+stem combinations covered?
# - Are stacked prefix rules correct?
# - Are there missing morphotactic patterns?
# ============================================================

morphotactics:
  # Single noun-class prefix + stem (one per class)
  - id: noun-class-1-stem
    sequence: "noun-class-1 stem"
  - id: noun-class-1a-stem
    sequence: "noun-class-1a stem"
  - id: noun-class-2-stem
    sequence: "noun-class-2 stem"
  - id: noun-class-2a-stem
    sequence: "noun-class-2a stem"
  - id: noun-class-3-stem
    sequence: "noun-class-3 stem"
  - id: noun-class-4-stem
    sequence: "noun-class-4 stem"
  - id: noun-class-5-stem
    sequence: "noun-class-5 stem"
  - id: noun-class-6-stem
    sequence: "noun-class-6 stem"
  - id: noun-class-7-stem
    sequence: "noun-class-7 stem"
  - id: noun-class-8-stem
    sequence: "noun-class-8 stem"
  - id: noun-class-9-stem
    sequence: "noun-class-9 stem"
  - id: noun-class-10-stem
    sequence: "noun-class-10 stem"
  - id: noun-class-11-stem
    sequence: "noun-class-11 stem"
  - id: noun-class-12-stem
    sequence: "noun-class-12 stem"
  - id: noun-class-13-stem
    sequence: "noun-class-13 stem"
  - id: noun-class-14-stem
    sequence: "noun-class-14 stem"
  - id: noun-class-15-stem
    sequence: "noun-class-15 stem"
  - id: noun-class-16-stem
    sequence: "noun-class-16 stem"
  - id: noun-class-17-stem
    sequence: "noun-class-17 stem"
  - id: noun-class-18-stem
    sequence: "noun-class-18 stem"

  # Conjugated verb: 1sg SA + optional perfect + stem
  - id: sagr-tam-stem
    sequence: "sagr-1sg tam-perfect? stem"

  # Multi-prefix stacking
  - id: locative-17-over-class-7
    sequence: "noun-class-17 noun-class-7 stem"
  - id: locative-18-over-class-1
    sequence: "noun-class-18 noun-class-1 stem"
  - id: locative-18-over-class-3
    sequence: "noun-class-18 noun-class-3 stem"
  - id: locative-18-over-class-11
    sequence: "noun-class-18 noun-class-11 stem"
  - id: diminutive-12-over-class-1
    sequence: "noun-class-12 noun-class-1 stem"


# ============================================================
# SECTION 7: CONSTRAINTS (constraints.yaml)
# Grammar rules enforced by the engine
# ============================================================

constraints:
  # Noun-class agreement between prefix and stem
  - id: noun-class-agreement
    kind: noun_class_agreement
    params:
      outer_classes: ["16", "17", "18"]

  # Verbal stems take class-15 (infinitive) prefix only
  - id: verbal-infinitive-prefix
    kind: affix_stem_pos
    params:
      stem_pos: verb
      affix_classes: ["15"]

  # Conjugated-verb slots may only contain verb stems
  - id: verb-slot-stem-pos
    kind: slot_stem_pos
    params:
      affix_ids: ["sagr-1sg", "tam-perfect"]
      stem_pos: verb


# ============================================================
# SECTION 8: NORMALIZATION (normalization.yaml)
# Input text normalization rules
# ============================================================

normalization:
  lowercase: true
  unicode_form: NFC
  rules: []


# ============================================================
# SECTION 9: RANKING (ranking.yaml)
# Analysis ranking/scoring configuration
# ============================================================

ranking:
  prefer_lemmas: true
  penalties:
    no_lemma: 1.0
    longer_segmentation: 0.1


# ============================================================
# SECTION 10: RESOURCES (resources.yaml)
# Provenance records for all pack resources
# ============================================================

resources:
  - resource: lexicon
    source: "Standard chiShona course/dictionary references; widely attested, clearly segmentable stems. Additional class-1 human-noun stems curated from the MIT-licensed shona-spacy lexicon (shona-spacy/shona_spacy/data/shona_lexicon.json); each carries per-entry provenance."
    notes: "V1 starter set expanded with curated shona-spacy entries (incl. independent-evaluation resolutions: ana/mwana, rimi/murimi, nin'ina/munin'ina, dzidzisi/mudzidzisi); confidence draft."
  - resource: closed_class
    source: "MIT-licensed shona-spacy: independent pronouns and demonstratives from shona_spacy/data/shona_lexicon.json; conjunctions and adverbs from the shona-spacy closed-class word lists (shona_component.py). Each entry carries per-entry provenance."
    notes: "Small curated sample (14 entries; iye/isu resolve independent-evaluation disagreements); full closed-class import deferred."
  - resource: morphemes
    source: "Fortune (1984) An Analytical Grammar of Shona; standard pedagogical references."
    notes: "Shared/allomorphic surface forms represented explicitly as data."
  - resource: noun_classes
    source: "Fortune (1984) An Analytical Grammar of Shona; standard chiShona references."
    notes: "Classes 2b, 19, 21 marked 'disputed' — sources vary in classification."
  - resource: normalization
    source: "No invented orthographic transformations; lowercase + NFC only."
    notes: "Deliberately conservative for V1."
  - resource: morphotactics
    source: "Derived from the noun-class and verb-stem inventory listed above."
    notes: "Representative, not exhaustive."


# ============================================================
# SECTION 11: PARADIGMS (paradigms.yaml)
# Reserved for future work (currently empty)
# ============================================================

paradigms: []


# ============================================================
# SECTION 12: EVALUATION — INDEPENDENT SET (evaluation/independent.yaml)
# 40 entries from an external reference lexicon for evaluation
#
# REVIEW CHECKLIST:
# - Are source_annotation (reference lexicon) analyses correct?
# - Are the expected MSUNLI analyses correct?
# - Are the verification_status labels accurate?
# - Should any "disagree_msunli_unknown" entries be reclassified?
# ============================================================

evaluation_independent:
  # --- Class 1 singulars — agree ---
  - surface: murume
    verification_status: agree
    source_annotation:
      token: Murume
      lemma: rume
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: murume
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: rume, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: mukadzi
    verification_status: agree
    source_annotation:
      token: Mukadzi
      lemma: kadzi
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: mukadzi
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: kadzi, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: mukomana
    verification_status: agree
    source_annotation:
      token: Mukomana
      lemma: komana
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: mukomana
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: komana, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: musikana
    verification_status: agree
    source_annotation:
      token: musikana
      lemma: sikana
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: musikana
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: sikana, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: mukuwasha
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Mukuwasha
      lemma: kuWasha
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: mukuwasha
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: kuwasha, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: mukoma
    verification_status: agree
    source_annotation:
      token: Mukoma
      lemma: koma
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: mukoma
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: koma, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: mupfumi
    verification_status: agree
    source_annotation:
      token: Mupfumi
      lemma: pfumi
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: mupfumi
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: pfumi, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: murwere
    verification_status: agree
    source_annotation:
      token: Murwere
      lemma: rwere
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: murwere
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: rwere, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: mupurisa
    verification_status: agree
    source_annotation:
      token: Mupurisa
      lemma: purisa
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: mupurisa
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: purisa, type: stem}]
      features: {noun_class: "1", number: singular}

  # --- Class 1 singulars — disagree_msunli_unknown ---
  - surface: mwana
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Mwana
      lemma: mwana
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: mwana
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: ana, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: murimi
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Murimi
      lemma: rimi
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: murimi
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: rimi, type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: munin'ina
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: "Munin'ina"
      lemma: "n'ina"
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: munin'ina
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: "n'ina", type: stem}]
      features: {noun_class: "1", number: singular}

  - surface: mudzidzisi
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Mudzidzisi
      lemma: dzidzisi
      pos: NOUN
      noun_class: "1"
    expected_analysis:
      lemma: mudzidzisi
      pos: noun
      morphemes: [{surface: mu, type: noun-class-1}, {surface: dzidzisi, type: stem}]
      features: {noun_class: "1", number: singular}

  # --- Class 2 plurals — agree ---
  - surface: varume
    verification_status: agree
    source_annotation:
      token: Varume
      lemma: rume
      pos: NOUN
      noun_class: "2"
    expected_analysis:
      lemma: murume
      pos: noun
      morphemes: [{surface: va, type: noun-class-2}, {surface: rume, type: stem}]
      features: {noun_class: "2", number: plural}

  - surface: vakadzi
    verification_status: agree
    source_annotation:
      token: Vakadzi
      lemma: kadzi
      pos: NOUN
      noun_class: "2"
    expected_analysis:
      lemma: mukadzi
      pos: noun
      morphemes: [{surface: va, type: noun-class-2}, {surface: kadzi, type: stem}]
      features: {noun_class: "2", number: plural}

  - surface: vakomana
    verification_status: agree
    source_annotation:
      token: Vakomana
      lemma: komana
      pos: NOUN
      noun_class: "2"
    expected_analysis:
      lemma: mukomana
      pos: noun
      morphemes: [{surface: va, type: noun-class-2}, {surface: komana, type: stem}]
      features: {noun_class: "2", number: plural}

  - surface: vasikana
    verification_status: agree
    source_annotation:
      token: vasikana
      lemma: sikana
      pos: NOUN
      noun_class: "2"
    expected_analysis:
      lemma: musikana
      pos: noun
      morphemes: [{surface: va, type: noun-class-2}, {surface: sikana, type: stem}]
      features: {noun_class: "2", number: plural}

  - surface: vanhu
    verification_status: agree
    source_annotation:
      token: Vanhu
      lemma: nhu
      pos: NOUN
      noun_class: "2"
    expected_analysis:
      lemma: munhu
      pos: noun
      morphemes: [{surface: va, type: noun-class-2}, {surface: nhu, type: stem}]
      features: {noun_class: "2", number: plural}

  - surface: vaporofita
    verification_status: agree
    source_annotation:
      token: Vaporofita
      lemma: porofita
      pos: NOUN
      noun_class: "2"
    expected_analysis:
      lemma: muporofita
      pos: noun
      morphemes: [{surface: va, type: noun-class-2}, {surface: porofita, type: stem}]
      features: {noun_class: "2", number: plural}

  - surface: vakwasha
    verification_status: agree
    source_annotation:
      token: Vakwasha
      lemma: kuWasha
      pos: NOUN
      noun_class: "2"
    expected_analysis:
      lemma: mukuwasha
      pos: noun
      morphemes: [{surface: va, type: noun-class-2}, {surface: kwasha, type: stem}]
      features: {noun_class: "2", number: plural}

  # --- Locatives (17/18) — disagree_msunli_unknown ---
  - surface: kuchikoro
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Kuchikoro
      lemma: chikoro
      pos: NOUN
      noun_class: "17"
    expected_analysis:
      lemma: chikoro
      pos: noun
      morphemes: [{surface: ku, type: noun-class-17}, {surface: chi, type: noun-class-7}, {surface: koro, type: stem}]
      features: {noun_class: "17", number: singular}

  - surface: mumusha
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Mumusha
      lemma: musha
      pos: NOUN
      noun_class: "18"
    expected_analysis:
      lemma: musha
      pos: noun
      morphemes: [{surface: mu, type: noun-class-18}, {surface: musha, type: stem}]
      features: {noun_class: "18", number: singular}

  - surface: mumba
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Mumba
      lemma: imba
      pos: NOUN
      noun_class: "18"
    expected_analysis:
      lemma: imba
      pos: noun
      morphemes: [{surface: mu, type: noun-class-18}, {surface: mba, type: stem}]
      features: {noun_class: "18", number: singular}

  - surface: murwizi
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Murwizi
      lemma: rwizi
      pos: NOUN
      noun_class: "18"
    expected_analysis:
      lemma: rwizi
      pos: noun
      morphemes: [{surface: mu, type: noun-class-18}, {surface: rwizi, type: stem}]
      features: {noun_class: "18", number: singular}

  # --- Class 19 (pf- prefix) — disagree_msunli_unknown ---
  - surface: pfungwa
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Pfungwa
      lemma: fungwa
      pos: NOUN
      noun_class: "19"
    expected_analysis:
      lemma: pfungwa
      pos: noun
      morphemes: [{surface: pf, type: noun-class-19}, {surface: ungwa, type: stem}]
      features: {noun_class: "19", number: singular}

  - surface: pfumo
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Pfumo
      lemma: fumo
      pos: NOUN
      noun_class: "19"
    expected_analysis:
      lemma: pfumo
      pos: noun
      morphemes: [{surface: pf, type: noun-class-19}, {surface: umo, type: stem}]
      features: {noun_class: "19", number: singular}

  - surface: pfuma
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Pfuma
      lemma: fuma
      pos: NOUN
      noun_class: "19"
    expected_analysis:
      lemma: pfuma
      pos: noun
      morphemes: [{surface: pf, type: noun-class-19}, {surface: uma, type: stem}]
      features: {noun_class: "19", number: singular}

  # --- Class 20 (ku- nominalisations) ---
  - surface: kufamba
    verification_status: disagree_pos
    source_annotation:
      token: Kufamba
      lemma: famba
      pos: VERB_NOMINAL
      noun_class: "20"
    expected_analysis:
      lemma: famba
      pos: noun
      morphemes: [{surface: ku, type: noun-class-15}, {surface: famba, type: stem}]
      features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kudzidza
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Kudzidza
      lemma: dzidza
      pos: VERB_NOMINAL
      noun_class: "20"
    expected_analysis:
      lemma: dzidza
      pos: noun
      morphemes: [{surface: ku, type: noun-class-15}, {surface: dzidza, type: stem}]
      features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  # --- Diminutives/augmentatives ---
  - surface: kamwana
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Kamwana
      lemma: mwana
      pos: NOUN
      noun_class: "12"
    expected_analysis:
      lemma: kamwana
      pos: noun
      morphemes: [{surface: ka, type: noun-class-12}, {surface: mwana, type: stem}]
      features: {noun_class: "12", number: singular}

  - surface: kamukadzi
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Kamukadzi
      lemma: kamukadzi
      pos: NOUN
      noun_class: "12"
    expected_analysis:
      lemma: kamukadzi
      pos: noun
      morphemes: [{surface: ka, type: noun-class-12}, {surface: mu, type: noun-class-1}, {surface: kadzi, type: stem}]
      features: {noun_class: "12", number: singular}

  - surface: zimoto
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Zimoto
      lemma: moto
      pos: NOUN
      noun_class: "21"
    expected_analysis:
      lemma: zimoto
      pos: noun
      morphemes: [{surface: zi, type: noun-class-21}, {surface: moto, type: stem}]
      features: {noun_class: "21", number: singular}

  # --- Closed class — agree ---
  - surface: ini
    verification_status: agree
    source_annotation:
      token: Ini
      lemma: ini
      pos: PRON
    expected_analysis:
      lemma: ini
      pos: pron
      morphemes: [{surface: ini, type: closed_class}]
      features: {person: "1", number: singular}

  - surface: iwe
    verification_status: agree
    source_annotation:
      token: Iwe
      lemma: iwe
      pos: PRON
    expected_analysis:
      lemma: iwe
      pos: pron
      morphemes: [{surface: iwe, type: closed_class}]
      features: {person: "2", number: singular}

  - surface: ivo
    verification_status: agree
    source_annotation:
      token: Ivo
      lemma: ivo
      pos: PRON
    expected_analysis:
      lemma: ivo
      pos: pron
      morphemes: [{surface: ivo, type: closed_class}]
      features: {person: "3", number: plural}

  - surface: uyu
    verification_status: agree
    source_annotation:
      token: Uyu
      lemma: uyu
      pos: DET
      noun_class: "1"
    expected_analysis:
      lemma: uyu
      pos: det
      morphemes: [{surface: uyu, type: closed_class}]
      features: {noun_class: "1", proximity: near}

  - surface: uyo
    verification_status: agree
    source_annotation:
      token: Uyo
      lemma: uyo
      pos: DET
      noun_class: "1"
    expected_analysis:
      lemma: uyo
      pos: det
      morphemes: [{surface: uyo, type: closed_class}]
      features: {noun_class: "1", proximity: far}

  - surface: ichi
    verification_status: agree
    source_annotation:
      token: Ichi
      lemma: ichi
      pos: DET
      noun_class: "7"
    expected_analysis:
      lemma: ichi
      pos: det
      morphemes: [{surface: ichi, type: closed_class}]
      features: {noun_class: "7", proximity: near}

  - surface: mangwanani
    verification_status: agree
    source_annotation:
      token: Mangwanani
      lemma: mangwanani
      pos: ADV
    expected_analysis:
      lemma: mangwanani
      pos: adv
      morphemes: [{surface: mangwanani, type: closed_class}]
      features: {}

  # --- Closed class — disagree_msunli_unknown ---
  - surface: iye
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Iye
      lemma: iye
      pos: PRON
    expected_analysis:
      lemma: iye
      pos: pron
      morphemes: [{surface: iye, type: closed_class}]
      features: {person: "3", number: singular}

  - surface: isu
    verification_status: disagree_msunli_unknown
    source_annotation:
      token: Isu
      lemma: isu
      pos: PRON
    expected_analysis:
      lemma: isu
      pos: pron
      morphemes: [{surface: isu, type: closed_class}]
      features: {person: "1", number: plural}


# ============================================================
# SECTION 13: EVALUATION — GOLD STANDARD (evaluation/gold.yaml)
# ~75 entries from engine-verified output
#
# REVIEW CHECKLIST:
# - Are the surface forms and their analyses correct?
# - Are the plural forms correct?
# - Are the verb conjugations correct?
# - Are the normalization variants correct?
# - Are the true-negative probes appropriate?
# ============================================================

evaluation_gold:
  # --- Noun singulars and plurals ---
  - surface: murume
    status: analysed
    analyses:
      - lemma: murume
        pos: noun
        morphemes: [{surface: mu, type: noun-class-1}, {surface: rume, type: stem}]
        features: {noun_class: "1", number: singular}

  - surface: varume
    status: analysed
    analyses:
      - lemma: murume
        pos: noun
        morphemes: [{surface: va, type: noun-class-2}, {surface: rume, type: stem}]
        features: {noun_class: "2", number: plural}

  - surface: mukadzi
    status: analysed
    analyses:
      - lemma: mukadzi
        pos: noun
        morphemes: [{surface: mu, type: noun-class-1}, {surface: kadzi, type: stem}]
        features: {noun_class: "1", number: singular}

  - surface: vakadzi
    status: analysed
    analyses:
      - lemma: mukadzi
        pos: noun
        morphemes: [{surface: va, type: noun-class-2}, {surface: kadzi, type: stem}]
        features: {noun_class: "2", number: plural}

  - surface: mukomana
    status: analysed
    analyses:
      - lemma: mukomana
        pos: noun
        morphemes: [{surface: mu, type: noun-class-1}, {surface: komana, type: stem}]
        features: {noun_class: "1", number: singular}

  - surface: vakomana
    status: analysed
    analyses:
      - lemma: mukomana
        pos: noun
        morphemes: [{surface: va, type: noun-class-2}, {surface: komana, type: stem}]
        features: {noun_class: "2", number: plural}

  - surface: munhu
    status: analysed
    analyses:
      - lemma: munhu
        pos: noun
        morphemes: [{surface: mu, type: noun-class-1}, {surface: nhu, type: stem}]
        features: {noun_class: "1", number: singular}

  - surface: vanhu
    status: analysed
    analyses:
      - lemma: munhu
        pos: noun
        morphemes: [{surface: va, type: noun-class-2}, {surface: nhu, type: stem}]
        features: {noun_class: "2", number: plural}

  - surface: musikana
    status: analysed
    analyses:
      - lemma: musikana
        pos: noun
        morphemes: [{surface: mu, type: noun-class-1}, {surface: sikana, type: stem}]
        features: {noun_class: "1", number: singular}

  - surface: vasikana
    status: analysed
    analyses:
      - lemma: musikana
        pos: noun
        morphemes: [{surface: va, type: noun-class-2}, {surface: sikana, type: stem}]
        features: {noun_class: "2", number: plural}

  - surface: mukuru
    status: analysed
    analyses:
      - lemma: mukuru
        pos: noun
        morphemes: [{surface: mu, type: noun-class-1}, {surface: kuru, type: stem}]
        features: {noun_class: "1", number: singular}

  - surface: vakuru
    status: analysed
    analyses:
      - lemma: mukuru
        pos: noun
        morphemes: [{surface: va, type: noun-class-2}, {surface: kuru, type: stem}]
        features: {noun_class: "2", number: plural}

  - surface: mai
    status: analysed
    analyses:
      - lemma: mai
        pos: noun
        morphemes: [{surface: "", type: noun-class-1a}, {surface: mai, type: stem}]
        features: {noun_class: "1a", number: singular}

  - surface: baba
    status: analysed
    analyses:
      - lemma: baba
        pos: noun
        morphemes: [{surface: "", type: noun-class-1a}, {surface: baba, type: stem}]
        features: {noun_class: "1a", number: singular}

  - surface: muti
    status: analysed
    analyses:
      - lemma: muti
        pos: noun
        morphemes: [{surface: mu, type: noun-class-3}, {surface: ti, type: stem}]
        features: {noun_class: "3", number: singular}

  - surface: miti
    status: analysed
    analyses:
      - lemma: muti
        pos: noun
        morphemes: [{surface: mi, type: noun-class-4}, {surface: ti, type: stem}]
        features: {noun_class: "4", number: plural}

  - surface: mupata
    status: analysed
    analyses:
      - lemma: mupata
        pos: noun
        morphemes: [{surface: mu, type: noun-class-3}, {surface: pata, type: stem}]
        features: {noun_class: "3", number: singular}

  - surface: mipata
    status: analysed
    analyses:
      - lemma: mupata
        pos: noun
        morphemes: [{surface: mi, type: noun-class-4}, {surface: pata, type: stem}]
        features: {noun_class: "4", number: plural}

  - surface: zai
    status: unknown_word

  - surface: mazai
    status: analysed
    analyses:
      - lemma: zai
        pos: noun
        morphemes: [{surface: ma, type: noun-class-6}, {surface: zai, type: stem}]
        features: {noun_class: "6", number: plural}

  - surface: banga
    status: unknown_word

  - surface: mabanga
    status: analysed
    analyses:
      - lemma: banga
        pos: noun
        morphemes: [{surface: ma, type: noun-class-6}, {surface: banga, type: stem}]
        features: {noun_class: "6", number: plural}

  - surface: zita
    status: unknown_word

  - surface: mazita
    status: analysed
    analyses:
      - lemma: zita
        pos: noun
        morphemes: [{surface: ma, type: noun-class-6}, {surface: zita, type: stem}]
        features: {noun_class: "6", number: plural}

  - surface: doro
    status: unknown_word

  - surface: chikoro
    status: analysed
    analyses:
      - lemma: chikoro
        pos: noun
        morphemes: [{surface: chi, type: noun-class-7}, {surface: koro, type: stem}]
        features: {noun_class: "7", number: singular}

  - surface: zvikoro
    status: analysed
    analyses:
      - lemma: chikoro
        pos: noun
        morphemes: [{surface: zvi, type: noun-class-8}, {surface: koro, type: stem}]
        features: {noun_class: "8", number: plural}

  - surface: chigaro
    status: analysed
    analyses:
      - lemma: chigaro
        pos: noun
        morphemes: [{surface: chi, type: noun-class-7}, {surface: garo, type: stem}]
        features: {noun_class: "7", number: singular}

  - surface: zvigaro
    status: analysed
    analyses:
      - lemma: chigaro
        pos: noun
        morphemes: [{surface: zvi, type: noun-class-8}, {surface: garo, type: stem}]
        features: {noun_class: "8", number: plural}

  - surface: chipfeko
    status: analysed
    analyses:
      - lemma: chipfeko
        pos: noun
        morphemes: [{surface: chi, type: noun-class-7}, {surface: pfeko, type: stem}]
        features: {noun_class: "7", number: singular}

  - surface: zvipfeko
    status: analysed
    analyses:
      - lemma: chipfeko
        pos: noun
        morphemes: [{surface: zvi, type: noun-class-8}, {surface: pfeko, type: stem}]
        features: {noun_class: "8", number: plural}

  - surface: chiShona
    status: analysed
    analyses:
      - lemma: chiShona
        pos: noun
        morphemes: [{surface: chi, type: noun-class-7}, {surface: shona, type: stem}]
        features: {noun_class: "7", number: singular}

  - surface: zviShona
    status: analysed
    analyses:
      - lemma: chiShona
        pos: noun
        morphemes: [{surface: zvi, type: noun-class-8}, {surface: shona, type: stem}]
        features: {noun_class: "8", number: plural}

  - surface: chiRungu
    status: analysed
    analyses:
      - lemma: chiRungu
        pos: noun
        morphemes: [{surface: chi, type: noun-class-7}, {surface: rungu, type: stem}]
        features: {noun_class: "7", number: singular}

  - surface: zviRungu
    status: analysed
    analyses:
      - lemma: chiRungu
        pos: noun
        morphemes: [{surface: zvi, type: noun-class-8}, {surface: rungu, type: stem}]
        features: {noun_class: "8", number: plural}

  - surface: kavana
    status: analysed
    analyses:
      - lemma: kavana
        pos: noun
        morphemes: [{surface: ka, type: noun-class-12}, {surface: vana, type: stem}]
        features: {noun_class: "12", number: singular}

  - surface: tuvana
    status: analysed
    analyses:
      - lemma: kavana
        pos: noun
        morphemes: [{surface: tu, type: noun-class-13}, {surface: vana, type: stem}]
        features: {noun_class: "13", number: plural}

  - surface: uhama
    status: analysed
    analyses:
      - lemma: uhama
        pos: noun
        morphemes: [{surface: u, type: noun-class-14}, {surface: hama, type: stem}]
        features: {noun_class: "14", number: singular}

  - surface: ushe
    status: analysed
    analyses:
      - lemma: ushe
        pos: noun
        morphemes: [{surface: u, type: noun-class-14}, {surface: she, type: stem}]
        features: {noun_class: "14", number: singular}

  - surface: mudzidzisi
    status: analysed
    analyses:
      - lemma: mudzidzisi
        pos: noun
        morphemes: [{surface: mu, type: noun-class-1}, {surface: dzidzisi, type: stem}]
        features: {noun_class: "1", number: singular}

  - surface: mwana
    status: analysed
    analyses:
      - lemma: mwana
        pos: noun
        morphemes: [{surface: mw, type: noun-class-1}, {surface: ana, type: stem}]
        features: {noun_class: "1", number: singular}

  # --- Verb infinitives (class 15 ku-) ---
  - surface: kuenda
    status: analysed
    analyses:
      - lemma: enda
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: enda, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kuuya
    status: analysed
    analyses:
      - lemma: uya
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: uya, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kubika
    status: analysed
    analyses:
      - lemma: bika
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: bika, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kutaura
    status: analysed
    analyses:
      - lemma: taura
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: taura, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kufamba
    status: analysed
    analyses:
      - lemma: famba
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: famba, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kuverenga
    status: analysed
    analyses:
      - lemma: verenga
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: verenga, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kurara
    status: analysed
    analyses:
      - lemma: rara
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: rara, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kushanda
    status: analysed
    analyses:
      - lemma: shanda
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: shanda, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kuita
    status: analysed
    analyses:
      - lemma: ita
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: ita, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  - surface: kunwa
    status: analysed
    analyses:
      - lemma: nwa
        pos: verb
        morphemes: [{surface: ku, type: noun-class-15}, {surface: nwa, type: stem}]
        features: {noun_class: "15", number: singular, pos: verbal_infinitive}

  # --- Verb 1sg perfect conjugated forms ---
  - surface: ndaenda
    status: analysed
    analyses:
      - lemma: enda
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: enda, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndauya
    status: analysed
    analyses:
      - lemma: uya
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: uya, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndabika
    status: analysed
    analyses:
      - lemma: bika
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: bika, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndataura
    status: analysed
    analyses:
      - lemma: taura
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: taura, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndafamba
    status: analysed
    analyses:
      - lemma: famba
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: famba, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndaverenga
    status: analysed
    analyses:
      - lemma: verenga
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: verenga, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndarara
    status: analysed
    analyses:
      - lemma: rara
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: rara, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndashanda
    status: analysed
    analyses:
      - lemma: shanda
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: shanda, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndaita
    status: analysed
    analyses:
      - lemma: ita
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: ita, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  - surface: ndanwa
    status: analysed
    analyses:
      - lemma: nwa
        pos: verb
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: nwa, type: stem}]
        features: {person: "1", number: singular, role: subject, tense: perfect, aspect: anterior}

  # --- True-negative probes (should NOT be analysed) ---
  - surface: zzz
    status: unknown_word
  - surface: mumba
    status: unknown_word
  - surface: chikororo
    status: unknown_word
  - surface: banana
    status: unknown_word
  - surface: harahwa
    status: unknown_word
  - surface: gudyanga
    status: unknown_word
  - surface: mupfudze
    status: unknown_word
  - surface: tsiva
    status: unknown_word
  - surface: mushonga
    status: unknown_word
  - surface: mari
    status: unknown_word
  - surface: sadza
    status: unknown_word
  - surface: nyama
    status: unknown_word
  - surface: huku
    status: unknown_word
  - surface: mbudzi
    status: unknown_word
  - surface: nguva
    status: unknown_word
  - surface: musoro
    status: unknown_word
  - surface: shoko
    status: unknown_word
  - surface: moyo
    status: unknown_word


# ============================================================
# SECTION 14: TESTS (tests/analyses.yaml)
# Test expectations for the analysis engine
#
# REVIEW CHECKLIST:
# - Do the expected analyses match your linguistic knowledge?
# - Are there test cases that should fail or be added?
# ============================================================

tests_analyses:
  # Basic nouns
  - surface: murume
    status: analysed
    analyses:
      - pos: noun
        lemma: murume
        morphemes: [{surface: mu, type: noun-class-1}, {surface: rume, type: stem}]

  - surface: varume
    status: analysed
    analyses:
      - pos: noun
        lemma: murume
        morphemes: [{surface: va, type: noun-class-2}, {surface: rume, type: stem}]

  - surface: mukadzi
    status: analysed
    analyses:
      - pos: noun
        lemma: mukadzi
        morphemes: [{surface: mu, type: noun-class-1}, {surface: kadzi, type: stem}]

  - surface: vakadzi
    status: analysed
    analyses:
      - pos: noun
        lemma: mukadzi

  - surface: muti
    status: analysed
    analyses:
      - pos: noun
        lemma: muti
        morphemes: [{surface: mu, type: noun-class-3}, {surface: ti, type: stem}]

  - surface: miti
    status: analysed
    analyses:
      - pos: noun
        lemma: muti
        morphemes: [{surface: mi, type: noun-class-4}, {surface: ti, type: stem}]

  - surface: chikoro
    status: analysed
    analyses:
      - pos: noun
        lemma: chikoro
        morphemes: [{surface: chi, type: noun-class-7}, {surface: koro, type: stem}]

  - surface: zvikoro
    status: analysed
    analyses:
      - pos: noun
        lemma: chikoro
        morphemes: [{surface: zvi, type: noun-class-8}, {surface: koro, type: stem}]

  - surface: mai
    status: analysed
    analyses:
      - pos: noun
        lemma: mai

  # Verbs
  - surface: kuenda
    status: analysed
    analyses:
      - pos: verb
        lemma: enda
        morphemes: [{surface: ku, type: noun-class-15}, {surface: enda, type: stem}]

  - surface: ndaenda
    status: analysed
    analyses:
      - pos: verb
        lemma: enda
        morphemes: [{surface: nd, type: sagr-1sg}, {surface: a, type: tam-perfect}, {surface: enda, type: stem}]

  # Unknown words
  - surface: qqqq
    status: unknown_word
    analyses: []

  - surface: ikramu
    status: unknown_word
    analyses: []

  # Closed-class words
  - surface: ini
    status: analysed
    analyses:
      - pos: pron
        lemma: ini
        morphemes: [{surface: ini, type: closed_class}]
        features: {person: "1", number: singular}

  - surface: kana
    status: analysed
    analyses:
      - pos: cconj
        lemma: kana
        morphemes: [{surface: kana, type: closed_class}]

  - surface: mangwanani
    status: analysed
    analyses:
      - pos: adv
        lemma: mangwanani
        morphemes: [{surface: mangwanani, type: closed_class}]

  - surface: uyu
    status: analysed
    analyses:
      - pos: det
        lemma: uyu
        morphemes: [{surface: uyu, type: closed_class}]
        features: {noun_class: "1", proximity: near}

  # Multi-prefix stacking
  - surface: kuchikoro
    status: analysed
    analyses:
      - pos: noun
        lemma: chikoro
        morphemes: [{surface: ku, type: noun-class-17}, {surface: chi, type: noun-class-7}, {surface: koro, type: stem}]
        features: {noun_class: "17", number: singular}

  - surface: mumusha
    status: analysed
    analyses:
      - pos: noun
        lemma: musha
        morphemes: [{surface: mu, type: noun-class-18}, {surface: mu, type: noun-class-3}, {surface: sha, type: stem}]
        features: {noun_class: "18", number: singular}

  - surface: murwizi
    status: analysed
    analyses:
      - pos: noun
        lemma: rwizi
        morphemes: [{surface: mu, type: noun-class-18}, {surface: rw, type: noun-class-11}, {surface: izi, type: stem}]
        features: {noun_class: "18", number: singular}

  - surface: kamukadzi
    status: unknown_word
    analyses: []


# ============================================================
# END OF SHONA LANGUAGE PACK EXPORT
# ============================================================
#
# SUMMARY OF DATA SCOPE
# ----------------------
# Total files exported:       14
# Noun classes defined:       22 (including 3 disputed)
# Lexicon stems:             ~45 (nouns + verbs)
# Closed-class words:         14 (pronouns, conjunctions, adverbs, determiners)
# Morphemes declared:         22 (20 noun-class prefixes + 2 verbal)
# Morphotactic rules:         27 (20 single-prefix + 1 conjugated + 5 stacked + 1 infinitive)
# Constraints:                 3
# Evaluation entries:         ~40 (independent) + ~75 (gold)
# Test cases:                 ~25
#
# KNOWN LIMITATIONS (from manifest.yaml)
# - No complete morphophonological rules (e.g. nasal assimilation)
# - No derivational morphology
# - No tone/accent representation
# - Dialectal variation not modelled beyond notes
#
# KEY AREAS FOR EXPERT REVIEW
# ---------------------------
# 1. LEXICON: Add missing common Shona words across all noun classes
# 2. VERBAL MORPHOLOGY: Add more subject agreements (2sg, 3sg, 1pl, 2pl, 3pl)
#    and tense/aspect markers (recent past, remote past, habitual, progressive, etc.)
# 3. NOUN CLASSES: Verify disputed classes 2b, 19, 21
# 4. STEMS: Verify stem-to-lemma mappings, especially contracted forms
# 5. CLOSED CLASS: Add missing pronouns, conjunctions, adverbs, prepositions
# 6. MORPHOTACTICS: Add missing prefix-stacking patterns
# 7. CONSTRAINTS: Verify agreement rules and exceptions
#
# ============================================================
