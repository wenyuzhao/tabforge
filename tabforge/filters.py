import math
from typing import Callable, Any
import numpy as np


def fmt(x, prec=3, nan="--"):
    if x is None or math.isnan(x):
        return nan
    return "{:.{prec}f}".format(x, prec=prec)


def bold(x):
    return "\\textbf{" + x + "}"


def italic(x):
    return "\\textit{" + x + "}"


def underline(x):
    return "\\underline{" + x + "}"


def emph(x):
    return "\\emph{" + x + "}"


def cancel(x):
    return "\\cancel{" + x + "}"


def vcenter(x):
    return f"\\multicolumn{{1}}{{c}}{{{x}}}"


def hcenter(x):
    return f"\\begin{{tabular}}{{@{{}}c@{{}}}}{{{x}}}\\end{{tabular}}"


def fontsize(size):
    def f(x):
        return f"\\{size}{{{x}}}"

    return f


def textcolor(c):
    def f(x):
        return color(x, c)

    return f


def color(x, color):
    return "{" + f"\\textcolor{{{color}}}" + "{" + x + "}}"


ALL_FILTERS = {
    "fmt": fmt,
    # colors
    "color": color,
    "black": textcolor("black"),
    "blue": textcolor("blue"),
    "brown": textcolor("brown"),
    "cyan": textcolor("cyan"),
    "darkgray": textcolor("darkgray"),
    "gray": textcolor("gray"),
    "green": textcolor("green"),
    "lightgray": textcolor("lightgray"),
    "lime": textcolor("lime"),
    "magenta": textcolor("magenta"),
    "olive": textcolor("olive"),
    "orange": textcolor("orange"),
    "pink": textcolor("pink"),
    "purple": textcolor("purple"),
    "red": textcolor("red"),
    "teal": textcolor("teal"),
    "violet": textcolor("violet"),
    "white": textcolor("white"),
    "yellow": textcolor("yellow"),
    # text styles
    "bold": bold,
    "italic": italic,
    "underline": underline,
    "emph": emph,
    "cancel": cancel,
    # alignment
    "center.v": vcenter,
    "center.h": hcenter,
    # font sizes
    "tiny": fontsize("tiny"),
    "scriptsize": fontsize("scriptsize"),
    "footnotesize": fontsize("footnotesize"),
    "small": fontsize("small"),
    "normalsize": fontsize("normalsize"),
    "large": fontsize("large"),
    "Large": fontsize("Large"),
    "LARGE": fontsize("LARGE"),
    "huge": fontsize("huge"),
    "Huge": fontsize("Huge"),
}
