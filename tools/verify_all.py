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
    """(номер задания, текст условия, ответ, источник) для tasks/*.md и variants/*.md."""
    items = []
    for path in sorted(glob.glob(os.path.join(ROOT, "tasks", "*.md"))):
        no = int(os.path.basename(path)[:2])
        text = open(path, encoding="utf-8").read()
        m = re.search(r"<!-- BEGIN:generated -->(.*)<!-- END:generated -->", text, re.S)
        if not m or no > 10:
            continue
        for block in re.split(r"\n### Задача \d+\n", m.group(1))[1:]:
            ans = re.search(r"<summary>Ответ</summary>\s*\*\*(.+?)\*\*", block).group(1)
            items.append((no, block.split("<details>")[0], ans, os.path.basename(path)))
    for path in sorted(glob.glob(os.path.join(ROOT, "variants", "variant-*.md"))):
        text = open(path, encoding="utf-8").read()
        key = text.split("**Задания 1–12**")[1].split("**Задание 13**")[0]
        answers = dict(re.findall(r"^\| (\d+) \| (.+?) \|$", key, re.M))
        for no in range(1, 11):
            m = re.search(rf"### Задание {no}\n(.*?)(?=\n### Задание|\n## Часть)", text, re.S)
            items.append((no, m.group(1), answers[str(no)], os.path.basename(path)))
    return items


# ------------------------------------------------------------------ решатели 1–10

def solve1(t):
    bits = int(re.search(r"кодируется (\d+) бит", t).group(1))
    if "страниц" in t:
        nums = [int(x) for x in re.findall(r"(\d+) (?:страниц|строк|символ)", t)]
        p, l, c = nums[:3]
        return str(p * l * c * bits // 8 // 1024)
    sentence = re.search(r"«(.+?) – ", t).group(1)
    words = sentence.split(", ")
    m = re.search(r"на (\d+) (байт|бит)", t)
    delta = int(m.group(1)) * (8 if m.group(2).startswith("байт") else 1)
    cands = [w for w in words if (len(w) + 2) * bits == delta]
    assert len(cands) == 1, cands
    return cands[0].lower()


def solve2(t):
    head, codes = re.findall(r"^\| (.+) \|$", t, re.M)[:2]
    table = dict(zip(head.split(" | "), [c.strip("`") for c in codes.split(" | ")]))

    def decs(s, distinct):
        if not s:
            return [""]
        res = []
        for k, c in table.items():
            if s.startswith(c):
                res += [k + r for r in decs(s[len(c):], distinct) if not (distinct and k in r)]
        return res

    chains = re.findall(r"`([^`]+)`", t.split(codes)[1])
    if "не повторяются" in t:
        return [d for d in decs(chains[0], True) if len(set(d)) == len(d)][0] if len(
            [d for d in decs(chains[0], True) if len(set(d)) == len(d)]) == 1 else "НЕОДНОЗНАЧНО"
    uniq = [decs(c, False) for c in chains]
    ones = [d[0] for d in uniq if len(d) == 1]
    return ones[0] if len(ones) == 1 else "НЕОДНОЗНАЧНО"


VOW = set("АЕЁИОУЫЭЮЯаеёиоуыэюя")


def solve3(t):
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
    e = re.sub(r"X делится на (\d+)", r"X % \1 == 0", expr)
    e = e.replace("X чётное", "X % 2 == 0").replace("X нечётное", "X % 2 == 1")
    e = e.replace("НЕ ", " not ").replace(" ИЛИ ", " or ").replace(" И ", " and ").replace("<=", "<=")
    want = "истинно" in t
    xs = [x for x in range(1, 20001) if eval(e, {"X": x}) == want]
    if "наименьшее" in t:
        return str(min(xs))
    assert max(xs) < 10000, "множество не ограничено"
    return str(max(xs))


def parse_roads(t):
    rows = re.findall(r"^\| \*\*(\w)\*\* \|(.*)\|$", t, re.M)
    names = [r[0] for r in rows]
    INF = 10 ** 9
    d = {a: {b: (0 if a == b else INF) for b in names} for a in names}
    for a, cells in rows:
        for b, c in zip(names, cells.split("|")):
            if c.strip():
                d[a][b] = int(c)
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


def solve4(t):
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


def solve5(t):
    cmds = re.findall(r"^\d\. \*\*(.+?)\*\*$", t, re.M)

    def op(c, b=None):
        m = re.match(r"(прибавь|вычти|умножь на|раздели на) (\w+)", c)
        k = b if m.group(2) == "b" else int(m.group(2))
        return {"прибавь": lambda x: x + k, "вычти": lambda x: x - k, "умножь на": lambda x: x * k,
                "раздели на": lambda x: x / k}[m.group(1)]

    if "Определите значение b" in t:
        prog, a, z = re.search(r"программа \*\*(\d+)\*\* переводит число (\d+) в число (\d+)", t).groups()
        good = []
        for b in range(2, 1000):
            x = int(a)
            for c in prog:
                x = op(cmds[int(c) - 1], b)(x)
            if x == int(z):
                good.append(b)
        return str(good[0]) if len(good) == 1 else "НЕОДНОЗНАЧНО"
    a, z = map(int, re.search(r"преобразует число (\d+) в число (\d+)", t).groups())
    for L in range(1, 6):
        for p in itertools.product("12", repeat=L):
            x = a
            for c in p:
                x = op(cmds[int(c) - 1])(x)
            if x == z:
                return "".join(p)
    return "НЕТ"


def run6(code, s, t, A=None):
    data = iter([str(s), str(t)])
    buf = io.StringIO()
    env = {"input": lambda *_: next(data)}
    if A is not None:
        env["A"] = A
    with redirect_stdout(buf):
        exec(code, env)
    return buf.getvalue().strip()


def solve6(t):
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


def solve7(t):
    file, server, proto = re.search(r"файлу \*\*(.+?)\*\*.*сервере \*\*(.+?)\*\*.*протоколу \*\*(.+?)\*\*", t).groups()
    url = f"{proto}://{server}/{file}"
    frags = dict(re.findall(r"^(\w)\) `(.+?)`$", t, re.M))
    # перебор всех перестановок — независимо от «смысла» фрагментов
    for perm in itertools.permutations(frags):
        if "".join(frags[x] for x in perm) == url:
            return "".join(perm)
    return "НЕТ"


def solve8(t):
    rows = {r.replace("\\|", "|"): int(v) for r, v in re.findall(r"^\| (.+?) \| (\d+) \|$", t, re.M)}
    target = re.search(r"по запросу \*\*(.+?)\*\*", t).group(1)
    words = [w for w in rows if "|" not in w and "&" not in w] + [target]
    pair = next(k for k in list(rows) + [target] if "|" in k or "&" in k)
    a, b = re.split(r" [|&] ", pair)
    # неизвестные области: x = только A, y = только B, z = оба; перебор по сетке
    for z in range(0, 20001, 10):
        for x in range(0, 20001, 10):
            vals = {a: x + z}
            known = dict(rows)
            if f"{a} & {b}" in known and known[f"{a} & {b}"] != z:
                break
            if a in known and known[a] != x + z:
                continue
            # y из любого известного соотношения
            if b in known:
                y = known[b] - z
            elif f"{a} | {b}" in known:
                y = known[f"{a} | {b}"] - x - z
            else:
                continue
            allv = {a: x + z, b: y + z, f"{a} | {b}": x + y + z, f"{a} & {b}": z}
            if all(allv[k] == v for k, v in known.items()) and y >= 0:
                return str(allv[target])
    return "НЕТ"


def solve9(t, src):
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


def solve10(t):
    nums = [(n, int(b)) for n, b in re.findall(r"([0-9A-F]+)<sub>(\d+)</sub>", t)]
    if "Переведите число" in t and "в десятичную" in t and nums:
        return str(int(nums[0][0], nums[0][1]))
    if "из десятичной" in t:
        n = int(re.search(r"Переведите число (\d+)", t).group(1))
        b = bin(n)[2:]
        return str(b.count("1") if "единиц" in t else b.count("0"))
    vals = [int(n, b) for n, b in nums]
    return str(max(vals) if "максимальное" in t else min(vals))


SOLVERS = {1: solve1, 2: solve2, 3: solve3, 4: solve4, 5: solve5, 6: solve6, 7: solve7, 8: solve8,
           10: solve10}


def check_1_10():
    for no, text, ans, src in task_items():
        try:
            got = solve9(text, src) if no == 9 else SOLVERS[no](text)
        except Exception as ex:  # noqa: BLE001
            got = f"ошибка решателя: {ex!r}"
        ok(no, got.lower() == ans.lower(), f"{src}: записано {ans!r}, пересчитано {got!r}")


# ------------------------------------------------------------------ 11, 12

def check_11_12():
    corpus = json.load(open(os.path.join(HERE, "corpus_questions.json"), encoding="utf-8"))
    root = pathlib.Path(ROOT, "materials", "archive")
    texts = {p: p.read_text(encoding="utf-8") for p in root.rglob("*") if p.suffix in (".txt", ".htm")}
    for q in corpus["q11"]:
        hits = [p for p, tx in texts.items() if q["search"] in tx]
        ok(11, len(hits) == 1 and q["answer"] in texts[hits[0]], f"{q['q'][:60]}… найдено файлов: {len(hits)}")
    files = [p for p in root.rglob("*") if p.is_file()]
    for q in corpus["q12"]:
        m = re.search(r"\*\*(\.\w+)\*\*", q["q"])
        if q.get("kind") == "ext":
            n = sum(1 for p in files if p.suffix == m.group(1))
        elif q.get("kind") == "year":
            y = re.search(r"archive/(\d+)", q["q"]).group(1)
            n = sum(1 for p in (root / y).rglob("*" + m.group(1)) if p.is_file())
        elif q.get("kind") == "size":
            lim = int(re.search(r"более (\d+) Кбайт", q["q"]).group(1))
            n = sum(1 for p in files if p.suffix == m.group(1) and p.stat().st_size > lim * 1024)
        elif q.get("kind") == "name":
            n = sum(1 for p in files if p.stem == "article-1")
        else:
            n = round(sum(p.stat().st_size for p in (root / "photo").rglob("*") if p.is_file()) / 1024)
        ok(12, str(n) == q["answer"], f"{q['q'][:60]}… записано {q['answer']}, пересчитано {n}")
    # ответы в файлах совпадают с банком
    for path in glob.glob(os.path.join(ROOT, "variants", "variant-*.md")):
        text = open(path, encoding="utf-8").read()
        a11 = re.search(r"^\| 11 \| (.+?) \|$", text.split("**Задания 1–12**")[1], re.M).group(1)
        q11 = re.search(r"### Задание 11\n\n(.+?)\n", text).group(1)
        ok(11, any(q["q"] == q11 and q["answer"] == a11 for q in corpus["q11"]), f"{os.path.basename(path)}: 11")


# ------------------------------------------------------------------ 14

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
            ok(15, any(code.strip() == t["solution"].strip() for t in by_id.values()) or "| 1." in code,
               f"{os.path.basename(path)}: алгоритм не из проверенного банка")
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
