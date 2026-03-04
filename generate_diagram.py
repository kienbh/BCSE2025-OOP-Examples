"""Sinh class diagram cho Flappy Bird game bang matplotlib."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

fig, ax = plt.subplots(figsize=(18, 13))
ax.set_xlim(0, 18)
ax.set_ylim(0, 13)
ax.axis("off")
fig.patch.set_facecolor("#1e1e2e")
ax.set_facecolor("#1e1e2e")

# ── Palette ───────────────────────────────────────────────
C_BASE      = "#89b4fa"   # blue  – base class
C_INHERIT   = "#a6e3a1"   # green – subclasses
C_OTHER     = "#fab387"   # peach – standalone
C_HEADER_BG = "#313244"
C_BODY_BG   = "#1e1e2e"
C_BORDER    = "#6c7086"
C_TEXT      = "#cdd6f4"
C_ATTR      = "#cba6f7"
C_METHOD    = "#89dceb"
C_TITLE     = "#f5c2e7"
C_ARROW_INH = "#f38ba8"   # red   – inheritance
C_ARROW_USE = "#a6e3a1"   # green – uses/association
C_ARROW_AGG = "#fab387"   # peach – aggregation


def draw_class(ax, x, y, w, h, name, attributes, methods,
               color=C_INHERIT, stereotype=None):
    """Ve mot class box theo kieu UML."""
    row_h = 0.38
    header_h = 0.70 if stereotype else 0.55

    # Border
    border = mpatches.FancyBboxPatch(
        (x - 0.04, y - h - 0.04), w + 0.08, h + 0.08,
        boxstyle="round,pad=0.04",
        facecolor=color, edgecolor=color, linewidth=0, zorder=2)
    ax.add_patch(border)

    # Header background
    total_h = header_h + len(attributes) * row_h + 0.05 + len(methods) * row_h + 0.1
    header = mpatches.FancyBboxPatch(
        (x, y - header_h), w, header_h,
        boxstyle="round,pad=0.02",
        facecolor=color, edgecolor="none", linewidth=0, zorder=3)
    ax.add_patch(header)

    # Body background
    body_h = len(attributes) * row_h + 0.05 + len(methods) * row_h + 0.1
    body = mpatches.FancyBboxPatch(
        (x, y - header_h - body_h), w, body_h,
        boxstyle="square,pad=0",
        facecolor=C_HEADER_BG, edgecolor="none", linewidth=0, zorder=3)
    ax.add_patch(body)

    # Main border
    full = mpatches.FancyBboxPatch(
        (x, y - h), w, h,
        boxstyle="round,pad=0.02",
        facecolor="none", edgecolor=color, linewidth=1.5, zorder=4)
    ax.add_patch(full)

    # Stereotype
    ty = y - 0.18
    if stereotype:
        ax.text(x + w / 2, ty, f"«{stereotype}»",
                ha="center", va="center", fontsize=7,
                color=C_BODY_BG, fontweight="normal",
                fontfamily="monospace", zorder=5)
        ty -= 0.22

    # Class name
    ax.text(x + w / 2, ty, name,
            ha="center", va="center", fontsize=9.5,
            color=C_BODY_BG, fontweight="bold",
            fontfamily="monospace", zorder=5)

    # Divider 1
    div_y = y - header_h
    ax.plot([x + 0.05, x + w - 0.05], [div_y, div_y],
            color=color, linewidth=0.8, zorder=5)

    # Attributes
    for i, attr in enumerate(attributes):
        ay = div_y - 0.08 - (i + 0.5) * row_h
        ax.text(x + 0.15, ay, attr,
                ha="left", va="center", fontsize=7.2,
                color=C_ATTR, fontfamily="monospace", zorder=5)

    # Divider 2
    div2_y = div_y - len(attributes) * row_h - 0.05
    ax.plot([x + 0.05, x + w - 0.05], [div2_y, div2_y],
            color=color, linewidth=0.8, zorder=5)

    # Methods
    for i, meth in enumerate(methods):
        my = div2_y - 0.08 - (i + 0.5) * row_h
        ax.text(x + 0.15, my, meth,
                ha="left", va="center", fontsize=7.2,
                color=C_METHOD, fontfamily="monospace", zorder=5)

    # Return center-bottom and center-top for arrows
    cx = x + w / 2
    return {"top": (cx, y), "bottom": (cx, y - h),
            "left": (x, y - h / 2), "right": (x + w, y - h / 2)}


def arrow(ax, start, end, color, style="inherit", label=""):
    """Ve mui ten giua hai diem."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    if style == "inherit":
        arrowprops = dict(arrowstyle="-|>", color=color,
                          lw=1.8, mutation_scale=14)
    elif style == "dashed":
        arrowprops = dict(arrowstyle="-|>", color=color,
                          lw=1.4, mutation_scale=12,
                          linestyle="dashed")
    else:
        arrowprops = dict(arrowstyle="-", color=color,
                          lw=1.2, linestyle="dashed")

    ax.annotate("", xy=end, xytext=start,
                arrowprops=arrowprops, zorder=6)
    if label:
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(mx + 0.08, my, label, fontsize=7,
                color=color, fontfamily="monospace", zorder=7)


# ══════════════════════════════════════════════════════════
# DEFINE CLASSES
# ══════════════════════════════════════════════════════════

classes = {}

# 1. GameObject (abstract base)
classes["GameObject"] = draw_class(
    ax, 6.8, 12.6, 4.4, 2.1,
    "GameObject",
    ["# _x: float", "# _y: float", "# _w: int", "# _h: int"],
    ["+ rect: Rect  «property»", "# draw(surface)  «abstract»", "# update()"],
    color=C_BASE, stereotype="abstract"
)

# 2. Bird
classes["Bird"] = draw_class(
    ax, 0.4, 9.8, 4.2, 3.2,
    "Bird",
    ["# _vel_y: float", "# _alive: bool",
     "# _wing_state: int", "# _rotation: float"],
    ["+ jump()", "+ kill()", "+ alive «property»",
     "+ center «property»", "+ get_mask(): Mask",
     "# update()", "# draw(surface)"],
    color=C_INHERIT
)

# 3. Pipe
classes["Pipe"] = draw_class(
    ax, 5.2, 9.8, 4.2, 2.8,
    "Pipe",
    ["# _gap_y: int", "# _passed: bool",
     "  PIPE_W: int = 60"],
    ["+ passed «property»", "+ off_screen «property»",
     "+ get_rects(): tuple", "# update()", "# draw(surface)"],
    color=C_INHERIT
)

# 4. Ground
classes["Ground"] = draw_class(
    ax, 10.0, 9.8, 3.8, 2.4,
    "Ground",
    ["# _scroll: int", "  H: int = 80"],
    ["+ top «property»", "# update()", "# draw(surface)"],
    color=C_INHERIT
)

# 5. Background
classes["Background"] = draw_class(
    ax, 14.0, 9.8, 3.8, 2.2,
    "Background",
    ["# _clouds: list[dict]"],
    ["# update()", "# draw(surface)",
     "# _draw_cloud(...)"],
    color=C_INHERIT
)

# 6. Particle (standalone)
classes["Particle"] = draw_class(
    ax, 0.4, 5.6, 3.6, 2.8,
    "Particle",
    ["+ x, y: float", "+ vx, vy: float",
     "+ life: int", "+ color: tuple", "+ size: int"],
    ["+ update()", "+ draw(surface)"],
    color=C_OTHER
)

# 7. ScoreDisplay (standalone)
classes["ScoreDisplay"] = draw_class(
    ax, 4.6, 5.6, 4.0, 2.6,
    "ScoreDisplay",
    ["# _font_big: Font",
     "# _font_med: Font", "# _font_small: Font"],
    ["+ draw_score(surface, score)",
     "+ draw_best(surface, best)",
     "+ draw_panel(surface, score, best, state)",
     "+ draw_start(surface)"],
    color=C_OTHER
)

# 8. Game (controller)
classes["Game"] = draw_class(
    ax, 9.2, 5.8, 5.0, 3.6,
    "Game",
    ["# _bird: Bird", "# _pipes: list[Pipe]",
     "# _ground: Ground", "# _bg: Background",
     "# _particles: list[Particle]",
     "# _score_display: ScoreDisplay",
     "# _score, _best_score: int",
     "# _state: str"],
    ["+ run()", "# _reset()", "# _handle_events()",
     "# _update()", "# _draw()", "# _spawn_pipe()"],
    color=C_BASE
)

# ══════════════════════════════════════════════════════════
# ARROWS
# ══════════════════════════════════════════════════════════

base_bot = classes["GameObject"]["bottom"]

# Inheritance: Bird -> GameObject
arrow(ax, classes["Bird"]["top"],
      (base_bot[0] - 1.8, base_bot[1]),
      C_ARROW_INH, "inherit")

# Inheritance: Pipe -> GameObject
arrow(ax, classes["Pipe"]["top"],
      (base_bot[0] - 0.3, base_bot[1]),
      C_ARROW_INH, "inherit")

# Inheritance: Ground -> GameObject
arrow(ax, classes["Ground"]["top"],
      (base_bot[0] + 1.0, base_bot[1]),
      C_ARROW_INH, "inherit")

# Inheritance: Background -> GameObject
arrow(ax, classes["Background"]["top"],
      (base_bot[0] + 2.5, base_bot[1]),
      C_ARROW_INH, "inherit")

# Game aggregates Bird
arrow(ax, (classes["Game"]["left"][0], classes["Game"]["left"][1] + 0.6),
      classes["Bird"]["right"],
      C_ARROW_AGG, "dashed", "uses")

# Game aggregates Pipe
arrow(ax, (classes["Game"]["left"][0], classes["Game"]["left"][1] + 0.1),
      classes["Pipe"]["right"],
      C_ARROW_AGG, "dashed", "uses")

# Game aggregates Ground
arrow(ax, classes["Game"]["top"],
      classes["Ground"]["bottom"],
      C_ARROW_AGG, "dashed", "uses")

# Game aggregates Background
arrow(ax, (classes["Game"]["right"][0], classes["Game"]["right"][1] + 0.5),
      classes["Background"]["bottom"],
      C_ARROW_AGG, "dashed", "uses")

# Game uses Particle
arrow(ax, (classes["Game"]["left"][0], classes["Game"]["left"][1] - 0.5),
      classes["Particle"]["right"],
      C_ARROW_USE, "dashed", "uses")

# Game uses ScoreDisplay
arrow(ax, classes["Game"]["bottom"],
      classes["ScoreDisplay"]["top"],
      C_ARROW_USE, "dashed", "uses")

# ══════════════════════════════════════════════════════════
# LEGEND
# ══════════════════════════════════════════════════════════

legend_x, legend_y = 14.2, 4.6
ax.text(legend_x, legend_y, "Legend", fontsize=9,
        color=C_TEXT, fontweight="bold", fontfamily="monospace")

items = [
    (C_BASE,      "Abstract / Controller class"),
    (C_INHERIT,   "Subclass (extends GameObject)"),
    (C_OTHER,     "Standalone class"),
    (C_ARROW_INH, "── Inheritance"),
    (C_ARROW_AGG, "- - Association / Uses"),
]
for i, (c, lbl) in enumerate(items):
    iy = legend_y - 0.45 * (i + 1)
    rect = mpatches.FancyBboxPatch(
        (legend_x, iy - 0.13), 0.28, 0.26,
        boxstyle="round,pad=0.02",
        facecolor=c, edgecolor="none", zorder=5)
    ax.add_patch(rect)
    ax.text(legend_x + 0.4, iy, lbl, fontsize=7.5,
            color=C_TEXT, va="center", fontfamily="monospace")

# ══════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════

ax.text(9, 12.85, "Flappy Bird — Class Diagram (OOP Demo)",
        ha="center", va="center", fontsize=14,
        color=C_TITLE, fontweight="bold", fontfamily="monospace")

ax.text(9, 12.5, "Inheritance  •  Encapsulation  •  Polymorphism  •  Abstraction",
        ha="center", va="center", fontsize=8.5,
        color="#6c7086", fontfamily="monospace")

plt.tight_layout(pad=0.3)
out = "/Users/buihuykien/Desktop/OOP2025/Examples/class_diagram.png"
plt.savefig(out, dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print(f"Saved: {out}")
