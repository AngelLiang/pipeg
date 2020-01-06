"""用类修饰器实现继承

有时我们创建基类只是为了使子类能够继承其中的某些方法或数据。
当要创建的子类个数比较多时，这种设计方式就显得很灵活了，因为每个
子类无须重复实现基类的方法或数据。然而若是继承下来的那些方法或数据
在子类里都无须改动，那么可以改用类修饰器来达到目的。
"""
import collections


def mediated(Class):

    setattr(Class, "mediator", None)

    def on_change(self):
        if self.mediator is not None:
            self.mediator.on_change(self)

    setattr(Class, "on_change", on_change)

    return Class


@mediated
class Button:

    def __init__(self, text=""):
        super().__init__()
        self.enabled = True
        self.text = text

    def click(self):
        if self.enabled:
            self.on_change()

    def __str__(self):
        return "Button({!r}) {}".format(
            self.text, "enabled" if self.enabled else "disabled")


@mediated
class Text:

    def __init__(self, text=""):
        super().__init__()
        self.__text = text

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        if self.text != text:
            self.__text = text
            self.on_change()

    def __str__(self):
        return "Text({!r})".format(self.text)


class Form:

    def __init__(self):
        self.create_widgets()
        self.create_mediator()

    def create_widgets(self):
        self.nameText = Text()
        self.emailText = Text()
        self.okButton = Button("OK")
        self.cancelButton = Button("Cancel")

    def create_mediator(self):
        self.mediator = Mediator(((self.nameText, self.update_ui),
                                  (self.emailText, self.update_ui),
                                  (self.okButton, self.clicked),
                                  (self.cancelButton, self.clicked)))
        self.update_ui()

    def update_ui(self, widget=None):
        self.okButton.enabled = (bool(self.nameText.text) and
                                 bool(self.emailText.text))

    def clicked(self, widget):
        if widget == self.okButton:
            print("OK")
        elif widget == self.cancelButton:
            print("Cancel")


class Mediator:

    def __init__(self, widgetCallablePairs):
        self.callablesForWidget = collections.defaultdict(list)
        for widget, caller in widgetCallablePairs:
            self.callablesForWidget[widget].append(caller)
            widget.mediator = self

    def on_change(self, widget):
        callables = self.callablesForWidget.get(widget)
        if callables is not None:
            for caller in callables:
                caller(widget)
        else:
            raise AttributeError(
                "No on_change() method registered for {}".format(widget))


def test_user_interaction_with(form):
    form.okButton.click()           # Ignored because it is disabled
    print(form.okButton.enabled)    # False
    form.nameText.text = "Fred"
    print(form.okButton.enabled)    # False
    form.emailText.text = "fred@bloggers.com"
    print(form.okButton.enabled)    # True
    form.okButton.click()           # OK
    form.emailText.text = ""
    print(form.okButton.enabled)    # False
    form.cancelButton.click()       # Cancel


def main():
    form = Form()
    test_user_interaction_with(form)


if __name__ == "__main__":
    main()