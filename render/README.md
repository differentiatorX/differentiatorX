# How the profile is drawn

**Header** (`assets/hero.webp`): `blackhole.html` is a WebGL2 ray tracer. Every pixel fires a light ray backwards from the camera and steps it through Schwarzschild spacetime (in units of the Schwarzschild radius r<sub>s</sub>, a photon's path obeys x'' = -1.5 h² x / r⁵, where h is its angular momentum).

- Rays that cross the plane between 3 r<sub>s</sub> (the ISCO) and the disk edge pick up light from a thin accretion disk.
- The disk's temperature follows the Novikov-Thorne profile, and its colour is Planck's law sampled at three wavelengths.
- Brightness is scaled by g⁴, where g combines the Doppler shift of the orbiting gas with gravitational redshift. That is why the side spinning toward you is brighter.
- Rays that escape sample a star field, which is why the stars near the hole look bent.
- The "edge case" is a test particle on a decaying orbit. It dims as it falls because its light is redshifted.
- The disk texture is two copies one loop apart, crossfaded so the 10-second loop has no seam.

```bash
node render/frames.mjs "file:///ABSOLUTE/PATH/render/blackhole.html?v=A&ss=2" render/frames 120
python render/encode.py render/frames
```

`frames.mjs` drives headless Chrome (the path is set for Windows; change it in the script for other systems). `?v=A` is the header framing, `?v=D` the face-on view used in the whoami panel, and `ss=2` renders at twice the resolution for anti-aliasing.

**Panels** (`assets/*.svg`): `python render/build_assets.py` writes every card as an animated SVG with the fonts embedded. Every loop starts at its finished state, so a still render still shows everything.

**Telemetry**: `.github/workflows/telemetry.yml` runs `.github/scripts/telemetry.py` twice a day and publishes `telemetry.svg` and the snake to the `output` branch.
