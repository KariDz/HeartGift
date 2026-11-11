#!/usr/bin/env python3
"""Validate the browser-captured DLove viewer and user-edited 19.11 assets."""
from pathlib import Path
from PIL import Image
import json,sys,hashlib

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
CONFIG=SITE/'gift-config.json'
html=(SITE/'index.html').read_text(encoding='utf-8')
cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
expected='19.11 làm sao em để anh iu của em thiệt thòi được. Món quà nhỏ gửi đến anh, mong rằng mỗi ngày của anh đều ngập tràn hạnh phúc. Cảm ơn anh vì đã xuất hiện trong cuộc đời em.'
assert cfg.get('letter',{}).get('text')==expected,'19.11 wish changed unexpectedly'
assert isinstance(cfg.get('sphereImages'),list) and len(cfg['sphereImages'])>0,'Upload at least one photo'
assert len(set(cfg['sphereImages']))==len(cfg['sphereImages']),'Duplicate image paths in sphereImages'
assert html.count('gift-config.json')>=1,'Missing local gift config loader'
assert 'window.__DL_OFFLINE = true' in html,'Original remote config might be loaded'
assert 'if (window.__DL_OFFLINE) return;' in html,'GitHub Pages path could trigger remote DLove API'
assert 'three.module.js' in html and 'startCupidLetterSequence' in html,'Original viewer code missing'
assert (SITE/'vendor/three/build/three.module.js').is_file(),'Missing local Three.js'
assert (SITE/'assets/fonts/Pacifico-Regular.ttf').is_file(),'Missing local font'
assert not any((SITE/'assets/media').glob('*')) if (SITE/'assets/media').exists() else True, 'Original guest photos should not be published'
assert not list(SITE.rglob('noinaycoanh.mp3')),'Do not redistribute the original commercial song'
all_photos=[]
for i,p in enumerate(cfg['sphereImages'],1):
    photo=(SITE/p).resolve()
    assert photo.is_relative_to(SITE.resolve()),'Photo path outside site'
    assert photo.exists(),f'Missing {p}'
    assert photo.suffix.lower()=='.webp',f'Expected optimized WebP photo: {p}'
    assert photo.stat().st_size>10000, f'Placeholder or damaged photo {p}'
    with Image.open(photo) as im:
        im.verify()
    all_photos.append(photo)
assert len({hashlib.sha256(photo.read_bytes()).hexdigest() for photo in all_photos})==len(all_photos),'Exact duplicate photos found'
for key in ('particleImage','bgMusic'):
    p=(SITE/cfg[key]).resolve()
    assert p.is_relative_to(SITE.resolve()) and p.is_file(),f'Missing local {key} file'
for p in (SITE/cfg['letter']['image'],SITE/'qr/heartgift.png',SITE/'qr/heartgift.svg'):
    assert p.is_file(),f'Missing {p}'
with Image.open(SITE/cfg['letter']['image']) as letter_image:
    letter_image.verify()
print('VALIDATED: Original viewer,',len(all_photos),'unique WebP images, exact wish, local fonts/music/vendors, local QR')
print('Personal photos total:',sum(p.stat().st_size for p in all_photos),'bytes')
print('Website files:',sum(1 for _ in SITE.rglob('*') if _.is_file()))
