import sys
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]
for n in (192, 512):
    im = Image.new('RGB', (n, n), '#c0392b'); d = ImageDraw.Draw(im)
    # sea waves
    for k, c in enumerate(['#2e86c1', '#1b6fa8']):
        y = int(n * (0.70 + 0.09 * k)); d.rectangle([0, y, n, n], fill=c)
    d.ellipse([n*0.58, n*0.14, n*0.84, n*0.40], fill='#f9d56e')
    f = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', int(n * 0.36))
    d.text((n*0.5, n*0.47), '三亚', font=f, fill='white', anchor='mm')
    im.save(f'{out}/icon-{n}.png')
print('icons ok')
