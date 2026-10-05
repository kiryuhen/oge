"""Мини-интерпретатор исполнителя Робот (подмножество языка КуМир) и рисовалка полей в SVG.

Нужен, чтобы проверять решения задания 15 на многих полях разного размера.
Поддерживается: вверх/вниз/влево/вправо/закрасить, нц пока ... кц, нц N раз ... кц,
если ... то ... [иначе ...] все, условия с и/или/не и скобками, комментарии после «|».
"""

import re

DIRS = {"вверх": (0, -1), "вниз": (0, 1), "влево": (-1, 0), "вправо": (1, 0)}
SIDES = {"сверху": (0, -1), "снизу": (0, 1), "слева": (-1, 0), "справа": (1, 0)}


class RobotCrash(Exception):
    pass


class Field:
    """Поле w×h, стены хранятся как множество пар соседних клеток (в т.ч. с клеткой за краем)."""

    def __init__(self, w, h, start):
        self.w, self.h = w, h
        self.walls = set()
        self.pos = start
        self.painted = set()

    @staticmethod
    def _edge(a, b):
        return frozenset((a, b))

    def wall(self, cell, side):
        dx, dy = SIDES[side]
        self.walls.add(self._edge(cell, (cell[0] + dx, cell[1] + dy)))

    def hwall(self, y_between, x_from, x_to):
        """Горизонтальная стена между строками y_between-1 и y_between на столбцах x_from..x_to."""
        for x in range(x_from, x_to + 1):
            self.walls.add(self._edge((x, y_between - 1), (x, y_between)))

    def vwall(self, x_between, y_from, y_to):
        """Вертикальная стена между столбцами x_between-1 и x_between на строках y_from..y_to."""
        for y in range(y_from, y_to + 1):
            self.walls.add(self._edge((x_between - 1, y), (x_between, y)))

    def blocked(self, cell, d):
        nx, ny = cell[0] + d[0], cell[1] + d[1]
        if not (0 <= nx < self.w and 0 <= ny < self.h):
            return True
        return self._edge(cell, (nx, ny)) in self.walls


# ---------------------------------------------------------------- парсер

def _clean(src):
    lines = []
    for raw in src.splitlines():
        line = raw.split("|")[0].strip()
        if not line:
            continue
        for part in line.split(";"):
            part = part.strip()
            if part:
                lines.append(part)
    return lines


def parse(src):
    lines = _clean(src)
    # пропускаем заголовок
    i = 0
    while i < len(lines) and not lines[i].startswith("нач"):
        i += 1
    i += 1
    body, i = _block(lines, i, {"кон"})
    return body


def _block(lines, i, stop):
    stmts = []
    while i < len(lines):
        line = lines[i]
        first = line.split()[0]
        if first in stop:
            return stmts, i
        if line.startswith("нц пока"):
            cond = line[len("нц пока"):].strip()
            body, i = _block(lines, i + 1, {"кц"})
            stmts.append(("while", cond, body))
            i += 1
        elif line.startswith("нц"):
            m = re.match(r"нц\s+(\d+)\s+раз$", line)
            if not m:
                raise SyntaxError("непонятный цикл: " + line)
            body, i = _block(lines, i + 1, {"кц"})
            stmts.append(("repeat", int(m.group(1)), body))
            i += 1
        elif line.startswith("если"):
            m = re.match(r"если\s+(.*)\s+то$", line)
            if m:
                cond = m.group(1)
                then, i = _block(lines, i + 1, {"иначе", "все"})
            else:  # «если усл то команда» в одну строку не поддерживаем
                raise SyntaxError("ожидалось «если ... то»: " + line)
            other = []
            if lines[i].split()[0] == "иначе":
                rest = lines[i][len("иначе"):].strip()
                i += 1
                if rest:
                    lines.insert(i, rest)
                other, i = _block(lines, i, {"все"})
            stmts.append(("if", cond, then, other))
            i += 1
        else:
            for word in line.split():
                if word in DIRS or word == "закрасить":
                    stmts.append(("cmd", word))
                else:
                    raise SyntaxError("неизвестная команда: " + word)
            i += 1
    raise SyntaxError("нет конца блока " + str(stop))


# ---------------------------------------------------------------- условия

def _cond_tokens(s):
    s = s.replace("(", " ( ").replace(")", " ) ")
    words = s.split()
    toks = []
    i = 0
    while i < len(words):
        w = words[i]
        if w in ("(", ")", "и", "или", "не"):
            toks.append(w)
            i += 1
        elif w in SIDES and i + 1 < len(words) and words[i + 1] in ("свободно", "стена"):
            toks.append(("side", w, words[i + 1]))
            i += 2
        elif w == "клетка" and i + 1 < len(words) and words[i + 1] in ("закрашена", "чистая"):
            toks.append(("cell", words[i + 1]))
            i += 2
        else:
            raise SyntaxError("непонятное условие: " + s)
    return toks


def eval_cond(s, field):
    toks = _cond_tokens(s)
    pos = 0

    def atom():
        nonlocal pos
        t = toks[pos]
        if t == "не":
            pos += 1
            return not atom()
        if t == "(":
            pos += 1
            v = disj()
            pos += 1  # ")"
            return v
        pos += 1
        if t[0] == "side":
            free = not field.blocked(field.pos, SIDES[t[1]])
            return free if t[2] == "свободно" else not free
        painted = field.pos in field.painted
        return painted if t[1] == "закрашена" else not painted

    def conj():
        nonlocal pos
        v = atom()
        while pos < len(toks) and toks[pos] == "и":
            pos += 1
            r = atom()
            v = v and r
        return v

    def disj():
        nonlocal pos
        v = conj()
        while pos < len(toks) and toks[pos] == "или":
            pos += 1
            r = conj()
            v = v or r
        return v

    return disj()


# ---------------------------------------------------------------- выполнение

def run(src, field, limit=200000):
    prog = parse(src)
    steps = [0]

    def ex(stmts):
        for st in stmts:
            steps[0] += 1
            if steps[0] > limit:
                raise RobotCrash("слишком много шагов (зацикливание?)")
            kind = st[0]
            if kind == "cmd":
                if st[1] == "закрасить":
                    field.painted.add(field.pos)
                else:
                    d = DIRS[st[1]]
                    if field.blocked(field.pos, d):
                        raise RobotCrash(f"робот разбился: {st[1]} из {field.pos}")
                    field.pos = (field.pos[0] + d[0], field.pos[1] + d[1])
            elif kind == "while":
                while eval_cond(st[1], field):
                    steps[0] += 1
                    if steps[0] > limit:
                        raise RobotCrash("зацикливание")
                    ex(st[2])
            elif kind == "repeat":
                for _ in range(st[1]):
                    ex(st[2])
            elif kind == "if":
                ex(st[2] if eval_cond(st[1], field) else st[3])

    ex(prog)
    return field


# ---------------------------------------------------------------- SVG

def svg(field, painted=None, robot=True, cell=28, marks=None):
    """Рисует поле. painted — какие клетки закрасить (по умолчанию field.painted)."""
    painted = field.painted if painted is None else painted
    pad = 6
    W, H = field.w * cell + 2 * pad, field.h * cell + 2 * pad
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    for (x, y) in painted:
        out.append(f'<rect x="{pad + x * cell}" y="{pad + y * cell}" width="{cell}" height="{cell}" fill="#9e9e9e"/>')
    for (x, y) in (marks or []):
        cx, cy = pad + x * cell + cell / 2, pad + y * cell + cell / 2
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{cell * 0.12}" fill="#1565c0"/>')
    for x in range(field.w + 1):
        out.append(f'<line x1="{pad + x * cell}" y1="{pad}" x2="{pad + x * cell}" y2="{pad + field.h * cell}" stroke="#bdbdbd" stroke-width="1"/>')
    for y in range(field.h + 1):
        out.append(f'<line x1="{pad}" y1="{pad + y * cell}" x2="{pad + field.w * cell}" y2="{pad + y * cell}" stroke="#bdbdbd" stroke-width="1"/>')
    # рамка поля
    out.append(f'<rect x="{pad}" y="{pad}" width="{field.w * cell}" height="{field.h * cell}" fill="none" stroke="#000" stroke-width="2"/>')
    for e in field.walls:
        a, b = sorted(e)
        if a[0] == b[0]:  # вертикальные соседи → горизонтальная стена
            y = pad + max(a[1], b[1]) * cell
            x = pad + a[0] * cell
            out.append(f'<line x1="{x - 1}" y1="{y}" x2="{x + cell + 1}" y2="{y}" stroke="#000" stroke-width="5" stroke-linecap="square"/>')
        else:
            x = pad + max(a[0], b[0]) * cell
            y = pad + a[1] * cell
            out.append(f'<line x1="{x}" y1="{y - 1}" x2="{x}" y2="{y + cell + 1}" stroke="#000" stroke-width="5" stroke-linecap="square"/>')
    if robot:
        x, y = field.pos
        cx, cy, r = pad + x * cell + cell / 2, pad + y * cell + cell / 2, cell * 0.32
        out.append(f'<polygon points="{cx},{cy - r} {cx + r},{cy} {cx},{cy + r} {cx - r},{cy}" fill="#ffffff" stroke="#000" stroke-width="2"/>')
    out.append("</svg>")
    return "\n".join(out)
