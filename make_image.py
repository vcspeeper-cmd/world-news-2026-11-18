#!/usr/bin/env python3
"""Draw the make.fun "news-image-20261118" editorial poster.

Deterministic: no randomness, no clocks, no network, no locale-dependent
formatting.  Running this twice produces byte-identical PNG output.

Content: the world's news of Wednesday 18 November 2026, from the day's
reported stories -- the Beijing Trump-Xi-Putin summit, the widening Iran
war in the Gulf, the Nvidia-led sell-off and Fed hike warning, the declared
super El Nino, and the two Americans held in China.
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Canvas + palette
# --------------------------------------------------------------------------

W = H = 1024
M = 44

BG = (10, 16, 28)
DOT = (26, 36, 56)
PANEL = (17, 26, 44)
PANEL_EDGE = (36, 50, 76)
WHITE = (245, 248, 252)
GOLD = (228, 186, 76)
GREY = (150, 162, 180)
MUTED = (108, 120, 140)
RED = (222, 66, 66)
GREEN = (74, 190, 120)

US_RED = (178, 34, 52)
US_BLUE = (52, 56, 110)
CN_RED = (222, 41, 16)
CN_YELLOW = (255, 222, 0)
RU_BLUE = (0, 57, 166)
RU_RED = (213, 43, 30)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

_cache: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}


def F(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    key = (size, bold)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    return _cache[key]


def tw(d: ImageDraw.ImageDraw, s: str, size: int, bold: bool = False) -> float:
    return d.textlength(s, font=F(size, bold))


def fit(d: ImageDraw.ImageDraw, s: str, size: int, bold: bool, maxw: float) -> int:
    """Largest size <= size whose single-line width is <= maxw."""
    while size > 8 and tw(d, s, size, bold) > maxw:
        size -= 1
    return size


def wrap(d: ImageDraw.ImageDraw, s: str, size: int, bold: bool, maxw: float) -> list[str]:
    words = s.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(d, trial, size, bold) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, s, x, y, size, bold, color, maxw, lh):
    lines = wrap(d, s, size, bold, maxw)
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=F(size, bold), fill=color)
    return y + len(lines) * lh


# --------------------------------------------------------------------------
# Small vector marks
# --------------------------------------------------------------------------


def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    stripe = h / 13.0
    for i in range(13):
        if i % 2 == 0:
            d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe + 1], fill=US_RED)
    d.rectangle([x, y, x + w * 0.42, y + h * 0.54], fill=US_BLUE)
    for r in range(4):
        for c in range(5):
            cx = x + w * 0.05 + c * w * 0.08
            cy = y + h * 0.07 + r * h * 0.13
            d.ellipse([cx, cy, cx + w * 0.028, cy + h * 0.05], fill=WHITE)


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CN_RED)
    s = w * 0.16
    d.ellipse([x + w * 0.08, y + h * 0.18, x + w * 0.08 + s, y + h * 0.18 + s], fill=CN_YELLOW)
    for (fx, fy) in ((0.30, 0.10), (0.36, 0.22), (0.36, 0.36), (0.30, 0.48)):
        d.ellipse([x + w * fx, y + h * fy, x + w * fx + s * 0.45, y + h * fy + s * 0.45], fill=CN_YELLOW)


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3.0], fill=WHITE)
    d.rectangle([x, y + h / 3.0, x + w, y + 2 * h / 3.0], fill=RU_BLUE)
    d.rectangle([x, y + 2 * h / 3.0, x + w, y + h], fill=RU_RED)


def mark_missile(d, x, y, s, color):
    d.rounded_rectangle([x + s * 0.34, y + s * 0.05, x + s * 0.66, y + s * 0.62],
                        radius=s * 0.16, fill=color)
    d.polygon([(x + s * 0.34, y + s * 0.05), (x + s * 0.5, y - s * 0.12),
               (x + s * 0.66, y + s * 0.05)], fill=color)
    d.polygon([(x + s * 0.34, y + s * 0.62), (x + s * 0.22, y + s * 0.9),
               (x + s * 0.34, y + s * 0.78)], fill=color)
    d.polygon([(x + s * 0.66, y + s * 0.62), (x + s * 0.78, y + s * 0.9),
               (x + s * 0.66, y + s * 0.78)], fill=color)


def mark_chart_down(d, x, y, s, color):
    d.line([x, y + s * 0.1, x + s * 0.3, y + s * 0.42, x + s * 0.52, y + s * 0.28,
            x + s * 0.86, y + s * 0.78], fill=color, width=max(3, int(s * 0.09)))
    d.polygon([(x + s * 0.86, y + s * 0.86), (x + s * 0.84, y + s * 0.6),
               (x + s * 0.64, y + s * 0.8)], fill=color)


def mark_rate_up(d, x, y, s, color):
    d.line([x, y + s * 0.8, x + s * 0.32, y + s * 0.5, x + s * 0.56, y + s * 0.62,
            x + s * 0.86, y + s * 0.16], fill=color, width=max(3, int(s * 0.09)))
    d.polygon([(x + s * 0.9, y + s * 0.08), (x + s * 0.66, y + s * 0.14),
               (x + s * 0.82, y + s * 0.3)], fill=color)


def mark_thermo(d, x, y, s, color):
    d.rounded_rectangle([x + s * 0.38, y + s * 0.04, x + s * 0.62, y + s * 0.62],
                        radius=s * 0.12, fill=None, outline=color, width=max(3, int(s * 0.07)))
    d.ellipse([x + s * 0.3, y + s * 0.56, x + s * 0.7, y + s * 0.96], fill=color)
    d.rectangle([x + s * 0.44, y + s * 0.2, x + s * 0.56, y + s * 0.6], fill=color)


def mark_person(d, x, y, s, color):
    d.ellipse([x + s * 0.3, y, x + s * 0.7, y + s * 0.36], fill=color)
    d.rounded_rectangle([x + s * 0.14, y + s * 0.4, x + s * 0.86, y + s * 1.0],
                        radius=s * 0.22, fill=color)


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------

MAST_BOTTOM = 118
RULE_1 = 124

MAIN_TOP, MAIN_BOT = 142, 462
SEC_TOP, SEC_BOT = 476, 620
BRIEF_TOP, BRIEF_BOT = 634, 826
RULE_2 = 946
FOOT_TOP = 958


def panel(d, box, edge=PANEL_EDGE, fill=PANEL):
    d.rounded_rectangle(box, radius=14, fill=fill, outline=edge, width=2)


def build() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # faint dot grid for texture
    for gy in range(14, H, 34):
        for gx in range(14, W, 34):
            d.point((gx, gy), fill=DOT)

    # ---------------- masthead ----------------
    d.text((M, 22), "THE WORLD TODAY", font=F(60, True), fill=WHITE)
    d.text((W - M, 34), "ONE DAY, ONE PICTURE", font=F(19, True), fill=GREY, anchor="ra")
    d.text((W - M, 60), "EDITION 18.11.26", font=F(19), fill=MUTED, anchor="ra")
    d.text((M, 92), "WEDNESDAY 18 NOVEMBER 2026", font=F(25, True), fill=GOLD)
    d.rectangle([M, RULE_1, W - M, RULE_1 + 3], fill=GOLD)

    # ---------------- main story ----------------
    panel(d, [M, MAIN_TOP, W - M, MAIN_BOT])
    fx, fy, fw, fh, fg = M + 24, MAIN_TOP + 20, 66, 43, 12
    flag_us(d, fx, fy, fw, fh)
    flag_cn(d, fx + fw + fg, fy, fw, fh)
    flag_ru(d, fx + 2 * (fw + fg), fy, fw, fh)

    d.text((M + 24, MAIN_TOP + 78), "BEIJING  \u00b7  TRILATERAL SUMMIT",
           font=F(19, True), fill=GOLD)

    head = "TRUMP, XI AND PUTIN MEET IN BEIJING"
    hsize = fit(d, head, 50, True, W - 2 * M - 48)
    d.text((M + 24, MAIN_TOP + 106), head, font=F(hsize, True), fill=WHITE)

    body = ("The first three-way summit of the three leaders: a trade truce, "
            "talks on cutting nuclear arsenals, and the two Americans held in China.")
    draw_wrapped(d, body, M + 24, MAIN_TOP + 172, 21, False, GREY,
                 W - M - 300, 30)

    # three leader silhouettes
    bx, by, bs = W - M - 246, MAIN_TOP + 150, 58
    mark_person(d, bx, by, bs, (72, 118, 210))
    mark_person(d, bx + 74, by - 8, bs, (196, 62, 62))
    mark_person(d, bx + 148, by, bs, (150, 158, 172))

    d.text((M + 24, MAIN_BOT - 34), "FIRST-EVER TRILATERAL  \u00b7  BEIJING, CHINA",
           font=F(17, True), fill=MUTED)

    # ---------------- second story ----------------
    panel(d, [M, SEC_TOP, W - M, SEC_BOT])
    mark_missile(d, M + 26, SEC_TOP + 34, 52, RED)
    d.text((M + 104, SEC_TOP + 22), "IRAN WAR WIDENS ACROSS THE GULF",
           font=F(fit(d, "IRAN WAR WIDENS ACROSS THE GULF", 31, True, W - 2 * M - 130), True),
           fill=WHITE)
    draw_wrapped(d, "US strikes a missile launch site; Tehran hits Gulf shipping "
                    "and threatens the Strait of Hormuz.", M + 104, SEC_TOP + 66,
                 20, False, GREY, W - 2 * M - 132, 28)

    # ---------------- three briefs ----------------
    gap = 16
    cw = (W - 2 * M - 2 * gap) / 3.0
    briefs = [
        ("NVIDIA ROUT", "Earnings fail to soothe; the S&P 500 breaks support as "
                        "Fed minutes signal more hikes.", mark_chart_down, RED),
        ("SUPER EL NI\u00d1O", "The Climate Prediction Center declares a super "
                              "El Ni\u00f1o, warning of extreme weather.", mark_thermo, GOLD),
        ("EU MIGRATION SPLIT", "Rights groups urge Europe to drop Rwanda "
                               "deportation plans as Ceuta crossings surge.", mark_person, (96, 150, 220)),
    ]
    for i, (title, text, mark, color) in enumerate(briefs):
        x0 = M + i * (cw + gap)
        x1 = x0 + cw
        panel(d, [x0, BRIEF_TOP, x1, BRIEF_BOT], edge=(30, 42, 64), fill=(14, 22, 38))
        mark(d, x0 + 16, BRIEF_TOP + 16, 34, color)
        d.text((x0 + 60, BRIEF_TOP + 18),
               title, font=F(fit(d, title, 24, True, cw - 76), True), fill=WHITE)
        draw_wrapped(d, text, x0 + 16, BRIEF_TOP + 62, 17, False, GREY, cw - 32, 24)

    # ---------------- ticker ----------------
    tick_y = 846
    d.text((M, tick_y), "ALSO TODAY", font=F(15, True), fill=GOLD)
    lines = [
        "Ceuta: 1,200 cross in a day   \u00b7   Brent above $94 on Hormuz fears",
        "Fed minutes point to a December hike   \u00b7   Kyiv: drones hit the grid",
    ]
    for i, ln in enumerate(lines):
        d.text((M, tick_y + 28 + i * 26), ln, font=F(15), fill=GREY)

    # ---------------- footer ----------------
    d.rectangle([M, RULE_2, W - M, RULE_2 + 3], fill=GOLD)
    d.text((M, FOOT_TOP), "18 NOVEMBER 2026  \u00b7  THE DAY IN ONE IMAGE",
           font=F(21, True), fill=GOLD)
    d.text((W - M, FOOT_TOP + 3), "BEIJING  \u00b7  TEHRAN  \u00b7  NEW YORK  \u00b7  GENEVA",
           font=F(16), fill=MUTED, anchor="ra")

    return img


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print(f"wrote {os.path.getsize(path)} bytes to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
