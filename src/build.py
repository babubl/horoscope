"""Build the site from src/: index.html (English) plus /ta/ /ml/ /te/ /kn/ /hi/ language pages,
per-language manifests and sitemap.xml.  Run from the repo root:  python3 src/build.py"""
import html
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from seo import SEO, LANGS, NATIVE, LOCALE, BRAND  # noqa: E402

SITE = 'https://subajathagam.in'
tmpl = open('src/template.html').read()
astro = open('src/vendor/astronomy.browser.min.js').read()
engine = open('src/engine.js').read()
i18n = open('src/i18n.js').read()
culture = open('src/culture.js').read()

base = tmpl.replace('<script>/*ASTRONOMY*/</script>', '<script>/* astronomy-engine 2.1.19 (MIT) — Don Cross, https://github.com/cosinekitty/astronomy */\n' + astro + '\n</script>')
base = base.replace('<script>/*ENGINE*/</script>', '<script>\n' + engine + '\n</script>\n<script>\n' + i18n + '\n</script>\n<script>\n' + culture + '\n</script>')

# ---- the merged UI dictionaries, evaluated with node exactly as the page does
i0 = tmpl.index('const I = {')
i1 = tmpl.index('\n};\n', i0) + 3
js = i18n + '\n' + tmpl[i0:i1] + '''
Object.assign(I.en, I_EXTRA.en); Object.assign(I.ta, I_EXTRA.ta);
for (const l of ['ml', 'te', 'kn', 'hi']) I[l] = Object.assign({}, I.en, I_EXTRA[l]);
process.stdout.write(JSON.stringify(I));'''
I = json.loads(subprocess.run(['node', '-'], input=js, capture_output=True, text=True, check=True).stdout)


def path(l):
    return '/' if l == 'en' else f'/{l}/'


def esc(x):
    return html.escape(x, quote=True)


def seo_section(l):
    d = SEO[l]
    faq = ''.join(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>' for q, a in d['faq'])
    links = ''.join(f'<a href="{path(x)}" hreflang="{x}" lang="{x}">{NATIVE[x]}</a>' for x in LANGS if x != l)
    return f'''<section class="card seo" id="about-site" lang="{l}">
    <h2>{esc(d['h2'])}</h2>
    <p>{esc(d['intro'])}</p>
    {faq}
    <nav class="langs" aria-label="Languages">{links}</nav>
  </section>'''


def jsonld(l):
    d = SEO[l]
    url = SITE + path(l)
    g = [
        {'@type': 'WebSite', '@id': SITE + '/#site', 'name': 'Suba Jathagam', 'alternateName': [BRAND[x] for x in LANGS if x != 'en'],
         'url': SITE + '/', 'inLanguage': LANGS},
        {'@type': 'WebApplication', 'name': BRAND[l], 'url': url, 'applicationCategory': 'LifestyleApplication', 'operatingSystem': 'Any',
         'inLanguage': l, 'description': d['desc'], 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'INR'}, 'isAccessibleForFree': True,
         'featureList': ['Rasi and Navamsa charts (South and North Indian style)', 'Vimshottari dasa and bhukti', '10 porutham and 36 guna marriage matching',
                         'Daily panchangam and Rahu kalam', 'Traditional printable horoscope', 'Tamil, Malayalam, Telugu, Kannada, Hindi and English']},
        {'@type': 'FAQPage', 'inLanguage': l, 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in d['faq']]},
    ]
    return '<script type="application/ld+json">\n' + json.dumps({'@context': 'https://schema.org', '@graph': g}, ensure_ascii=False) + '\n</script>\n'


def prerender(page, l):
    """Fill data-t elements with the language's text, so search engines and slow phones see it before scripts run."""
    D = I[l]
    head, rest = page.split('<body>', 1)
    body, tail = rest.split('<script>/* astronomy-engine', 1)

    def fill(m):
        k = m.group(2)
        v = D.get(k, I['en'].get(k))
        return m.group(1) + esc(v) + m.group(4) if isinstance(v, str) else m.group(0)
    body = re.sub(r'(<[a-z0-9]+[^>]*\bdata-t="(\w+)"[^>]*>)([^<]*)(<)', fill, body)
    body = body.replace(f'<option value="{l}" lang="{l}">', f'<option value="{l}" lang="{l}" selected>')
    body = body.replace('<span id="langCur">English</span>', f'<span id="langCur">{NATIVE[l]}</span>', 1)
    body = body.replace(f'data-lang="{l}" lang="{l}" hreflang', f'class="on" data-lang="{l}" lang="{l}" hreflang', 1)
    open_tag = '<body class="indic">' if l != 'en' else '<body>'
    return head + open_tag + body + '<script>/* astronomy-engine' + tail


titles = {l: SEO[l]['title'] for l in LANGS}
alts = ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{path(l)}">\n' for l in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{SITE}/">\n'

for l in LANGS:
    d = SEO[l]
    p = base
    p = p.replace('<html lang="en">', f'<html lang="{l}">', 1)
    p = re.sub(r'<title>.*?</title>', f'<title>{esc(d["title"])}</title>', p, count=1)
    p = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(d["desc"])}">', p, count=1)
    p = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{esc(d["keywords"])}">', p, count=1)
    p = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{SITE}{path(l)}">\n' + alts.rstrip('\n'), p, count=1)
    p = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(d["title"])}">', p, count=1)
    p = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(d["desc"])}">', p, count=1)
    p = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{SITE}{path(l)}">', p, count=1)
    p = re.sub(r'<meta property="og:locale" content="[^"]*">\n<meta property="og:locale:alternate" content="[^"]*">',
               f'<meta property="og:locale" content="{LOCALE[l]}">\n' + '\n'.join(f'<meta property="og:locale:alternate" content="{LOCALE[x]}">' for x in LANGS if x != l), p, count=1)
    p = re.sub(r'<script type="application/ld\+json">.*?</script>\n', lambda m: jsonld(l), p, count=1, flags=re.S)
    p = p.replace('<link rel="manifest" href="/manifest.webmanifest">', f'<link rel="manifest" href="{"/" if l == "en" else path(l)}manifest.webmanifest">', 1)
    p = p.replace('</head>', f'<script>window.SJ_LANG={json.dumps(l)};window.SJ_TITLES={json.dumps(titles, ensure_ascii=False)};</script>\n</head>', 1)
    p = p.replace('<!--SEO-->', seo_section(l), 1)
    p = prerender(p, l)
    out = 'index.html' if l == 'en' else f'{l}/index.html'
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    open(out, 'w').write(p)
    print(out, len(p))

# ---- manifests
for l in LANGS:
    m = {
        'name': f'{BRAND[l]} · Suba Jathagam' if l != 'en' else 'Suba Jathagam',
        'short_name': BRAND[l] if l != 'en' else 'Suba Jathagam',
        'description': SEO[l]['desc'], 'lang': l, 'dir': 'ltr',
        'id': path(l), 'start_url': path(l) + '?source=pwa', 'scope': '/',
        'display': 'standalone', 'orientation': 'portrait', 'background_color': '#f7efe0', 'theme_color': '#6e1216',
        'categories': ['lifestyle', 'entertainment', 'books'],
        'icons': [{'src': '/icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
                  {'src': '/icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
                  {'src': '/icons/icon-maskable-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'maskable'},
                  {'src': '/icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}],
        'shortcuts': [{'name': I[l]['tabHoro'], 'url': path(l) + '?source=pwa#horo', 'icons': [{'src': '/icons/icon-192.png', 'sizes': '192x192'}]},
                      {'name': I[l]['tabMatch'], 'url': path(l) + '?source=pwa#match', 'icons': [{'src': '/icons/icon-192.png', 'sizes': '192x192'}]},
                      {'name': I[l]['tabPanch'], 'url': path(l) + '?source=pwa#panch', 'icons': [{'src': '/icons/icon-192.png', 'sizes': '192x192'}]}],
    }
    out = 'manifest.webmanifest' if l == 'en' else f'{l}/manifest.webmanifest'
    open(out, 'w').write(json.dumps(m, ensure_ascii=False, indent=2) + '\n')

# ---- sitemap with language alternates
xl = ''.join(f'    <xhtml:link rel="alternate" hreflang="{x}" href="{SITE}{path(x)}"/>\n' for x in LANGS) + f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/>\n'
urls = ''.join(f'  <url><loc>{SITE}{path(l)}</loc><changefreq>weekly</changefreq><priority>{"1.0" if l == "en" else "0.9"}</priority>\n{xl}  </url>\n' for l in LANGS)
for pg, fq, pr in [('guide.html', 'monthly', '0.7'), ('about.html', 'yearly', '0.4'), ('privacy.html', 'yearly', '0.3'), ('terms.html', 'yearly', '0.3')]:
    urls += f'  <url><loc>{SITE}/{pg}</loc><changefreq>{fq}</changefreq><priority>{pr}</priority></url>\n'
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + '</urlset>\n')
print('manifests, sitemap.xml')
