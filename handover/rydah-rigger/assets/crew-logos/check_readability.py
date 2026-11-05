#!/usr/bin/env python3
"""Composite each patch on its own jacket base color at 256/96/64 px."""
import json, os
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(f'{OUT}/jacket-colorways.json'))['crews']
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
CW, CH = 470, 330
sheet = Image.new('RGB', (2*CW, 5*CH+60), (20, 20, 26)); d = ImageDraw.Draw(sheet)
d.text((16, 18), 'PATCH READABILITY on own jacket base (256 / 96 / 64 px)', font=f, fill=(235, 235, 235))
for i, (slug, e) in enumerate(J.items()):
    x0, y0 = i % 2*CW, 60+i//2*CH
    d.rectangle((x0+8, y0+8, x0+CW-8, y0+CH-8), fill=e['base']['hex'])
    logo = Image.open(e['patch']['albedo_with_shadow']).convert('RGBA')
    for sz, (dx, dy) in ((256, (20, 40)), (96, (300, 60)), (64, (316, 190))):
        sheet.paste(logo.resize((sz, sz), Image.LANCZOS), (x0+dx, y0+dy), logo.resize((sz, sz), Image.LANCZOS))
    d.rectangle((x0+8, y0+8, x0+CW-8, y0+34), fill=(0, 0, 0))
    d.text((x0+16, y0+11), f"{e['name']}  (jacket {e['base']['hex']})", font=f, fill=(240, 240, 240))
sheet.save(f'{OUT}/patch-readability-check.png')
