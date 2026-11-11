#!/usr/bin/env python3
"""Create a real, editable heart QR code in the red-on-black diamond style.

Example:
    python tao_qr_trai_tim.py --url 'https://karidz.github.io/HeartGift/' \
        --output HeartGift-QR-Trai-Tim

Requires: pip install pillow qrcode[pil]
Optional QR verification: pip install opencv-python

Design:
    - Real QR code with high error correction, rotated 45 degrees
    - Procedural red QR-like tiles decorate the two heart lobes
    - A tiny white heart badge covers the center, leaving finder patterns intact
    - SVG contains actual paths (not a bitmap embedded in SVG)
    - A standard dark-on-light QR is also exported for maximum scanner compatibility
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "_vendor"))
import qrcode

CANVAS = (1400, 1820)
CENTER_X = 700
QR_CENTER_Y = 850
RED = (255, 50, 65)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MODULE_SIZE = 9
QUIET_MODULES = 2
SEED = 118


def heart_shape(cx: float, cy: float, scale_x: float, scale_y: float, steps=1200):
    """Sample the familiar parametric heart curve, clockwise closed."""
    points = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        points.append((cx + x * scale_x, cy - y * scale_y))
    return points


def solid_heart_logo(cx: int, cy: int):
    # A hand-drawn vector heart, with no emoji/font dependency.
    return heart_shape(cx, cy - 1, 1.36, 1.38, 200)


def build_qr(url: str):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=QUIET_MODULES,
    )
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    # This heart is designed for approximately version 5, but longer URLs can
    # be accommodated by shrinking tiles to fit the outline.
    side = len(matrix)
    box = min(MODULE_SIZE, max(4, int(370 / side)))
    return matrix, box


def heart_mask():
    mask = Image.new('L', CANVAS, 0)
    d = ImageDraw.Draw(mask)
    d.polygon(heart_shape(700, 740, 27, 26.5), fill=255)
    return mask


def filler_tiles(mask, tile_size, seed=SEED):
    """Generate decorative diamonds *outside* the true QR's black pixels.

    These are not QR payload; only the 45-degree QR diamond is machine-readable.
    Their centers and all vertices remain inside the heart silhouette.
    """
    rng = random.Random(seed)
    tiles = []
    length = 66
    diagonal = tile_size / math.sqrt(2)
    for v in range(-length, length + 1):
        for u in range(-length, length + 1):
            if rng.random() >= 0.55:
                continue
            x = CENTER_X + (u - v) * diagonal
            y = QR_CENTER_Y + (u + v) * diagonal
            if not (0 < x < CANVAS[0] and 0 < y < CANVAS[1]):
                continue
            shape = ((x, y - diagonal), (x + diagonal, y),
                     (x, y + diagonal), (x - diagonal, y))
            if any(not (0 <= px < CANVAS[0] and 0 <= py < CANVAS[1]
                        and mask.getpixel((int(px), int(py))) > 0)
                   for px, py in shape):
                continue
            tiles.append(shape)
    return tiles


def render_png(matrix, box, tiles, output):
    image = Image.new('RGB', CANVAS, BLACK)
    draw = ImageDraw.Draw(image)
    for shape in tiles:
        draw.polygon(shape, fill=RED)

    side = len(matrix) * box
    raw = Image.new('RGBA', (side, side), (0, 0, 0, 255))
    rd = ImageDraw.Draw(raw)
    for j, row in enumerate(matrix):
        for i, bit in enumerate(row):
            if bit:
                rd.rectangle((i * box, j * box, (i + 1) * box - 1, (j + 1) * box - 1),
                             fill=(*RED, 255))
    # Pillow: negative angles are clockwise on the screen, so the QR's three
    # finder markers sit at the top, lower left, and lower right.
    turned = raw.rotate(-45, resample=Image.Resampling.NEAREST,
                        expand=True, fillcolor=(0, 0, 0, 0))
    image.paste(turned, (CENTER_X - turned.width // 2,
                         QR_CENTER_Y - turned.height // 2), turned.getchannel('A'))

    draw = ImageDraw.Draw(image)
    radius = 38
    draw.ellipse((CENTER_X - radius - 2, QR_CENTER_Y - radius - 2,
                  CENTER_X + radius + 2, QR_CENTER_Y + radius + 2),
                 fill=(220, 220, 220))
    draw.ellipse((CENTER_X - radius, QR_CENTER_Y - radius,
                  CENTER_X + radius, QR_CENTER_Y + radius), fill=WHITE)
    draw.polygon(solid_heart_logo(CENTER_X, QR_CENTER_Y), fill=(225, 20, 50))
    # A small highlight gives the badge the pleasant red-heart emoji appearance.
    draw.ellipse((CENTER_X - 15, QR_CENTER_Y - 14,
                  CENTER_X - 8, QR_CENTER_Y - 8), fill=(255, 120, 135))
    image.save(output, optimize=True)
    return image


def svg_path_from_polygon(points, precision=2):
    return 'M ' + ' L '.join(f'{x:.{precision}f},{y:.{precision}f}' for x, y in points) + ' Z'


def render_svg(matrix, box, tiles, output):
    red = '#%02x%02x%02x' % RED
    side = len(matrix) * box
    tile_commands = ' '.join(svg_path_from_polygon(tile, precision=2) for tile in tiles)
    qr_commands = []
    for j, row in enumerate(matrix):
        for i, bit in enumerate(row):
            if bit:
                qr_commands.append(f'M {i*box} {j*box} h {box} v {box} h -{box} Z')
    logo = svg_path_from_polygon(solid_heart_logo(CENTER_X, QR_CENTER_Y))
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1820" '
        'width="1400" height="1820" role="img" aria-label="Heart-shaped QR for HeartGift">',
        '<title>HeartGift — scan me</title>',
        '<rect width="1400" height="1820" fill="#000"/>',
        f'<path d="{tile_commands}" fill="{red}"/>',
        f'<g transform="translate({CENTER_X} {QR_CENTER_Y}) rotate(45) translate(-{side/2} -{side/2})">',
        f'  <rect x="0" y="0" width="{side}" height="{side}" fill="#000"/>',
        f'  <path d="{" ".join(qr_commands)}" fill="{red}"/>',
        '</g>',
        f'<circle cx="{CENTER_X}" cy="{QR_CENTER_Y}" r="40" fill="#ddd"/>',
        f'<circle cx="{CENTER_X}" cy="{QR_CENTER_Y}" r="38" fill="#fff"/>',
        f'<path d="{logo}" fill="#e11432"/>',
        f'<circle cx="{CENTER_X-12}" cy="{QR_CENTER_Y-11}" r="3.5" fill="#ff7887"/>',
        '</svg>',
    ]
    output.write_text('\n'.join(svg), encoding='utf-8')


def render_fallback(url, output):
    """A scanner-safe dark-on-light companion (no rotation or cut-outs)."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=18, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color='#881a37', back_color='#ffffff').convert('RGB').save(output, optimize=True)


def check_qr(url, artwork_path, fallback_path):
    try:
        import cv2
        import numpy as np
    except ImportError:
        print('Optional check skipped: install opencv-python for automatic scan testing.')
        return
    decoder = cv2.QRCodeDetector()
    art = cv2.imread(str(artwork_path))
    # Red QR modules on black are positive/luminous. OpenCV's QR reader expects
    # dark-on-light modules, so invert for verification; some phone apps auto-invert.
    inverted = cv2.bitwise_not(art)
    text, _, _ = decoder.detectAndDecode(inverted)
    if text != url:
        raise RuntimeError('Stylized QR verification failed. Decoded: ' + repr(text))
    fallback = cv2.imread(str(fallback_path))
    text2, _, _ = decoder.detectAndDecode(fallback)
    if text2 != url:
        raise RuntimeError('Fallback QR verification failed. Decoded: ' + repr(text2))
    print('PASS: stylized QR (inverted scan) and standard QR both encode:', url)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url', default='https://karidz.github.io/HeartGift/', help='URL to encode')
    p.add_argument('--output', default='HeartGift-QR-Trai-Tim', help='Output filename stem (without extension)')
    p.add_argument('--seed', type=int, default=SEED, help='Deterministic decoration seed')
    args = p.parse_args()
    if not args.url.startswith(('https://', 'http://')):
        p.error('URL must start with http:// or https://')
    stem = Path(args.output)
    stem.parent.mkdir(parents=True, exist_ok=True)
    matrix, box = build_qr(args.url)
    mask = heart_mask()
    decoration = filler_tiles(mask, MODULE_SIZE, seed=args.seed)
    png = stem.with_suffix('.png')
    svg = stem.with_suffix('.svg')
    standard = stem.parent / (stem.name + '-scan-safe.png')
    render_png(matrix, box, decoration, png)
    render_svg(matrix, box, decoration, svg)
    render_fallback(args.url, standard)
    check_qr(args.url, png, standard)
    print(f'Made {png} ({png.stat().st_size:,} bytes)')
    print(f'Made {svg} ({svg.stat().st_size:,} bytes)')
    print(f'Made {standard} ({standard.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()