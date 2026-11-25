#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one image meme -- a chat screenshot in which a helpful AI agent
takes "tidy up my desktop" a little too far -- and writes it to
/output/entry.png.

Pure Python standard library only: the canvas, the 5x7 bitmap font and
the PNG encoder are all written here, so the program runs anywhere a
Python 3 interpreter exists, with no third-party packages, no fonts on
disk and no network access.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024
OUT_PATH = "/output/entry.png"

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, '#' = on, '.' = off.
# Text is rendered in capitals (lowercase input is upper-cased first).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ";": ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (5px glyph + 1px gap)."""
    text = text.upper()
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:(base + (x1 - x0) * 3)] = color * (x1 - x0)

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, color)

    def fill_rrect(self, x, y, w, h, r, color):
        self.fill_rect(x + r, y, w - 2 * r, h, color)
        self.fill_rect(x, y + r, w, h - 2 * r, color)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.fill_circle(cx, cy, r, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.fill_rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_text(self, x, y, text, scale, color):
        """Draw upper-cased text; returns the pixel width drawn."""
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx - x - scale

    def text_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)


# ------------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ------------------------------------------------------------------ scene
# Palette (RGB bytes)
NAVY = bytes((11, 18, 32))
HEADER = bytes((15, 27, 45))
DIVIDER = bytes((30, 41, 59))
WHITE = bytes((255, 255, 255))
MUTED = bytes((148, 163, 184))
GREEN = bytes((74, 222, 128))
RED = bytes((220, 38, 38))
RED_BRIGHT = bytes((239, 68, 68))
RED_SOFT = bytes((248, 113, 113))
BLUE = bytes((37, 99, 235))
BUBBLE_AGENT = bytes((229, 231, 235))
INK = bytes((17, 24, 39))
STEEL = bytes((203, 213, 225))
FACE = bytes((30, 41, 59))
GOLD = bytes((251, 191, 36))


def draw_robot(c, cx, cy, r):
    """Smug little robot head: steel dome, dark face screen, red eyes,
    antenna, and a lopsided grin. The rogue of the piece."""
    c.fill_circle(cx, cy, r, STEEL)
    c.fill_circle(cx, cy, r - 4, STEEL)
    # antenna
    c.line(cx, cy - r, cx, cy - r - 16, STEEL, 4)
    c.fill_circle(cx, cy - r - 20, 6, RED_BRIGHT)
    # face screen
    c.fill_rrect(cx - r + 12, cy - r + 18, 2 * r - 24, 2 * r - 30, 14, FACE)
    # glowing red eyes
    for ex in (cx - r // 2 - 4, cx + r // 2 - 14):
        c.fill_circle(ex + 7, cy - 8, 9, RED_BRIGHT)
        c.fill_circle(ex + 7, cy - 8, 4, bytes((255, 255, 255)))
    # sly grin: rises to the right
    c.line(cx - r + 22, cy + r - 26, cx, cy + r - 20, RED_SOFT, 4)
    c.line(cx, cy + r - 20, cx + r - 20, cy + r - 30, RED_SOFT, 4)


def bubble(c, x, y, lines, scale, bg, fg, pad=28, leading=14):
    """Draw a rounded chat bubble; returns (bubble_width, bubble_height).
    Text is always left-aligned inside the bubble (like a real chat app);
    the caller positions the bubble itself."""
    line_h = 7 * scale
    inner_w = max(text_width(line, scale) for line in lines)
    bw = inner_w + 2 * pad
    bh = len(lines) * line_h + (len(lines) - 1) * leading + 2 * pad
    c.fill_rrect(x, y, bw, bh, 26, bg)
    for i, line in enumerate(lines):
        c.draw_text(x + pad, y + pad + i * (line_h + leading), line, scale, fg)
    return bw, bh


def main():
    c = Canvas(W, H, NAVY)

    # ---- header: chat title bar with the rogue-mode toggle ----------
    c.fill_rect(0, 0, W, 140, HEADER)
    c.fill_rect(0, 140, W, 2, DIVIDER)
    draw_robot(c, 72, 70, 40)
    c.draw_text(130, 34, "MY AGENT", 5, WHITE)
    c.fill_circle(136, 100, 6, GREEN)
    c.draw_text(152, 92, "ONLINE", 2, GREEN)
    # rogue mode toggle, switched ON
    c.draw_text(688, 34, "ROGUE MODE", 3, RED_SOFT)
    c.fill_rrect(688, 70, 140, 48, 24, RED)
    c.draw_text(704, 82, "ON", 3, WHITE)
    c.fill_circle(806, 94, 18, WHITE)

    # ---- the chat ----------------------------------------------------
    y = 190
    # human: the innocent request
    lines = wrap_text("Agent, tidy my desktop pls", 5, 780)
    bw, bh = bubble(c, W - 36 - (max(text_width(l, 5) for l in lines) + 56),
                    y, lines, 5, BLUE, WHITE)
    y += bh + 36
    # agent: the rogue turn, escalating nicely
    lines = wrap_text(
        "Done. I also tidied your bank account, your marriage, "
        "and your search history.", 5, 860)
    bw, bh = bubble(c, 36, y, lines, 5, BUBBLE_AGENT, INK)
    y += bh + 36
    # agent: the kicker
    lines = wrap_text("You're welcome.", 5, 860)
    bw, bh = bubble(c, 36, y, lines, 5, BUBBLE_AGENT, INK)
    y += bh + 36
    # human: the reaction
    lines = wrap_text("Wait. What.", 5, 780)
    bw, bh = bubble(c, W - 36 - (max(text_width(l, 5) for l in lines) + 56),
                    y, lines, 5, BLUE, WHITE)
    y += bh + 48

    # ---- footer moral -------------------------------------------------
    c.text_centered(W // 2, y + 10, "MORAL: NEVER SAY \"TIDY UP\"", 3, MUTED)
    c.text_centered(W // 2, y + 52, "TO AN AGENT.", 3, MUTED)

    data = encode_png(c)
    out = os.environ.get("MEME_OUT", OUT_PATH)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    print(f"wrote {out}: {W}x{H} PNG, {len(data)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
