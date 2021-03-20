interface Key {
    x: number
    y: number
    w: number
}

interface State {
    row: number
    col: number
    x: number
    y: number
}

interface Modifier {
    x?: number
    y?: number
    w?: number
}

type Item = Modifier | string;
type KLE = Item[][];

function isModifier(mod: any): mod is Modifier {
    if (typeof mod === "string")
        return false;
    if ("x" in mod && typeof mod.x !== "number")
        return false;
    if ("y" in mod && typeof mod.y !== "number")
        return false;
    if ("w" in mod && typeof mod.w !== "number")
        return false;
    return true;
}

function isKle(data: any): data is KLE {
    if (data === null || data === undefined || !(data instanceof Array)) {
        return false;
    } else {
        for (const x of data) {
            if (!(x instanceof Array))
                return false;
            let wasMod = false;
            for (const y of x) {
                if (typeof y === "string") {
                    wasMod = false;
                } else if (!wasMod && isModifier(y)) {
                    wasMod = true;
                } else {
                    return false;
                }
            }
            if (wasMod)
                return false;
        }
    }
    return true;
}

async function readJson(path: string): Promise<null | KLE> {
    const text = await Deno.readTextFile(path);
    const data = JSON.parse(text);
    return isKle(data) ? data : null;
}

function nextKey(s: State, data: KLE): null | [State, Key] {
    const isLast = data[s.row].length == s.col;
    const { row, col, x, y } = isLast
        ? { row: s.row + 1, col: 0, x: 0, y: s.y + 1 }
        : s;

    if (data.length === row)
        return null;

    const v = data[row][col];
    const [newCol, m] = typeof v === "string"
        ? [col + 1, { x: 0, y: 0, w: 1 }]
        : [col + 2, { x: 0, y: 0, w: 1, ...v }];
    return [
        { row, col: newCol, x: x + m.x + m.w, y: y + m.y },
        { x: x + m.x, y: y + m.y, w: m.w }
    ];
}

function* iterKeys(data: KLE) {
    const s0: State = { row: 0, col: 0, x: 0, y: 0 };
    let res = nextKey(s0, data);
    while (res) {
        const [newState, key] = res;
        yield key;
        res = nextKey(newState, data);
    }
}

const s0: State = {
    row: 0,
    col: 0,
    x: 0,
    y: 0,
};

interface Show {
    toString(): string
}

interface Node {
    name: string
    attrs: Record<string, Show>
    children: Node[]
}

function makeAttrs(attrs: Record<string, Show>) {
    return Object.entries(attrs)
        .map(([k, v]) => `${k}="${v}"`).join(" ");
}

function nodes2xml(nodes: Node[]): string {
    return nodes.map(n => `<${n.name} ${makeAttrs(n.attrs)}>${nodes2xml(n.children)}</${n.name}>`).join("\n");
}

function keyToSvg({x, y, w}: Key): Node[] {
    const U = 19.05;
    return [
        {
            name: "rect",
            attrs: {
                "x": x * U,
                "y": y * U,
                "width": w * U,
                "height": U,
                "stroke": "black",
                "stroke-width": 0.2,
                "fill-opacity": 0.1,
            },
            children: []
        },
        {
            name: "rect",
            attrs: {
                "x": (x + w/2) * U - 7,
                "y": y * U + (U - 14) / 2,
                "width":  14,
                "height": 14,
                "fill-opacity": 0.3,
            },
            children: []
        },
        {
            name: "circle",
            attrs: { cx: (x + w/2) * U - 3.81, cy: (y + 0.5) * U - 2.54, r: 1.5 },
            children: []
        },
        {
            name: "circle",
            attrs: { cx: (x + w/2) * U + 2.54, cy: (y + 0.5) * U - 5.08, r: 1.5 },
            children: []
        },
        {
            name: "circle",
            attrs: { cx: (x + w/2) * U, cy: (y + 0.5) * U, r: 2 },
            children: []
        },
    ];
}

const path = "undiscipline.json";
const data = await readJson(path);
if (data) {
    const svg: Node[] = Array.from(iterKeys(data)).flatMap(keyToSvg);
    Deno.writeTextFile("undiscipline.svg", (
        '<?xml version="1.0" encoding="UTF-8" ?>'
        + '<svg width="800" viewBox="0 0 350 150" xmlns="http://www.w3.org/2000/svg">'
        + nodes2xml(svg)
        + '</svg>\n'
    )).then(() => console.log("Done!"));
} else {
    console.error(`Could not open file ${path}`);
}
