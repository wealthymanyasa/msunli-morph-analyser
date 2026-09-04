# Morphological Analyser — CLI

The `morph` command-line tool is a thin adapter over the application service.
It performs **no morphology of its own** — it resolves language packs, calls
`AnalysisService.analyze` (the same layer the REST API uses), and renders the
canonical `AnalysisResult` as text.

## Installation

```bash
pip install -e .
```

This registers the `morph` console script.

## Commands

### List registered languages

```bash
morph languages
```

```
sn	chiShona (Shona)	0.1.0
```

### Analyse a single word

```bash
morph analyze --language sn murume
```

```
surface:  murume
normalized: murume
language: sn
status:   analysed
  [1] lemma=murume, pos=noun, score=0.100
      mu  (type=noun-class-1) <noun-class-1>
      rume  (type=stem) <stem>
      features: noun_class=1, number=singular
--- murume ---
```

### Analyse a batch from a text file

```bash
morph analyze --language sn --file words.txt
```

Each non-empty line of the file is a surface form. Results are printed in file
order. `WORD` is omitted when `--file` is used; providing both is an error.

### Exit codes

| Code | Meaning                                              |
| ---- | ---------------------------------------------------- |
| 0    | Success                                              |
| 2    | Usage / application error (e.g. unknown language, missing file) |

## Language discovery

The CLI discovers language packs under `languages/` by default. Override the
location with the `MORPH_LANGUAGES_DIR` environment variable — the same variable
the REST API honours, so both adapters always see the same packs.

## Help

```bash
morph --help
morph analyze --help
```
