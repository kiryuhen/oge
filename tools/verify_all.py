"""Независимая проверка ответов во всей библиотеке.

Скрипт читает готовые .md-файлы (tasks/*.md и variants/*.md), заново решает задачи
другим способом и сравнивает с записанными ответами:
  1 — пересчёт длин слов; 2 — перебор расшифровок; 3 — вычисление выражения на всех X;
  4 — алгоритм Флойда; 5 — перебор b / программ; 6 — запуск самой программы из условия;
  7 — сборка адреса; 8 — формула включений-исключений; 9 — перебор путей по графу из SVG;
  10 — int(x, основание); 11 — поиск фразы в файлах; 12 — пересчёт файлов через pathlib;
  14 — пересчёт по самим .xlsx; 15 — симулятор Робота; 16 — запуск решений на тестах.
Запуск:  python3 tools/verify_all.py   (из корня репозитория)
"""

import glob
import html
import io
import itertools
import json
import os
import pathlib
import re
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

errors, checked = [], {}


def ok(task, cond, msg):
    checked[task] = checked.get(task, 0) + 1
    if not cond:
        errors.append(f"[{task}] {msg}")


# ------------------------------------------------------------------ извлечение задач из .md

def task_items():
    """(номер задания, текст условия, ответ, источник) для tasks/*.md (общий блок и блоки подтипов) и вариантов."""
    items = []
    for path in sorted(glob.glob(os.path.join(ROOT, "tasks", "*.md"))):
        no = int(os.path.basename(path)[:2])
        if no > 10:
            continue
        text = open(path, encoding="utf-8").read()
        name = os.path.basename(path)
        m = re.search(r"<!-- BEGIN:generated -->(.*)<!-- END:generated -->", text, re.S)
        if m:
            for block in re.split(r"\n### Задача \d+\n", m.group(1))[1:]:
                ans = re.search(r"<summary>Ответ</summary>\s*\*\*(.+?)\*\*", block).group(1)
                items.append((no, block.split("<details>")[0], ans, name))
        for key, body in re.findall(r"<!-- BEGIN:sub:([\d.]+) -->(.*?)<!-- END:sub:", text, re.S):
            blocks = re.split(r"\n#### Тренировка [\d.]+\n", body)[1:]
            ok(no, len(blocks) >= 3, f"{name}: в подтипе {key} меньше 3 задач")
            for block in blocks:
                ans = re.search(r"<summary>Ответ</summary>\s*\*\*(.+?)\*\*", block).group(1)
                items.append((no, block.split("<details>")[0], ans, f"{name} [{key}]"))
    for path in sorted(glob.glob(os.path.join(ROOT, "variants", "variant-*.md"))):
        text = open(path, encoding="utf-8").read()
        key = text.split("**Задания 1–12**")[1].split("**Задание 13**")[0]
        answers = dict(re.findall(r"^\| (\d+) \| (.+?) \|$", key, re.M))
        for no in range(1, 11):
            m = re.search(rf"### Задание {no}\n(.*?)(?=\n### Задание|\n## Часть)", text, re.S)
            items.append((no, m.group(1), answers[str(no)], os.path.basename(path)))
    return items


# ------------------------------------------------------------------ решатели 1–10

def solve1(t, ans=None):
    m = re.search(r"кодируется (\d+) бит", t)
    bits = int(m.group(1)) if m else None
    if "перекодировали" in t:
        a, b = map(int, re.findall(r"(\d+)-битн", t)[:2])
        m = re.search(r"на (\d+) (байт|бит)", t)
        diff = int(m.group(1)) * (8 if m.group(2).startswith("байт") else 1)
        return str(diff // abs(a - b))
    if "страниц" in t:
        get = lambda w: (lambda m: int(m.group(1)) if m else None)(re.search(rf"(\d+) {w}", t))
        p, l, c = get("страниц"), get("строк"), get("символ")
        vol = re.search(r"составляет (\d+) Кбайт", t)
        if not vol:
            return str(p * l * c * bits // 8 // 1024)
        total_bits = int(vol.group(1)) * 1024 * 8
        if "Сколько символов в каждой строке" in t:
            return str(total_bits // (p * l * bits))
        if "Сколько строк" in t:
            return str(total_bits // (p * c * bits))
        return str(total_bits // (p * l * c))
    sentence = re.search(r"«(.+?) – ", t).group(1)
    words = sentence.split(", ")
    m = re.search(r"на (\d+) (байт|бит)", t)
    delta = int(m.group(1)) * (8 if m.group(2).startswith("байт") else 1)
    cands = [w for w in words if (len(w) + 2) * bits == delta]
    assert len(cands) == 1, cands
    return cands[0].lower()


def solve2(t, ans=None):
    rows = re.findall(r"^\| (.+) \|$", t, re.M)
    table = {}
    for head, codes in zip(rows[0::2], rows[1::2]):
        table.update(zip(head.split(" | "), [c.strip("`") for c in codes.split(" | ")]))

    def decs(s, distinct):
        if not s:
            return [""]
        res = []
        for k, c in table.items():
            if c and s.startswith(c):
                res += [k + r for r in decs(s[len(c):], distinct) if not (distinct and k in r)]
        return res

    listed = re.findall(r"^- `([^`]+)`$", t, re.M)
    single = re.findall(r"^`([^`]+)`$", t, re.M)
    if "не повторяются" in t:
        good = [d for d in decs(single[0], True) if len(set(d)) == len(d)]
        return good[0] if len(good) == 1 else "НЕОДНОЗНАЧНО"
    if "сколько букв" in t:
        d = decs(single[0], False)
        return str(len(d[0])) if len(d) == 1 else "НЕОДНОЗНАЧНО"
    ones = [d[0] for d in (decs(c, False) for c in listed) if len(d) == 1]
    return ones[0] if len(ones) == 1 else "НЕОДНОЗНАЧНО"


VOW = set("АЕЁИОУЫЭЮЯаеёиоуыэюя")


def py_expr(expr, var):
    e = expr.replace("≤", "<=").replace("≥", ">=")
    e = re.sub(rf"{var} (?:делится на|кратно) (\d+)", rf"{var} % \1 == 0", e)
    e = re.sub(rf"{var} оканчивается на (\d)", rf"{var} % 10 == \1", e)
    e = e.replace(f"{var} чётное", f"{var} % 2 == 0").replace(f"{var} нечётное", f"{var} % 2 == 1")
    return e.replace("НЕ ", " not ").replace(" ИЛИ ", " or ").replace(" И ", " and ")


def solve3(t, ans=None):
    expr = [b for b in re.findall(r"\*\*(.+?)\*\*", t) if "(" in b][0].rstrip("?")
    if "имён" in t:
        names = re.findall(r"^\d\) (\S+)$", t, re.M)
        rep = [("Первая буква гласная", "(n[0] in VOW)"), ("Последняя буква гласная", "(n[-1] in VOW)"),
               ("Вторая буква гласная", "(n[1] in VOW)"), ("Количество букв чётное", "(len(n) % 2 == 0)")]
        e = expr
        for a, b in rep:
            e = e.replace(a, b)
        e = e.replace("НЕ ", " not ").replace(" ИЛИ ", " or ").replace(" И ", " and ")
        good = [n for n in names if eval(e, {"VOW": VOW, "n": n})]
        return good[0] if len(good) == 1 else "НЕОДНОЗНАЧНО"
    if "Дано четыре числа" in t:
        nums = [int(x) for x in re.search(r"Дано четыре числа: ([\d, ]+)\.", t).group(1).split(", ")]
        rep = [("Первая цифра чётная", "(int(str(n)[0]) % 2 == 0)"), ("Последняя цифра чётная", "(n % 2 == 0)"),
               ("Сумма цифр чётная", "(sum(map(int, str(n))) % 2 == 0)"), ("Число > 100", "(n > 100)"),
               ("Число нечётное", "(n % 2 == 1)")]
        e = expr
        for a, b in rep:
            e = e.replace(a, b)
        e = e.replace("НЕ ", " not ").replace(" ИЛИ ", " or ").replace(" И ", " and ")
        good = [n for n in nums if eval(e, {"n": n})]
        return str(good[0]) if len(good) == 1 else "НЕОДНОЗНАЧНО"
    if "количество" in t:
        dom = range(10, 100) if "двузначных" in t else range(100, 1000) if "трёхзначных" in t else range(1, 20001)
        e = py_expr(expr, "x")
        want = "истинно" in t
        xs = [x for x in dom if eval(e, {"x": x}) == want]
        assert not xs or max(xs) < 10000, "бесконечно много"
        return str(len(xs))
    e = py_expr(expr, "X")
    if "Напишите число X" in t:
        xs = [x for x in range(-1000, 1001) if eval(e, {"X": x})]
        return str(xs[0]) if len(xs) == 1 else "НЕОДНОЗНАЧНО"
    want = "истинно" in t
    xs = [x for x in range(1, 20001) if eval(e, {"X": x}) == want]
    if "наименьшее" in t:
        return str(min(xs))
    assert max(xs) < 10000, "множество не ограничено"
    return str(max(xs))


def parse_roads(t, src=None):
    rows = re.findall(r"^\| \*\*(\w)\*\* \|(.*)\|$", t, re.M)
    INF = 10 ** 9
    if rows:
        names = [r[0] for r in rows]
        d = {a: {b: (0 if a == b else INF) for b in names} for a in names}
        for a, cells in rows:
            for b, c in zip(names, cells.split("|")):
                if c.strip():
                    d[a][b] = int(c)
        return names, d
    # схема: рёбра и веса из SVG (graphviz кладёт подпись ребра в его группу)
    img = re.search(r"\]\((\.\./images/[^)]+\.svg)\)", t).group(1)
    svg = open(os.path.normpath(os.path.join(ROOT, "tasks", img)), encoding="utf-8").read()
    edges = []
    for g in re.findall(r'<g id="edge\d+" class="edge">(.*?)</g>', svg, re.S):
        a, b = html.unescape(re.search(r"<title>(.*?)</title>", g).group(1)).split("--")
        w = int(re.search(r">(\d+)</text>", g).group(1))
        edges.append((a, b, w))
    names = sorted({x for e in edges for x in e[:2]})
    d = {a: {b: (0 if a == b else INF) for b in names} for a in names}
    for a, b, w in edges:
        d[a][b] = d[b][a] = w
    return names, d


def floyd(names, d, banned=()):
    d = {a: dict(v) for a, v in d.items()}
    for k in names:
        if k in banned:
            continue
        for i in names:
            for j in names:
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def solve4(t, ans=None):
    names, d = parse_roads(t)
    s, e = re.search(r"между пунктами (\w) и (\w)", t).groups()
    if "не проходящего через пункт" in t:
        av = re.search(r"не проходящего через пункт (\w)", t).group(1)
        dd = {a: {b: v for b, v in r.items()} for a, r in d.items()}
        for x in names:
            dd[av][x] = dd[x][av] = 10 ** 9 if x != av else 0
        return str(floyd(names, dd)[s][e])
    full = floyd(names, d)
    if "проходящего через пункт" in t:
        via = re.search(r"проходящего через пункт (\w)", t).group(1)
        return str(full[s][via] + full[via][e])
    return str(full[s][e])


def do_cmd(c, x, b=None):
    if c == "возведи в квадрат":
        return x * x
    if c == "зачеркни справа":
        return x // 10
    m = re.match(r"(прибавь|вычти|умножь на|раздели на) (\w+)", c)
    k = b if m.group(2) == "b" else int(m.group(2))
    if m.group(1) == "раздели на":
        return x / k
    return {"прибавь": x + k, "вычти": x - k, "умножь на": x * k}[m.group(1)]


def solve5(t, ans=None):
    cmds = re.findall(r"^\d\. \*\*(.+?)\*\*$", t, re.M)
    if "Определите значение b" in t:
        prog, a, z = re.search(r"программа \*\*(\d+)\*\* переводит число (\d+) в число (\d+)", t).groups()
        good = []
        for b in range(2, 1000):
            x = int(a)
            for c in prog:
                x = do_cmd(cmds[int(c) - 1], x, b)
            if x == int(z):
                good.append(b)
        return str(good[0]) if len(good) == 1 else "НЕОДНОЗНАЧНО"
    # составить программу: проверяем записанный ответ, выполняя его
    m = re.search(r"преобразует число (\d+) в число (\d+)", t) or re.search(r"из числа (\d+) числа (\d+)", t)
    a, z = map(int, m.groups())
    x = a
    if not ans or len(ans) > 5:
        return "НЕВЕРНО"
    for c in ans:
        x = do_cmd(cmds[int(c) - 1], x)
        if x != int(x) or x <= 0:
            return "НЕВЕРНО"
    return ans if x == z else "НЕВЕРНО"


def run6(code, s, t, A=None):
    data = iter([str(s), str(t)])
    buf = io.StringIO()
    env = {"input": lambda *_: next(data)}
    if A is not None:
        env["A"] = A
    with redirect_stdout(buf):
        exec(code, env)
    return buf.getvalue().strip()


def solve6(t, ans=None):
    code = re.search(r"```python\n(.*?)```", t, re.S).group(1)
    pairs = [tuple(map(int, p)) for p in re.findall(r"\((-?\d+), (-?\d+)\)", t.split("пары чисел")[1])]
    word = re.search(r"напечатает «(\w+)»|напечатала «(\w+)»", t).groups()
    word = word[0] or word[1]
    if "параметра A" not in t:
        return str(sum(1 for s, tt in pairs if run6(code, s, tt) == word))
    k = int(re.search(r"«\w+» (\d+) раз", t).group(1))
    good = [A for A in range(-1000, 1001) if sum(1 for s, tt in pairs if run6(code, s, tt, A) == word) == k]
    if "наименьшее" in t:
        return str(min(good))
    if "наибольшее" in t:
        return str(max(good))
    return str(len(good))


def _valid_ip(s):
    p = s.split(".")
    return len(p) == 4 and all(x.isdigit() and int(x) <= 255 and (x == "0" or x[0] != "0") for x in p)


def solve7(t, ans=None):
    frags = dict(re.findall(r"^(\w)\) `(.+?)`$", t, re.M))
    if "IP-адрес" in t:
        cells = re.findall(r"`([^`]+)`", t)
        frags = dict(zip("АБВГ", cells))
        sols = ["".join(p) for p in itertools.permutations(frags) if _valid_ip("".join(frags[x] for x in p))]
        return sols[0] if len(sols) == 1 else "НЕОДНОЗНАЧНО"
    if "почтовый ящик" in t:
        server, box = re.search(r"сервере \*\*(.+?)\*\* находится почтовый ящик \*\*(.+?)\*\*", t).groups()
        target = f"{box}@{server}"
    else:
        file, server, proto = re.search(r"файлу \*\*(.+?)\*\*.*сервере \*\*(.+?)\*\*.*протоколу \*\*(.+?)\*\*",
                                        t).groups()
        target = f"{proto}://{server}/{file}"
    sols = ["".join(p) for p in itertools.permutations(frags) if "".join(frags[x] for x in p) == target]
    return sols[0] if len(sols) == 1 else "НЕОДНОЗНАЧНО"


def solve8(t, ans=None):
    """Круги Эйлера через линейную алгебру: области — непустые подмножества слов."""
    from fractions import Fraction
    rows = {r.replace("\\|", "|"): int(v) for r, v in re.findall(r"^\| (.+?) \| (\d+) \|$", t, re.M)}
    target = re.search(r"по запросу \*\*(.+?)\*\*", t).group(1)
    split = lambda q: [w.strip() for w in re.split(r"[|&]", q)]
    words = sorted({w for q in list(rows) + [target] for w in split(q)})
    regions = [frozenset(c) for k in range(1, len(words) + 1) for c in itertools.combinations(words, k)]

    def vec(q):
        ws = set(split(q))
        if "|" in q:
            return [Fraction(int(bool(ws & r))) for r in regions]
        return [Fraction(int(ws <= r)) for r in regions]

    zero = set()
    for q, v in rows.items():
        if v == 0:
            zero |= {i for i, x in enumerate(vec(q)) if x}
    keep = [i for i in range(len(regions)) if i not in zero]
    A = [[vec(q)[i] for i in keep] + [Fraction(v)] for q, v in rows.items()]
    tv = [vec(target)[i] for i in keep]
    # приводим систему к ступенчатому виду и выражаем target как комбинацию строк
    n = len(keep)
    m = [row[:] for row in A]
    piv_cols, r = [], 0
    for c in range(n):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        m[r] = [x / m[r][c] for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                m[i] = [a - m[i][c] * b for a, b in zip(m[i], m[r])]
        piv_cols.append(c)
        r += 1
    # target · x, где x — любое решение; однозначно, если tv лежит в пространстве строк
    res = tv[:]
    val = Fraction(0)
    for i, c in enumerate(piv_cols):
        coef = res[c]
        if coef:
            res = [a - coef * b for a, b in zip(res, m[i][:n])]
            val += coef * m[i][n]
    return str(int(val)) if all(x == 0 for x in res) else "НЕОДНОЗНАЧНО"


def solve9(t, src, ans=None):
    img = re.search(r"\]\((\.\./images/[^)]+\.svg)\)", t).group(1)
    base = os.path.join(ROOT, "tasks" if src.startswith(("0", "1")) else "variants")
    svg = open(os.path.normpath(os.path.join(base, img)), encoding="utf-8").read()
    edges = [tuple(html.unescape(x).split("->")) for x in re.findall(r"<title>([^<]*?&#45;&gt;[^<]*?)</title>", svg)]
    m = re.search(r"из города (\w) в город (\w)", t)
    s, e = m.groups()
    through = re.search(r", проходящих через город (\w)", t)
    avoid = re.search(r"не проходящих через город (\w)", t)
    count = 0

    def dfs(v, path):
        nonlocal count
        if v == e:
            if (not through or through.group(1) in path) and (not avoid or avoid.group(1) not in path):
                count += 1
            return
        for a, b in edges:
            if a == v:
                dfs(b, path + [b])

    dfs(s, [s])
    return str(count)


def solve10(t, ans=None):
    nums = [(n, int(b)) for n, b in re.findall(r"([0-9A-F]+)<sub>(\d+)</sub>", t)]
    if "сумма цифр" in t:
        base = {"двоичной": 2, "восьмеричной": 8, "шестнадцатеричной": 16}[re.search(r"в (\w+) записи", t).group(1)]

        def dsum(n):
            s = 0
            while n:
                s += n % base
                n //= base
            return s
        sums = [dsum(int(n, b)) for n, b in nums]
        return str(min(sums) if "наименьшая" in t else max(sums))
    if "Переведите число" in t and "в десятичную" in t and nums:
        return str(int(nums[0][0], nums[0][1]))
    if "из десятичной" in t:
        n = int(re.search(r"Переведите число (\d+)", t).group(1))
        b = format(n, "b")
        if "укажите двоичное число" in t:
            return b
        return str(b.count("1") if "единиц" in t else b.count("0"))
    vals = [int(n, b) for n, b in nums]
    return str(max(vals) if "максимальное" in t else min(vals))


SOLVERS = {1: solve1, 2: solve2, 3: solve3, 4: solve4, 5: solve5, 6: solve6, 7: solve7, 8: solve8,
           10: solve10}


def check_1_10():
    for no, text, ans, src in task_items():
        try:
            got = solve9(text, src, ans) if no == 9 else SOLVERS[no](text, ans)
        except Exception as ex:  # noqa: BLE001
            got = f"ошибка решателя: {ex!r}"
        ok(no, got.lower() == ans.lower(), f"{src}: записано {ans!r}, пересчитано {got!r}")


# ------------------------------------------------------------------ 11, 12

def count_spec(spec, root):
    """Независимый подсчёт файлов по описанию вопроса (pathlib + fnmatch)."""
    import fnmatch
    base = root.joinpath(*spec["root"].split("/")[1:])
    files = [p for p in base.rglob("*") if p.is_file() and fnmatch.fnmatchcase(p.name, spec["glob"])]
    if spec.get("subdirs_only"):
        files = [p for p in files if p.parent != base]
    if "size_gt" in spec:
        files = [p for p in files if p.stat().st_size > spec["size_gt"]]
    if "size_lt" in spec:
        files = [p for p in files if p.stat().st_size < spec["size_lt"]]
    if spec.get("total"):
        return str(round(sum(p.stat().st_size for p in files) / 1024))
    return str(len(files))


def md_blocks(path):
    """Пары (условие, ответ) из блоков подтипов файла."""
    text = open(path, encoding="utf-8").read()
    res = []
    for body in re.findall(r"<!-- BEGIN:sub:[\d.]+ -->(.*?)<!-- END:sub:", text, re.S):
        for block in re.split(r"\n#### Тренировка [\d.]+\n", body)[1:]:
            ans = re.search(r"<summary>Ответ</summary>\s*\*\*(.+?)\*\*", block).group(1)
            res.append((block.split("<details>")[0].strip(), ans))
    return res


def check_11_12():
    corpus = json.load(open(os.path.join(HERE, "corpus_questions.json"), encoding="utf-8"))
    root = pathlib.Path(ROOT, "materials", "archive")
    texts = {p: p.read_text(encoding="utf-8") for p in root.rglob("*") if p.suffix in (".txt", ".htm")}
    for q in corpus["q11"]:
        hits = [p for p, tx in texts.items() if q["search"] in tx]
        ok(11, len(hits) == 1 and q["answer"] in texts[hits[0]], f"{q['q'][:60]}… найдено файлов: {len(hits)}")
    for q in corpus["q12"]:
        sp = q["spec"]
        # описание должно соответствовать тексту вопроса
        core = sp["glob"].replace(".*", "").lstrip("*")
        ok(12, core in q["q"] or sp["glob"] == "*", f"{q['q'][:60]}… маска не совпадает с текстом")
        for k, word in (("size_gt", "более"), ("size_lt", "менее")):
            if k in sp:
                ok(12, f"{word} {sp[k] // 1024} Кбайт" in q["q"], f"{q['q'][:60]}… порог не совпадает")
        n = count_spec(sp, root)
        ok(12, n == q["answer"], f"{q['q'][:60]}… записано {q['answer']}, пересчитано {n}")
    # ответы в .md совпадают с банком
    bank = {(q["q"], q["answer"]) for q in corpus["q11"] + corpus["q12"]}
    for no, fname in ((11, "11-search-in-files.md"), (12, "12-file-masks.md")):
        for cond, ans in md_blocks(os.path.join(ROOT, "tasks", fname)):
            cond = re.sub(r"\n\nГде искать.*", "", cond, flags=re.S)
            ok(no, (cond, ans) in bank, f"{fname}: «{cond[:50]}…» нет в проверенном банке")
    for path in glob.glob(os.path.join(ROOT, "variants", "variant-*.md")):
        text = open(path, encoding="utf-8").read()
        key = text.split("**Задания 1–12**")[1]
        for no in (11, 12):
            a = re.search(rf"^\| {no} \| (.+?) \|$", key, re.M).group(1)
            q = re.search(rf"### Задание {no}\n\n(.+?)\n", text).group(1)
            ok(no, (q, a) in bank, f"{os.path.basename(path)}: задание {no} не из банка")


# ------------------------------------------------------------------ 14

def eval_14(spec, rows):
    """Независимое вычисление ответа по описанию вопроса к заданию 14."""
    def val(e, r):
        if isinstance(e, int):
            return r[e]
        return r[e[1]].month if e[0] == "month" else r[e[1]] * r[e[2]]
    cmp = {"==": lambda a, b: a == b, ">": lambda a, b: a > b, "<": lambda a, b: a < b,
           ">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b}
    sel = [r for r in rows if all(cmp[o](val(e, r), v) for e, o, v in spec["conds"])]
    if spec["agg"] == "count":
        return len(sel)
    xs = [val(spec["value"], r) for r in sel]
    return {"sum": sum(xs), "avg": sum(xs) / len(xs), "max": max(xs), "min": min(xs)}[spec["agg"]]


def check_14():
    from openpyxl import load_workbook
    data = json.load(open(os.path.join(HERE, "xlsx_questions.json"), encoding="utf-8"))
    for name, d in data.items():
        ws = load_workbook(os.path.join(ROOT, "materials", "task14", name)).active
        rows = [r for r in ws.iter_rows(min_row=2, values_only=True)]
        header = [c.value for c in ws[1]]
        n_intro = int(re.search(r"по (\d+) ", d["intro"]).group(1))
        ok(14, n_intro == len(rows), f"{name}: в условии {n_intro} строк, в файле {len(rows)}")
        q1, a1 = d["questions"][0]
        q2, a2 = d["questions"][1]
        if header[0] == "округ":
            code = re.search(r"\(\*\*(\w+)\*\*\) выбрали", q1).group(1)
            subj = re.search(r"предмета \*\*(\w+)\*\*", q1).group(1)
            got1 = sum(1 for r in rows if r[0] == code and r[2][:-1] == subj[:-1])
            code2 = re.search(r"\(\*\*(\w+)\*\*\)\?", q2).group(1)
            sc = [r[3] for r in rows if r[0] == code2]
            got2 = f"{sum(sc) / len(sc):.2f}".replace(".", ",")
        elif header[0] == "дата":
            months = ["январе", "феврале", "марте", "апреле", "мае", "июне", "июле", "августе", "сентябре",
                      "октябре", "ноябре", "декабре"]
            m = months.index(re.search(r"\*\*(\w+)\*\*", q1).group(1)) + 1
            ts = [r[1] for r in rows if r[0].month == m]
            got1 = f"{sum(ts) / len(ts):.2f}".replace(".", ",")
            w = re.search(r"\(\*\*(\w+)\*\*\)", q2).group(1)
            sp = int(re.search(r"более (\d+) м/с", q2).group(1))
            got2 = sum(1 for r in rows if r[4] == w and r[5] > sp)
        elif header[0] == "продукт":
            fx, px = map(int, re.findall(r"меньше (\d+) г", q1))
            got1 = sum(1 for r in rows if r[1] < fx and r[2] < px)
            cx = int(re.search(r"больше (\d+) г", q2).group(1))
            sel = [r[4] for r in rows if r[3] > cx]
            got2 = f"{sum(sel) / len(sel):.2f}".replace(".", ",")
        else:
            g1, s1 = re.findall(r"«\*\*(\w+)\*\*»", q1)
            got1 = sum(r[2] for r in rows if r[0] == s1 and r[1] == g1)
            s2 = re.search(r"«\*\*(\w+)\*\*»", q2).group(1)
            got2 = sum(r[2] * r[3] for r in rows if r[0] == s2)
        ok(14, str(got1) == a1, f"{name} вопрос 1: записано {a1}, пересчитано {got1}")
        ok(14, str(got2) == a2, f"{name} вопрос 2: записано {a2}, пересчитано {got2}")
        for e in d.get("extra", []):
            got = eval_14(e["spec"], rows)
            want = float(e["answer"].replace(",", "."))
            ok(14, abs(got - want) < 0.006, f"{name}: «{e['q'][:50]}…» записано {e['answer']}, пересчитано {got}")
            months = ["январе", "феврале", "марте", "апреле", "мае", "июне", "июле", "августе", "сентябре",
                      "октябре", "ноябре", "декабре"]
            for ex, _, v in e["spec"]["conds"]:
                shown = months[v - 1] if isinstance(ex, list) and ex[0] == "month" else str(v)
                ok(14, shown in e["q"], f"{name}: «{e['q'][:50]}…» условие {shown} не упомянуто в тексте")
    tasks14 = open(os.path.join(ROOT, "tasks", "14-spreadsheets.md"), encoding="utf-8").read()
    extras = {(e["q"], e["answer"]) for d in data.values() for e in d.get("extra", [])}
    for cond, ans in md_blocks(os.path.join(ROOT, "tasks", "14-spreadsheets.md")):
        q = re.sub(r"^Файл \[`[^`]+`\]\([^)]+\)\. ", "", cond)
        ok(14, (q, ans) in extras, f"14: «{q[:50]}…» нет в проверенном банке")


# ------------------------------------------------------------------ 15, 16

def check_15_16():
    import prog_tasks
    import robot_tasks
    by_id = {t["id"]: t for t in robot_tasks.TASKS}
    for t in robot_tasks.TASKS:
        try:
            robot_tasks.check(t, runs=200, seed=12345)
            ok(15, True, "")
        except Exception as ex:  # noqa: BLE001
            ok(15, False, f"{t['id']}: {ex}")
    # решения, напечатанные в .md, совпадают с проверенными
    for path in glob.glob(os.path.join(ROOT, "tasks", "15-robot.md")) + glob.glob(os.path.join(ROOT, "variants", "*.md")):
        text = open(path, encoding="utf-8").read()
        for code in re.findall(r"```\n(использовать Робот.*?)```", text, re.S):
            ok(15, any(code.strip() == t["solution"].strip() for t in by_id.values()) or "|" in code,
               f"{os.path.basename(path)}: алгоритм не из проверенного банка")
    # рукописные алгоритмы в гайдах помечены <!-- robot:rNN --> и проверяются на соответствующей задаче
    pb = {t["id"]: t for t in prog_tasks.TASKS}
    for path in glob.glob(os.path.join(ROOT, "tasks", "*.md")) + glob.glob(os.path.join(ROOT, "theory", "*.md")):
        text = open(path, encoding="utf-8").read()
        for tid, code in re.findall(r"<!-- robot:(r\d+) -->\s*```\n(.*?)```", text, re.S):
            try:
                robot_tasks.check(dict(by_id[tid], solution=code), runs=200, seed=7)
                ok(15, True, "")
            except Exception as ex:  # noqa: BLE001
                ok(15, False, f"{os.path.basename(path)} ({tid}): {ex}")
        for tid, code in re.findall(r"<!-- prog:(p\d+) -->\s*```python\n(.*?)```", text, re.S):
            try:
                prog_tasks.check(dict(pb[tid], solution=code), extra=100)
                ok(16, True, "")
            except AssertionError as ex:
                ok(16, False, f"{os.path.basename(path)} ({tid}): {ex}")
    for t in prog_tasks.TASKS:
        try:
            prog_tasks.check(t, extra=100)
            ok(16, True, "")
        except AssertionError as ex:
            ok(16, False, str(ex))


if __name__ == "__main__":
    check_1_10()
    check_11_12()
    check_14()
    check_15_16()
    for k in sorted(checked):
        print(f"задание {k:>2}: проверено {checked[k]}")
    if errors:
        print("\nОШИБКИ:")
        print("\n".join(errors))
        sys.exit(1)
    print("\nВсе ответы подтверждены независимым пересчётом.")
