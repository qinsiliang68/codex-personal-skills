---
name: parser-output-manual-annotation
description: Manual annotation protocol for parser-output Markdown from OCR/PDF parsers such as PaddleOCR, Docling, Marker, or similar pipelines. Use when Codex is asked to label parser output documents, repair annotation tags, create human-review extracts, compare labels, or prepare training data from parsed Markdown while preserving original text.
---

# Parser Output Manual Annotation

## Prime Rule

Never use scripts, regular expressions, Markdown heading markers, article-number patterns, or bulk generation to decide labels or insert annotation tags.

Annotation decisions must be made by reading the document text and nearby context. Scripts may only:

- find candidate regions for human review
- extract already tagged blocks into review files
- count tags
- verify tag balance
- verify that removing tag lines restores the original Markdown text

If a script decided or inserted labels, treat that document as contaminated until a human manually reviews and repairs it.

## Source Of Truth

Edit the copied annotation workspace only, not immutable parser evidence.

For `law-database-retrieval`, parser evidence lives under:

```text
review_artifacts/01_parsed/
```

Training annotation source files live under:

```text
review_artifacts/06_model_training/00_parsed_annotation_workspace/01_documents/<doc>/0X_<parser>/markdown_document/output.annotated.md
```

For Docling, use:

```text
03_docling/markdown_document/output.annotated.md
```

If `output.annotated.md` does not exist, create it by copying that parser's `output.md` into the annotation workspace and then manually adding tags.

Do not project labels from another parser automatically. Paddle, Marker, and
Docling outputs may be used as references, but a Docling label must be decided
from the Docling text and its local context, not copied from Paddle or Marker by
alignment, regex, or script.

## Label Set

Use only this compact set unless the user explicitly changes it:

- `<heading>`: real title/header lines that should be learned as structural headings
- `<body>`: substantive document text, including clauses, articles, explanations, numbered items, and text that should remain searchable
- `<table>`: table content
- `<formula>`: formula content
- `<noise>`: parser metadata, page markers, printed page numbers, page headers/footers, table of contents, OCR garbage, empty-page notices, duplicated fragments, and other text to drop or quarantine

In the current project rule, page headers and footers are noise. Do not use `<header_footer>` unless the user explicitly reintroduces that label.

## Heading Discipline

Do not trust Markdown syntax blindly, but treat it as useful evidence.

Current project preference:

- Lines with explicit parser heading syntax such as `# ...` or `### ## ...` are likely heading candidates.
- Lines without heading syntax are suspicious inside `<heading>` and must be checked carefully.
- A chapter heading followed by a plain `第一节...` line should usually be split: the `### ## 第X章...` line remains `<heading>`, while the plain `第一节...` line goes to `<body>` unless the user explicitly says otherwise.
- Decree numbers, judicial interpretation numbers, publication numbers, and similar citation metadata usually go to `<body>` unless the user explicitly treats them as headings.
- Table-of-contents pages are `<noise>` in the annotation source and should be filtered out of human noise-review extracts.

Examples:

```md
<heading>
### ## 第三章行政强制措施实施程序
</heading>

<body>
第一节一般规定
</body>
```

```md
<heading>
# 中华人民共和国主席令
</heading>

<body>
第八十号
</body>
```

```md
<noise>
### ## 目录

第一章总则

第二章行政许可的设定
</noise>
```

## Work One Document At A Time

Process one book/document at a time.

Before editing a document:

1. Locate the parser-specific `output.md` and `output.annotated.md`.
2. Read enough context around the target region.
3. Decide labels manually.
4. Apply small patches, not whole-file rewrites.

During editing:

- Do not delete and regenerate the whole file.
- Do not perform bulk search/replace for labels unless it is a non-semantic rename explicitly requested by the user, such as `<header_footer>` to `<noise>`.
- Preserve all original text characters.
- Only add, remove, or move tag lines unless the user explicitly asks to correct OCR text.
- Keep diffs reviewable: small line-level changes are preferred.
- Treat each document as a separate work unit. Do not mix unrelated documents in
  one annotation patch unless the user explicitly asks for a batch mechanical
  rename.

After finishing a document:

1. Verify tag balance.
2. Verify that removing tag lines preserves the original `output.md` text at least at non-whitespace-character level.
3. Regenerate any human-review extract requested by the user.
4. Commit only when the user requests commit. For annotation assets, prefer one
   document per commit so each book can be rolled back independently.

## Human Review Extracts

Human-review files are not training source. They are views generated from `output.annotated.md`.

For the current `law-database-retrieval` project, the default desktop review
package requested by the user is:

```text
%USERPROFILE%\Desktop\non_body_label_review_20260705_201318
```

For quick review, extract only the text inside relevant tags:

```md
<heading>
### ## 第八节时效
</heading>
```

becomes:

```md
### ## 第八节时效
```

Keep review extracts clean:

- no sha256
- no source paths
- no doc ids
- no block ids
- no line ranges unless the user asks
- separate blocks with `---`
- omit empty labels such as table/formula when they have zero blocks
- delete obsolete review files and empty label folders when they no longer match
  the current review rule

For noise review extracts, filter out obvious shared noise when the user wants shorter review files:

- parser metadata
- pure `## Page N`
- pure printed page numbers
- empty-page notices
- table of contents and TOC continuation pages

Do not let review-extract filtering change the annotation source.

Generated structured training datasets or JSON files must be derived from tags
by code. Do not ask an LLM or VLM to rewrite a document or produce the final
structured content directly. Models may label; deterministic code performs file
changes, slicing, extraction, merging, and JSON generation.

## Verification Checklist

Run these checks after each annotation pass:

- tag counts by label
- opening and closing tag balance
- no obsolete labels such as `<header_footer>` when the project rule has merged them into noise
- removing tag lines does not change non-whitespace characters compared with `output.md`
- human-review extract contains only the files and labels the user asked to inspect

If a check fails, fix the annotation source before continuing.

## Stop Conditions

Stop and report instead of continuing when:

- source `output.md` is missing
- parser output appears corrupted or wrong parser folder is selected
- a requested change would require guessing many labels without human-visible review
- the user asks for a bulk operation that would make training data untrustworthy
- text changes, not just tag changes, would be required
