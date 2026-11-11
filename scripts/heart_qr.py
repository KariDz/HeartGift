#!/usr/bin/env python3
"""Create a romantic heart-framed QR code (PNG + SVG) without breaking scanability.

The data grid remains an ordinary, high-correction QR code. Heart framing and
decorations are OUTSIDE the QR quiet zone and cannot corrupt the encoded URL.
"""
import argparse
import html
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "_vendor"))
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError as exc:
    raise SystemExit("Missing dependencies. Install: pip install -r requirements-qr.txt") from exc

SIZE=(1600,1840)
PINK="#ffe6f0"
ROSE="#f1a9c5"
DARK="#85254f"
BG="#fff9fb"
LABEL_COLOR="#893459"

def make_heart_path(cx,cy,sx,sy):
    return [(cx+16*math.sin(t)**3*sx,
             cy-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))*sy)
            for t in (2*math.pi*i/540 for i in range(541))]

def generate(url, output, label):
    if not url.startswith(("https://","http://")):
        raise ValueError("A scannable web QR requires an http(s) URL")
    qr=qrcode.QRCode(version=None,error_correction=qrcode.constants.ERROR_CORRECT_H,
                     box_size=12,border=4)
    qr.add_data(url);qr.make(fit=True)
    matrix=qr.get_matrix() # includes the four-module quiet zone
    count=len(matrix)
    width,height=SIZE
    box=int(880/count)
    qr_size=count*box
    startx=(width-qr_size)//2
    starty=518
    im=Image.new("RGB",SIZE,BG)
    heart=make_heart_path(800,890,41.7,43)
    shadow=Image.new("RGBA",SIZE,(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    sd.polygon([(x+6,y+22) for x,y in heart],fill=(156,40,93,100))
    shadow=shadow.filter(ImageFilter.GaussianBlur(46))
    im=Image.alpha_composite(im.convert("RGBA"),shadow)
    d=ImageDraw.Draw(im)
    d.polygon(heart,fill=PINK)
    d.line(heart,fill=ROSE,width=23,joint="curve")
    # Solid, high-contrast light background and full quiet zone.
    pad=25
    d.rounded_rectangle((startx-pad,starty-pad,startx+qr_size+pad,starty+qr_size+pad),
                        radius=33,fill="white")
    for j,row in enumerate(matrix):
        for i,value in enumerate(row):
            if not value:continue
            x=startx+i*box;y=starty+j*box
            # Rounded dark cells have high contrast, no overlays over data.
            r=max(1,round(box*.11))
            d.rounded_rectangle((x,y,x+box-1,y+box-1),radius=r,fill=DARK)
    d.text((800,186),"♥",anchor="mm",fill=DARK,font=ImageFont.truetype("DejaVuSans.ttf",130))
    try:
        font=ImageFont.truetype("DejaVuSans.ttf",45)
    except OSError:font=ImageFont.load_default()
    d.text((800,1690),label,anchor="mm",fill=LABEL_COLOR,font=font)
    im=im.convert("RGB")
    output.parent.mkdir(parents=True,exist_ok=True)
    png=output.with_suffix(".png");svg=output.with_suffix(".svg")
    im.save(png,optimize=True)

    # Vector QR with the SAME data bits: perfect for print at any size.
    hpoints=" ".join(f"{x:.2f},{y:.2f}" for x,y in heart)
    buf=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Heart-shaped QR code">',
         f'<rect width="{width}" height="{height}" fill="{BG}"/>',
         f'<polygon points="{hpoints}" fill="{PINK}" stroke="{ROSE}" stroke-width="23"/>',
         f'<rect x="{startx-pad}" y="{starty-pad}" width="{qr_size+2*pad}" height="{qr_size+2*pad}" rx="33" fill="white"/>']
    for j,row in enumerate(matrix):
        for i,value in enumerate(row):
            if value:
                buf.append(f'<rect x="{startx+i*box}" y="{starty+j*box}" width="{box}" height="{box}" rx="{max(1,round(box*.11))}" fill="{DARK}"/>')
    buf += [f'<text x="800" y="220" font-size="130" fill="{DARK}" text-anchor="middle">♥</text>',
            f'<text x="800" y="1690" font-family="sans-serif" font-size="45" fill="{LABEL_COLOR}" text-anchor="middle">{html.escape(label)}</text>',
            '</svg>']
    svg.write_text("\n".join(buf)+"\n",encoding="utf8")
    print("URL:",url)
    print("Modules:",count,"QR box:",box)
    print("PNG:",png,"SVG:",svg)
    return png,svg

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url",required=True,help="The complete public URL to encode")
    p.add_argument("--output",default="site/qr/heartgift",type=Path,help="Output filename stem")
    p.add_argument("--label",default="SCAN WITH LOVE",help="Caption below the heart")
    args=p.parse_args()
    generate(args.url,args.output,args.label)
