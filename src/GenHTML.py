from pathlib import Path
from typing import List, Optional

__all__ = ["GenHomePage", "GenSingleton"]

"""Helpers to generate directory index pages and standalone article pages."""


def _load_helpers():
    """Import helper functions from x module lazily to avoid circular imports."""
    from . import x as core
    return core._convert_lines, core._build_links, core._embed_in_template, core.is_valid_dir


def GenHomePage(root_dir: Path, valid_dirs: List[str], *, base_root: Optional[Path] = None) -> None:
    """Generate HTML homepages for subdirectories containing a README."""
    convert, build_links, embed, is_valid = _load_helpers()

    root_dir = Path(root_dir)
    base_root = root_dir if base_root is None else Path(base_root)
    out_root = base_root / "example_output"

    for name in valid_dirs:
        subdir = root_dir / name
        readme = subdir / "README.md"
        if not readme.exists():
            continue

        # Discover markdown files and further subdirectories
        terminal_sites = [p.name for p in subdir.glob("*.md") if p.name.lower() != "readme.md"]
        sub_valid_dirs = [d.name for d in subdir.iterdir() if d.is_dir() and is_valid(d)]

        # Recursively generate children first
        if sub_valid_dirs:
            GenHomePage(subdir, sub_valid_dirs, base_root=base_root)
        if terminal_sites:
            GenSingleton(subdir, terminal_sites, base_root=base_root)

        # Convert README
        lines = readme.read_text(encoding="utf8").splitlines()
        parts = []
        parts.extend(convert(lines))
        parts.extend(build_links(terminal_sites, sub_valid_dirs, Path('.')))
        html = embed("\n".join(parts), Path("src/index.html"))

        out_dir = out_root / subdir.relative_to(base_root)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(html, encoding="utf8")


def GenSingleton(root_dir: Path, terminal_sites: List[str], *, base_root: Optional[Path] = None) -> None:
    """Generate HTML pages for individual markdown files."""
    convert, _, embed, _ = _load_helpers()

    root_dir = Path(root_dir)
    base_root = root_dir if base_root is None else Path(base_root)
    out_root = base_root / "example_output"
    rel_dir = root_dir.relative_to(base_root)
    out_dir = out_root / rel_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    for md_name in terminal_sites:
        md_path = root_dir / md_name
        if not md_path.is_file():
            continue
        lines = md_path.read_text(encoding="utf8").splitlines()
        html = embed("\n".join(convert(lines)), Path("src/index.html"))
        out_file = out_dir / Path(md_name).with_suffix(".html")
        out_file.write_text(html, encoding="utf8")
