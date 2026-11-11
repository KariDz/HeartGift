#!/usr/bin/env python3
"""Generate license-free abstract placeholder portraits for the community demo."""
from pathlib import Path
import colorsys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"public/images/photos"
OUT.mkdir(parents=True,exist_ok=True)
fontpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
try:
    title=ImageFont.truetype(fontpath,36)
    small=ImageFont.truetype(fontpath,21)
except OSError:
    title=small=ImageFont.load_default()

for n in range(1,12):
    random.seed(n)
    w,h=600,750
    a=(n*.073+.7)%1
    def rgb(hue, sat, lig):
        # HLS: pastel, with contrast for readable lettering.
        return tuple(int(255*x) for x in colorsys.hls_to_rgb(hue%1,lig,sat))
    color1=rgb(a,.58,.73);color2=rgb(a+.11,.45,.84)
    im=Image.new("RGB",(w,h))
    pix=im.load()
    for y in range(h):
        t=y/max(h-1,1)
        row=tuple(int(color1[c]*(1-t)+color2[c]*t) for c in range(3))
        for x in range(w):pix[x,y]=row
    d=ImageDraw.Draw(im,"RGBA")
    for i in range(10):
        cx=random.randint(-80,w+80);cy=random.randint(-60,h+60)
        r=random.randint(32,150)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,255,255,random.randint(12,55)))
    # DIY minimal memory-card illustration; no third-party photos.
    d.rounded_rectangle((46,45,w-46,h-48),radius=35,outline=(255,255,255,170),width=5)
    for j in range(8):
        cx=random.randrange(80,w-80);cy=random.randrange(120,h-140)
        d.ellipse((cx-3,cy-3,cx+3,cy+3),fill=(255,255,255,190))
    title_text=f"MEMORY {n:02d}"
    bbox=d.textbbox((0,0),title_text,font=title)
    d.text(((w-(bbox[2]-bbox[0]))/2,310),title_text,font=title,fill=(95,44,93,255))
    sub="Your favorite moment here"
    bb=d.textbbox((0,0),sub,font=small)
    d.text(((w-(bb[2]-bb[0]))/2,375),sub,font=small,fill=(109,58,100,225))
    d.text((268,196),"♥",font=title,fill=(143,49,104,210))
    target=OUT/f"{n:02d}.webp"
    im.save(target,"WEBP",quality=83,method=5)
    print(target.relative_to(ROOT),target.stat().st_size)
