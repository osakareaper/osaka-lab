import sys
from pprint import pprint
from dataclasses import dataclass
from string import ascii_letters, digits

type JSON = str | int | list["JSON"] | dict[str, "JSON"]

STRING_CHARS = {
    *ascii_letters,
    *digits,
    " ",
    "!",
    "#",
    "$",
    "%",
    "&",
    "'",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
}


def parse(source: str) -> JSON:
    parser = Parser(source)
    value = parser.value()
    if parser.position != len(source):
        raise ValueError("extra data after JSON value")
    return value


@dataclass
class Parser:
    source: str
    position: int = 0

    def value(self) -> JSON:
        self.ws()

        match self.peek():
            case "[":
                value = self.array()
            case "{":
                value = self.object()
            case "t":
                self.literal("true")
                value = True
            case "f":
                self.literal("false")
                value = False
            case "n":
                self.literal("null")
                value = None
            case '"':
                value = self.string()
            case c if c in "0123456789":
                value = self.number()
            case x:
                raise ValueError(f"unexpected character: {x!r}")

        self.ws()
        return value

    def array(self) -> list[JSON]:
        self.read("[")
        self.ws()
        items = []

        # LISTA VAZIA
        if self.peek() == "]":
            self.position += 1
            return items

        # LER PRIMEIRO VALOR
        value = self.value()
        items.append(value)

        while self.peek() == ",":
            self.position += 1
            value = self.value()
            items.append(value)

        self.read("]")
        return items

    def object(self) -> dict[str, JSON]:
        self.read("{")
        self.ws()
        items = {}

        # OBJETO VAZIO
        if self.peek() == "}":
            self.position += 1
            return items

        # LER PRIMEIRO VALOR
        self.ws()
        key = self.string()
        self.ws()
        self.read(":")
        self.ws()
        value = self.value()
        items[key] = value

        while self.peek() == ",":
            self.position += 1
            self.ws()
            key = self.string()
            self.ws()
            self.read(":")
            self.ws()
            value = self.value()
            items[key] = value

        self.read("}")
        return items

    def string(self) -> str:
        chars = []
        self.read('"')
        while self.peek() in STRING_CHARS:
            chars.append(self.peek())
            self.position += 1
        self.read('"')
        return "".join(chars)

    def number(self) -> int:
        chars = []
        while self.peek() in "0123456789":
            chars.append(self.peek())
            self.position += 1
        text = "".join(chars)
        return int(text)

    def peek(self) -> str:
        if self.position < len(self.source):
            return self.source[self.position]
        return "\0"

    def ws(self) -> None:
        while self.peek() in " \t\n\r":
            self.position += 1

    def read(self, expected: str) -> None:
        if self.position >= len(self.source):
            raise ValueError("unexpected end of input")
        if self.source[self.position] != expected:
            raise ValueError("unexpected character")
        self.position += 1

    def literal(self, text: str) -> None:
        if self.source.startswith(text, self.position):
            self.position += len(text)
        else:
            raise ValueError(f"unexpected character: {self.peek()!r}")


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        source = f.read()
    result = parse(source)
    pprint(type(result))
    pprint(result)
