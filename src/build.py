"""Build index.html from src/template.html + src/engine.js + vendored astronomy-engine. Run from repo root: python3 src/build.py"""
s = open('src/template.html').read()
a = open('src/vendor/astronomy.browser.min.js').read()
e = open('src/engine.js').read()
s = s.replace('<script>/*ASTRONOMY*/</script>', '<script>/* astronomy-engine 2.1.19 (MIT) — Don Cross, https://github.com/cosinekitty/astronomy */\n' + a + '\n</script>')
s = s.replace('<script>/*ENGINE*/</script>', '<script>\n' + e + '\n</script>')
open('index.html', 'w').write(s)
print('index.html', len(s))
