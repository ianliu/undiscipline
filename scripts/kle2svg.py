import json
from itertools import chain
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional, Union, Iterable


@dataclass
class Key:
    x: Decimal
    y: Decimal
    w: Decimal
    ith: int


@dataclass
class State:
    ith: int
    row: int
    col: int
    x: Decimal
    y: Decimal


@dataclass
class Modifier:
    x: Decimal
    y: Decimal
    w: Decimal


Item = Union[Modifier, str]
KLE = list[list[Item]]


def parse_item(mod: Any) -> Optional[Item]:
    if type(mod) == str:
        return mod
    if type(mod) == dict:
        return Modifier(
            mod.get("x", Decimal(0)), mod.get("y", Decimal(0)), mod.get("w", Decimal(1))
        )
    return None


def parse_kle(data: Any) -> Optional[KLE]:
    kle: KLE = []
    if type(data) != list:
        return None
    for inner in data:
        if type(inner) != list:
            return None
        kle.append([])
        for x in inner:
            item = parse_item(x)
            if item is None:
                return None
            kle[-1].append(item)
    return kle


def parse_json(path: str) -> Optional[KLE]:
    with open(path) as f:
        data = json.load(f, parse_float=Decimal, parse_int=Decimal)
    return parse_kle(data)


def next_key(s: State, data: KLE) -> Optional[tuple[State, Key]]:
    if len(data[s.row]) == s.col:
        row, col, x, y = s.row + 1, 0, 0, s.y + 1
    else:
        row, col, x, y = s.row, s.col, s.x, s.y

    if len(data) == row:
        return None

    v = data[row][col]
    if type(v) == str:
        newCol = col + 1
        m = Modifier(x=Decimal(0), y=Decimal(0), w=Decimal(1))
    else:
        newCol = col + 2
        m = v
    return (State(s.ith + 1, row, newCol, x + m.x + m.w, y + m.y), Key(x + m.x, y + m.y, m.w, s.ith))


def iter_keys(data: KLE):
    s0 = State(1, 0, 0, Decimal(0), Decimal(0))
    res = next_key(s0, data)
    while res:
        newState, key = res
        yield key
        res = next_key(newState, data)

Content = Union[None, list["Node"], str]

@dataclass
class Node:
    name: str
    attrs: dict[str, Any] = field(default_factory=dict)
    content: Content = None


def make_attrs(attrs: dict[str, Any]) -> str:
    return " ".join(map(lambda x: f'{x[0]}="{x[1]}"', attrs.items()))


def nodes2xml(nodes: Iterable[Node]) -> str:
    def render_content(content: Content) -> str:
        if content is None:
            return ""
        elif isinstance(content, str):
            return content
        else:
            return nodes2xml(content)
    txts = (
        f"<{n.name} {make_attrs(n.attrs)}>{render_content(n.content)}</{n.name}>"
        for n in nodes
    )
    return "\n".join(txts)


def key2svg(key: Key) -> list[Node]:
    x = key.x
    y = key.y
    w = key.w
    U = Decimal("19.05")
    print(f"key {key.ith}:", (x + w / Decimal("2")) * U * 1000000, (y + Decimal("0.5")) * U * 1000000)
    return [
        Node(
            name="rect",
            attrs={
                "x": x * U,
                "y": y * U,
                "width": w * U,
                "height": U,
                "stroke": "black",
                "stroke-width": 0.2,
                "fill": "#eee",
            },
        ),
        Node(
            name="rect",
            attrs={
                "x": (x + w / 2) * U - 7,
                "y": y * U + (U - 14) / 2,
                "width": 14,
                "height": 14,
                "fill": "#aaa",
            },
        ),
        Node(
            name="circle",
            attrs={
                "cx": (x + w / 2) * U - Decimal("3.81"),
                "cy": (y + Decimal("0.5")) * U - Decimal("2.54"),
                "r": 1.5,
            },
        ),
        Node(
            name="circle",
            attrs={
                "cx": (x + w / 2) * U + Decimal("2.54"),
                "cy": (y + Decimal("0.5")) * U - Decimal("5.08"),
                "r": 1.5,
            },
        ),
        Node(
            name="circle",
            attrs={"cx": (x + w / 2) * U, "cy": (y + Decimal("0.5")) * U, "r": 2},
        ),
        Node(
            name="text",
            attrs={
                "text-anchor": "end",
                "font-size": "4pt",
                "fill": "red",
                "x": (x+ w / 2) * U + 7,
                "y": y * U + 16
            },
            content=str(key.ith),
        )
    ]


if __name__ == "__main__":
    path = "undiscipline.json"
    data = parse_json(path)
    if data:
        svg = chain.from_iterable(map(key2svg, iter_keys(data)))
        with open("undiscipline.svg", "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8" ?>')
            f.write(
                '<svg width="420mm" height="297mm" viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg">'
            )
            f.write(nodes2xml(svg))
            f.write("</svg>")
    else:
        print(f"Could not open file {path}")
