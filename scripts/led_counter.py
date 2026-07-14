import re
import urllib.request

USERNAME = "parmesh-kumar-ai"
LABEL = "PROFILE VISITORS"
OUT_PATH = "dist/led-counter.svg"

def fetch_count():
    url = f"https://komarev.com/ghpvc/?username={USERNAME}&style=flat"
    with urllib.request.urlopen(url, timeout=15) as resp:
        svg_text = resp.read().decode("utf-8")
    matches = re.findall(r'>([\d,]{2,})<', svg_text)
    if not matches:
        raise ValueError("Could not parse visitor count from badge")
    return matches[-1].replace(",", "")

def hseg_points(cx, cy, seg_w, t):
    half_w, half_t = seg_w / 2, t / 2
    tip = half_t
    pts = [
        (cx - half_w, cy), (cx - half_w + tip, cy - half_t),
        (cx + half_w - tip, cy - half_t), (cx + half_w, cy),
        (cx + half_w - tip, cy + half_t), (cx - half_w + tip, cy + half_t),
    ]
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

def vseg_points(cx, cy, seg_h, t):
    half_h, half_t = seg_h / 2, t / 2
    tip = half_t
    pts = [
        (cx, cy - half_h), (cx + half_t, cy - half_h + tip),
        (cx + half_t, cy + half_h - tip), (cx, cy + half_h),
        (cx - half_t, cy + half_h - tip), (cx - half_t, cy - half_h + tip),
    ]
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

DIGIT_SEGMENTS = {
    '0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd',
    '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc',
    '8': 'abcdefg', '9': 'abcdfg',
}

# --- Reduced-height parameters (width formula unchanged) ---
W = 40          # digit segment width -- kept same so overall width is unchanged
T = 6           # segment thickness
H = 22          # half-digit height (roughly half the original overall height)
TOP_PAD = 14
LABEL_H = 22
LABEL_SIZE = 9

# --- White-theme colors ---
ON_COLOR = "#0506A1"    # lit segments -> brand indigo (good contrast on white)
OFF_COLOR = "#E5E7EB"   # unlit segments -> light gray, faintly visible on white
BORDER_COLOR = "#0506A1"
ACCENT_COLOR = "#FFD900"
LABEL_COLOR = "#4B5563"

def digit_svg(digit, ox, oy, w=W, t=T, h=H, on_color=ON_COLOR, off_color=OFF_COLOR):
    lit = DIGIT_SEGMENTS.get(digit, '')
    segs = {
        'a': ('h', w / 2, 0), 'f': ('v', 0, h / 2), 'b': ('v', w, h / 2),
        'g': ('h', w / 2, h), 'e': ('v', 0, h + h / 2), 'c': ('v', w, h + h / 2),
        'd': ('h', w / 2, 2 * h),
    }
    out = []
    for name, (orient, sx, sy) in segs.items():
        cx, cy = ox + sx, oy + sy
        color = on_color if name in lit else off_color
        pts = hseg_points(cx, cy, w - t * 0.4, t) if orient == 'h' else vseg_points(cx, cy, h - t * 0.4, t)
        out.append(f'<polygon points="{pts}" fill="{color}"/>')
    return "\n".join(out)

def build_led_display(number_str, label=LABEL):
    digit_width = W + 22
    n = len(number_str)
    panel_w = n * digit_width + 50
    panel_h = 2 * H + TOP_PAD + LABEL_H

    digits_svg = [digit_svg(ch, 25 + i * digit_width, TOP_PAD) for i, ch in enumerate(number_str)]

    defs = f'''
    <filter id="ledGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="1.6" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#FFFFFF"/>
    </linearGradient>
    '''

    return f'''<svg viewBox="0 0 {panel_w} {panel_h}" xmlns="http://www.w3.org/2000/svg" font-family="Arial, sans-serif">
<defs>{defs}</defs>
<rect x="0" y="0" width="{panel_w}" height="{panel_h}" rx="10" fill="url(#panelGrad)" stroke="{BORDER_COLOR}" stroke-width="2.5"/>
<rect x="3" y="3" width="{panel_w-6}" height="{panel_h-6}" rx="7" fill="none" stroke="{ACCENT_COLOR}" stroke-width="1" opacity="0.6"/>
<g filter="url(#ledGlow)">
  <g>
    <animate attributeName="opacity" values="1;0.94;1;0.97;1" dur="4s" repeatCount="indefinite"/>
    {"".join(digits_svg)}
  </g>
</g>
<text x="{panel_w/2}" y="{panel_h-6}" text-anchor="middle" fill="{LABEL_COLOR}" font-size="{LABEL_SIZE}" letter-spacing="2" font-weight="bold">{label}</text>
</svg>'''

if __name__ == "__main__":
    import os
    count = fetch_count()
    svg = build_led_display(count)
    os.makedirs("dist", exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Generated LED counter for count={count}")
