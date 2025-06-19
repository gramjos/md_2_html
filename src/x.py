#!/usr/bin/env python3
"""Minimal Markdown to HTML conversion utility."""

from pathlib import Path
from typing import List, Tuple, Union

import html
import re
import templates as t
# from templates import CODE_BLOCK_TEMPLATE

USAGE = "Usage: python Main.py FILE.md "

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
    """Return ``text`` with inline Markdown converted to HTML."""
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
    """Return HTML for an admonition-style callout block."""
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

def is_valid_dir(path:Path) -> bool:
    for item in path.iterdir():
        b=item.name.lower().startswith('readme')
        bb=item.name.lower().endswith('.md')
        if item.is_file() and b and bb: return True
    return False

def GenHomePage(root_dir: Path, home_pgs: List[str]) -> None:
    """
    for each md in homepags: 
        - generate an html file from template at `src/index.html` with the same markdown file name.
        - convert to html and embed in at div id="placement"
    """
    items = list(root_dir.iterdir())
    ig_lst = ['README.md', 'readme.md', '.DS_Store'] 
    singletons = [item for item in items if item.suffix == '.md' and item.name not in ig_lst]
    home_pgs = [directory for directory in items if directory.is_dir() and is_valid_dir(directory) and directory.name not in ig_lst]

    fp = root_dir / Path("README.md")
    t=fp.read_text(encoding="utf8").splitlines()
    html_parts: List[str] = []
    html_parts.extend(_convert_lines(t))

    # placeholder content representing the home page body
    html_parts.append("<p>This is the <em>home/README</em> page.</p>")

    built_links = _build_links(singletons, home_pgs, root_dir)
    html_parts.extend(built_links)

    content_html = "\n".join(html_parts)
    template_path = Path("src/index.html")
    ret = _embed_in_template(content_html, template_path)
    bytes_written = output_path.write_text(html_out, encoding="utf8")
    pass


def GenSingleton(root_dir: Path, singletons: List[str]) -> None:
    """
    for each md in singletons: 
        - generate an html file from template at `src/index.html` with the same markdown file name.
        - convert to html and embed in at div id="placement"
    """
    pass

# ────────────────────────────  conversion helpers  ────────────────────── #

def _convert_lines(lines: List[str]) -> List[str]:
    """Convert markdown ``lines`` into HTML fragments."""
    html_parts: List[str] = []
    line_idx = 0

    # front matter
    if lines and lines[0].strip() == "---":
        line_idx += 1
        while line_idx < len(lines) and lines[line_idx].strip() != "---":
            line_idx += 1
        line_idx += 1

    while line_idx < len(lines):
        line = lines[line_idx]

        if RE_BLANK.match(line):
            line_idx += 1
            continue

        if m := RE_CALLOUT.match(line):
            kind = m.group(1)
            title_text = m.group(2).strip()
            body: List[str] = []
            line_idx += 1
            while line_idx < len(lines) and lines[line_idx].startswith('>'):
                body.append(lines[line_idx][1:].lstrip())
                line_idx += 1
            html_parts.append(build_callout(kind, title_text, body))
            continue

        if m := RE_FENCE.match(line):
            lang = m.group(1)
            code_lines: List[str] = []
            line_idx += 1
            while line_idx < len(lines) and not RE_FENCE.match(lines[line_idx]):
                code_lines.append(lines[line_idx].rstrip("\n"))
                line_idx += 1
            line_idx += 1
            code = html.escape("\n".join(code_lines))
            html_parts.append(t.CODE_BLOCK_TEMPLATE.format(lang=lang, code=code))
            continue

        if RE_LATEX_BLOCK.match(line):
            block: List[str] = []
            line_idx += 1
            while line_idx < len(lines) and not RE_LATEX_BLOCK.match(lines[line_idx]):
                block.append(lines[line_idx].rstrip("\n"))
                line_idx += 1
            if line_idx < len(lines):
                line_idx += 1
            latex_content = "\n".join(block)
            html_parts.append(f"<p>$$\n{latex_content}\n$$</p>")
            continue

        if m := RE_HEADER.match(line):
            level = len(m.group(1))
            hdr = inline_md(m.group(2).strip())
            html_parts.append(f"<h{level}>{hdr}</h{level}>")
            line_idx += 1
            continue

        if m := RE_IMAGE.match(line):
            name = html.escape(m.group(1).strip())
            html_parts.append(f'<img src="../graphics/{name}" alt="{name}">')
            line_idx += 1
            continue

        l=line.rstrip("\n")
        paragraph = inline_md(l)
        html_parts.append(f"<p>{paragraph}</p>")
        line_idx += 1

    return html_parts


def _build_links(terminal_sites: List[str], valid_dirs: List[str], root_dir: Path) -> List[str]:
    """Return link list HTML for articles and directories."""
    parts: List[str] = []

    def make_link(item: str) -> str:
        href = html.escape(str((root_dir / item).as_posix()))
        text = html.escape(str(item))
        return f'<a href="{href}">{text}</a>'

    if terminal_sites:
        parts.append("<ul>")
        for site in terminal_sites:
            site = str(Path(site).with_suffix(".html"))
            parts.append(f"<li>{make_link(site)}</li>")
        parts.append("</ul>")

    if valid_dirs:
        parts.append("<ul>")
        for directory in valid_dirs:
            parts.append(f"<li>{make_link(directory)}</li>")
        parts.append("</ul>")

    return parts


def _embed_in_template(content_html: str, template_path: Path) -> str:
    """Insert ``content_html`` into ``template_path`` using the placement div."""
    placeholder = '<div id="placement"></div>'
    template = template_path.read_text(encoding="utf8")
    return template.replace(placeholder, f'<div id="placement">{content_html}</div>')


# ────────────────────────────  main converter  ───────────────────────── #

def markdown_to_html( root_dir: Path, title: str = "Document",) -> str:
    """Return a full HTML page for ``md_input`` using ``index.html`` template."""

    if not is_valid_dir(root_dir): raise ValueError(f"Invalid root directory: {root_dir=}")

    template_path = Path("src/index.html")

    items = list(root_dir.iterdir())
    ig_lst = ['README.md', 'readme.md', '.DS_Store'] 
    singletons = [item for item in items if item.suffix == '.md' and item.name not in ig_lst]
    home_pgs = [directory for directory in items if directory.is_dir() and is_valid_dir(directory) and directory.name not in ig_lst]

    GenHomePage(root_dir, home_pgs)
    GenSingleton(root_dir, singletons)

    html_parts: List[str] = []
    fp=root_dir/Path("README.md")
    t=fp.read_text(encoding="utf8").splitlines()
    html_parts.extend(_convert_lines(t))

    # placeholder content representing the home page body
    html_parts.append("<p>This is the <em>home/README</em> page.</p>")

    built_links = _build_links(singletons, home_pgs, root_dir)
    html_parts.extend(built_links)

    content_html = "\n".join(html_parts)
    ret = _embed_in_template(content_html, template_path)
    return ret

# ────────────────────────────  CLI  ──────────────────────────── #

def main() -> None:
    """CLI entry point used for manual testing."""

    md_input = Path('example_input/pipe.md').read_text(encoding='utf8')
    output_path = Path('example_output/pipe.html')
    root_dir = Path('/Users/gramjos/Documents/try_hosting_Vault')

    html_out = markdown_to_html( root_dir=root_dir)
    bytes_written = output_path.write_text(html_out, encoding="utf8")
    print(f"{bytes_written=}")
    print(f"✓  wrote {output_path}")

if __name__ == "__main__": main()
