from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont


WIDTH = 21
STEPS = 8
CENTER = 10
WINDOW_RADIUS = 6
CELL = 26
PANEL_GAP = 58
TOP = 86
LEFT = 52
OUT_PATH = Path(__file__).with_name("fig6_moving_oscillator.png")


def eca_step(state: list[int], rule: int) -> list[int]:
    """One periodic-boundary ECA step using Wolfram bit order."""
    nxt = []
    for i, value in enumerate(state):
        left = state[(i - 1) % WIDTH]
        right = state[(i + 1) % WIDTH]
        idx = (left << 2) | (value << 1) | right
        nxt.append((rule >> idx) & 1)
    return nxt


def simulate(rule: int) -> list[list[int]]:
    state = [0] * WIDTH
    state[CENTER] = 1
    frames = []
    for _ in range(STEPS):
        frames.append(state[:])
        state = eca_step(state, rule)
    return frames


def fixed_window(frames: list[list[int]]) -> list[list[int]]:
    """Fixed window around the initial active cell so translation remains visible."""
    cols = [(CENTER + offset) % WIDTH for offset in range(-WINDOW_RADIUS, WINDOW_RADIUS + 1)]
    return [[row[col] for col in cols] for row in frames]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill: str) -> None:
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - (bbox[2] - bbox[0]) / 2, y), text, font=fnt, fill=fill)


def draw_panel(
    draw: ImageDraw.ImageDraw,
    data: list[list[int]],
    x0: int,
    title: str,
    title_font,
    label_font,
) -> None:
    panel_width = (2 * WINDOW_RADIUS + 1) * CELL
    draw_centered(draw, (x0 + panel_width // 2, 48), title, title_font, "#111111")

    for t, row in enumerate(data):
        y = TOP + t * CELL
        draw.text((x0 - 36, y + 6), f"t={t}", font=label_font, fill="#333333")
        for j, value in enumerate(row):
            x = x0 + j * CELL
            fill = "#1a1a2e" if value else "#e8e8f0"
            draw.rectangle((x, y, x + CELL - 2, y + CELL - 2), fill=fill)

    # Thin period guides after t=2,4,6.
    for t in (2, 4, 6):
        y = TOP + t * CELL - 4
        draw.line((x0, y, x0 + panel_width - 2, y), fill="#c45850", width=2)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rule20 = fixed_window(simulate(20))
    rule6 = fixed_window(simulate(6))

    panel_width = (2 * WINDOW_RADIUS + 1) * CELL
    width = LEFT * 2 + panel_width * 2 + PANEL_GAP
    height = TOP + STEPS * CELL + 148

    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    title_font = font(24, bold=True)
    panel_title_font = font(18, bold=True)
    label_font = font(12)
    foot_font = font(13)

    draw_centered(
        draw,
        (width // 2, 12),
        "Figure 6. Moving oscillator (glider) -- period T=2, speed 1",
        title_font,
        "#111111",
    )

    draw_panel(draw, rule20, LEFT, "rule_20  (drift +2)", panel_title_font, label_font)
    draw_panel(
        draw,
        rule6,
        LEFT + panel_width + PANEL_GAP,
        "rule_6  (drift -2)",
        panel_title_font,
        label_font,
    )

    footnote = (
        "Left: rule_20 (right-moving, drift +2 per period). Right: rule_6 "
        "(left-moving, drift -2 per period). Active cells dark; quiescent "
        "background light. Rows are time steps t=0..7. The oscillator alternates "
        "[0] <-> [0,1] while translating one cell per step."
    )
    wrapped = "\n".join(textwrap.wrap(footnote, width=110))
    draw.multiline_text((LEFT, height - 112), wrapped, font=foot_font, fill="#222222", spacing=4)

    image.save(OUT_PATH)


if __name__ == "__main__":
    main()
