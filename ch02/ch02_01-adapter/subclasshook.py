""" 测试 __subclasshook__ 方法

Renderer1 没有相关方法，返回为 False
>>> class Renderer1:
...     pass
...
>>> isinstance(Renderer1(), Renderer)
False


Renderer2 有相关方法，返回为 True
>>> class Renderer2:
...     def header(self):
...         pass
...
...     def paragraph(self):
...         pass
...
...     def footer(self):
...         pass
...
>>> isinstance(Renderer2(), Renderer)
True


相关方法也可以是属性
>>> class Renderer3:
...     header = None
...     paragraph = None
...     footer = None
...
>>> isinstance(Renderer3(), Renderer)
True
"""

import abc
import collections


class Renderer(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(Class, Subclass):
        """可以在无须继承特定基类的前提下，创建出某套符合接口的对象"""
        if Class is Renderer:
            # 调用 Subclass.__mro__() 方法
            # 遍历 Subclass 及其超类的 Superclass.__dict__
            attributes = collections.ChainMap(
                *(Superclass.__dict__ for Superclass in Subclass.__mro__))
            # 将待检测的方法放在一个元组中
            methods = ("header", "paragraph", "footer")
            # 遍历元组中的方法，判断这些方法是不是都在 attributes 映射表中
            if all(method in attributes for method in methods):
                # 如果 methods 中每个方法都在 attributes 映射表里，那就返回 True
                return True
        # 通过 Class 参数判断自己是不是在 Renderer 类上调用
        # 不是则返回 NotImplemented
        return NotImplemented


if __name__ == "__main__":
    import doctest
    doctest.testmod()
