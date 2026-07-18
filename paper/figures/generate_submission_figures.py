from __future__ import annotations

import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


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


def text_center(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fnt, fill="#111") -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = box[0] + (box[2] - box[0] - (bbox[2] - bbox[0])) / 2
    y = box[1] + (box[3] - box[1] - (bbox[3] - bbox[1])) / 2
    draw.text((x, y), text, font=fnt, fill=fill)


def eca_step(state: list[int], rule: int) -> list[int]:
    nxt = []
    n = len(state)
    for i, c in enumerate(state):
        idx = (state[(i - 1) % n] << 2) | (c << 1) | state[(i + 1) % n]
        nxt.append((rule >> idx) & 1)
    return nxt


def fig1_rule108() -> None:
    width, steps, center = 19, 8, 9
    state = [0] * width
    for pos in (center - 1, center + 1):
        state[pos] = 1
    frames = []
    for _ in range(steps):
        frames.append(state[:])
        state = eca_step(state, 108)

    cell, left, top = 28, 86, 92
    img = Image.new("RGB", (760, 430), "#ffffff")
    draw = ImageDraw.Draw(img)
    title = font(24, True)
    small = font(13)
    draw.text((42, 28), "rule_108 stationary local oscillator", font=title, fill="#111")
    draw.text((42, 58), "Seed #.# alternates with ### on a quiescent background (T=2).", font=small, fill="#333")

    for t, row in enumerate(frames):
        y = top + t * cell
        draw.text((36, y + 6), f"t={t}", font=small, fill="#333")
        for x, value in enumerate(row):
            px = left + x * cell
            fill = "#111827" if value else "#eef0f4"
            draw.rectangle((px, y, px + cell - 2, y + cell - 2), fill=fill)
    draw.rectangle((left + (center - 2) * cell - 3, top - 3, left + (center + 3) * cell, top + steps * cell + 1), outline="#c2410c", width=3)
    draw.text((42, 348), "Orange box marks the active local support used by the stationary oscillator baseline.", font=small, fill="#333")
    img.save(OUT / "fig1_rule108_oscillator.png")


def parse_law_map() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    text = (ROOT / "outputs/world_taxonomy/law_map.md").read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| ")]
    taxonomy = []
    law_rows = []
    mode = None
    headers: list[str] = []
    for line in rows:
        parts = [p.strip() for p in line.strip("|").split("|")]
        if parts[0] == "world" and "category" in parts:
            mode, headers = "taxonomy", parts
            continue
        if parts[0] == "world" and "vel" in parts:
            mode, headers = "laws", parts
            continue
        if parts[0] == "---":
            continue
        if mode == "taxonomy" and len(parts) == len(headers):
            taxonomy.append(dict(zip(headers, parts)))
        elif mode == "laws" and len(parts) == len(headers):
            law_rows.append(dict(zip(headers, parts)))
    return taxonomy, law_rows


def fig2_law_matrix() -> None:
    _, rows = parse_law_map()
    laws = ["vel", "per", "den", "tipo", "compl", "front", "tss"]
    cell_w, cell_h = 48, 26
    left, top = 170, 94
    img = Image.new("RGB", (760, 720), "#ffffff")
    draw = ImageDraw.Draw(img)
    title = font(23, True)
    small = font(12)
    tiny = font(11)
    draw.text((36, 28), "Law coverage matrix for the 20-world atlas", font=title, fill="#111")
    draw.text((36, 58), "Dark = accepted; light = rejected; mid = partial/observer-dependent marker.", font=small, fill="#333")

    for j, law in enumerate(laws):
        text_center(draw, (left + j * cell_w, top - 30, left + (j + 1) * cell_w, top - 4), law, tiny)
    for i, row in enumerate(rows):
        y = top + i * cell_h
        draw.text((28, y + 6), row["world"], font=tiny, fill="#222")
        for j, law in enumerate(laws):
            value = row[law]
            if value == "✓":
                fill, label, color = "#111827", "", "#fff"
            elif value == "·":
                fill, label, color = "#94a3b8", "p", "#111"
            else:
                fill, label, color = "#eef2f7", "", "#111"
            x = left + j * cell_w
            draw.rectangle((x, y, x + cell_w - 3, y + cell_h - 3), fill=fill, outline="#cbd5e1")
            if label:
                text_center(draw, (x, y, x + cell_w - 3, y + cell_h - 3), label, tiny, color)
    img.save(OUT / "fig2_law_coverage_matrix.png")


def fig3_fragility() -> None:
    taxonomy, _ = parse_law_map()
    points = []
    for row in taxonomy:
        if row["fragility_total"] == "n/a" or row["core_fragility"] == "n/a":
            continue
        points.append((row["world"], float(row["fragility_total"]), float(row["core_fragility"]), row["category"]))

    img = Image.new("RGB", (760, 620), "#ffffff")
    draw = ImageDraw.Draw(img)
    title = font(23, True)
    small = font(12)
    tiny = font(10)
    draw.text((42, 28), "Fragility spectrum", font=title, fill="#111")
    draw.text((42, 58), "One-bit IC fragility separates total disruption from core-law disruption.", font=small, fill="#333")
    left, top, w, h = 90, 96, 580, 380
    draw.rectangle((left, top, left + w, top + h), outline="#111", width=2)
    for k in range(6):
        x = left + k * w / 5
        y = top + h - k * h / 5
        draw.line((x, top, x, top + h), fill="#e5e7eb")
        draw.line((left, y, left + w, y), fill="#e5e7eb")
        draw.text((x - 8, top + h + 8), f"{k/5:.1f}", font=tiny, fill="#333")
        draw.text((left - 38, y - 6), f"{k/5:.1f}", font=tiny, fill="#333")
    draw.text((left + 220, top + h + 38), "f_total", font=small, fill="#111")
    draw.text((16, top + 162), "f_core", font=small, fill="#111")
    colors = {
        "frontera-rich-estable": "#2563eb",
        "multiregimen-productivo": "#dc2626",
        "noise-bounded": "#7c3aed",
        "periodicidad-global": "#0f766e",
        "oscilador-local": "#c2410c",
        "sin-evidencia-multiregimen": "#64748b",
        "multiregimen-escala-dependiente": "#ca8a04",
    }
    for name, xval, yval, cat in points:
        x = left + xval * w
        y = top + h - yval * h
        fill = colors.get(cat, "#111")
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=fill, outline="#111")
        if name in {"rule_108", "rule_54", "life_blinker", "rule_208", "rule_209"}:
            draw.text((x + 7, y - 8), name, font=tiny, fill="#111")
    draw.text((42, 570), "Labels show representative extremes; synthetic controls are omitted from the scatter.", font=small, fill="#333")
    img.save(OUT / "fig3_fragility_spectrum.png")


def fig4_anf_gradient() -> None:
    data = json.loads((ROOT / "outputs/periodic_backgrounds_len8/anf_stratification_results.json").read_text(encoding="utf-8"))
    by_dist = data["by_dist"]
    fit = data["monomial_law"]["linear_fit"]
    intercept, slope, r2 = fit["intercept"], fit["slope"], fit["r2"]

    xs = [row["dist"] for row in by_dist]
    ys = [row["log10_monomials_mean"] for row in by_dist]
    ymins = [row["log10_monomials_min"] for row in by_dist]
    ymaxs = [row["log10_monomials_max"] for row in by_dist]
    xmin, xmax = min(xs), max(xs)
    ymin = min(ymins) - 0.15
    ymax = max(ymaxs) + 0.15

    img = Image.new("RGB", (760, 620), "#ffffff")
    draw = ImageDraw.Draw(img)
    title = font(23, True)
    small = font(12)
    tiny = font(10)
    draw.text((42, 28), "ANF monomial gradient in the T=15 causal cone", font=title, fill="#111")
    draw.text((42, 58), f"log10(monomials) = {intercept:.6f} {slope:+.6f} * d, R^2 = {r2:.6f}", font=small, fill="#333")
    left, top, w, h = 90, 112, 580, 360
    draw.rectangle((left, top, left + w, top + h), outline="#111", width=2)

    def sx(x: float) -> float:
        return left + (x - xmin) / (xmax - xmin) * w

    def sy(y: float) -> float:
        return top + h - (y - ymin) / (ymax - ymin) * h

    for k in range(xmin, xmax + 1):
        x = sx(k)
        draw.line((x, top, x, top + h), fill="#eef2f7")
        draw.text((x - 4, top + h + 8), str(k), font=tiny, fill="#333")
    for ytick in range(math.floor(ymin), math.ceil(ymax) + 1):
        y = sy(ytick)
        if y < top or y > top + h:
            continue
        draw.line((left, y, left + w, y), fill="#eef2f7")
        draw.text((left - 32, y - 6), str(ytick), font=tiny, fill="#333")

    fit_points = [(sx(x), sy(intercept + slope * x)) for x in xs]
    draw.line(fit_points, fill="#dc2626", width=3)
    for x, y, ylo, yhi in zip(xs, ys, ymins, ymaxs):
        px, py = sx(x), sy(y)
        draw.line((px, sy(ylo), px, sy(yhi)), fill="#2563eb", width=2)
        draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill="#2563eb", outline="#111")
    draw.text((left + 210, top + h + 42), "distance from defect center (d)", font=small, fill="#111")
    draw.text((15, top + 160), "log10 monomials", font=small, fill="#111")
    draw.text((42, 570), "Blue points: mean by distance with min/max bars. Red line: fitted gradient.", font=small, fill="#333")
    img.save(OUT / "fig4_anf_gradient.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig1_rule108()
    fig2_law_matrix()
    fig3_fragility()
    fig4_anf_gradient()
    print("Generated submission figures: fig1, fig2, fig3, fig4")


if __name__ == "__main__":
    main()
