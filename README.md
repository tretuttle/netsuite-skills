# Netsuite Skills

Reusable AI agent skill for building and searching a complete Oracle NetSuite help index from Oracle's live documentation TOC.

## Install

```bash
npx skills add https://github.com/<owner>/netsuite-skills --skill get-netsuite-docs
```

## Contents

- `get-netsuite-docs/`
  - `SKILL.md`
  - `agents/openai.yaml`
  - `agents/claude.md`
  - `scripts/build_oracle_netsuite_help_index.py`

## What It Does

- fetches Oracle's live NetSuite help TOC
- generates an alphabetical Markdown index
- generates a hierarchical Markdown TOC
- supports title search with `--query`
- fetches individual doc pages as AI-friendly markdown with `--fetch`

## Local Usage

```bash
python3 get-netsuite-docs/scripts/build_oracle_netsuite_help_index.py --output-dir .
python3 get-netsuite-docs/scripts/build_oracle_netsuite_help_index.py --query "SuiteScript"
python3 get-netsuite-docs/scripts/build_oracle_netsuite_help_index.py --fetch "https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4640429410.html"
```

## Supported Agents

| Platform | Config |
|----------|--------|
| OpenAI Codex | `agents/openai.yaml` |
| Claude Code | `agents/claude.md` |
