#!/usr/bin/env python3
"""
md2html.py  –  Convert a restricted‑flavor Markdown file to standalone HTML

Usage:
    python Main.py FILE.md [output.html]

Features implemented:

* Skip YAML front‑matter delimited by leading/ending lines with exactly `---`
* Paragraphs → <p>
* ATX headers (# … ######) → <h1> … <h6>
* Images in Obsidian format  ![[name.ext]] → <img src="../graphics/name.ext">
* Fenced code blocks (```lang) get:
      <div class="code-block">
          <button class="copy" onclick="copySibling(this)">Copy</button>
          <pre><code class="language-lang">…</code></pre>
      </div>
* Inline markup inside headers/paragraphs (but **not** in code blocks):
      `code`   *em*   _em_   **strong**   __underline__
* Everything else becomes plain text in the surrounding <p> or left literal.
-------------------------------------------------------------------------"""

import re
import sys
import html
from pathlib import Path
from typing import List, Tuple

USAGE = "Usage: python Main.py FILE.md [output.html]"

# ────────────────────────────  regexes  ──────────────────────────────── #

# image syntax: Obsidian style ![[name.ext]] or ![[name.ext|option]]
RE_IMAGE   = re.compile(r"^\s*!\[\[([^|\]]+)(?:\|[^]]*)?]]\s*$")
RE_HEADER  = re.compile(r"^(#{1,6})\s+(.*)$")
RE_FENCE   = re.compile(r"^```(\w*)\s*$")
RE_BLANK   = re.compile(r"^\s*$")

# inline (apply in **this** order)
INLINE_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"`([^`]+)`"),      r"<code>\1</code>"),
    (re.compile(r"\*\*([^\*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"__([^_]+)__"),    r"<u>\1</u>"),
    (re.compile(r"\*([^*]+)\*"),    r"<em>\1</em>"),
    (re.compile(r"_([^_]+)_"),      r"<em>\1</em>"),
]

# ────────────────────────────  helpers  ──────────────────────────────── #

def inline_md(text: str) -> str:
    """Escape HTML then replace inline markdown."""
    text = html.escape(text, quote=False)
    for rx, repl in INLINE_RULES:
        text = rx.sub(repl, text)
    return text

def flush_paragraph(buf: List[str], out: List[str]) -> None:
    """Write and clear the current paragraph buffer."""
    if buf:
        paragraph = inline_md(" ".join(buf))
        out.append(f"<p>{paragraph}</p>")
        buf.clear()

# ────────────────────────────  main converter  ───────────────────────── #

def markdown_to_html(md_text: str, title: str = "Document") -> str:
    lines = md_text.splitlines()
    out: List[str] = []
    pbuf: List[str] = []
    i = 0

    # 1) strip front‑matter
    if lines and lines[0].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1   # skip closing '---'

    # 2) scan line‑by‑line
    while i < len(lines):
        line = lines[i]

        # blank → paragraph boundary
        if RE_BLANK.match(line):
            flush_paragraph(pbuf, out)
            i += 1
            continue

        # fenced code block
        m = RE_FENCE.match(line)
        if m:
            flush_paragraph(pbuf, out)
            lang = m.group(1)
            code_lines = []
            i += 1
            while i < len(lines) and not RE_FENCE.match(lines[i]):
                code_lines.append(lines[i].rstrip("\n"))
                i += 1
            i += 1  # skip closing fence
            code = html.escape("\n".join(code_lines))
            out.append(
                '<div class="code-block">'
                '<button class="copy" onclick="copySibling(this)">Copy</button>'
                f'<pre><code class="language-{lang}">{code}</code></pre>'
                "</div>"
            )
            continue

        # header
        m = RE_HEADER.match(line)
        if m:
            flush_paragraph(pbuf, out)
            level = len(m.group(1))
            hdr = inline_md(m.group(2).strip())
            out.append(f"<h{level}>{hdr}</h{level}>")
            i += 1
            continue

        # image
        m = RE_IMAGE.match(line)
        if m:
            flush_paragraph(pbuf, out)
            name = html.escape(m.group(1).strip())
            out.append(f'<img src="../graphics/{name}" alt="{name}">')
            i += 1
            continue

        # default → paragraph text
        pbuf.append(line.rstrip("\n"))
        i += 1

    flush_paragraph(pbuf, out)

    # 3) wrap with boilerplate
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body{{font-family:system-ui,Helvetica,Arial,sans-serif;line-height:1.4;max-width:72ch;margin:2rem auto;padding:0 1rem}}
h1,h2,h3,h4,h5,h6{{margin:1.1em 0 0.6em}}
.code-block{{position:relative;background:#f5f5f5;border:1px solid #ddd;padding:0.75rem 0.5rem;margin:1em 0}}
.code-block pre{{margin:0;overflow-x:auto}}
.code-block button.copy{{position:absolute;top:0.3rem;right:0.3rem;border:none;background:#eaeaea;padding:0.2rem 0.5rem;cursor:pointer}}
.code-block button.copy:active{{background:#d5d5d5}}
</style>
<script>
function copySibling(btn){{
    navigator.clipboard.writeText(btn.nextElementSibling.innerText).then(function(){{
        const orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(function(){{btn.textContent = orig;}}, 1000);
    }});
}}
</script>
</head>
<body>
"""
    tail = "\n</body>\n</html>"
    return head + "\n".join(out) + tail

# ────────────────────────────  CLI  ──────────────────────────── #

def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    in_path  = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else in_path.with_suffix(".html")

    md_text = in_path.read_text(encoding="utf8")
    title   = in_path.stem.replace("_", " ").title()

    html_out = markdown_to_html(md_text, title=title)
    out_path.write_text(html_out, encoding="utf8")
    print(f"✓  wrote {out_path}")

if __name__ == "__main__":
    main()
