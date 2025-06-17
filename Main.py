#!/usr/bin/env python3

import re
import sys
import html
from templates import get_head, CODE_BLOCK_TEMPLATE
from pathlib import Path
from typing import List, Tuple

USAGE = "Usage: python Main.py FILE.md [output.html]"

# ────────────────────────────  regexes  ──────────────────────────────── #

# image syntax: Obsidian style ![[name.ext]] or ![[name.ext|option]]
RE_IMAGE   = re.compile(r"^\s*!\[\[([^|\]]+)(?:\|[^]]*)?]]\s*$")
RE_HEADER  = re.compile(r"^(#{1,6})\s*(.*)$")
RE_FENCE   = re.compile(r"^```(\w*)\s*$")
RE_LATEX_BLOCK = re.compile(r"^\$\$\s*$")
RE_BLANK   = re.compile(r"^\s*$")
RE_CALLOUT = re.compile(r'^>\s*\[!(\w+)\]\s*(.*)$')

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


CALLOUT_ICONS = {
    "NOTE": "&#8505;",      # ℹ
    "INFO": "&#8505;",
    "TIP": "&#128161;",      # 💡
    "IMPORTANT": "&#10071;", # ❗
    "WARNING": "&#9888;",    # ⚠
    "CAUTION": "&#9888;",
    "DANGER": "&#128293;",   # 🔥
}


def build_callout(kind: str, title: str, body_lines: List[str]) -> str:
    """Return HTML for a callout block."""
    icon = CALLOUT_ICONS.get(kind.upper(), "&#8505;")
    title_html = inline_md(title) if title else ""
    body_html = "".join(f"<p>{inline_md(ln)}</p>" for ln in body_lines)
    return (
        f'<div class="callout callout-{kind.lower()}">'  # container
        f'<div class="callout-title">{icon} {title_html}'
        f'<button class="toggle" onclick="toggleCallout(this)">-</button>'
        f'</div>'
        f'<div class="callout-body">{body_html}</div>'
        f'</div>'
    )


# ────────────────────────────  main converter  ───────────────────────── #

def markdown_to_html(md_text: str, title: str = "Document") -> str:
    lines = md_text.splitlines()
    out: List[str] = []
    i = 0

    # 1) strip front‑matter
    if lines and lines[0].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            # TODO: process front-matter 
            i += 1
        i += 1   # skip closing '---'

    # 2) scan line‑by‑line
    while i < len(lines):
        line = lines[i]

        # blank line → skip
        if RE_BLANK.match(line):
            i += 1
            continue

        # callout block starting with "> [!TYPE] Title"
        if m := RE_CALLOUT.match(line):
            kind = m.group(1)
            title_text = m.group(2).strip()
            body_lines = []
            i += 1
            while i < len(lines) and lines[i].startswith('>'):
                body_lines.append(lines[i][1:].lstrip())
                i += 1
            out.append(build_callout(kind, title_text, body_lines))
            continue

        # fenced code block
        if m := RE_FENCE.match(line):
            lang = m.group(1)
            code_lines = []
            i += 1
            while i < len(lines) and not RE_FENCE.match(lines[i]):
                code_lines.append(lines[i].rstrip("\n"))
                i += 1
            i += 1  # skip closing fence
            code = html.escape("\n".join(code_lines))
            out.append(
                CODE_BLOCK_TEMPLATE.format(lang=lang, code=code)
            )
            continue

        # multiline LaTeX block delimited by $$
        if RE_LATEX_BLOCK.match(line):
            latex_lines = []
            i += 1
            while i < len(lines) and not RE_LATEX_BLOCK.match(lines[i]):
                latex_lines.append(lines[i].rstrip("\n"))
                i += 1
            if i < len(lines):
                i += 1  # skip closing $$
            latex_content = "\n".join(latex_lines)
            out.append(f"<p>$$\n{latex_content}\n$$</p>")
            continue

        # header
        if m := RE_HEADER.match(line):
            level = len(m.group(1))
            hdr = inline_md(m.group(2).strip())
            out.append(f"<h{level}>{hdr}</h{level}>")
            i += 1
            continue

        # image
        if m := RE_IMAGE.match(line):
            name = html.escape(m.group(1).strip())
            out.append(f'<img src="../graphics/{name}" alt="{name}">')
            i += 1
            continue

        # default → paragraph text
        paragraph = inline_md(line.rstrip("\n"))
        out.append(f"<p>{paragraph}</p>")
        i += 1

    # 3) wrap with boilerplate
    head = get_head(title)
    tail = "\n</body>\n</html>"
    return head + "\n".join(out) + tail

# ────────────────────────────  CLI  ──────────────────────────── #

def main() -> None:
    # if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
    #     print(USAGE, file=sys.stderr)
    #     sys.exit(1)

    # in_path  = Path(sys.argv[1])
    # out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else in_path.with_suffix(".html")

    in_path  = Path('pipe.md')
    out_path = in_path.with_suffix(".html")

    md_text = in_path.read_text(encoding="utf8")
    title   = in_path.stem.replace("_", " ").title()

    html_out = markdown_to_html(md_text, title=title)
    x= out_path.write_text(html_out, encoding="utf8")
    print(f"{x=}")
    print(f"✓  wrote {out_path}")

if __name__ == "__main__": main()
