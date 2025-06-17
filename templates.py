"""HTML templates used by markdown_to_html"""
import html


def get_head(title: str) -> str:
    """Return the HTML <head> section with the given title."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
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


CODE_BLOCK_TEMPLATE = (
    '<div class="code-block">'
    '<button class="copy" onclick="copySibling(this)">Copy</button>'
    '<pre><code class="language-{lang}">{code}</code></pre>'
    "</div>"
)
