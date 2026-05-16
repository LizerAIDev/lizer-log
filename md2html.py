# md2html.py
"""Markdown to HTML converter CLI tool."""

from typing import Optional
import argparse
import re
from pathlib import Path


def md_to_html(md_text: str, theme: Optional[str] = None) -> str:
    """Convert Markdown text to HTML.
    
    Args:
        md_text: Markdown source text.
        theme: Optional CSS theme name.
        
    Returns:
        HTML string.
    """
    lines = md_text.split("\n")
    html_lines = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            html_lines.append("</code></pre>" if in_code_block else "<pre><code>")
            continue
            
        if in_code_block:
            html_lines.append(line)
            continue
            
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("- "):
            html_lines.append(f"<li>{line[2:]}</li>")
        elif line.startswith("http"):
            html_lines.append(f"<p><a href=\"{line}\">{line}</a></p>")
        elif line.strip():
            # Basic link pattern: [text](url)
            line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)
            html_lines.append(f"<p>{line}</p>")
            
    body = "\n".join(html_lines)
    theme_css = f"<link rel=\"stylesheet\" href=\"{theme}.css\">" if theme else ""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">{theme_css}</head>
<body>
{body}
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Markdown to HTML converter")
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("-o", "--output", help="Output HTML file")
    parser.add_argument("--theme", help="CSS theme file")
    args = parser.parse_args()
    
    md_text = Path(args.input).read_text(encoding="utf-8")
    html = md_to_html(md_text, args.theme)
    
    output_path = args.output or Path(args.input).with_suffix(".html")
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Converted: {args.input} -> {output_path}")


if __name__ == "__main__":
    main()
