"""
Tiny pure-Python RGB drawing canvas with PNG export and a built-in 5x7 bitmap
font. No external dependencies (uses only zlib + struct from the stdlib).

Created because matplotlib/PIL are not installable in this offline sandbox, yet
the thesis needs real embedded figures.

Capabilities: pixels, lines, rectangles (outline + filled), circles, polylines,
and scalable text. Coordinates are (x, y) with origin at the top-left.
"""

import struct
import zlib

# ---------------------------------------------------------------------------
# 5x7 bitmap font.  Each glyph = 7 rows of 5 columns ('#' = on).
# ---------------------------------------------------------------------------
_F = {
    "0": [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "  ## ", " #   ", "#    ", "#####"],
    "3": ["#####", "    #", "   # ", "  ## ", "    #", "#   #", " ### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ### "],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": [" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "J": ["  ###", "   # ", "   # ", "   # ", "#  # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "#   #", "# # #", "## ##", "#   #"],
    "X": ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "a": ["     ", "     ", " ### ", "    #", " ####", "#   #", " ####"],
    "b": ["#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "],
    "c": ["     ", "     ", " ####", "#    ", "#    ", "#    ", " ####"],
    "d": ["    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"],
    "e": ["     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "],
    "f": ["  ## ", " #  #", " #   ", "###  ", " #   ", " #   ", " #   "],
    "g": ["     ", " ####", "#   #", "#   #", " ####", "    #", " ### "],
    "h": ["#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#   #"],
    "i": ["  #  ", "     ", " ##  ", "  #  ", "  #  ", "  #  ", " ### "],
    "j": ["   # ", "     ", "  ## ", "   # ", "   # ", "#  # ", " ##  "],
    "k": ["#    ", "#    ", "#  # ", "# #  ", "##   ", "# #  ", "#  # "],
    "l": [" ##  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "m": ["     ", "     ", "## # ", "# # #", "# # #", "# # #", "#   #"],
    "n": ["     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"],
    "o": ["     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "],
    "p": ["     ", "#### ", "#   #", "#   #", "#### ", "#    ", "#    "],
    "q": ["     ", " ####", "#   #", "#   #", " ####", "    #", "    #"],
    "r": ["     ", "     ", "# ## ", "##  #", "#    ", "#    ", "#    "],
    "s": ["     ", "     ", " ####", "#    ", " ### ", "    #", "#### "],
    "t": [" #   ", " #   ", "###  ", " #   ", " #   ", " #  #", "  ## "],
    "u": ["     ", "     ", "#   #", "#   #", "#   #", "#   #", " ####"],
    "v": ["     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "w": ["     ", "     ", "#   #", "#   #", "# # #", "# # #", " # # "],
    "x": ["     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"],
    "y": ["     ", "#   #", "#   #", "#   #", " ####", "    #", " ### "],
    "z": ["     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"],
    " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
    ".": ["     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "],
    ",": ["     ", "     ", "     ", "     ", " ##  ", "  #  ", " #   "],
    "-": ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
    "/": ["    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "],
    ":": ["     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "],
    "%": ["##  #", "##  #", "   # ", "  #  ", " #   ", "#  ##", "#  ##"],
    "(": ["  #  ", " #   ", "#    ", "#    ", "#    ", " #   ", "  #  "],
    ")": ["  #  ", "   # ", "    #", "    #", "    #", "   # ", "  #  "],
    "+": ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "],
    "=": ["     ", "     ", "#####", "     ", "#####", "     ", "     "],
}
GLYPH_W, GLYPH_H = 5, 7


class Canvas:
    def __init__(self, width, height, bg=(255, 255, 255)):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    # -- primitives --------------------------------------------------------
    def set(self, x, y, color):
        x = int(x); y = int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]; self.px[i + 1] = color[1]; self.px[i + 2] = color[2]

    def hline(self, x0, x1, y, color):
        if x1 < x0:
            x0, x1 = x1, x0
        for x in range(int(x0), int(x1) + 1):
            self.set(x, y, color)

    def vline(self, x, y0, y1, color):
        if y1 < y0:
            y0, y1 = y1, y0
        for y in range(int(y0), int(y1) + 1):
            self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx = abs(x1 - x0); dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for ox in range(width):
                for oy in range(width):
                    self.set(x0 + ox, y0 + oy, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def rect(self, x, y, w, h, color, width=1):
        for i in range(width):
            self.hline(x, x + w, y + i, color)
            self.hline(x, x + w, y + h - i, color)
            self.vline(x + i, y, y + h, color)
            self.vline(x + w - i, y, y + h, color)

    def fill_rect(self, x, y, w, h, color):
        for yy in range(int(y), int(y + h)):
            self.hline(x, x + w, yy, color)

    def circle(self, cx, cy, r, color, fill=False):
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, color)
                else:
                    if (r - 1) ** 2 <= d2 <= r * r:
                        self.set(xx, yy, color)

    def polyline(self, points, color, width=2):
        for i in range(len(points) - 1):
            x0, y0 = points[i]; x1, y1 = points[i + 1]
            self.line(x0, y0, x1, y1, color, width=width)

    # -- text --------------------------------------------------------------
    def text(self, x, y, s, color=(0, 0, 0), scale=2):
        cx = int(x)
        for ch in s:
            glyph = _F.get(ch, _F.get(ch.upper(), _F[" "]))
            for ry, row in enumerate(glyph):
                for rx, c in enumerate(row):
                    if c == "#":
                        self.fill_rect(cx + rx * scale, int(y) + ry * scale,
                                       scale, scale, color)
            cx += (GLYPH_W + 1) * scale
        return cx

    def text_w(self, s, scale=2):
        return len(s) * (GLYPH_W + 1) * scale

    def text_center(self, cx, y, s, color=(0, 0, 0), scale=2):
        self.text(cx - self.text_w(s, scale) // 2, y, s, color, scale)

    def text_right(self, x, y, s, color=(0, 0, 0), scale=2):
        self.text(x - self.text_w(s, scale), y, s, color, scale)

    # -- export ------------------------------------------------------------
    def save_png(self, path):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter type 0
            raw.extend(self.px[y * stride:(y + 1) * stride])
        comp = zlib.compress(bytes(raw), 9)

        def chunk(tag, data):
            c = struct.pack(">I", len(data)) + tag + data
            c += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
            return c

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", comp)
        png += chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)
        return path


def png_size(path):
    """Return (width, height) of a PNG by reading its IHDR chunk."""
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">I", head[16:20])[0], struct.unpack(">I", head[20:24])[0]


if __name__ == "__main__":
    c = Canvas(320, 80)
    c.rect(0, 0, 319, 79, (0, 0, 0))
    c.text(10, 12, "Font test 0123 ABCxyz", (20, 20, 120), 3)
    c.text(10, 45, "Accuracy / F1-score %", (180, 30, 30), 2)
    c.save_png("tools/_fonttest.png")
    print("wrote tools/_fonttest.png", png_size("tools/_fonttest.png"))
