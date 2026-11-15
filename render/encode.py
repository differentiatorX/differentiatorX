"""Packs rendered frames into the profile header.

    node render/frames.mjs "file:///<abs path>/render/blackhole.html?v=A&ss=2" render/frames 120
    python render/encode.py render/frames

Writes assets/hero.webp (a 10 s loop at 12 fps) and assets/hero-still.jpg, the frame
shown to people who turn animations off."""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
frames = sorted(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "render" / "frames").glob("f*.png"))
if not frames:
    raise SystemExit("no frames found; run render/frames.mjs first")
ims = [Image.open(f).convert("RGB") for f in frames]
ims[0].save(ROOT / "assets" / "hero.webp", save_all=True, append_images=ims[1:], duration=round(10000 / len(ims)),
            loop=0, quality=80, method=6, minimize_size=True)
ims[len(ims) // 3].save(ROOT / "assets" / "hero-still.jpg", quality=88)
print(f"{len(ims)} frames -> assets/hero.webp, assets/hero-still.jpg")
