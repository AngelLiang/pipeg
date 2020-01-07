
import os
import tempfile
try:
    import cyImage as Image
except ImportError:
    import Image


YELLOW, CYAN, BLUE, RED, BLACK = (
    Image.color_for_name(color)
    for color in ("yellow", "cyan", "blue", "red", "black"))


class ImageProxy:
    """
    ImageProxy 的设计方式决定了其首个命令一定是新建图像，所以
    我们采用特殊方式来处理第一天命令：将执行该命令所得的返回值
    保存起来，这个返回值肯定是个 Image.Image 或 cyImage.Image 。
    然后遍历剩下的命令，并依次执行。
    由于执行的都是非绑定方法，所以需要把 image 变量作为首个参数
    （也就是self）传进去。最后调用 Image.save() 方法，保存图像。
    """

    def __init__(self, ImageClass, width=None, height=None, filename=None):
        assert (width is not None and height is not None) or \
            filename is not None
        self.Image = ImageClass
        self.commands = []
        # ImageProxy 的设计方式决定了其首个命令一定是新建图像
        if filename is not None:
            self.load(filename)
        else:
            self.commands = [(self.Image, width, height)]

    def load(self, filename):

        self.commands = [(self.Image, None, None, filename)]

    def save(self, filename=None):
        """
        只有在保存时才创建真正的图像，也只有此时才会有真正的
        处理开销及内存开销。
        """
        command = self.commands.pop(0)
        function, *args = command
        image = function(*args)
        for command in self.commands:
            function, *args = command
            function(image, *args)
        image.save(filename)
        return image

    def set_pixel(self, x, y, color):
        self.commands.append((self.Image.set_pixel, x, y, color))

    def line(self, x0, y0, x1, y1, color):
        self.commands.append((self.Image.line, x0, y0, x1, y1, color))

    def rectangle(self, x0, y0, x1, y1, outline=None, fill=None):
        self.commands.append((self.Image.rectangle, x0, y0, x1, y1,
                              outline, fill))

    def ellipse(self, x0, y0, x1, y1, outline=None, fill=None):
        self.commands.append((self.Image.ellipse, x0, y0, x1, y1,
                              outline, fill))

    # Incomplete API. Unsupported are:
    # pixel(), subsample(), scale(), and size()


def draw_and_save_image(image, filename):
    image.rectangle(0, 0, 299, 59, fill=YELLOW)
    image.ellipse(0, 0, 299, 59, fill=CYAN)
    image.ellipse(60, 20, 120, 40, BLUE, RED)
    image.ellipse(180, 20, 240, 40, BLUE, RED)
    image.rectangle(180, 32, 240, 41, fill=CYAN)
    image.line(181, 32, 239, 32, BLUE)
    image.line(140, 50, 160, 50, BLACK)
    image.save(filename)
    print("saved", filename)


def main():
    filename = os.path.join(tempfile.gettempdir(), "image.xpm")
    image = Image.Image(300, 60)
    draw_and_save_image(image, filename)

    filename = os.path.join(tempfile.gettempdir(), "proxy.xpm")
    image = ImageProxy(Image.Image, 300, 60)
    draw_and_save_image(image, filename)


if __name__ == "__main__":
    main()
