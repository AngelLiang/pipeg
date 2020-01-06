
import abc
import os
import re
import tempfile
import tkinter as tk
import Qtrac


@Qtrac.has_methods("initialize", "draw_caption", "draw_bar", "finalize")
class BarRenderer(metaclass=abc.ABCMeta):
    pass


class BarCharter:

    def __init__(self, renderer):
        self.__renderer = renderer

    def render(self, caption, pairs):
        maximum = max(value for _, value in pairs)
        self.__renderer.initialize(len(pairs), maximum)
        self.__renderer.draw_caption(caption)
        for name, value in pairs:
            self.__renderer.draw_bar(name, value)
        self.__renderer.finalize()


class TextBarRenderer:

    def __init__(self, scaleFactor=40):
        self.scaleFactor = scaleFactor

    def initialize(self, bars, maximum):
        assert bars > 0 and maximum > 0
        self.scale = self.scaleFactor / maximum

    def draw_caption(self, caption):
        print("{0:^{2}}\n{1:^{2}}".format(caption, "=" * len(caption),
                                          self.scaleFactor))

    def draw_bar(self, name, value):
        print("{} {}".format("*" * int(value * self.scale), name))

    def finalize(self):
        pass


class ImageBarRenderer:

    COLORS = ("red", "green", "blue", "yellow", "magenta", "cyan")

    def __init__(self, stepHeight=10, barWidth=30, barGap=2):
        self.stepHeight = stepHeight
        self.barWidth = barWidth
        self.barGap = barGap

    def initialize(self, bars, maximum):
        assert bars > 0 and maximum > 0
        if tk._default_root is None:
            self.gui = tk.Tk()
            self.inGui = False
        else:
            self.gui = tk._default_root
            self.inGui = True
        self.index = 0
        self.width = bars * (self.barWidth + self.barGap)
        self.height = maximum * self.stepHeight
        self.image = tk.PhotoImage(width=self.width, height=self.height)
        self.image.put("white", (0, 0, self.width, self.height))

    def draw_caption(self, caption):
        self.filename = os.path.join(tempfile.gettempdir(),
                                     re.sub(r"\W+", "_", caption) + ".gif")

    def draw_bar(self, name, value):
        color = ImageBarRenderer.COLORS[self.index %
                                        len(ImageBarRenderer.COLORS)]
        x0 = self.index * (self.barWidth + self.barGap)
        x1 = x0 + self.barWidth
        y0 = self.height - (value * self.stepHeight)
        y1 = self.height - 1
        self.image.put(color, (x0, y0, x1, y1))
        self.index += 1

    def finalize(self):
        self.image.write(self.filename, "gif")
        print("wrote", self.filename)
        if not self.inGui:
            self.gui.quit()


def main():
    pairs = (("Mon", 16), ("Tue", 17), ("Wed", 19), ("Thu", 22),
             ("Fri", 24), ("Sat", 21), ("Sun", 19))
    textBarCharter = BarCharter(TextBarRenderer())
    textBarCharter.render("Forecast 6/8", pairs)
    imageBarCharter = BarCharter(ImageBarRenderer())
    imageBarCharter.render("Forecast 6/8", pairs)


if __name__ == "__main__":
    main()
