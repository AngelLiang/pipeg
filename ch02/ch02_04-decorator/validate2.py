"""用类修饰新增属性

有些程序员不喜欢把多个类修饰器叠加在一起，他们会把相关的 attreibute 都放在类里面，
然后只用一个类修饰器来修饰，这样写出来的代码更易读懂。
"""
import numbers
import re


def is_non_empty_str(name, value):
    if not isinstance(value, str):
        raise ValueError("{} must be of type str".format(name))
    if not bool(value):
        raise ValueError("{} may not be empty".format(name))


def is_in_range(minimum=None, maximum=None):
    assert minimum is not None or maximum is not None

    def is_in_range(name, value):
        if not isinstance(value, numbers.Number):
            raise ValueError("{} must be a number".format(name))
        if minimum is not None and value < minimum:
            raise ValueError("{} {} is too small".format(name, value))
        if maximum is not None and value > maximum:
            raise ValueError("{} {} is too big".format(name, value))
    return is_in_range


# Code adapted from the Regular Expressions Cookbook
# (ISBN-13: 978-0-596-52068-7), Chapter 4, Section 4.13, Validate ISBNs.
def is_valid_isbn(name, isbn):
    regex = re.compile(r"^(?:ISBN(?:-1[03])?:? )?(?=[-0-9 ]{17}$|"
                       r"[-0-9X ]{13}$|[0-9X]{10}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?"
                       r"(?:[0-9]+[- ]?){2}[0-9X]$")
    if regex.match(isbn):
        digits = list(re.sub("[^0-9X]", "", isbn))
        checkSumDigit = digits.pop()
        if len(digits) == 9:  # ISBN-10
            value = sum((x + 2) * int(y) for x, y in enumerate(
                reversed(digits)))
            check = 11 - (value % 11)
            if check == 10:
                check = "X"
            elif check == 11:
                check = "0"
        else:  # ISBN-13
            value = sum((x % 2 * 2 + 1) * int(y) for x, y in enumerate(
                digits))
            check = 10 - (value % 10)
            if check == 10:
                check = "0"
        if str(check) != checkSumDigit:
            raise ValueError("{} is not a valid ISBN".format(isbn))
        return
    raise ValueError("{} is not a valid ISBN".format(isbn))


class Ensure:

    def __init__(self, validate, doc=None):
        self.validate = validate
        self.doc = doc


def do_ensure(Class):
    """ 这个类修饰器可以分为三部分

    一、定义了 make_property() 嵌套函数，该函数
    有两个属性，一个是属性名，另一个是 Ensure 类型的 attribute 。
    此函数返回一个属性，该属性会把其值保存在私有的 attribute 中。
    属性的 setter 函数还会调用原来 Ensure 实例的验证器函数。

    二、遍历类中的每一个 attribute ，并用新的属性来替换原先的 Ensure 实例

    三、把修改后的类返回

    从理论上说，可以不写这个 make_property() 嵌套函数，而是把其中
    的代码都放在 if isinstance() 语句下面。但实际上，由于
    “后期绑定（late binding）”机制的问题，没法这么做，所以必须把相关
    代码单独放在一个函数里。
    """
    def make_property(name, attribute):
        """
        :param name: str, 属性名
        :param attribute: Ensure, Ensure 类型的 attribute
        """

        privateName = "__" + name

        def getter(self):
            return getattr(self, privateName)

        def setter(self, value):
            attribute.validate(name, value)
            setattr(self, privateName, value)

        return property(getter, setter, doc=attribute.doc)

    # 遍历类中的每一个 attribute ，并用新的属性来替换原先的 Ensure 实例
    for name, attribute in Class.__dict__.items():
        if isinstance(attribute, Ensure):
            setattr(Class, name, make_property(name, attribute))

    # 把修改后的类返回
    return Class


@do_ensure
class Book:

    title = Ensure(is_non_empty_str)
    isbn = Ensure(is_valid_isbn)
    price = Ensure(is_in_range(1, 10000))
    quantity = Ensure(is_in_range(0, 1000000))

    def __init__(self, title, isbn, price, quantity):
        self.title = title
        self.isbn = isbn
        self.price = price
        self.quantity = quantity

    @property
    def value(self):
        return self.price * self.quantity

    def __repr__(self):
        return ("Book({0.title!r}, {0.isbn!r}, {0.price!r}, "
                "{0.quantity!r})".format(self))


"""
ensure("title", is_non_empty_str)( # Pseudo-code
    ensure("isbn", is_valid_isbn)(
        ensure("price", is_in_range(1, 10000))(
            ensure("quantity", is_in_range(0, 1000000))(class Book: ...))))
"""


def main():
    try:
        book = Book("", "ISBN 0321635906", 54.99, 7830)
        assert False, "failed empty string test"
    except ValueError as err:
        assert str(err).endswith("may not be empty")
    try:
        book = Book(88, "ISBN 0321635906", 54.99, 7830)
        assert False, "failed non-string test"
    except ValueError as err:
        assert str(err).endswith("must be of type str")
    try:
        book = Book("Title", "ISBN 0321635907", 54.99, 7830)
        assert False, "failed invalid ISBN test"
    except ValueError as err:
        assert str(err).endswith("is not a valid ISBN")
    try:
        book = Book("Title", "ISBN 0321635906", 0, 7830)
        assert False, "failed too small test"
    except ValueError as err:
        assert str(err).endswith("is too small")
    try:
        book = Book("Title", "ISBN 0321635906", 2e6, 7830)
        assert False, "failed too big test"
    except ValueError as err:
        assert str(err).endswith("is too big")
    try:
        book = Book("Title", "ISBN 0321635906", 100, "x17")
        assert False, "failed non-number test"
    except ValueError as err:
        assert str(err).endswith("must be a number")

    books = []
    for title, isbn, price, quantity in (
            ("Advanced Qt Programming", "ISBN 0321635906", 54.99, 7830),
            ("Programming in Go", "ISBN 0321774639", 44.99, 5220),
            ("Programming in Python 3", "ISBN-13: 9780321680563", 49.99,
             10960),
            ("Rapid GUI Programming with Python and Qt", "ISBN 0132354187",
             54.99, 11735),
            ("C++ GUI Programming with Qt 4", "0132354160", 69.99, 15872)):
        books.append(Book(title, isbn, price, quantity))
    for book in books:
        print(book)


if __name__ == "__main__":
    main()
