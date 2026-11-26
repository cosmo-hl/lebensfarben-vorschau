#!/usr/bin/env python3
"""Holt Kristins Bilder von lebensfarben.net (Jimdo-CDN) und erzeugt 800/1600-px-JPEGs in site/img/.

Läuft in GitHub Actions (dort ist das Netz offen). Ohne Netz entstehen Platzhalter,
damit die Seite lokal trotzdem gebaut werden kann (--placeholder).
"""
import io, pathlib, sys, urllib.request
from PIL import Image, ImageOps

OUT = pathlib.Path(__file__).resolve().parent.parent / 'site' / 'img'
B = 'https://primary.jwwb.nl/public/i/g/v/temp-ljqojfxjnemcmhcxdoxa/'

# name: (Quelle, Bearbeitung)
IMAGES = {
    'weite':               (B + 'kristin-damaschke-lebensfarben-psychotherapie-somatic-experiencing-high.jpg', 'left'),
    'raum':                (B + '25b4eac1-46bb-43f1-adb2-7a3b7f025c60-high.png', None),
    'art-erde':            (B + 'img_0756-kopie-high-z1vao1.jpg', None),
    'art-pink':            (B + 'bildschirmfoto-2026-08-16-um-22-49-57-standard.png', None),
    'art-gruen':           (B + 'bildschirmfoto-2026-08-16-um-22-49-38-standard.png', None),
    'art-tuerkis':         (B + 'bildschirmfoto-2026-08-16-um-22-56-58-high.png', None),
    'art-ocker':           (B + 'bildschirmfoto-2026-08-16-um-22-57-23-high.png', None),
    'art-blau':            (B + 'bildschirmfoto-2026-08-16-um-22-56-12-high.png', None),
    'ausstellung-luebeck': (B + 'img_2065-high.jpg', None),
    'ausstellung-wand':    (B + 'img_2058-high.jpg', None),
    'ausstellung-haengung':(B + 'img_5137-high.jpg', None),
    'ausstellung-rot':     (B + 'img_0832-high.jpg', None),
}


def trim_white(im, thresh=238):
    """Schneidet weiße Ränder ab."""
    g = im.convert('L').point(lambda v: 255 if v < thresh else 0)
    box = g.getbbox()
    return im.crop(box) if box else im


def split_left(im, thresh=238):
    """Das Bildpaar der alten Startseite ist eine Datei: linkes Foto (Weite) herausschneiden."""
    im = trim_white(im, thresh)
    g = im.convert('L')
    w, h = g.size
    px = g.load()
    white_cols = [x for x in range(w) if min(px[x, y] for y in range(h // 4, 3 * h // 4, 4)) >= thresh]
    # erste weiße Spalte in der mittleren Hälfte = Trennfuge
    gap = next((x for x in white_cols if w * 0.25 < x < w * 0.75), w // 2)
    return trim_white(im.crop((0, 0, gap, h)), thresh)


def save(im, name):
    im = ImageOps.exif_transpose(im).convert('RGB')
    for width in (800, 1600):
        x = im.copy()
        if x.width > width:
            x = x.resize((width, round(x.height * width / x.width)), Image.LANCZOS)
        x.save(OUT / f'{name}-{width}.jpg', 'JPEG', quality=82, optimize=True, progressive=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    placeholder = '--placeholder' in sys.argv
    for name, (url, op) in IMAGES.items():
        if (OUT / f'{name}-1600.jpg').exists() and not placeholder:
            continue
        if placeholder:
            save(Image.new('RGB', (1600, 1200), (233, 223, 207)), name)
            continue
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Vorschau-Build)'})
        data = urllib.request.urlopen(req, timeout=60).read()
        im = Image.open(io.BytesIO(data))
        im.load()
        if im.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', im.size, (255, 255, 255))
            im = im.convert('RGBA'); bg.paste(im, mask=im.split()[-1]); im = bg
        if op == 'left':
            im = split_left(im)
        elif name.startswith('art-') and name in ('art-pink', 'art-gruen', 'art-tuerkis', 'art-ocker', 'art-blau'):
            im = trim_white(im, 250)  # Bildschirmfotos: helle Ränder entfernen
        save(im, name)
        print('ok', name, im.size)


if __name__ == '__main__':
    main()
