#!/usr/bin/env python3
"""Append new photos to HeartGift without repeating existing or near-identical images.

Input may be a directory or ZIP of your own images. Originals stay outside Git.
"""
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image, ImageOps
from zipfile import ZipFile, BadZipFile
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CFG = SITE / 'gift-config.json'
IMAGE_ROOT = SITE / 'images/photos'
EXT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
MAX_ITEMS = 100
MAX_TOTAL = 220 * 1024 * 1024
MAX_FILE = 25 * 1024 * 1024

def normalized_image(data):
    with Image.open(BytesIO(data)) as image:
        if image.width * image.height > 50_000_000:
            raise ValueError('Oversized pixel dimensions')
        return ImageOps.exif_transpose(image).convert('RGB')

def dhash(image):
    gray = image.convert('L').resize((9, 8), Image.Resampling.LANCZOS)
    values = list(gray.getdata())
    score = 0
    for y in range(8):
        for x in range(8):
            score = (score << 1) | (values[y * 9 + x] > values[y * 9 + x + 1])
    return score

def sources(path):
    if path.is_dir():
        files = sorted((p for p in path.iterdir() if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXT), key=lambda p: p.name.casefold())
        if len(files) > MAX_ITEMS:
            raise ValueError('Too many files; maximum 100 at a time')
        for item in files:
            if item.stat().st_size > MAX_FILE:
                print('SKIP oversized:', item.name)
                continue
            yield item.name, item.read_bytes()
    elif path.is_file() and path.suffix.lower() == '.zip':
        with ZipFile(path) as z:
            infos = sorted((info for info in z.infolist() if not info.is_dir()
                and Path(info.filename).suffix.lower() in EXT), key=lambda info: info.filename.casefold())
            if len(infos) > MAX_ITEMS:
                raise ValueError('Too many images in ZIP; maximum 100 at a time')
            if sum(info.file_size for info in infos) > MAX_TOTAL:
                raise ValueError('Uncompressed ZIP images exceed 220 MB')
            for info in infos:
                if info.file_size > MAX_FILE:
                    print('SKIP oversized:', info.filename)
                    continue
                yield Path(info.filename).name, z.read(info)
    else:
        raise ValueError('Pass a directory with photos or a ZIP archive')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path, help='Directory or ZIP of new photos')
    ap.add_argument('--quality', type=int, default=82)
    ap.add_argument('--max-edge', type=int, default=1200)
    ap.add_argument('--keep-similar', action='store_true', help='Do not skip visually similar photos')
    args = ap.parse_args()
    if not 40 <= args.quality <= 95 or not 500 <= args.max_edge <= 2500:
        ap.error('Quality 40–95, longest edge 500–2500 px')
    config = json.loads(CFG.read_text(encoding='utf8'))
    configured = config.get('sphereImages', [])
    if not isinstance(configured,list):
        raise ValueError('sphereImages must be an array')
    known_hashes, known_dhash = set(), []
    for relative in configured:
        location = (SITE / relative).resolve()
        if not location.is_relative_to(SITE.resolve()):
            raise ValueError('Photo path outside website')
        raw = location.read_bytes()
        known_hashes.add(hashlib.sha256(raw).digest())
        known_dhash.append(dhash(normalized_image(raw)))
    candidates, total = [], 0
    for name, data in sources(args.input.expanduser().resolve()):
        total += len(data)
        if total > MAX_TOTAL:
            raise ValueError('Input photos exceed 220 MB')
        try:
            image = normalized_image(data)
        except (ValueError, OSError) as exc:
            print('SKIP invalid:', name, exc)
            continue
        visual_hash = dhash(image)
        if not args.keep_similar and any((visual_hash ^ h).bit_count() <= 5 for h in known_dhash):
            print('SKIP duplicate/near-identical:', name)
            continue
        image.thumbnail((args.max_edge, args.max_edge), Image.Resampling.LANCZOS)
        dest = BytesIO()
        image.save(dest, 'WEBP', quality=args.quality, method=6)
        output = dest.getvalue()
        digest = hashlib.sha256(output).digest()
        if digest in known_hashes:
            print('SKIP byte-identical:', name)
            continue
        known_hashes.add(digest)
        known_dhash.append(visual_hash)
        candidates.append((name, output))
    if not candidates:
        print('No new unique photos to add. Existing website unchanged.')
        return
    backup = ROOT.parent.parent / 'temp/heartgift/photo-import-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CFG,backup/'gift-config.json')
    next_num = max((int(Path(p).stem) for p in configured if Path(p).stem.isdigit()), default=0) + 1
    IMAGE_ROOT.mkdir(parents=True,exist_ok=True)
    for name, data in candidates:
        while (IMAGE_ROOT / f'{next_num:02d}.webp').exists():
            next_num += 1
        filename = f'{next_num:02d}.webp'
        (IMAGE_ROOT / filename).write_bytes(data)
        configured.append('images/photos/' + filename)
        print('ADDED', name, '->', filename, len(data), 'bytes')
        next_num += 1
    config['sphereImages'] = configured
    CFG.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Added',len(candidates),'unique photos; total gallery:',len(configured))
    print('Config backup:',backup)
    print('Run npm run check && npm run build && npm test before publishing.')

if __name__ == '__main__':
    main()
