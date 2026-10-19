"""
Interactive placement of ROI pairs.

Per pair:
  1st left click  -> INSIDE (on-vessel) ROI, label 2r-1 (denominator)
  move the mouse  -> the OUTSIDE ROI preview follows, locked on a ring at
                     `distance` (center to center) around the first ROI
  2nd left click  -> OUTSIDE (background) ROI, label 2r (numerator)

Keys / buttons:
  Enter                    finish this image
  Right click / Backspace  undo (cancels a pending first click, else removes last pair)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from skimage.draw import disk as draw_disk


def select_roi_pairs(img, radius, distance, title="", max_pairs=0):
    """Returns an int32 label image: pair r has inside = 2r-1, outside = 2r."""
    shape = img.shape[:2]
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.imshow(img, cmap="gist_gray")
    ax.set_title(title + "\nClick 1: INSIDE (vessel) | Click 2: OUTSIDE (background) | "
                 "Enter: finish | Right click/Backspace: undo")

    state = {"first": None, "pairs": [], "preview": None}
    artists = []  # permanent artists, one list of artists per pair

    def second_center(first, x, y):
        dx, dy = x - first[0], y - first[1]
        n = np.hypot(dx, dy)
        if n == 0:
            return None
        return (first[0] + distance * dx / n, first[1] + distance * dy / n)

    def clear_pending():
        for a in state.get("pending_artists", []):
            a.remove()
        state["pending_artists"] = []
        state["preview"] = None

    def draw_pending(x=None, y=None):
        clear_pending()
        if state["first"] is None:
            # preview of the inside ROI following the mouse, before the first click
            if x is not None:
                prev = Circle((x, y), radius, fill=False, ec="lime", ls=":", lw=1)
                ax.add_patch(prev)
                state["pending_artists"] = [prev]
            return
        f = state["first"]
        arts = [
            Circle(f, radius, fill=False, ec="lime", lw=1),
            Circle(f, distance, fill=False, ec="yellow", ls="--", lw=1),
        ]
        if x is not None:
            c = second_center(f, x, y)
            if c is not None:
                state["preview"] = c
                arts.append(Circle(c, radius, fill=False, ec="red", ls=":", lw=1))
        for a in arts:
            ax.add_patch(a)
        state["pending_artists"] = arts

    def redraw_pairs():
        for group in artists:
            for a in group:
                a.remove()
        artists.clear()
        for k, (c1, c2) in enumerate(state["pairs"], start=1):
            group = [
                Circle(c1, radius, fill=False, ec="lime", lw=1),
                Circle(c2, radius, fill=False, ec="red", lw=1),
            ]
            for a in group:
                ax.add_patch(a)
            group.append(ax.text(c1[0], c1[1], str(k), color="lime", ha="center", va="center"))
            group.append(ax.text(c2[0], c2[1], str(k), color="red", ha="center", va="center"))
            artists.append(group)

    def on_move(event):
        if event.inaxes is not ax:
            return
        draw_pending(event.xdata, event.ydata)
        fig.canvas.draw_idle()

    def undo():
        if state["first"] is not None:
            state["first"] = None
            clear_pending()
        elif state["pairs"]:
            state["pairs"].pop()
            redraw_pairs()
        fig.canvas.draw_idle()

    def on_click(event):
        if event.inaxes is not ax:
            return
        if event.button == 3:
            undo()
            return
        if event.button != 1:
            return
        if state["first"] is None:
            state["first"] = (event.xdata, event.ydata)
            draw_pending()
        else:
            c = second_center(state["first"], event.xdata, event.ydata)
            if c is None:
                return
            state["pairs"].append((state["first"], c))
            state["first"] = None
            clear_pending()
            redraw_pairs()
            if max_pairs and len(state["pairs"]) >= max_pairs:
                plt.close(fig)
                return
        fig.canvas.draw_idle()

    def on_key(event):
        if event.key == "enter":
            plt.close(fig)
        elif event.key == "backspace":
            undo()

    fig.canvas.mpl_connect("motion_notify_event", on_move)
    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show(block=True)

    # Build the label image (pending, unfinished pairs are ignored)
    labels = np.zeros(shape, dtype=np.int32)
    for k, (c1, c2) in enumerate(state["pairs"], start=1):
        rr, cc = draw_disk((c1[1], c1[0]), radius, shape=shape)
        labels[rr, cc] = 2 * k - 1  # inside, denominator
        rr, cc = draw_disk((c2[1], c2[0]), radius, shape=shape)
        labels[rr, cc] = 2 * k      # outside, numerator
    return labels
