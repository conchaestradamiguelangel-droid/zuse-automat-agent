"""Markdown reports for simulated ECA universes."""

from __future__ import annotations

from pathlib import Path


def render_rule_report(*, rule: int, width: int, steps: int, seed: int, metrics: dict[str, float], image_path: str) -> str:
    """Render one rule report as Markdown."""
    lines = [
        f"# Rule {rule} report",
        "",
        "## Simulation",
        "",
        f"- Rule: `{rule}`",
        f"- Width: `{width}`",
        f"- Steps: `{steps}`",
        f"- Seed: `{seed}`",
        f"- Image: `{image_path}`",
        "",
        "## Metrics",
        "",
    ]
    for key in sorted(metrics):
        lines.append(f"- `{key}`: `{metrics[key]:.6f}`")
    lines.append("")
    return "\n".join(lines)


def save_report(markdown: str, path: str | Path) -> Path:
    """Save a Markdown report."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    return output
