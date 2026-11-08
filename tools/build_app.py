import math, os, re, sys, shutil, json, hashlib
from urllib.parse import quote

S, PROJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'tiles'), exist_ok=True)
Z, TX0, TY0 = 16, 52701, 29391

def px(lat, lon):
    n = 2 ** Z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return (x - TX0) * 256, (y - TY0) * 256

cx0, cy0 = px(18.2300, 109.5085)
cx1, cy1 = px(18.2165, 109.5280)
W, H = cx1 - cx0, cy1 - cy0
parts = [f'<svg viewBox="{cx0:.0f} {cy0:.0f} {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Карта района Дадунхай">']
for f in sorted(os.listdir(os.path.join(S, 'tiles'))):
    x, y = map(int, f[:-4].split('_'))
    ox, oy = (x - TX0) * 256, (y - TY0) * 256
    if ox + 256 < cx0 or ox > cx1 or oy + 256 < cy0 or oy > cy1:
        continue
    shutil.copy(os.path.join(S, 'tiles', f), os.path.join(OUT, 'tiles', f))
    parts.append(f'<image href="tiles/{f}" x="{ox}" y="{oy}" width="257" height="257"/>')

def label(x, y, text, size=24, anchor='middle', weight=700, color='#1f2328'):
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}" '
            f'stroke="#fff" stroke-width="6" paint-order="stroke" font-family="Segoe UI,Roboto,sans-serif">{text}</text>')
def pin(lat, lon, text, color, r=11, dy=-18, anchor='middle', size=24, dx=0):
    x, y = px(lat, lon)
    return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{color}" stroke="#fff" stroke-width="4"/>'
            + label(x + dx, y + dy, text, size, anchor, color=color))
hx, hy = px(18.22513, 109.51698)
parts.append(f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="34" fill="#c0392b" fill-opacity=".18"/>')
parts.append(pin(18.22513, 109.51698, 'ВАШ ОТЕЛЬ', '#c0392b', r=15, dy=-24, size=30, anchor='end', dx=-10))
parts.append(pin(18.22517, 109.51920, 'ТЦ «Лето»', '#1d5fa8', dy=40))
parts.append(pin(18.22457, 109.52518, 'ТЦ «Ананас»', '#1d5fa8', dy=-18))
parts.append(pin(18.22380, 109.52217, 'Площадь Дадунхай', '#1e7d4f', dy=34))
parts.append(pin(18.2263, 109.5232, '🦌 YUMMY', '#d35400', dy=-18))
bx, by = px(18.2195, 109.5205); parts.append(label(bx, by, 'ПЛЯЖ ДАДУНХАЙ · море', 30, color='#0b5d8a'))
rx, ry = px(18.2274, 109.5160); parts.append(label(rx, ry, 'кафе с русским меню ↓', 22, color='#9a6700'))
lx, ly = px(18.2205, 109.5105)
parts.append(label(lx, ly, '← «Олень повернул голову»', 22, anchor='start', color='#5b6370'))
parts.append(label(lx, ly + 28, '10 мин на такси', 20, anchor='start', weight=400, color='#5b6370'))
m_per_px = 156543.03 * math.cos(math.radians(18.225)) / 2 ** Z
sb = 200 / m_per_px; sx, sy = cx0 + 20, cy1 - 24
parts.append(f'<rect x="{sx-6:.0f}" y="{sy-30:.0f}" width="{sb+12:.0f}" height="40" fill="#fff" fill-opacity=".85" rx="6"/>')
parts.append(f'<line x1="{sx:.0f}" y1="{sy:.0f}" x2="{sx+sb:.0f}" y2="{sy:.0f}" stroke="#1f2328" stroke-width="5"/>')
parts.append(label(sx + sb / 2, sy - 9, '200 м', 18))
parts.append('</svg>')

html = open(os.path.join(PROJ, 'template.html'), encoding='utf-8').read()
html = html.replace('{{MAP}}', '\n'.join(parts))

imgs = []
def img(m):
    key = m.group(1)
    p = os.path.join(S, 'img', key + '.jpg')
    files = [p] if os.path.exists(p) else []
    i = 1
    while os.path.exists(os.path.join(S, 'img', 'car', f'{key}_{i}.jpg')):
        files.append(os.path.join(S, 'img', 'car', f'{key}_{i}.jpg')); i += 1
    if not files: return ''
    pos = ' style="object-position:center 15%"' if key in ('nanshan', 'wuzhizhou') else ''
    tags = []
    for f in files:
        name = os.path.basename(f); shutil.copy(f, os.path.join(OUT, 'img', name)); imgs.append('img/' + name)
        tags.append(f'<img src="img/{name}" alt="" loading="lazy"{pos if f == p else ""}>')
    if len(tags) == 1: return tags[0]
    return (f'<div class="car"><div class="track">{"".join(tags)}</div>'
            f'<div class="carhint">👉 листайте фото вбок · {len(tags)} фото</div></div>')
html = re.sub(r'\{\{IMG:(\w+)\}\}', img, html)

def a(href, text, cls):
    return f'<a class="mp {cls}" href="{href}" target="_blank" rel="noopener">{text}</a>'
def go(m):
    lat, lon, mode, name, lab = m.groups()
    pre = f'<span class="mpl">{lab}:</span>' if lab else ''
    n = quote(name)
    if mode == 'walk':
        return pre + a(f'https://yandex.ru/maps/?rtext=~{lat}%2C{lon}&rtt=pd', '🚶 Яндекс Карты', 'ya') + \
            a(f'https://uri.amap.com/navigation?to={lon},{lat},{n}&mode=walk&coordinate=wgs84&callnative=1&src=memo', '🚶 Amap', 'am')
    if mode == 'pt':
        ya = f'https://yandex.ru/maps/?pt={lon}%2C{lat}&z=15&l=map'
        am = f'https://uri.amap.com/marker?position={lon},{lat}&name={n}&coordinate=wgs84&callnative=1&src=memo'
    else:
        ya = f'https://yandex.ru/maps/?text={n}&ll=109.5170%2C18.2500&z=11'
        am = f'https://uri.amap.com/search?keyword={n}&city=460200&callnative=1&src=memo'
    return pre + a(ya, '🗺 Яндекс Карты', 'ya') + a(am, '🗺 Amap', 'am')
html = re.sub(r'\{\{GO:([\d.]*),([\d.]*),?(walk|pt|kw)\|([^|}]*)\|([^}]*)\}\}', go, html)
html = re.sub(r'\{\{YA:([^}]*)\}\}', lambda m: a(f'https://yandex.ru/maps/?text={quote(m.group(1))}&ll=109.5180%2C18.2260&z=16', '🗺 Яндекс Карты', 'ya'), html)
assert '{{' not in html, re.findall(r'\{\{.*?\}\}', html)

# --- split into sections
style = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
body = html.split('<div class="wrap">', 1)[1].split('<div class="big-show" id="big">', 1)[0]
body = body.rsplit('</div>', 1)[0]
body = body.replace('<div class="note red">🆘', '<div class="note red" id="sos">🆘', 1)
idx = [(m.start(), m.group(1)) for m in re.finditer(r'(?:<!-- =+[^>]*-->\s*)?<h2 id="(\w+)"', body)]
sec = {}
for k, (pos, sid) in enumerate(idx):
    end = idx[k + 1][0] if k + 1 < len(idx) else len(body)
    sec[sid] = body[pos:end]
intro = body[:idx[0][0]]
TABS = [('home', '🏠', 'Главная', ['plan', 'home', 'trips', 'flight']),
        ('places', '📚', 'Места', ['places', 'walk']),
        ('food', '🍲', 'Еда', ['food', 'map']),
        ('shop', '🛍', 'Шопинг', ['shop']),
        ('phrases', '🗣', 'Фразы', ['phrases']),
        ('info', 'ℹ️', 'Инфо', ['pay', 'didi', 'more'] + (['costs'] if 'costs' in sec else []))]
used = sum((t[3] for t in TABS), [])
assert sorted(used) == sorted(sec), (used, list(sec))

today = '''<div class="today" id="today"></div>
<div class="quick">
  <button class="qb red" data-show="请送我到这个酒店：&lt;br&gt;三亚柏瑞精品海景酒店&lt;br&gt;（大东海广场店）&lt;br&gt;大东海海韵路16号">🚕<span>Такси в отель</span></button>
  <a class="qb" href="#phrases/sos">🆘<span>Помощь</span></a>
  <a class="qb" href="#phrases">🗣<span>Фразы</span></a>
</div>
<div class="note blue small2"><b>Как пользоваться.</b> «Копировать» копирует китайское название (его можно вставить в DiDi). «Показать крупно» выводит надпись на весь экран — покажите водителю или прохожему. Приложение работает и без интернета.</div>
'''
panes = []
for tid, ic, name, ids in TABS:
    inner = (today if tid == 'home' else '') + ''.join(sec[i] for i in ids)
    panes.append(f'<section class="pane" id="p-{tid}" hidden>{inner}</section>')
nav = ''.join(f'<a href="#{t[0]}" data-tab="{t[0]}"><b>{t[1]}</b><span>{t[2]}</span></a>' for t in TABS)

app_css = open(os.path.join(os.path.dirname(__file__), 'app_extra.css'), encoding='utf-8').read()
style = style.replace('body{padding-top:50px}', '')
page = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#c0392b">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Санья">
<title>Санья: памятка</title>
<link rel="manifest" href="manifest.json">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="top"><h1>Санья · памятка для Рифа и Альфии</h1><p>4–13 декабря 2026 · бухта Дадунхай</p></header>
<main class="wrap">
{''.join(panes)}
</main>
<nav class="tabs">{nav}</nav>
<div class="big-show" id="big"><div class="zh" id="bigtxt"></div><button type="button" id="bigclose">✕ Закрыть</button></div>
<script src="app.js"></script>
</body>
</html>
'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
open(os.path.join(OUT, 'style.css'), 'w', encoding='utf-8').write(style.strip() + '\n' + app_css)
files = ['./', 'index.html', 'style.css', 'app.js', 'manifest.json', 'icon-192.png', 'icon-512.png'] + \
    sorted(set(imgs)) + ['tiles/' + f for f in sorted(os.listdir(os.path.join(OUT, 'tiles')))]
json.dump(files, open(os.path.join(OUT, 'files.json'), 'w'), indent=0)
print('ok', len(page) // 1000, 'KB html,', len(imgs), 'img, intro dropped chars:', len(intro))

# --- sw.js: keep VERSION, refresh FILES
swp = os.path.join(OUT, 'sw.js'); ver = 'v1'
if os.path.exists(swp):
    m = re.search(r"VERSION = '(v\d+)'", open(swp, encoding='utf-8').read()); ver = m.group(1) if m else ver
sw = open(os.path.join(os.path.dirname(__file__), 'sw_tpl.js'), encoding='utf-8').read()
sw = sw.replace('__VER__', ver).replace('__FILES__', json.dumps(files, ensure_ascii=False, indent=1))
open(swp, 'w', encoding='utf-8').write(sw)
os.remove(os.path.join(OUT, 'files.json'))
print('sw', ver, len(files), 'files')
