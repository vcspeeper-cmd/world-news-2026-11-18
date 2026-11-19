"""Editorial news poster generator for Wednesday 18 November 2026."""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 44

# Colors
BG = (10, 16, 28)
DOT = (26, 36, 56)
PANEL = (17, 26, 44)
PANEL_EDGE = (36, 50, 76)
WHITE = (245, 248, 252)
GREY = (150, 162, 180)
MUTED = (108, 120, 140)
GOLD = (228, 186, 76)
RED = (222, 66, 66)

_fonts = {}

def F(size, bold=False):
    """Get cached font."""
    key = (size, bold)
    if key not in _fonts:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        _fonts[key] = ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)
    return _fonts[key]

def tw(d, s, size, bold=False):
    """Text width."""
    return d.textlength(s, font=F(size, bold))

def fit(d, s, size, bold, maxw):
    """Shrink size until text fits in maxw."""
    while size > 8 and tw(d, s, size, bold) > maxw:
        size -= 1
    return size

def wrap(d, s, size, bold, maxw):
    """Word-wrap text into lines."""
    lines = []
    words = s.split()
    line = ""
    for w in words:
        test = line + (" " if line else "") + w
        if tw(d, test, size, bold) <= maxw:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_wrapped(d, s, x, y, size, bold, color, maxw, lh):
    """Draw wrapped lines, return y after last line."""
    lines = wrap(d, s, size, bold, maxw)
    for line in lines:
        d.text((x, y), line, fill=color, font=F(size, bold))
        y += lh
    return y

def panel(d, box, edge=PANEL_EDGE, fill=PANEL):
    """Draw rounded panel."""
    d.rounded_rectangle(box, radius=14, outline=edge, fill=fill, width=2)

def flag_us(d, x, y, w, h):
    """Draw US flag: white field, red/white stripes, blue canton with dots."""
    d.rectangle((x, y, x+w, y+h), fill=WHITE)
    stripe_h = h // 13
    for i in range(13):
        if i % 2 == 0:
            d.rectangle((x, y+i*stripe_h, x+w, y+(i+1)*stripe_h), fill=RED)
    canton_w = int(w * 0.4)
    canton_h = stripe_h * 7
    d.rectangle((x, y, x+canton_w, y+canton_h), fill=(0, 33, 71))
    dot_cols, dot_rows = 4, 5
    dot_w = canton_w / dot_cols
    dot_h = canton_h / dot_rows
    dot_r = int(min(dot_w, dot_h) * 0.15)
    for row in range(dot_rows):
        for col in range(dot_cols):
            cx = int(x + dot_w * (col + 0.5))
            cy = int(y + dot_h * (row + 0.5))
            d.ellipse((cx-dot_r, cy-dot_r, cx+dot_r, cy+dot_r), fill=WHITE)

def flag_cn(d, x, y, w, h):
    """Draw Chinese flag: red field, yellow dots."""
    d.rectangle((x, y, x+w, y+h), fill=(187, 19, 62))
    big_dot_x = int(x + w * 0.6)
    big_dot_y = int(y + h * 0.35)
    big_dot_r = int(w * 0.15)
    d.ellipse((big_dot_x-big_dot_r, big_dot_y-big_dot_r, big_dot_x+big_dot_r, big_dot_y+big_dot_r), fill=GOLD)
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        small_x = int(x + w * 0.6 + dx * w * 0.25)
        small_y = int(y + h * 0.35 + dy * h * 0.25)
        small_r = int(w * 0.05)
        d.ellipse((small_x-small_r, small_y-small_r, small_x+small_r, small_y+small_r), fill=GOLD)

def flag_ru(d, x, y, w, h):
    """Draw Russian flag: white/blue/red horizontal bands."""
    band_h = h // 3
    d.rectangle((x, y, x+w, y+band_h), fill=WHITE)
    d.rectangle((x, y+band_h, x+w, y+2*band_h), fill=(0, 56, 147))
    d.rectangle((x, y+2*band_h, x+w, y+h), fill=RED)

def mark_missile(d, x, y, s, color):
    """Draw missile: vertical body with pointed nose and swept fins."""
    body_w = int(s * 0.2)
    d.rectangle((x-body_w//2, y, x+body_w//2, y+int(s*0.7)), fill=color)
    points = [(x-body_w//2, y+int(s*0.7)), (x+body_w//2, y+int(s*0.7)), (x, y+s)]
    d.polygon(points, fill=color)
    fin_w = int(s * 0.15)
    d.polygon([(x-body_w//2, y+int(s*0.5)), (x-body_w//2-fin_w, y+int(s*0.65)), (x-body_w//2, y+int(s*0.8))], fill=color)
    d.polygon([(x+body_w//2, y+int(s*0.5)), (x+body_w//2+fin_w, y+int(s*0.65)), (x+body_w//2, y+int(s*0.8))], fill=color)

def mark_chart_down(d, x, y, s, color):
    """Draw descending polyline with arrowhead."""
    points = [(x, y), (x+int(s*0.4), y+int(s*0.3)), (x+s, y+int(s*0.8))]
    d.line(points, fill=color, width=3)
    dx, dy = int(s*0.2), int(s*0.2)
    arrow = [(x+s, y+int(s*0.8)), (x+s-dx-dy, y+int(s*0.8)-dy+dx), (x+s-dx+dy, y+int(s*0.8)-dy-dx)]
    d.polygon(arrow, fill=color)

def mark_rate_up(d, x, y, s, color):
    """Draw rising polyline with arrowhead."""
    points = [(x, y+s), (x+int(s*0.4), y+int(s*0.5)), (x+s, y)]
    d.line(points, fill=color, width=3)
    dx, dy = int(s*0.2), int(s*0.2)
    arrow = [(x+s, y), (x+s-dx-dy, y-dy+dx), (x+s-dx+dy, y-dy-dx)]
    d.polygon(arrow, fill=color)

def mark_thermo(d, x, y, s, color):
    """Draw thermometer: outlined tube, filled column and a round bulb."""
    tube_w = int(s * 0.22)
    cx = x + s // 2
    top = y
    bot = y + int(s * 0.6)
    d.rounded_rectangle((cx - tube_w // 2, top, cx + tube_w // 2, bot),
                        radius=tube_w // 2, outline=color, width=3)
    bulb_r = int(s * 0.16)
    d.ellipse((cx - bulb_r, bot - bulb_r // 2, cx + bulb_r, bot + bulb_r + bulb_r // 2),
              outline=color, fill=color, width=3)
    d.rectangle((cx - tube_w // 4, top + int(s * 0.24), cx + tube_w // 4, bot), fill=color)


def mark_explosion(d, x, y, s, color):
    """Draw explosion burst: central circle with radiating points."""
    center_r = int(s * 0.15)
    d.ellipse((x-center_r, y-center_r, x+center_r, y+center_r), fill=color)
    point_len = int(s * 0.4)
    for angle_idx in range(8):
        angle = angle_idx * 45
        rad = angle * 3.14159 / 180
        import math
        px = x + int(point_len * math.cos(rad))
        py = y + int(point_len * math.sin(rad))
        points = [(x, y), (px-int(s*0.08), py-int(s*0.08)), (px+int(s*0.08), py+int(s*0.08))]
        d.polygon(points, fill=color)

def mark_person(d, x, y, s, color):
    """Draw person: rounded head and tapered body."""
    head_r = int(s * 0.18)
    d.ellipse((x-head_r, y-head_r, x+head_r, y+head_r), outline=color, fill=color, width=2)
    body_top_w = int(s * 0.22)
    body_bot_w = int(s * 0.1)
    body_h = int(s * 0.5)
    points = [
        (x - body_top_w // 2, y + head_r),
        (x + body_top_w // 2, y + head_r),
        (x + body_bot_w // 2, y + head_r + body_h),
        (x - body_bot_w // 2, y + head_r + body_h),
    ]
    d.polygon(points, outline=color, fill=color)

def main():
    """Build and save the poster."""
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Dot grid
    for yi in range(14, H, 34):
        for xi in range(14, W, 34):
            d.point((xi, yi), fill=DOT)

    # Masthead
    d.text((M, 22), "THE WORLD TODAY", fill=WHITE, font=F(60, True))
    s1 = "ONE DAY, ONE PICTURE"
    d.text((W-M-tw(d, s1, 19, True), 34), s1, fill=GREY, font=F(19, True))
    s2 = "EDITION 18.11.26"
    d.text((W-M-tw(d, s2, 19, False), 60), s2, fill=MUTED, font=F(19, False))
    d.text((M, 92), "WEDNESDAY 18 NOVEMBER 2026", fill=GOLD, font=F(25, True))
    d.line((M, 124, W-M, 127), fill=GOLD, width=3)
    d.line((M, 132, W-M, 133), fill=GREY, width=1)

    # Lead panel
    panel(d, (M, 142, W-M, 462))
    flag_us(d, M+24, 162, 66, 43)
    flag_cn(d, M+102, 162, 66, 43)
    flag_ru(d, M+180, 162, 66, 43)

    d.text((M+24, 220), "BEIJING  ·  TRILATERAL SUMMIT", fill=GOLD, font=F(19, True))

    headline = "TRUMP, XI AND PUTIN MEET IN BEIJING"
    h_size = fit(d, headline, 50, True, W-M-300)
    d.text((M+24, 248), headline, fill=WHITE, font=F(h_size, True))

    body1 = "The first three-way summit of the three leaders: a trade truce, talks on cutting nuclear arsenals, and the two Americans held in China."
    draw_wrapped(d, body1, M+24, 314, 21, False, GREY, W-M-240, 28)

    mark_person(d, W-M-100-30, 292, 58, (72, 118, 210))
    mark_person(d, W-M-100, 284, 58, (196, 62, 62))
    mark_person(d, W-M-100+30, 292, 58, (150, 158, 172))

    d.text((M+24, 428), "FIRST-EVER TRILATERAL  ·  BEIJING, CHINA", fill=MUTED, font=F(17, True))

    # Second panel
    panel(d, (M, 476, W-M, 620))
    mark_explosion(d, M+26, 530, 52, RED)

    title2 = "IRAN WAR WIDENS ACROSS THE GULF"
    t2_size = fit(d, title2, 31, True, W-2*M-130)
    d.text((M+104, 498), title2, fill=WHITE, font=F(t2_size, True))

    body2 = "US strikes a missile launch site; Tehran hits Gulf shipping and threatens the Strait of Hormuz."
    draw_wrapped(d, body2, M+104, 542, 20, False, GREY, W-2*M-132, 26)

    # Three briefs
    cw = (W - 2*M - 32) // 3
    briefs = [
        ("NVIDIA ROUT", mark_chart_down, RED, "Earnings fail to soothe; the S&P 500 breaks support as Fed minutes signal more hikes."),
        ("SUPER EL NIÑO", mark_thermo, GOLD, "The Climate Prediction Center declares a super El Niño, warning of extreme weather."),
        ("EU MIGRATION SPLIT", mark_person, (96, 150, 220), "Rights groups urge Europe to drop Rwanda deportation plans as Ceuta crossings surge."),
    ]

    for i, (title, mark_func, mark_color, body) in enumerate(briefs):
        x0 = M + i * (cw + 16)
        panel(d, (x0, 634, x0+cw, 826), edge=(30, 42, 64), fill=(14, 22, 38))
        mark_func(d, x0+16, 650, 34, mark_color)
        t_size = fit(d, title, 24, True, cw-76)
        d.text((x0+60, 652), title, fill=WHITE, font=F(t_size, True))
        draw_wrapped(d, body, x0+16, 696, 17, False, GREY, cw-32, 24)

    # Ticker
    d.text((M, 846), "ALSO TODAY", fill=GOLD, font=F(15, True))
    d.text((M, 874), "Ceuta: 1,200 cross in a day · Brent above $94 on Hormuz fears", fill=GREY, font=F(15, False))
    d.text((M, 900), "Fed minutes point to a December hike · Kyiv: drones hit the grid", fill=GREY, font=F(15, False))

    # Footer
    d.line((M, 946, W-M, 949), fill=GOLD, width=3)
    d.text((M, 958), "18 NOVEMBER 2026  ·  THE DAY IN ONE IMAGE", fill=GOLD, font=F(21, True))
    s3 = "BEIJING  ·  TEHRAN  ·  NEW YORK  ·  GENEVA"
    d.text((W-M-tw(d, s3, 16, False), 961), s3, fill=MUTED, font=F(16, False))

    outpath = os.path.join(outdir, "entry.png")
    img.save(outpath, "PNG", optimize=True)
    size = os.path.getsize(outpath)
    print(f"{size} bytes → {outpath}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
