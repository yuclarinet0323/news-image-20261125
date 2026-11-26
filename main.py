#!/usr/bin/env python3
"""The World Today: 25 November 2026 in one image.

A deterministic newspaper front page drawn with the Python standard
library only.  The program builds a 1024x1024 RGB canvas pixel by
pixel, then writes it as a PNG to /output/entry.png (or to the
directory named by MAKEFUN_OUTPUT_DIR when that is set).

Lead story: Yemen's Houthis attack Saudi Arabia's largest oil
refinery at Ras Tanura while tankers hit mines in Hormuz.
"""
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 240, 224)
INK = (24, 24, 22)
FAINT = (104, 98, 84)
RULE = (24, 24, 22)
RED = (178, 34, 28)
BLUE = (30, 74, 138)
SKY = (168, 198, 224)
SKY2 = (214, 228, 240)
SEA = (52, 104, 148)
SAND = (226, 204, 160)
FIRE = (238, 118, 30)
FIRE2 = (250, 186, 52)
SMOKE = (70, 68, 66)
WHITE = (252, 252, 250)
GOLD = (196, 148, 44)
GREEN = (44, 118, 74)

canvas = bytearray(W * H * 3)


def px(x, y, col):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i] = col[0]
        canvas[i + 1] = col[1]
        canvas[i + 2] = col[2]


def rect(x, y, w, h, col):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, col)


def frame(x, y, w, h, col, t=3):
    rect(x, y, w, t, col)
    rect(x, y + h - t, w, t, col)
    rect(x, y, t, h, col)
    rect(x + w - t, y, t, h, col)


def disc(cx, cy, r, col):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, col)


def line(x0, y0, x1, y1, col, t=3):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    half = t // 2
    for s in range(steps + 1):
        x = x0 + (x1 - x0) * s // steps
        y = y0 + (y1 - y0) * s // steps
        rect(x - half, y - half, t, t, col)


def tri(x0, y0, x1, y1, x2, y2, col):
    lo_x, hi_x = min(x0, x1, x2), max(x0, x1, x2)
    lo_y, hi_y = min(y0, y1, y2), max(y0, y1, y2)
    d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if d == 0:
        return
    for yy in range(lo_y, hi_y + 1):
        for xx in range(lo_x, hi_x + 1):
            a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
            b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
            c = 1.0 - a - b
            if a >= 0 and b >= 0 and c >= 0:
                px(xx, yy, col)


# ---------------------------------------------------------------- font
# A compact 5x7 bitmap font, defined as seven strings of five bits per
# glyph.  Only the characters the page uses are included.
GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, col, bold=False):
    cx = x
    shift = max(1, scale // 2)
    for ch in s.upper():
        glyph = GLYPHS.get(ch, GLYPHS[" "])
        for row in range(7):
            bits = glyph[row]
            for col_i in range(5):
                if bits[col_i] == "#":
                    rect(cx + col_i * scale, y + row * scale, scale, scale, col)
                    if bold:
                        rect(cx + col_i * scale + shift, y + row * scale,
                             scale, scale, col)
        cx += 6 * scale
    return cx


def centered(y, s, scale, col, bold=False):
    x = (W - text_w(s, scale)) // 2
    draw_text(x, y, s, scale, col, bold)


def wrapped(x, y, s, scale, col, max_w, leading=None, bold=False):
    if leading is None:
        leading = 9 * scale
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * leading, ln, scale, col, bold)
    return y + len(lines) * leading



# ---------------------------------------------------------------- scenes
def draw_refinery(x, y, w, h):
    """Lead visual: a coastal refinery on fire, smoke, a drone above."""
    rect(x, y, w, h, SKY2)
    rect(x, y, w, h // 3, SKY)
    disc(x + w - 70, y + 46, 24, FIRE2)
    # distant skyline tower (Riyadh) on the left horizon
    rect(x + 26, y + h // 3 - 66, 26, 66, (120, 130, 142))
    tri(x + 26, y + h // 3 - 66, x + 52, y + h // 3 - 66, x + 39, y + h // 3 - 92, (120, 130, 142))
    # smoke plumes rising from the plant
    for cx, cy, r in ((x + 300, y + 58, 30), (x + 345, y + 44, 38),
                      (x + 398, y + 56, 30), (x + 440, y + 74, 24),
                      (x + 262, y + 76, 22)):
        disc(cx, cy, r, SMOKE)
        disc(cx - r // 3, cy - r // 4, r // 2, (96, 94, 92))
    # ground and sea
    gy = y + h - 64
    rect(x, gy, w, 64, SEA)
    rect(x, gy - 26, w, 26, SAND)
    # storage tanks
    for tx in (x + 36, x + 118, x + 470):
        rect(tx, gy - 62, 66, 40, WHITE)
        rect(tx, gy - 68, 66, 8, (188, 188, 184))
        rect(tx, gy - 40, 66, 5, (188, 60, 44))
    # distillation towers
    for tx in (x + 236, x + 292, x + 356):
        rect(tx, gy - 128, 30, 106, (150, 156, 164))
        rect(tx - 4, gy - 134, 38, 8, (110, 116, 124))
        rect(tx + 4, gy - 104, 22, 5, (110, 116, 124))
        rect(tx + 4, gy - 78, 22, 5, (110, 116, 124))
    line(x + 220, gy - 20, x + 470, gy - 20, (90, 96, 104), 5)
    # flames at the tower bases and one tank
    for fx, fs in ((x + 250, 30), (x + 306, 40), (x + 370, 28), (x + 140, 24)):
        tri(fx - fs // 2, gy - 22, fx + fs // 2, gy - 22, fx, gy - 22 - fs * 2, FIRE)
        tri(fx - fs // 4, gy - 22, fx + fs // 4, gy - 22, fx, gy - 22 - fs, FIRE2)
    # a drone silhouette crossing the sky
    dx, dy = x + 150, y + 52
    rect(dx - 26, dy - 4, 52, 8, INK)
    rect(dx - 4, dy - 12, 8, 24, INK)
    line(dx - 26, dy - 4, dx - 44, dy - 16, INK, 4)
    line(dx + 26, dy - 4, dx + 44, dy - 16, INK, 4)
    disc(dx - 46, dy - 18, 6, INK)
    disc(dx + 46, dy - 18, 6, INK)
    frame(x, y, w, h, INK, 3)


def draw_tanker(x, y, w, h):
    rect(x, y, w, h, SKY2)
    rect(x, y + h - 26, w, 26, SEA)
    # hull and deck cargo
    rect(x + 14, y + h - 52, w - 28, 16, (150, 44, 36))
    rect(x + 22, y + h - 64, w - 90, 12, (90, 96, 104))
    rect(x + w - 56, y + h - 84, 22, 32, WHITE)
    rect(x + w - 50, y + h - 78, 10, 8, BLUE)
    # a naval mine in the water, and a burst of flame at the bow
    disc(x + w - 34, y + h - 18, 9, INK)
    for a in range(8):
        import math
        mx = x + w - 34 + int(13 * math.cos(a * 0.785))
        my = y + h - 18 + int(13 * math.sin(a * 0.785))
        px(mx, my, INK)
    tri(x + 26, y + h - 52, x + 52, y + h - 52, x + 39, y + h - 96, FIRE)
    tri(x + 32, y + h - 52, x + 46, y + h - 52, x + 39, y + h - 76, FIRE2)


def draw_chart(x, y, w, h):
    rect(x, y, w, h, WHITE)
    for i in range(4):
        rect(x + 10, y + 14 + i * 22, w - 20, 2, (216, 212, 200))
    pts = ((x + 12, y + 20), (x + 44, y + 34), (x + 72, y + 30),
           (x + 100, y + 58), (x + 128, y + 52), (x + w - 16, y + 72))
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 5)
    tri(x + w - 30, y + 58, x + w - 8, y + 68, x + w - 24, y + 80, RED)
    draw_text(x + 6, y + h - 18, "NASDAQ-3.9%", 2, RED)


def draw_islands(x, y, w, h):
    rect(x, y, w, h, SEA)
    disc(x + 52, y + 56, 26, SAND)
    disc(x + 118, y + 40, 18, SAND)
    disc(x + 132, y + 74, 14, SAND)
    disc(x + 52, y + 50, 8, GREEN)
    disc(x + 118, y + 36, 6, GREEN)
    # shield of agreement in the middle
    rect(x + 74, y + 22, 34, 40, GOLD)
    tri(x + 74, y + 62, x + 108, y + 62, x + 91, y + 82, GOLD)
    draw_text(x + 84, y + 34, "NO", 2, INK)
    draw_text(x + 80, y + 48, "BASE", 1, INK)


def draw_drones(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x, y + h - 22, w, 22, (128, 138, 120))
    for dx, dy in ((x + 40, y + 26), (x + 96, y + 44), (x + 140, y + 20)):
        rect(dx - 14, dy - 3, 28, 6, INK)
        disc(dx - 18, dy - 8, 4, INK)
        disc(dx + 18, dy - 8, 4, INK)
    # apartment block with one corner lit by fire
    rect(x + 18, y + h - 74, 44, 52, (140, 144, 150))
    for r in range(3):
        for c in range(3):
            rect(x + 24 + c * 13, y + h - 66 + r * 15, 8, 9, FIRE2)
    tri(x + 52, y + h - 40, x + 70, y + h - 40, x + 61, y + h - 66, FIRE)


def draw_city(x, y, w, h):
    rect(x, y, w, h, (196, 178, 150))
    rect(x + 10, y + h - 56, 30, 56, (150, 146, 138))
    rect(x + 52, y + h - 78, 38, 78, (164, 158, 148))
    rect(x + 102, y + h - 44, 30, 44, (150, 146, 138))
    for wx in (x + 58, x + 72):
        for wy in range(4):
            rect(wx, y + h - 68 + wy * 16, 8, 9, (90, 96, 104))
    disc(x + 70, y + 30, 16, FIRE)
    disc(x + 58, y + 40, 11, SMOKE)
    disc(x + 84, y + 38, 12, SMOKE)


def panel(x, y, w, tag, tag_col, headline, body, art):
    frame(x, y, w, 220, INK, 3)
    rect(x + 3, y + 3, w - 6, 30, tag_col)
    draw_text(x + 12, y + 10, tag, 2, WHITE, bold=True)
    art(x + w - 158, y + 40, 148, 100)
    wrapped(x + 12, y + 44, headline, 3, INK, w - 178, leading=29, bold=True)
    wrapped(x + 12, y + 148, body, 2, INK, w - 24, leading=18)


def mini_panel(x, y, w, tag, tag_col, headline, body):
    frame(x, y, w, 154, INK, 3)
    rect(x + 3, y + 3, w - 6, 26, tag_col)
    draw_text(x + 10, y + 9, tag, 2, WHITE, bold=True)
    wrapped(x + 10, y + 36, headline, 2, INK, w - 20, leading=18, bold=True)
    wrapped(x + 10, y + 76, body, 2, INK, w - 20, leading=17)


def build_page():
    rect(0, 0, W, H, PAPER)
    # masthead
    rect(28, 22, W - 56, 5, INK)
    centered(36, "THE WORLD TODAY", 10, INK, bold=True)
    rect(28, 114, W - 56, 3, INK)
    centered(126, "WEDNESDAY 25 NOVEMBER 2026", 4, RED, bold=True)
    centered(162, "THE DAY'S WORLD NEWS IN ONE IMAGE", 2, FAINT)
    rect(28, 186, W - 56, 5, INK)

    # lead story
    draw_text(28, 202, "MIDDLE EAST OIL WAR WIDENS", 2, RED, bold=True)
    wrapped(28, 228, "HOUTHIS HIT SAUDI ARABIA'S BIGGEST REFINERY", 5, INK,
            W - 56, leading=48, bold=True)
    draw_refinery(28, 330, 560, 196)
    wrapped(604, 336,
            "FIRES AT RAS TANURA, THE KINGDOM'S LARGEST REFINERY "
            "(550,000 BARRELS A DAY). SATELLITES SHOW BLACK SMOKE. "
            "SAUDI DEFENCES SAY 4 DRONES WERE DOWNED. RIYADH'S "
            "TALLEST TOWER WAS HIT A DAY EARLIER: 11 WOUNDED. "
            "OIL UP OVER 2%, BRENT OVER $93.",
            2, INK, 392, leading=19)
    rect(28, 538, W - 56, 3, INK)

    # two feature panels
    panel(28, 550, 482, "STRAIT OF HORMUZ", RED,
          "TANKERS HIT NAVAL MINES",
          "IRAN SAYS OIL TANKERS STRUCK MINES, EXPLODED AND CAUGHT "
          "FIRE. AN LNG SHIP WAS ABLAZE BY EVENING. THE CLAIMS "
          "WERE NOT INDEPENDENTLY VERIFIED.",
          draw_tanker)
    panel(514, 550, 482, "TRADE", BLUE,
          "NEW US TARIFFS ON 14 PARTNERS",
          "HEADLINE RATES OF 20-40% ON CHINA, THE EU, JAPAN AND 11 "
          "OTHERS. NO DUTIES BEFORE A JAN 25 HEARING. STOCKS "
          "TUMBLED, THEN TRIMMED LOSSES.",
          draw_chart)

    # three shorter stories
    mini_panel(28, 782, 314, "PACIFIC", GREEN,
               "NO FOREIGN BASE: SOLOMONS PACT",
               "AUSTRALIA NAMED THE SOLOMONS' PRIMARY SECURITY "
               "PARTNER; A$740M PLEDGED OVER 10 YEARS.")
    mini_panel(354, 782, 314, "UKRAINE", BLUE,
               "RUSSIA KILLS 7; KYIV HITS BACK",
               "RUSSIAN DRONES KILL 7 IN 6 REGIONS. KYIV HITS 3 "
               "RUSSIAN REFINERIES, AN AIRFIELD.")
    mini_panel(680, 782, 316, "SUDAN", (150, 90, 20),
               "RSF DRONES KILL 19 CIVILIANS",
               "DRONES HIT HOMES IN DAMAZIN, BLUE NILE STATE; 20 "
               "WOUNDED, A RIGHTS GROUP SAYS.")

    # ticker band
    rect(28, 948, W - 56, 66, INK)
    wrapped(40, 958,
            "BANGLADESH GARMENT WAGE UP 36% TO 17,000 TAKA * COLOMBIA "
            "FREES 30 HOSTAGES IN CARTAGENA * UK ENERGY PRICE CAP UP "
            "26% FROM JANUARY * GAZA STRIKE KILLS HAMAS SECURITY CHIEF",
            2, WHITE, W - 80, leading=18)


def write_png(path):
    raw = bytearray()
    row = W * 3
    for yy in range(H):
        raw.append(0)
        raw += canvas[yy * row:(yy + 1) * row]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    build_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
