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
3. **3D memory sphere** — all eleven photos mapped around a sphere.
4. **Click twice** — zoom into the sphere and release the floating photo gallery.
5. **Cupid delivers an envelope** — tap the letter button, then the envelope.
6. **A typewriter love letter** — the exact 19.11 wish appears, followed by a final photograph.

The eleven supplied photographs were optimized as WebP. They are configured in `site/gift-config.json`. The original viewer's third-party guest photos, telemetry loader and commercial song are **not** redistributed here; a short, newly synthesized ambient loop is used instead.

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

Put new images under `site/images/photos/` and update the paths in `site/gift-config.json`. We recommend WebP, with the longest edge around 1200 px. This repository currently contains **eleven real personal images**, not placeholder examples, at `site/images/photos/01.webp` through `11.webp`. The image at `10.webp` is used for the glowing morph; `11.webp` is also the photo in the letter.

**Privacy:** Because this repository and GitHub Pages are public, anyone with the URL can view the photos and text. Obtain the appropriate consent before publishing someone else's photographs or private messages. Deleting an image in a later commit does not necessarily remove it from Git history.

## Project structure

```text
HeartGift/
├── site/
│   ├── index.html                # DLove browser-delivered viewer (adapted)
│   ├── gift-config.json          # All editable content and toggles
│   ├── gift-config.example.json
│   ├── images/photos/            # 11 personal WebP pictures
│   ├── assets/                   # Original viewer's required static assets/fonts
│   ├── musics/heartgift-ambient.wav
│   ├── vendor/                   # Local Three.js & simplex-noise
│   └── qr/                       # Heart QR PNG + SVG
├── scripts/
│   ├── validate_site.py         # Ensure the offline site has all required files
│   ├── build_site.py            # Copy the static website to dist/
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

A ready-to-scan QR encoding the deployed website is available at `site/qr/heartgift.png` and `site/qr/heartgift.svg`.

To regenerate it for a different URL:

```bash
python3 -m pip install Pillow
python3 scripts/heart_qr.py \
  --url 'https://YOUR-NAME.github.io/HeartGift/' \
  --output site/qr/heartgift \
  --label 'SCAN WITH LOVE'
```

The QR data is an unmodified high-error-correction square surrounded by a decorative heart, not cropped into an unreadable shape. You can check the generated PNG with any QR scanner.

## Source and rights

The browser-viewer source and imagery originated from the linked **DLove** webpage, and are distinct from the previous independently implemented HeartGift application. The original creator retains their rights. A webpage being publicly accessible **does not** automatically make its code and illustrations open source. **No MIT license is asserted for the extracted viewer or upstream assets.** See [SOURCE.md](SOURCE.md) for provenance and changes, [SECURITY.md](SECURITY.md) for privacy, and [CONTRIBUTING.md](CONTRIBUTING.md) for contributor guidance.

This is a reproduction of the **frontend delivered to visitors**, not the original private backend, database or developer project files.
