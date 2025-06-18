# Markdown to HTML Converter
| filename | description | No. lines |
|----------|----------|----------|
| `x.py`   | line by line parsing and then html creation  | 190   |
| `templates.py`   | web templates   | 55   |
| `test_md2html.py`   | tests   | 41   |

This repository contains a Python script that turns a small subset of Markdown into a standalone HTML page. It is meant for quick static pages with minimal styling.

This program takes a single markdown and creates two types of web pages:
1. 'README home page' holds content, links to singleton articles, and links to other 'README home page' (valid directories)
2. 'Singleton Articles' no links just content
Both, 1 & 2 use the template `index.html`

## Program Sequential Overview
0.  Homepage or Singleton?
1. expect metadata
2. line-by-line:
    - regexes check for a starting pattern blank line, starting of code block, header or image
    - No starting pattern matched, the each remaining line is wrapped in `<p>`
3. if Homepage, then embed additional hyperlinks (to other Homepages and Singletons)

## HTML Tag Parsing Algorithm Overview
- Skip YAML front matter delimited by `---`.
- Each non-blank line becomes its own `<p>` tag.
- ATX headers (`#` ... `######`) map to `<h1>`&ndash;`<h6>`.
- Images written as `![[name.ext]]` are loaded from `../graphics/`.
- Fenced code blocks are wrapped with a Copy button.
- Inline markup for `*em*`, `_em_`, `**strong**`, `__underline__` and `` `code` `` is processed in headers and paragraphs.
- All other text is left as plain text.

## Usage
```
python src/x.py FILE.md 
```
_writes FILE.html to disk_

### Additional Information Embedded
`markdown_to_html` function accepts:
- `md_text` : `str` raw markdown to be parsed
- `terminal_sites`: `List[str]` Singleton articles
- `valid_dirs`: `List[str]` Homepages
- `root_dir`: `Path` startingpoint

#### Supported Markdown
- [ ] inline images
- [ ] excalidraw images
- [x] headers
- [ x ] code blocks with copy buttons
- [ x ] bold, code-face
- [ x ] images on own line
- [ x ] inline latex
latex is rendered in `p` tags when these scripts are present
```html
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```
