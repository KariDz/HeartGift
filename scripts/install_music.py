#!/usr/bin/env python3
"""Install a user-supplied, authorized music file as the HeartGift soundtrack.

This script never downloads or copies songs from streaming sites.
All music in a public GitHub Pages repository can be downloaded by visitors.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CFG = SITE / 'gift-config.json'
EXTENSIONS = {'.mp3', '.ogg', '.wav', '.m4a'}
MAX_BYTES = 80 * 1024 * 1024

def valid_audio_header(data: bytes, ext: str):
    if ext == '.mp3':
        return data.startswith(b'ID3') or (len(data) > 2 and data[0] == 0xff and data[1] & 0xe0 == 0xe0)
    if ext == '.ogg':
        return data.startswith(b'OggS')
    if ext == '.wav':
        return data.startswith(b'RIFF') and data[8:12] == b'WAVE'
    if ext == '.m4a':
        return data[4:8] == b'ftyp'
    return False

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('file', type=Path, help='Locally supplied authorized audio file')
    ap.add_argument('--confirm-public-usage-rights', action='store_true',
                    help='Confirm you have permission to publish/redistribute the audio publicly')
    args = ap.parse_args()
    if not args.confirm_public_usage_rights:
        ap.error('This public website needs permission to redistribute the selected recording; pass --confirm-public-usage-rights only when this is true.')
    source = args.file.expanduser().resolve()
    ext = source.suffix.lower()
    if ext not in EXTENSIONS:
        ap.error('Supported files: MP3, OGG, WAV, M4A')
    if not source.is_file() or not 1000 < source.stat().st_size < MAX_BYTES:
        ap.error('File missing or invalid size (1 KB – 80 MB)')
    with source.open('rb') as stream:
        signature = stream.read(16)
    if not valid_audio_header(signature, ext):
        ap.error('Audio file header does not match its extension')
    conf = json.loads(CFG.read_text(encoding='utf8'))
    track = SITE / 'musics' / ('noi-nay-co-anh' + ext)
    track.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = ROOT.parent.parent / 'temp' / 'heartgift' / 'music-backup' / timestamp
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CFG, backup / 'gift-config.json')
    if track.exists():
        shutil.copy2(track, backup / track.name)
    temp = track.with_suffix(track.suffix + '.part')
    shutil.copyfile(source, temp)
    temp.replace(track)
    conf['bgMusic'] = 'musics/' + track.name
    CFG.write_text(json.dumps(conf, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('Installed authorized music to', track)
    print('Config path:', conf['bgMusic'])
    print('Backup:', backup)
    print('Next: npm run check && npm run build && npm test; then commit and push')

if __name__ == '__main__':
    main()
