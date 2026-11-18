#!/usr/bin/env python3
"""Build the DOK Prime Ventures static site.

    python3 build.py

Reads   src/pages/*.html      page content, each starting with a front-matter block
        src/partials/*.html   header and footer shared by every page
        src/data/site.json    business details (WhatsApp number, phone, address...)
        src/data/products.json  product catalogue
Copies  src/css, src/js, src/assets
Writes  dist/  the finished site; upload this folder to the web host.

Placeholders available inside pages and partials:
    {{nav}}                      main navigation, current page highlighted
    {{phone}} {{email}} {{address}} {{hours}} {{form_endpoint}} {{whatsapp}}
    {{wa:Message text}}          href/target/rel attributes for a WhatsApp chat link
    {{products:featured}}        product cards (also :poultry, :clothing, :all)
"""
import html
import json
import os
import re
import shutil
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

site = json.loads((SRC / "data" / "site.json").read_text(encoding="utf-8"))
products = json.loads((SRC / "data" / "products.json").read_text(encoding="utf-8"))
header = (SRC / "partials" / "header.html").read_text(encoding="utf-8")
footer = (SRC / "partials" / "footer.html").read_text(encoding="utf-8")

CATEGORY = {
    "poultry": {"label": "Poultry", "icon": "hen", "style": "ph-poultry"},
    "clothing": {"label": "Clothing", "icon": "smock", "style": "ph-smock"},
}

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">{base}
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="website">
  <meta name="theme-color" content="#1F4D2B">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>

  <a class="skip-link" href="#main">Skip to content</a>

  {header}
  <main id="main">
{body}
  </main>

  {footer}
  <script src="js/main.js"></script>
</body>
</html>
"""


def wa_attrs(message: str) -> str:
    url = f"https://wa.me/{site['whatsapp']}?text={urllib.parse.quote(message)}"
    return f'href="{html.escape(url)}" target="_blank" rel="noopener"'


def nav_html(current: str) -> str:
    items = []
    for key, href, label in site["nav"]:
        cur = ' aria-current="page"' if key == current else ""
        items.append(f'          <li><a href="{href}"{cur}>{label}</a></li>')
    return "<ul>\n" + "\n".join(items) + "\n        </ul>"


def product_card(p: dict) -> str:
    c = CATEGORY[p["category"]]
    name = html.escape(p["name"])
    price = html.escape(p["price"]) if p.get("price") else "Ask for price"
    msg = f"Hello DOK Prime Ventures, I'm interested in: {p['name']}. Is it available?"
    return f"""          <article class="product">
            <div class="ph {c['style']}" aria-hidden="true">
              <span class="product-tag">{c['label']}</span>
              <svg class="ph-icon"><use href="#i-{c['icon']}"/></svg>
            </div>
            <div class="product-body">
              <h3>{name}</h3>
              <p>{html.escape(p['description'])}</p>
              <div class="price">{price}</div>
              <a class="btn btn-green" {wa_attrs(msg)}>
                <svg class="icon" aria-hidden="true"><use href="#i-whatsapp"/></svg>
                Order on WhatsApp
              </a>
            </div>
          </article>"""


def products_html(which: str) -> str:
    if which == "featured":
        chosen = [p for p in products if p.get("featured")]
    elif which == "all":
        chosen = products
    else:
        chosen = [p for p in products if p["category"] == which]
    return "\n".join(product_card(p) for p in chosen)


def fill(text: str, current: str) -> str:
    text = text.replace("{{nav}}", nav_html(current))
    text = re.sub(r"\{\{products:(\w+)\}\}", lambda m: products_html(m.group(1)), text)
    text = re.sub(r"\{\{wa:(.*?)\}\}", lambda m: wa_attrs(html.unescape(m.group(1))), text)
    for key in ("phone", "email", "address", "hours", "form_endpoint", "whatsapp"):
        text = text.replace("{{" + key + "}}", html.escape(site[key]))
    left = re.findall(r"\{\{[^}]*\}\}", text)
    if left:
        raise SystemExit(f"Unknown placeholder(s) in page '{current}': {sorted(set(left))}")
    return text


def parse(path: Path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing front matter")
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    return meta, raw[m.end():]


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for folder in ("css", "js", "assets"):
        if (SRC / folder).exists():
            shutil.copytree(SRC / folder, DIST / folder)

    for path in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse(path)
        nav = meta.get("nav", "")
        base_path = os.environ.get("BASE_PATH") or site.get("base_path", "/")
        base_href = base_path if meta.get("base") == "auto" else meta.get("base")
        base = f'\n  <base href="{base_href}">' if base_href else ""
        page = PAGE.format(
            base=base,
            title=html.escape(meta["title"]),
            description=html.escape(meta["description"]),
            header=fill(header.strip(), nav),
            footer=fill(footer.strip(), nav),
            body=fill(body.rstrip(), nav),
        )
        (DIST / path.name).write_text(page, encoding="utf-8")
        print("built", path.name)


if __name__ == "__main__":
    main()
