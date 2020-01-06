import sys
if sys.version_info[:2] < (3, 2):
    from xml.sax.saxutils import escape
else:
    from html import escape


WINNERS = ("Nikolai Andrianov", "Matt Biondi", "Bjørn Dæhlie",
           "Birgit Fischer", "Sawao Kato", "Larisa Latynina", "Carl Lewis",
           "Michael Phelps", "Mark Spitz", "Jenny Thompson")


class Layout:

    def __init__(self, tabulator):
        self.tabulator = tabulator

    def tabulate(self, rows, items):
        return self.tabulator(rows, items)


def html_tabulator(rows, items):
    columns, remainder = divmod(len(items), rows)
    if remainder:
        columns += 1
    column = 0
    table = ['<table border="1">\n']
    for item in items:
        if column == 0:
            table.append("<tr>")
        table.append("<td>{}</td>".format(escape(str(item))))
        column += 1
        if column == columns:
            table.append("</tr>\n")
        column %= columns
    if table[-1][-1] != "\n":
        table.append("</tr>\n")
    table.append("</table>\n")
    return "".join(table)


def text_tabulator(rows, items):
    columns, remainder = divmod(len(items), rows)
    if remainder:
        columns += 1
        remainder = (rows * columns) - len(items)
        if remainder == columns:
            remainder = 0
    column = columnWidth = 0
    for item in items:
        columnWidth = max(columnWidth, len(item))
    columnDivider = ("-" * (columnWidth + 2)) + "+"
    divider = "+" + (columnDivider * columns) + "\n"
    table = [divider]
    for item in items + (("",) * remainder):
        if column == 0:
            table.append("|")
        table.append(" {:<{}} |".format(item, columnWidth))
        column += 1
        if column == columns:
            table.append("\n")
        column %= columns
    table.append(divider)
    return "".join(table)


def main():
    # 选择 html_tabulator 策略
    htmlLayout = Layout(html_tabulator)
    for rows in range(2, 6):
        print(htmlLayout.tabulate(rows, WINNERS))

    # 选择 text_tabulator 策略
    textLayout = Layout(text_tabulator)
    for rows in range(2, 6):
        print(textLayout.tabulate(rows, WINNERS))


if __name__ == "__main__":
    main()
