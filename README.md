<div align="center">

# 💗 HeartGift · 19.11

**The original DLove browser experience, personalized with memories and a letter.**

**[Open the live gift](https://karidz.github.io/HeartGift/)** · [Configuration](#customize-your-gift) · [QR Code](#heart-shaped-qr-code) · [Source & licensing](#source-and-rights)

</div>

## About this edition

This **19.11 edition uses the browser-delivered HTML, CSS, JavaScript and animations** of the [DLove gift viewer](https://w.dlove.vn/index.html?e0c7194b6d25b713), downloaded for the linked gift and adapted for local static hosting. This is **not** the independently reimplemented HeartGift v1 UI. The previous independent implementation is preserved on the Git branch `backup-independent-v1`.

The current gift retains the original viewer's interactive sequence:

1. **Hold to begin** — start the surprise.
2. **Glowing particle morphs** — animated text and a personal photo.
3. **3D memory sphere** — all 37 unique photos mapped around a sphere.
4. **Click twice** — zoom into the sphere and release the floating photo gallery.
5. **Cupid delivers an envelope** — tap the letter button, then the envelope.
6. **A typewriter love letter** — the exact 19.11 wish appears, followed by a final photograph.

The 37 configured photographs were optimized as WebP and are configured in `site/gift-config.json`. Third-party guest photos and telemetry are excluded. The original DLove soundtrack **“Nơi Này Có Anh”** is now included at the request of the project owner, who confirmed permission for **noncommercial use**. Music rights remain with their respective holder and are not granted to downstream forks.

## Start locally

Only Python 3 is needed to serve the saved website; no production backend, API token or remote resources are needed.

```bash
git clone https://github.com/KariDz/HeartGift.git
cd HeartGift
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open **http://127.0.0.1:8000/**. Opening `site/index.html` via `file://` does not reliably work because browsers restrict local JSON fetching.

For the optional build and automated tests:

```bash
npm ci
python3 -m pip install Pillow
npm run check
npm run build
npm test
```

The completed static deployment is in `dist/`.

## Customize your gift

**Edit only `site/gift-config.json`** to change the gift, or start with `site/gift-config.example.json`.

| Setting | Function |
| --- | --- |
| `appTitle` | Browser title and mobile app name |
| `morphTexts` | Animated lines displayed during the particle effect |
| `particleImage` | Picture that forms from glowing particles |
| `sphereImages` | Photos around the 3D sphere, in order |
| `letter.text` | Full typed-out letter |
| `letter.image` | Final picture shown below the message |
| `letter.caption` | Caption accompanying the final image |
| `bgMusic` | Path to a locally hosted, appropriately licensed music file |
| `enableMorphEffect`, `enableSphere`, `enableLetter` | Turn individual stages on/off |

The existing edition intentionally uses the exact message:

> 19.11 làm sao em để anh iu của em thiệt thòi được. Món quà nhỏ gửi đến anh, mong rằng mỗi ngày của anh đều ngập tràn hạnh phúc. Cảm ơn anh vì đã xuất hiện trong cuộc đời em.

### Replace the pictures

Put new images under `site/images/photos/` and update the paths in `site/gift-config.json`. We recommend WebP, with the longest edge around 1200 px. This repository currently contains **37 real personal images**, not placeholder examples, at `site/images/photos/01.webp` through `37.webp`. The image at `10.webp` is used for the glowing morph. **`01.webp`** is now the newly supplied two-person photo; the old `01.webp` was preserved as **`23.webp`**. The letter ends with **`11.webp`**, the photo containing the words **“em yêu phong”**.

**Update of 11 November 2026:** 38 JPGs were reviewed; 11 were visually near-identical to existing photos and one pair of new JPGs was near-identical. The remaining **26 photos** were added as `12.webp`–`37.webp`. The separately supplied photo of two people (also present in the ZIP) was originally saved as `23.webp`; after the later request it was moved to image 1, with the original image 1 swapped to 23. The final letter now uses image 11.

**No artificial repeats:** the original viewer rendered 84 sphere image tiles and 40 floating photos from 11 inputs. This edition dynamically creates **exactly one sphere tile and one flying photo per input image**. Adding more photos automatically expands the gallery without cycling textures.

For a folder or ZIP containing extra pictures, the included importer converts them to optimized WebP, skips exact and visually near-identical duplicates, and appends them to the configuration:

```bash
python3 scripts/add_photos.py /path/to/new-photos.zip
npm run check
npm run build
npm test
```

A backup of the configuration is kept in `workspace/temp/heartgift/photo-import-backups/`. Use `--keep-similar` only if you intentionally want similar pictures. The script never pushes your photos automatically; review what you are publishing first.

### Background music

The live gift now uses the original DLove **“Nơi Này Có Anh”** MP3, stored at `site/musics/noinaycoanh.mp3` and referenced by `bgMusic` in `site/gift-config.json`. The previous synthesized ambient loop is retained as an optional local alternative, but is no longer the default.

The project owner stated that they obtained permission to use this song **for noncommercial purposes**. That statement does not license the recording for general open-source redistribution, remixes, or commercial use by other people. The rights holder retains their rights. GitHub Pages makes the file publicly downloadable; please verify that your authorization covers hosting on a public site.

To replace the background music with another recording for which you have publishing rights:

```bash
python3 scripts/install_music.py /path/to/authorized-track.mp3 --confirm-public-usage-rights
npm run check
npm run build
npm test
```

Music begins after a user gesture to comply with browser autoplay restrictions. The MP3 is served locally and does not need any API or third-party streaming service.

**Privacy:** Because this repository and GitHub Pages are public, anyone with the URL can view the photos and text. Obtain the appropriate consent before publishing someone else's photographs or private messages. Deleting an image in a later commit does not necessarily remove it from Git history.

## Project structure

```text
HeartGift/
├── site/
│   ├── index.html                # DLove browser-delivered viewer (adapted)
│   ├── gift-config.json          # All editable content and toggles
│   ├── gift-config.example.json
│   ├── images/photos/            # 37 personal WebP pictures
│   ├── assets/                   # Original viewer's required static assets/fonts
│   ├── musics/noinaycoanh.mp3    # Selected soundtrack (noncommercial permission)
│   ├── musics/heartgift-ambient.wav  # Optional local instrumental
│   ├── vendor/                   # Local Three.js & simplex-noise
│   └── qr/                       # Heart QR PNG + SVG
├── scripts/
│   ├── validate_site.py         # Ensure the offline site has all required files
│   ├── build_site.py            # Copy the static website to dist/
│   ├── add_photos.py            # Add + deduplicate WebP photos
│   ├── install_music.py         # Install authorized local soundtrack
│   ├── heart_qr.py              # QR-code generator
│   └── _vendor/                 # Python qrcode library (BSD-3-Clause)
├── tests/
│   └── dlove-smoke.mjs           # Test the original interaction from start to letter
├── .github/workflows/pages.yml
└── SOURCE.md                     # Source provenance and rights
```

The viewer JavaScript and CSS were originally inline in the HTML; they remain there intentionally to preserve the exact behavior of the captured website. The customizable content has been separated into JSON and independent photo files.

## GitHub Pages

GitHub Actions automatically validates, builds and publishes `site/` (as `dist/`) whenever `main` changes.

**Deployed URL:** https://karidz.github.io/HeartGift/

You can review the workflow in [Actions](https://github.com/KariDz/HeartGift/actions).

## Heart-shaped QR code

The QR is now generated **entirely by Python** and visually matches the red-on-black heart reference:

- The real QR data is rotated **45°**, placing its three large finder patterns at the top, left, and right of a diamond.
- Procedural red tiles around that data form the two lobes and point of the heart.
- A small white circular badge with a red heart decorates the center.
- The encoded URL is **https://karidz.github.io/HeartGift/**, with QR error correction level **H**.

Files: `site/qr/heartgift.png` (1400×1820), `site/qr/heartgift.svg` (scalable vector), and `site/qr/heartgift-scan-safe.png` (standard high-contrast QR). The original simple heart-framed generator is still available in `scripts/heart_qr.py`.

To regenerate the *red, diamond QR* for any website URL:

```bash
python3 -m pip install Pillow
python3 scripts/heart_qr_style.py \
  --url 'https://YOUR-NAME.github.io/HeartGift/' \
  --output site/qr/heartgift
```

The repository includes the QR encoder under `scripts/_vendor`; the generator does not need a backend or third-party QR service. Optional automatic decoding validation uses OpenCV if installed (`python3 -m pip install opencv-python`). The generated SVG is real vector geometry and can be edited or printed at any size.

**Scanning note:** Red QR modules on a black background are *light-on-dark*. The stylized PNG/SVG decode correctly with OpenCV and ZBar **after color inversion**. Some phone scanners may automatically handle inversion, but others may not. Use `heartgift-scan-safe.png` when reliable scanning matters most, especially for print, and test with a real phone before sharing.

## Source and rights

The browser-viewer source and imagery originated from the linked **DLove** webpage, and are distinct from the previous independently implemented HeartGift application. The original creator retains their rights. A webpage being publicly accessible **does not** automatically make its code and illustrations open source. **No MIT license is asserted for the extracted viewer or upstream assets.** See [SOURCE.md](SOURCE.md) for provenance and changes, [SECURITY.md](SECURITY.md) for privacy, and [CONTRIBUTING.md](CONTRIBUTING.md) for contributor guidance.

This is a reproduction of the **frontend delivered to visitors**, not the original private backend, database or developer project files.
