"""Рисует иллюстрации для теории и разборов (images/theory/*.svg, *.png).

Запуск:  python3 tools/build_images.py   (из корня репозитория)
Нужны: graphviz (dot), matplotlib.
"""

import os
import subprocess

OUT = os.path.join(os.path.dirname(__file__), "..", "images", "theory")
FONT = 'fontname="DejaVu Sans"'


def dot(name, src):
    svg = subprocess.run(["dot", "-Tsvg"], input=src.encode(), capture_output=True, check=True).stdout
    with open(os.path.join(OUT, name), "wb") as f:
        f.write(svg)


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(text)


def code_tree():
    dot("code-tree.svg", f"""digraph T {{ bgcolor=white; node [{FONT}, shape=circle, width=0.35, fixedsize=true, label=""];
    edge [{FONT}, fontsize=12];
    r; n1; n11; A [label="А", style=filled, fillcolor="#c8e6c9"]; B [label="Б", style=filled, fillcolor="#c8e6c9"];
    C [label="В", style=filled, fillcolor="#c8e6c9"]; D [label="Г", style=filled, fillcolor="#c8e6c9"];
    r -> A [label=" 0"]; r -> n1 [label=" 1"]; n1 -> B [label=" 0"]; n1 -> n11 [label=" 1"];
    n11 -> C [label=" 0"]; n11 -> D [label=" 1"]; }}""")


def weighted_graph():
    dot("graph-weighted.svg", f"""graph G {{ bgcolor=white; layout=neato; node [{FONT}, shape=circle, width=0.45, fixedsize=true];
    edge [{FONT}, fontsize=13, fontcolor="#1565c0"];
    A [pos="0,1!"]; B [pos="1.6,2!"]; C [pos="1.6,0!"]; D [pos="3.2,2!"]; E [pos="4.8,1!"]; F [pos="3.2,0!"];
    A -- B [label="2"]; A -- C [label="5"]; B -- C [label="1"]; B -- D [label="7"]; C -- F [label="3"];
    D -- E [label="1"]; F -- E [label="6"]; D -- F [label="2"]; }}""")


def dag_count():
    edges = [("А", "Б"), ("А", "В"), ("Б", "В"), ("А", "Г"), ("В", "Д"), ("Г", "Д"), ("В", "Е"), ("Д", "Е"),
             ("Б", "Е"), ("Д", "Ж"), ("Е", "Ж")]
    nodes = {v: 0 for v in "АБВГДЕЖ"}
    nodes["А"] = 1
    for v in "БВГДЕЖ":  # вершины уже в топологическом порядке
        nodes[v] = sum(nodes[a] for a, b in edges if b == v)
    lines = ["digraph G { bgcolor=white; rankdir=LR; nodesep=0.5;",
             f'node [{FONT}, shape=circle, width=0.6, fixedsize=true, fontsize=13];']
    for v, c in nodes.items():
        lines.append(f'"{v}" [label=<{v}<BR/><FONT COLOR="#c62828" POINT-SIZE="11">{c}</FONT>>];')
    lines += [f'"{a}" -> "{b}";' for a, b in edges]
    lines.append("}")
    dot("dag-count.svg", "\n".join(lines))


def file_tree():
    dot("file-tree.svg", f"""digraph F {{ bgcolor=white; rankdir=LR; node [{FONT}, shape=box, style="rounded", fontsize=12];
    edge [arrowhead=none];
    root [label="C:\\\\", style="rounded,filled", fillcolor="#e3f2fd"];
    school [label="Школа", style="rounded,filled", fillcolor="#fff9c4"];
    alg [label="Алгебра", style="rounded,filled", fillcolor="#fff9c4"];
    inf [label="Информатика", style="rounded,filled", fillcolor="#fff9c4"];
    games [label="Игры", style="rounded,filled", fillcolor="#fff9c4"];
    f1 [label="дз1.docx"]; f2 [label="дз2.docx"]; f3 [label="проект.py"]; f4 [label="отчёт.odt"]; f5 [label="chess.exe"];
    root -> school; root -> games; school -> alg; school -> inf; alg -> f1; alg -> f2; inf -> f3; inf -> f4; games -> f5; }}""")


def flowcharts():
    dot("flow-if.svg", f"""digraph F {{ bgcolor=white; node [{FONT}, fontsize=12]; edge [{FONT}, fontsize=11];
    s [label="начало", shape=oval]; i [label="ввод s, t", shape=parallelogram];
    c [label="s > 10 или t > 10 ?", shape=diamond]; y [label="вывод «YES»", shape=parallelogram];
    n [label="вывод «NO»", shape=parallelogram]; e [label="конец", shape=oval];
    s -> i -> c; c -> y [label="да"]; c -> n [label="нет"]; y -> e; n -> e; }}""")
    dot("flow-while.svg", f"""digraph F {{ bgcolor=white; node [{FONT}, fontsize=12]; edge [{FONT}, fontsize=11];
    s [label="начало", shape=oval]; a [label="count = 0", shape=box]; i [label="ввод x", shape=parallelogram];
    c [label="x ≠ 0 ?", shape=diamond]; k [label="x % 10 == 7 ?", shape=diamond]; inc [label="count = count + 1", shape=box];
    i2 [label="ввод x", shape=parallelogram]; o [label="вывод count", shape=parallelogram]; e [label="конец", shape=oval];
    s -> a -> i -> c; c -> k [label="да"]; k -> inc [label="да"]; k -> i2 [label="нет"]; inc -> i2; i2 -> c;
    c -> o [label="нет"]; o -> e; }}""")


def euler():
    # два круга
    write("euler-2.svg", """<svg xmlns="http://www.w3.org/2000/svg" width="420" height="240" viewBox="0 0 420 240">
<rect width="420" height="240" fill="#fff"/>
<circle cx="160" cy="120" r="95" fill="#1e88e5" fill-opacity="0.18" stroke="#1565c0" stroke-width="2"/>
<circle cx="260" cy="120" r="95" fill="#e53935" fill-opacity="0.18" stroke="#c62828" stroke-width="2"/>
<g font-family="DejaVu Sans" font-size="18" text-anchor="middle">
<text x="110" y="126">1</text><text x="210" y="126">2</text><text x="310" y="126">3</text>
<text x="95" y="30" fill="#1565c0" font-weight="bold">A</text><text x="325" y="30" fill="#c62828" font-weight="bold">B</text>
</g>
<g font-family="DejaVu Sans" font-size="12" text-anchor="middle" fill="#444">
<text x="110" y="146">только A</text><text x="210" y="146">A и B</text><text x="310" y="146">только B</text>
</g></svg>""")
    write("euler-3.svg", """<svg xmlns="http://www.w3.org/2000/svg" width="420" height="380" viewBox="0 0 420 380">
<rect width="420" height="380" fill="#fff"/>
<circle cx="160" cy="140" r="100" fill="#1e88e5" fill-opacity="0.16" stroke="#1565c0" stroke-width="2"/>
<circle cx="260" cy="140" r="100" fill="#e53935" fill-opacity="0.16" stroke="#c62828" stroke-width="2"/>
<circle cx="210" cy="230" r="100" fill="#43a047" fill-opacity="0.16" stroke="#2e7d32" stroke-width="2"/>
<g font-family="DejaVu Sans" font-size="18" text-anchor="middle">
<text x="110" y="115">1</text><text x="210" y="95">2</text><text x="310" y="115">3</text>
<text x="160" y="205">4</text><text x="210" y="180">5</text><text x="260" y="205">6</text><text x="210" y="290">7</text>
<text x="70" y="40" fill="#1565c0" font-weight="bold">A</text><text x="350" y="40" fill="#c62828" font-weight="bold">B</text>
<text x="210" y="365" fill="#2e7d32" font-weight="bold">C</text>
</g></svg>""")


def number_line():
    # НЕ (X < 5) И (X < 12): закрашен отрезок [5; 11]
    W, x0, step = 620, 30, 40
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="150" viewBox="0 0 {W} 150">',
             f'<rect width="{W}" height="150" fill="#fff"/>',
             f'<line x1="{x0 - 10}" y1="100" x2="{W - 15}" y2="100" stroke="#000" stroke-width="1.5"/>',
             f'<polygon points="{W - 15},95 {W - 5},100 {W - 15},105" fill="#000"/>']
    for k in range(0, 15):
        x = x0 + k * step
        parts.append(f'<line x1="{x}" y1="95" x2="{x}" y2="105" stroke="#000"/>')
        parts.append(f'<text x="{x}" y="125" font-family="DejaVu Sans" font-size="13" text-anchor="middle">{k}</text>')
    # X >= 5 (синяя), X < 12 (красная)
    parts.append(f'<line x1="{x0 + 5 * step}" y1="50" x2="{W - 15}" y2="50" stroke="#1565c0" stroke-width="4"/>')
    parts.append(f'<circle cx="{x0 + 5 * step}" cy="50" r="5" fill="#1565c0"/>')
    parts.append(f'<text x="{x0 + 5 * step + 5}" y="40" font-family="DejaVu Sans" font-size="13" fill="#1565c0">НЕ (X &lt; 5), т.е. X ≥ 5</text>')
    parts.append(f'<line x1="{x0 - 10}" y1="72" x2="{x0 + 12 * step}" y2="72" stroke="#c62828" stroke-width="4"/>')
    parts.append(f'<circle cx="{x0 + 12 * step}" cy="72" r="5" fill="#fff" stroke="#c62828" stroke-width="2"/>')
    parts.append(f'<text x="{x0}" y="66" font-family="DejaVu Sans" font-size="13" fill="#c62828">X &lt; 12</text>')
    for k in range(5, 12):
        parts.append(f'<circle cx="{x0 + k * step}" cy="100" r="6" fill="#2e7d32"/>')
    parts.append("</svg>")
    write("number-line.svg", "\n".join(parts))


def pie():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(5, 3.4), dpi=110)
    vals, labels = [79, 62, 65], ["ЮВ", "СЗ", "СВ"]
    ax.pie(vals, labels=[str(v) for v in vals], colors=["#1e88e5", "#e53935", "#fdd835"], startangle=90,
           counterclock=False, wedgeprops={"edgecolor": "white"})
    ax.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)
    ax.set_title("Число участников по округам")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "pie-example.png"), facecolor="white")


def task_examples():
    """Картинки к разборам заданий (images/tasks/)."""
    global OUT
    saved, OUT = OUT, os.path.join(os.path.dirname(__file__), "..", "images", "tasks")
    os.makedirs(OUT, exist_ok=True)
    dot("t04-example.svg", f"""graph G {{ bgcolor=white; layout=neato; node [{FONT}, shape=circle, width=0.45, fixedsize=true];
    edge [{FONT}, fontsize=13, fontcolor="#1565c0"];
    A [pos="0,1!"]; B [pos="1.6,2!"]; C [pos="1.6,0!"]; D [pos="3.2,1.4!"]; E [pos="4.6,0.4!"];
    A -- B [label="2", color="#2e7d32", penwidth=2.5]; A -- C [label="5"]; B -- C [label="2", color="#2e7d32", penwidth=2.5];
    B -- D [label="7"]; C -- D [label="3", color="#2e7d32", penwidth=2.5]; C -- E [label="9"];
    D -- E [label="1", color="#2e7d32", penwidth=2.5]; }}""")
    for name, (layers, edges) in TASK9.items():
        lines = ["digraph G { bgcolor=white; rankdir=LR; nodesep=0.5; ranksep=0.7;",
                 f'node [{FONT}, shape=circle, width=0.45, fixedsize=true, fontsize=14]; edge [arrowsize=0.7];']
        for L in layers:
            lines.append("{rank=same; " + " ".join(f'"{v}"' for v in L) + "}")
        lines += [f'"{a}" -> "{b}";' for a, b in edges]
        lines.append("}")
        dot(name, "\n".join(lines))
    OUT = saved


def _e(s):
    return [tuple(x.split(">")) for x in s.split()]


# схемы дорог к заданию 9 (слои — для красивой раскладки)
TASK9 = {
    "t09-example.svg": ([["А"], ["Б", "В", "Г"], ["Д", "Е"], ["Ж"], ["И", "К"], ["Л"]],
                        _e("А>Б А>В А>Г Б>В В>Г Б>Д В>Д В>Е Г>Е Д>Ж Е>Ж Д>И Ж>И Ж>К Е>К И>Л К>Л")),
    "t09-a1.svg": ([["А"], ["Б", "В"], ["Г", "Д"], ["Е"]], _e("А>Б А>В Б>В Б>Г В>Г В>Д Г>Д Г>Е Д>Е")),
    "t09-a2.svg": ([["А"], ["Б", "В", "Г"], ["Д", "Е"], ["Ж", "И"], ["К"]],
                   _e("А>Б А>В А>Г Б>Д В>Д В>Е Г>Е Д>Ж Д>И Е>И Е>Ж Ж>К И>К Б>В В>Г")),
    "t09-a3.svg": ([["А"], ["Б", "В"], ["Г", "Д", "Е"], ["Ж", "И"], ["К"]],
                   _e("А>Б А>В Б>Г Б>Д В>Д В>Е Г>Ж Д>Ж Д>И Е>И Ж>К И>К Г>Д Ж>И")),
    "t09-a4.svg": ([["А"], ["Б", "В"], ["Г", "Д"], ["Е", "Ж"], ["И"]],
                   _e("А>Б А>В Б>Г Б>Д В>Д В>Ж Г>Е Д>Е Д>Ж Е>И Ж>И Г>Д Е>Ж")),
}


def count_paths(edges, s, t, avoid=None):
    order = []
    nodes = {v for e in edges for v in e}
    while len(order) < len(nodes):  # топологическая сортировка
        for v in sorted(nodes):
            if v not in order and all(a in order for a, b in edges if b == v):
                order.append(v)
    cnt = {v: 0 for v in nodes}
    cnt[s] = 1
    for v in order:
        if v == avoid:
            cnt[v] = 0
        for a, b in edges:
            if a == v:
                cnt[b] += cnt[v]
    return cnt[t]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    task_examples()
    code_tree()
    weighted_graph()
    dag_count()
    file_tree()
    flowcharts()
    euler()
    number_line()
    pie()
    print("готово:", sorted(os.listdir(OUT)))
