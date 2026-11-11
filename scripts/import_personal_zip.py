#!/usr/bin/env python3
"""Import the 11 personal photos from a HeartGift or DLove photo ZIP.

Reads only photos; never imports the original vendor source, music, API response,
secrets, or unrelated content. The ZIP is not added to Git history.
"""
from pathlib import Path
import io,zipfile, argparse,json,sys,datetime,hashlib,shutil
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('archive',type=Path,help='ZIP with user photos (HeartGift-personal-19-11.zip or dlove-1911-anh-iu-webp-update.zip)')
parser.add_argument('--max-edge',type=int,default=1200)
parser.add_argument('--quality',type=int,default=78)
args=parser.parse_args()
if args.max_edge<200 or args.max_edge>4000:parser.error('--max-edge must be 200..4000')
if args.quality<30 or args.quality>95:parser.error('--quality must be 30..95')
if not args.archive.is_file():parser.error('Archive file does not exist')
target=ROOT/'site/images/photos'
target.mkdir(parents=True,exist_ok=True)
conf=ROOT/'site/gift-config.json'
original=json.loads(conf.read_text())
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=ROOT/'../../temp/heartgift/photo-backup'/now
backup.mkdir(parents=True,exist_ok=True)
processed=[]
with zipfile.ZipFile(args.archive) as z:
    if z.testzip() is not None:raise RuntimeError('ZIP CRC error')
    names=z.namelist()
    for i in range(1,12):
        ending=f'/public/assets/images/photos/{i:02d}.webp'
        ending_alt=f'birthday/assets/memories/{i:02d}.webp'
        matches=[n for n in names if n.endswith(ending) and '/dist/' not in n]
        if not matches:
            matches=[n for n in names if n.endswith(ending_alt)]
        if len(matches)!=1:raise RuntimeError(f'Missing or ambiguous photo {i:02d}')
        raw=z.read(matches[0])
        if len(raw)>20_000_000:raise RuntimeError('Image exceeds 20MB safety limit')
        with Image.open(io.BytesIO(raw)) as loaded:
            im=ImageOps.exif_transpose(loaded)
            im.thumbnail((args.max_edge,args.max_edge),Image.Resampling.LANCZOS)
            out=io.BytesIO()
            im.convert('RGB').save(out,'WEBP',quality=args.quality,method=6)
            processed.append((target/f'{i:02d}.webp',out.getvalue()))
for p,data in processed:
    if p.exists():shutil.copy2(p,backup/p.name)
    temp=p.with_suffix('.new')
    temp.write_bytes(data)
    temp.replace(p)
shutil.copy2(conf,backup/'config.json')
original['sphereImages']=[f'images/photos/{i:02d}.webp' for i in range(1,12)]
original['particleImage']='images/photos/10.webp'
original['letter']['image']='images/photos/11.webp'
original['letter']['caption']='Một khoảnh khắc chỉ dành cho anh 💗'
conf.write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n')
print('Imported',len(processed),'photos; optimized total',sum(len(d) for _,d in processed),'bytes')
print('Backups:',backup)
print('Next: npm run build && npm test; git add site/gift-config.json site/images/photos && git commit ... && git push origin main')
