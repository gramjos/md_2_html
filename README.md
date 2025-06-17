# Markdown to HTML Converter
| filename | description | No. lines |
|----------|----------|----------|
| `Main.py`   | line by line parsing   | 190   |
| `templates.py`   | web templates   | 55   |
| `test_md2html.py`   | tests   | 41   |

This repository contains a Python script that turns a small subset of Markdown into a standalone HTML page. It is meant for quick static pages with minimal styling.

## Algorithm Overview

- Skip YAML front matter delimited by `---`.
- Each non-blank line becomes its own `<p>` tag.
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
    - Each remaining line is wrapped in `<p>`

## Usage
```
python Main.py FILE.md [output.html]
```

If the output path is omitted, `FILE.html` is created next to the input.  See `Pipeline_example.md` for an example and `test_md2html.py` for a basic test suite.

### Additional Information Embedded
`markdown_to_html` now accepts a path to a home page, a list of site links and a
list of directory links. These are appended to the generated HTML so the home
page text is displayed and the links are clickable.

#### Supported Markdown
- [ ] inline images
- [ ] excalidraw images
- [x] headers
- [ x ] code blocks with copy buttons
- [ x ] bold, code-face
- [ x ] images on own line
- [ x ] inline latex
```html
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```
