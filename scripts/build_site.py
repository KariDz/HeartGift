#!/usr/bin/env python3
"""Build the static, browser-captured DLove viewer for GitHub Pages."""
from pathlib import Path
from shutil import copytree,rmtree
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
OUT=ROOT/'dist'
subprocess.run(['python3',str(ROOT/'scripts/validate_site.py')],check=True,cwd=ROOT)
if OUT.is_symlink():
    raise SystemExit('Refusing to replace a symlinked dist directory')
if OUT.exists():
    assert OUT.is_dir()
    rmtree(OUT)
copytree(SITE,OUT)
print('GitHub Pages output:',OUT,'files:',sum(1 for p in OUT.rglob('*') if p.is_file()))
