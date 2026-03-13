---
name: oracle-netsuite-help-index
description: Build, refresh, and search complete Oracle NetSuite help indexes from Oracle's live documentation table of contents. Use when Codex needs a full NetSuite docs link list, a hierarchical TOC, an alphabetical index, or quick lookup of Oracle help URLs by title. Use this instead of inferring opaque document IDs from URL patterns alone.
---

# Oracle NetSuite Help Index

## Overview

Use this skill to generate a current NetSuite documentation index from Oracle's live TOC:
`https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/toc.htm`

Oracle's URL pattern is useful for recognizing links, but it is not enough to discover all docs because the document IDs are opaque. Always fetch the live TOC and derive links from that source.

## Quick Start

Run the bundled script:

```bash
python3 /home/trent/.codex/skills/oracle-netsuite-help-index/scripts/build_oracle_netsuite_help_index.py --output-dir .
```

This writes:

- `oracle_netsuite_full_toc.md`
- `oracle_netsuite_full_toc_hierarchy.md`

To search without opening the full files:

```bash
python3 /home/trent/.codex/skills/oracle-netsuite-help-index/scripts/build_oracle_netsuite_help_index.py --query "SuiteScript"
```

## Workflow

1. Fetch Oracle's live `toc.htm`.
2. Extract all `.html` doc links and their titles.
3. Generate an alphabetical deduplicated Markdown index for quick editor search.
4. Generate a hierarchical Markdown index that preserves Oracle's nested TOC structure.
5. If the user only needs a subset, run a query and return matching titles and URLs.

## Output Rules

- Prefer the live TOC over local HTML fragments unless the user explicitly wants a local-only extraction.
- Do not claim that inferred URL patterns can produce undiscovered Oracle doc IDs.
- Keep `infer.html` or other source files unchanged unless the user explicitly asks to edit them.
- When generating outputs in a repo, write new files rather than overwriting unrelated existing files without asking.

## Script

Use:
`scripts/build_oracle_netsuite_help_index.py`

Supported flags:

- `--output-dir <path>`: write Markdown indexes there
- `--alphabetical-name <name>`: override alphabetical filename
- `--hierarchy-name <name>`: override hierarchy filename
- `--query <text>`: print matching title and URL pairs instead of only writing files
- `--toc-url <url>`: override the default Oracle TOC endpoint if needed

## Validation

After edits to the skill or script, run:

```bash
python3 /home/trent/.codex/skills/.system/skill-creator/scripts/quick_validate.py /home/trent/.codex/skills/oracle-netsuite-help-index
python3 /home/trent/.codex/skills/oracle-netsuite-help-index/scripts/build_oracle_netsuite_help_index.py --query "SuiteScript"
```
