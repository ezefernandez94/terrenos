"""Generate SVG placeholder art for the landing page.

Deliberately designed vector placeholders (aerial parcel/land motif) rather than
stock photography — the design system lists "Poor photos" as an anti-pattern for
this vertical, so a clean geometric stand-in reads better than a stretched JPEG.
"""
import os
import math

OUT = "/home/ezequiel/Repositories/terrenos/terrenos/static/img"
os.makedirs(OUT, exist_ok=True)

# Palette drawn from the persisted design system (trust teal + professional blue),
# with a restrained gold for the "upcoming" tier.
SCHEMES = [
    ("#0F766E", "#134E4A", "#5EEAD4"),
    ("#0369A1", "#0C4A6E", "#7DD3FC"),
    ("#14B8A6", "#115E59", "#99F6E4"),
    ("#0E7490", "#164E63", "#67E8F9"),
    ("#1D4ED8", "#172554", "#93C5FD"),
    ("#0F766E", "#042F2E", "#2DD4BF"),
    ("#A16207", "#422006", "#FDE68A"),
    ("#B45309", "#431407", "#FCD34D"),
    ("#92400E", "#451A03", "#FDE68A"),
]


def parcels(seed, w, h, rows, cols, opacity=0.16):
    """Grid of land parcels in perspective, drawn as stroked polygons."""
    out = []
    rnd = seed
    for r in range(rows):
        for c in range(cols):
            rnd = (rnd * 1103515245 + 12345) % 2147483648
            jitter = (rnd % 100) / 100.0
            # Perspective: rows further "back" are shorter and narrower.
            depth = r / max(rows - 1, 1)
            cw = w / cols * (0.55 + 0.45 * depth)
            ch = h / rows * (0.4 + 0.6 * depth)
            x = (w - cw * cols) / 2 + c * cw
            y = h - (r + 1) * ch
            skew = (0.5 - depth) * 60
            pts = " ".join(
                f"{px:.1f},{py:.1f}"
                for px, py in [
                    (x + skew, y),
                    (x + cw + skew, y),
                    (x + cw + skew * 0.72, y + ch),
                    (x + skew * 0.72, y + ch),
                ]
            )
            op = opacity * (0.45 + 0.55 * jitter)
            out.append(
                f'<polygon points="{pts}" fill="#FFFFFF" fill-opacity="{op:.3f}" '
                f'stroke="#FFFFFF" stroke-opacity="{op + 0.14:.3f}" stroke-width="1.5"/>'
            )
    return "\n    ".join(out)


def contours(w, h, count, color="#FFFFFF"):
    """Topographic contour lines."""
    out = []
    for i in range(count):
        t = i / count
        amp = h * (0.05 + 0.05 * t)
        base = h * (0.28 + 0.62 * t)
        d = [f"M -20 {base:.1f}"]
        steps = 14
        for s in range(1, steps + 1):
            x = -20 + (w + 40) * s / steps
            y = base + math.sin(s * 0.85 + i * 1.3) * amp
            d.append(f"L {x:.1f} {y:.1f}")
        out.append(
            f'<path d="{" ".join(d)}" fill="none" stroke="{color}" '
            f'stroke-opacity="{0.06 + 0.10 * (1 - t):.3f}" stroke-width="2"/>'
        )
    return "\n    ".join(out)


def card(idx, w=800, h=500):
    a, b, light = SCHEMES[idx % len(SCHEMES)]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-hidden="true">
  <defs>
    <linearGradient id="g{idx}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{a}"/>
      <stop offset="100%" stop-color="{b}"/>
    </linearGradient>
    <radialGradient id="l{idx}" cx="0.78" cy="0.16" r="0.75">
      <stop offset="0%" stop-color="{light}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{light}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#g{idx})"/>
  <g>
    {contours(w, h, 7)}
  </g>
  <rect width="{w}" height="{h}" fill="url(#l{idx})"/>
  <g>
    {parcels(idx * 977 + 13, w, h, 4, 6)}
  </g>
  <path d="M 0 {h * 0.62:.0f} Q {w * 0.35:.0f} {h * 0.5:.0f} {w * 0.62:.0f} {h * 0.66:.0f} T {w} {h * 0.6:.0f}"
        fill="none" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="3" stroke-dasharray="14 10"/>
</svg>
"""


def hero_poster(w=1920, h=1080):
    a, b, light = "#0F766E", "#042F2E", "#5EEAD4"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-hidden="true">
  <defs>
    <linearGradient id="hg" x1="0.1" y1="0" x2="0.9" y2="1">
      <stop offset="0%" stop-color="{a}"/>
      <stop offset="55%" stop-color="#0C4A6E"/>
      <stop offset="100%" stop-color="{b}"/>
    </linearGradient>
    <radialGradient id="hl" cx="0.72" cy="0.18" r="0.8">
      <stop offset="0%" stop-color="{light}" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="{light}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#hg)"/>
  <g>
    {contours(w, h, 11)}
  </g>
  <rect width="{w}" height="{h}" fill="url(#hl)"/>
  <g>
    {parcels(4242, w, h, 5, 9, opacity=0.13)}
  </g>
</svg>
"""


def map_placeholder(w=880, h=520):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-hidden="true">
  <defs>
    <linearGradient id="mg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#E8F0F3"/>
      <stop offset="100%" stop-color="#CCFBF1"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#mg)"/>
  <g stroke="#0F766E" stroke-opacity="0.16" stroke-width="1.5" fill="none">
    {"".join(f'<path d="M 0 {y} H {w}"/>' for y in range(40, h, 52))}
    {"".join(f'<path d="M {x} 0 V {h}"/>' for x in range(44, w, 58))}
  </g>
  <path d="M -10 {h * 0.68:.0f} Q {w * 0.3:.0f} {h * 0.45:.0f} {w * 0.55:.0f} {h * 0.6:.0f} T {w + 10} {h * 0.42:.0f}"
        fill="none" stroke="#0F766E" stroke-opacity="0.5" stroke-width="10" stroke-linecap="round"/>
  <path d="M {w * 0.12:.0f} -10 Q {w * 0.28:.0f} {h * 0.4:.0f} {w * 0.2:.0f} {h + 10:.0f}"
        fill="none" stroke="#0369A1" stroke-opacity="0.35" stroke-width="7" stroke-linecap="round"/>
  <circle cx="{w * 0.55:.0f}" cy="{h * 0.52:.0f}" r="46" fill="#0F766E" fill-opacity="0.12"/>
  <circle cx="{w * 0.55:.0f}" cy="{h * 0.52:.0f}" r="16" fill="#0F766E"/>
  <circle cx="{w * 0.55:.0f}" cy="{h * 0.52:.0f}" r="6" fill="#FFFFFF"/>
</svg>
"""


def editorial(idx, w=900, h=640):
    """Neutral image block for the two placeholder content sections."""
    a, b, light = SCHEMES[(idx + 2) % len(SCHEMES)]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-hidden="true">
  <defs>
    <linearGradient id="eg{idx}" x1="0" y1="0" x2="0.8" y2="1">
      <stop offset="0%" stop-color="{a}"/>
      <stop offset="100%" stop-color="{b}"/>
    </linearGradient>
    <radialGradient id="el{idx}" cx="0.25" cy="0.2" r="0.8">
      <stop offset="0%" stop-color="{light}" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="{light}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#eg{idx})"/>
  <g>{contours(w, h, 8)}</g>
  <rect width="{w}" height="{h}" fill="url(#el{idx})"/>
  <g>{parcels(idx * 331 + 7, w, h, 3, 4, opacity=0.14)}</g>
</svg>
"""


for i in range(9):
    with open(f"{OUT}/parcela-{i + 1}.svg", "w") as f:
        f.write(card(i))

with open(f"{OUT}/hero-poster.svg", "w") as f:
    f.write(hero_poster())

with open(f"{OUT}/mapa-placeholder.svg", "w") as f:
    f.write(map_placeholder())

for i in range(2):
    with open(f"{OUT}/editorial-{i + 1}.svg", "w") as f:
        f.write(editorial(i))

print("wrote:", sorted(os.listdir(OUT)))
