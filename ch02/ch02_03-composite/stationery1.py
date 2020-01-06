
import abc
import sys


class AbstractItem(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def composite(self):
        """要求所有子类对象能汇报自己是不是组合体"""
        pass

    def __iter__(self):
        """要求子类对象必须可迭代"""
        return iter([])


class SimpleItem(AbstractItem):

    def __init__(self, name, price=0.00):
        self.name = name
        self.price = price

    @property
    def composite(self):
        return False

    def print(self, indent="", file=sys.stdout):
        print("{}${:.2f} {}".format(indent, self.price, self.name),
              file=file)


class AbstractCompositeItem(AbstractItem):
    """实现了组合体所需的添加（add），移除（remove）和迭代（iter）等功能"""

    def __init__(self, *items):
        self.children = []
        if items:
            self.add(*items)

    def add(self, first, *items):
        """添加功能"""
        self.children.append(first)
        if items:
            self.children.extend(items)

    def remove(self, item):
        """移除功能"""
        self.children.remove(item)

    def __iter__(self):
        """迭代功能"""
        return iter(self.children)


class CompositeItem(AbstractCompositeItem):

    def __init__(self, name, *items):
        super().__init__(*items)
        self.name = name

    @property
    def composite(self):
        return True

    @property
    def price(self):

        # 递归计算子对象的价格
        # for item in self 表达式使得 Python 调用 iter(self) 来获取针对
        # self 的迭代器，而这又会调用 __iter__() 特殊方法，该方法返回指向
        # self.children 的迭代器。
        return sum(item.price for item in self)

    def print(self, indent="", file=sys.stdout):
        print("{}${:.2f} {}".format(indent, self.price, self.name),
              file=file)
        for child in self:
            child.print(indent + "      ")


def main():
    pencil = SimpleItem("Pencil", 0.40)
    ruler = SimpleItem("Ruler", 1.60)
    eraser = SimpleItem("Eraser", 0.20)
    pencilSet = CompositeItem("Pencil Set", pencil, ruler, eraser)
    box = SimpleItem("Box", 1.00)
    boxedPencilSet = CompositeItem("Boxed Pencil Set", box, pencilSet)
    boxedPencilSet.add(pencil)
    for item in (pencil, ruler, eraser, pencilSet, boxedPencilSet):
        item.print()


if __name__ == "__main__":
    main()
