# DOK Prime Ventures website

A static website built by Mos EdTech for DOK Prime Ventures (poultry, smocks & traditional clothing, mobile money services).

## Structure

```
build.py              builds the site into dist/
src/
  data/site.json      WhatsApp number, phone, email, address, hours, form endpoint, menu
  data/products.json  product catalogue (featured: true = shown on the home page)
  partials/           header and footer shared by every page
  pages/              one file per page (front matter + page content)
  css/ js/ assets/    styles, small script, favicon
dist/                 generated site: upload this folder to the host
mockups/              screenshots for client review
```

## Build

```bash
python3 build.py
```

No packages needed (Python 3 standard library only). Open `dist/index.html` in a browser to preview.

## Before launch: what still needs filling in

1. `src/data/site.json`: real WhatsApp number (international format, digits only), phone, address, opening hours.
2. Contact form: create a free Formspree form and put its URL in `form_endpoint`.
3. Map: replace the placeholder on `contact.html` with a Google Maps embed once the address is confirmed.
4. Logo, photos (`.ph` placeholder blocks), and real testimonials and impact stories.
5. Anything highlighted on the pages (`class="tbc"`) needs the client to confirm it, e.g. delivery area, payment methods, MoMo networks, founding year, founder bio.
6. Products and prices in `src/data/products.json`.
7. Blog post publish dates.

## Hosting

The site is hosted on Vercel at https://dokprime.vercel.app/ and redeploys automatically on every push to `main`
(pushes to other branches get preview deployments). Settings are in `vercel.json`: build `python3 build.py`, output `dist`.

`base_path` in `src/data/site.json` is the folder the site is served from (used by the 404 page). It is `/` on Vercel,
including with a custom domain. A `BASE_PATH` environment variable overrides it if the site is ever served from a sub-folder.

`dist/` also works on any other static host (Netlify, Cloudflare Pages): build command `python3 build.py`, publish folder `dist`.
