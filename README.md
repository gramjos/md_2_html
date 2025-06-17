# Markdown to HTML Converter

This repository contains a Python script that turns a small subset of Markdown into a standalone HTML page. It is meant for quick static pages with minimal styling.

## Algorithm Overview

- Skip YAML front matter delimited by `---`.
- Paragraphs become `<p>` tags.
- ATX headers (`#` ... `######`) map to `<h1>`&ndash;`<h6>`.
- Images written as `![[name.ext]]` are loaded from `../graphics/`.
- Fenced code blocks are wrapped with a Copy button.
- Inline markup for `*em*`, `_em_`, `**strong**`, `__underline__` and `` `code` `` is processed in headers and paragraphs.
- All other text is left as plain text.

## Sequential Overview
1. expect metadata
2. line-by-line:
    - regexes check for a starting pattern blank line, starting of code block, header or image
    - No starting pattern

## Usage

```
python Main.py FILE.md [output.html]
```

If the output path is omitted, `FILE.html` is created next to the input.  See `Pipeline_example.md` for an example and `test_md2html.py` for a basic test suite.

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
| Cell 7   | Cell 8   | Cell 9   |