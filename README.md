<div align="center">

# ♥ HeartGift

**A small gift. A whole lot of love.**

A delightful, interactive love letter with a starry background, 3D memory sphere, animated envelope and personal message. Built with modern web technologies and designed to be easy to customize.

[Live website](https://karidz.github.io/HeartGift/) · [Customize](#personalization) · [Deploy](#deploy-with-github-pages) · [Heart QR](#heart-shaped-qr-code)

</div>

## What makes HeartGift special?

- **Romantic, interactive introduction:** press and hold to open your present (keyboard: Enter/Space).
- **Personalized words:** a sequence of animated messages before your memories appear.
- **3D photo sphere:** rotate, zoom, and scatter memories with two taps.
- **Animated love letter:** open an envelope and read a typewriter-style message.
- **Fully static:** no accounts, databases, tracking, or backend.
- **Privacy-conscious:** demo images are original generated placeholders, while your own memories can be added as local files.
- **Responsive:** supports desktop and mobile layouts and reduced motion.
- **Heart-shaped QR:** included Python tool creates PNG and SVG codes designed to remain reliably scannable.

## Getting started

Prerequisites: **Node.js 22+** and npm.

```bash
git clone https://github.com/KariDz/HeartGift.git
cd HeartGift
npm ci
npm run dev
```

Open the local address printed by Vite. Production build:

```bash
npm run check
npm run build
npm run preview
```

The compiled static website is in `dist/`.

## Personalization

**All user-facing content is configured in `public/config.json`.** You can replace your text and images without editing JavaScript.

```json
{
  "pageTitle": "A special gift for you",
  "morphTexts": ["YOU", "ARE", "LOVED"],
  "photos": [
    "images/photos/01.webp",
    "images/photos/02.webp"
  ],
  "letter": {
    "greeting": "Dear you,",
    "message": "Thank you for being here.",
    "image": "images/letter-cover.svg",
    "caption": "One little memory",
    "signature": "With love ♡"
  },
  "music": {
    "src": "",
    "volume": 0.45
  }
}
```

An editable example is provided in `public/config.example.json`.

| What to change | File / setting |
| --- | --- |
| Website title and introductory text | `public/config.json` → `pageTitle`, `intro` |
| Animated greeting words | `morphTexts` |
| Pictures in the 3D sphere | `photos` |
| Opening greeting, full letter, photo and signature | `letter` |
| Optional background music | `music.src`, `music.volume` |

### Replace photos

1. Put your WebP/JPG/PNG photos in `public/images/photos/`. WebP and a longest edge of roughly 800–1200 px are recommended.
2. Update the `photos` paths in `public/config.json`. You can have fewer or more than 11 photos.
3. To show a personal image at the end of the letter, set `letter.image` to the image path.
4. Preview with `npm run dev` and rebuild with `npm run build`.

To add music, place a file you have permission to use in `public/music/`, then set `music.src`, for example `"music/our-song.mp3"`. Audio starts only after user interaction, respecting browser autoplay rules.

> **Privacy warning:** Everything in `public/` is accessible to everyone on a public deployment. Do not commit private or identifying photos or messages without the appropriate consent. Git history can retain previous files even after you delete them.

## Source organization

```text
HeartGift/
├── public/
│   ├── config.json               # Personalize text, images and music
│   ├── config.example.json
│   ├── images/
│   │   ├── photos/               # Your own gallery
│   │   ├── heart.svg
│   │   └── letter-cover.svg
│   └── qr/                       # Scannable QR images
├── src/
│   ├── main.js                   # Experience controller
│   ├── config.js                 # Read and validate configuration
│   ├── particles.js              # Ambient starlight
│   ├── sphere.js                 # Interactive 3D memory sphere
│   ├── letter.js                 # Envelope + typed message
│   └── styles.css                # Theme, accessibility, responsiveness
├── scripts/
│   ├── generate_demo_photos.py
│   ├── heart_qr.py               # QR generator
│   └── _vendor/                  # BSD-licensed QR encoder
├── .github/workflows/pages.yml  # Automatic GitHub Pages publishing
└── README.md
```

## Deploy with GitHub Pages

A workflow in `.github/workflows/pages.yml` builds and publishes this website on every push to `main`.

1. Create a GitHub repository and push this source to its `main` branch.
2. In the repository, go to **Settings → Pages**.
3. Under **Build and deployment**, choose **GitHub Actions**.
4. Verify **Actions → Build and deploy HeartGift** finishes successfully.
5. Visit `https://YOUR-USERNAME.github.io/YOUR-REPO/` or your configured custom domain.

The Vite configuration uses a relative base path to support GitHub Pages project URLs.

## Heart-shaped QR code

`scripts/heart_qr.py` generates two files: a printable PNG and a vector SVG. The QR matrix keeps its rectangular quiet zone, while a heart surrounds it as a design element. This preserves scannability.

Prerequisites: Python 3.10+ and Pillow. A BSD-3-Clause-licensed version of the `qrcode` library is included under `scripts/_vendor/`.

```bash
python3 -m pip install Pillow
python3 scripts/heart_qr.py \
  --url "https://YOUR-USERNAME.github.io/YOUR-REPO/" \
  --output public/qr/heartgift \
  --label "SCAN WITH LOVE"
```

The included QR currently encodes `https://karidz.github.io/HeartGift/`. Recreate it if you change your website's address. Do not distribute a QR until you verify the actual deployed URL.

## Tests

```bash
npm run check
npm run build
npm test
```

Browser tests require Chromium; install with `npx playwright install chromium` when necessary.

## Open source

HeartGift's **independent application code and original demo visuals** use the [MIT License](LICENSE). Three.js is MIT licensed; the vendored Python `qrcode` library is BSD-3-Clause licensed (see `scripts/_vendor/LICENSE-qrcode.txt`).

HeartGift does not incorporate the original proprietary DLove viewer, its branding, third-party photos, or licensed music. It is not affiliated with that service.

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
