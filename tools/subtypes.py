"""Генераторы задач по подтипам для заданий 1–10 (для подробных гайдов tasks/*.md).

SUBTYPES[ключ] = (название, функция(rng) -> {"text", "answer", ["image"]}).
Ключ вида "3.2": задание 3, подтип 2. Ответы вычисляются программно, а независимо
перепроверяются в tools/verify_all.py.
"""

import itertools
import random
import subprocess

import gen_tasks as g

FONT = 'fontname="DejaVu Sans"'


def retry(fn, cond, rng, tries=5000):
    for _ in range(tries):
        r = fn(rng)
        if cond(r):
            return r
    raise RuntimeError(fn.__name__)


# ------------------------------------------------------------------ 1. объём текста

ENC_BY_BITS = {8: "КОИ-8", 16: "UTF-16", 32: "UTF-32"}


def t1_inverse(rng):
    """Известен объём — найти число символов в строке / строк на странице / бит на символ."""
    while True:
        p = rng.choice([4, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64])
        l = rng.choice([30, 32, 40, 48, 56, 64])
        c = rng.choice([32, 40, 48, 50, 56, 60, 64])
        i = rng.choice([8, 16])
        total = p * l * c * i
        if total % (8 * 1024) == 0:
            break
    kb = total // 8 // 1024
    what = rng.choice(["chars", "lines", "bits"])
    doc = rng.choice(["Реферат", "Доклад", "Рассказ"])
    if what == "chars":
        text = (f"{doc}, набранный на компьютере, содержит {p} {g.plural(p, 'страницу', 'страницы', 'страниц')}, "
                f"на каждой странице {l} {g.plural(l, 'строка', 'строки', 'строк')}. Каждый символ кодируется "
                f"{i} битами. Информационный объём текста составляет {kb} Кбайт. "
                "Сколько символов в каждой строке?")
        ans = c
    elif what == "lines":
        text = (f"{doc}, набранный на компьютере, содержит {p} {g.plural(p, 'страницу', 'страницы', 'страниц')}, "
                f"в каждой строке {c} {g.plural(c, 'символ', 'символа', 'символов')}. Каждый символ кодируется "
                f"{i} битами. Информационный объём текста составляет {kb} Кбайт. "
                "Сколько строк на каждой странице?")
        ans = l
    else:
        text = (f"{doc}, набранный на компьютере, содержит {p} {g.plural(p, 'страницу', 'страницы', 'страниц')}, "
                f"на каждой странице {l} {g.plural(l, 'строка', 'строки', 'строк')}, в каждой строке {c} "
                f"{g.plural(c, 'символ', 'символа', 'символов')}. Информационный объём текста составляет {kb} Кбайт. "
                "Сколькими битами кодируется каждый символ?")
        ans = i
    return {"text": text, "answer": str(ans)}


def t1_recode(rng):
    """Текст перекодировали — объём изменился — найти число символов."""
    a, b = rng.choice([(16, 8), (32, 16), (32, 8), (8, 16)])
    k = rng.randint(12, 120)
    diff_bits = abs(a - b) * k
    unit = rng.choice(["бит", "байт"])
    if unit == "байт" and diff_bits % 8:
        unit = "бит"
    diff = diff_bits if unit == "бит" else diff_bits // 8
    word = "уменьшился" if a > b else "увеличился"
    text = (f"Текст был записан в {a}-битной кодировке ({ENC_BY_BITS[a]}), а затем его перекодировали в "
            f"{b}-битную кодировку ({ENC_BY_BITS[b]}). При этом информационный объём текста {word} на {diff} "
            f"{g.plural(diff, unit, unit + 'а', unit)}. Сколько символов в тексте?").replace("байта", "байта")
    return {"text": text, "answer": str(k)}


# ------------------------------------------------------------------ 2. декодирование

ALPHA = {chr(65 + i): str(i + 1) for i in range(26)}
EN_WORDS = ["CAT", "DOG", "HAT", "BEE", "TEA", "SUN", "MAP", "BAG", "CAKE", "BIKE", "LAKE", "BALL", "TREE",
            "FISH", "BIRD", "KITE", "HATE", "FARM", "BEAR", "HERO", "IDEA", "JAZZ", "QUIZ", "WAVE", "ZERO",
            "BOOK", "MILK", "PARK", "ROAD", "STAR", "TOWN", "WIND", "GIFT", "HOME", "LAMP"]


def _alpha_table_md():
    a = [chr(65 + i) for i in range(13)]
    b = [chr(65 + i) for i in range(13, 26)]
    return ("| " + " | ".join(a) + " |\n|" + "---|" * 13 + "\n| " + " | ".join(ALPHA[x] for x in a) + " |\n\n"
            "| " + " | ".join(b) + " |\n|" + "---|" * 13 + "\n| " + " | ".join(ALPHA[x] for x in b) + " |")


def t2_alpha(rng):
    """Номера букв латинского алфавита: из четырёх шифровок одна расшифровывается однозначно."""
    uniq = [w for w in EN_WORDS if len(g._decodings(g._enc(w, ALPHA), ALPHA, limit=10)) == 1]
    amb = [w for w in EN_WORDS if len(g._decodings(g._enc(w, ALPHA), ALPHA, limit=10)) > 1]
    ans = rng.choice(uniq)
    codes = [g._enc(w, ALPHA) for w in [ans] + rng.sample(amb, 3)]
    rng.shuffle(codes)
    name = rng.choice(["Кирилл", "Петя", "Маша", "Аня"])
    text = (f"{name} шифрует английские слова, записывая вместо каждой буквы её номер в алфавите (без пробелов). "
            f"Номера букв даны в таблице:\n\n{_alpha_table_md()}\n\n"
            "Некоторые шифровки можно расшифровать не одним способом. Например, `16118` может означать «AFAR», "
            "может — «PAR», а может — «AFAAH». Даны четыре шифровки:\n\n" + "\n".join(f"- `{c}`" for c in codes) +
            "\n\nТолько одна из них расшифровывается единственным способом. Найдите её и расшифруйте. "
            "То, что получилось, запишите в качестве ответа.")
    return {"text": text, "answer": ans}


MORSE = {"А": "•–", "Б": "–•••", "В": "•––", "Г": "––•", "Д": "–••", "Е": "•", "Ж": "•••–", "З": "––••",
         "И": "••", "К": "–•–", "Л": "•–••", "М": "––", "Н": "–•", "О": "–––", "П": "•––•", "Р": "•–•",
         "С": "•••", "Т": "–", "У": "••–", "Щ": "––•–"}


def t2_count(rng):
    """Сколько букв в сообщении: неравномерный код (азбука Морзе или цифры), расшифровка единственна."""
    for _ in range(50000):
        if rng.random() < 0.5:
            letters = rng.sample(sorted(MORSE), 5)
            table = {c: MORSE[c] for c in letters}
            intro = ("От разведчика была получена шифрованная радиограмма, переданная с использованием азбуки "
                     "Морзе. При передаче радиограммы было потеряно разбиение на буквы, но известно, что "
                     "в радиограмме использовались только следующие буквы:")
        else:
            letters = rng.sample("АБВГДЕЖ", 6)
            codes = rng.sample(["10", "101", "12", "102", "122", "22", "120", "21", "201", "11", "212"], 6)
            table = dict(zip(sorted(letters), codes))
            intro = ("Мальчики играли в шпионов и закодировали сообщение придуманным шифром. В сообщении "
                     "присутствуют только буквы из приведённого фрагмента кодовой таблицы:")
        msg = "".join(rng.choice(sorted(table)) for _ in range(rng.randint(4, 7)))
        s = g._enc(msg, table)
        if len(g._decodings(s, table, limit=5)) == 1 and len(s) >= 7:
            text = (f"{intro}\n\n{g._table_md(dict(sorted(table.items())))}\n\nСообщение:\n\n`{s}`\n\n"
                    "Определите текст сообщения. В ответе укажите, сколько букв было в исходном сообщении.")
            return {"text": text, "answer": str(len(msg))}
    raise RuntimeError


# ------------------------------------------------------------------ 3. логика

def _atom_text(a):
    k, v = a
    return {"<": f"x < {v}", ">": f"x > {v}", "<=": f"x ≤ {v}", ">=": f"x ≥ {v}", "even": "x чётное",
            "odd": "x нечётное", "div": f"x кратно {v}", "end": f"x оканчивается на {v}"}[k]


def _atom_eval(a, x):
    k, v = a
    return {"<": lambda: x < v, ">": lambda: x > v, "<=": lambda: x <= v, ">=": lambda: x >= v,
            "even": lambda: x % 2 == 0, "odd": lambda: x % 2 == 1, "div": lambda: x % v == 0,
            "end": lambda: x % 10 == v}[k]()


def t3_count(rng):
    """Количество чисел (натуральных, двузначных, трёхзначных), для которых выражение истинно/ложно."""
    for _ in range(20000):
        dom_name, dom = rng.choice([("натуральных", None), ("натуральных двузначных", range(10, 100)),
                                    ("натуральных трёхзначных", range(100, 1000))])
        lo_v, hi_v = (10, 99) if dom is None or dom.start == 10 else (100, 999)
        a = (rng.choice(["<", ">", "<=", ">="]), rng.randint(lo_v, hi_v))
        b = rng.choice([(rng.choice(["<", ">", "<=", ">="]), rng.randint(lo_v, hi_v)), ("even", 0), ("odd", 0),
                        ("div", rng.choice([3, 4, 5, 7, 9, 11, 13])), ("end", rng.randint(0, 9))])
        na, nb = rng.random() < 0.5, rng.random() < 0.5
        op = rng.choice(["И", "ИЛИ"])
        want = rng.choice([True, True, False])
        outer_not = rng.random() < 0.25

        def f(x):
            va = _atom_eval(a, x) != na
            vb = _atom_eval(b, x) != nb
            r = (va and vb) if op == "И" else (va or vb)
            return (not r) if outer_not else r

        rng_x = dom if dom is not None else range(1, 5000)
        xs = [x for x in rng_x if f(x) == want]
        if dom is None and xs and max(xs) > 4000:
            continue  # бесконечно много
        if not 2 <= len(xs) <= 70:
            continue
        ta = ("НЕ " if na else "") + f"({_atom_text(a)})"
        tb = ("НЕ " if nb else "") + f"({_atom_text(b)})"
        expr = f"{ta} {op} {tb}"
        if outer_not:
            expr = f"НЕ ({expr})"
        text = (f"Определите количество {dom_name} чисел x, для которых {'истинно' if want else 'ложно'} "
                f"логическое выражение:\n\n**{expr}**")
        return {"text": text, "answer": str(len(xs))}
    raise RuntimeError


def t3_extreme(want):
    def gen(rng):
        return retry(g.t3_number, lambda r: (("истинно" in r["text"]) == want), rng)
    gen.__name__ = f"t3_extreme_{want}"
    return gen


def t3_unique(rng):
    """Напишите число X, для которого истинно … (подходит ровно одно целое число)."""
    for _ in range(5000):
        v = rng.randint(3, 40)
        # строим «X ≥ v» и «X ≤ v» разными способами
        low = rng.choice([(">=", v), (">", v - 1)])
        high = rng.choice([("<=", v), ("<", v + 1)])
        parts = []
        for atom, neg_form in ((low, {">=": ("<", v), ">": ("<=", v - 1)}),
                               (high, {"<=": (">", v), "<": (">=", v + 1)})):
            if rng.random() < 0.5:
                parts.append("НЕ (" + _atom_text(neg_form[atom[0]]).replace("x", "X") + ")")
            else:
                parts.append("(" + _atom_text(atom).replace("x", "X") + ")")
        rng.shuffle(parts)
        text = f"Напишите число X, для которого истинно высказывание:\n\n**{parts[0]} И {parts[1]}**"
        return {"text": text, "answer": str(v)}
    raise RuntimeError


def t3_pick_numbers(rng):
    """Выбор из четырёх чисел по свойствам цифр."""
    atoms = {
        "Первая цифра чётная": lambda n: int(str(n)[0]) % 2 == 0,
        "Последняя цифра чётная": lambda n: n % 2 == 0,
        "Сумма цифр чётная": lambda n: sum(map(int, str(n))) % 2 == 0,
        "Число > 100": lambda n: n > 100,
        "Число нечётное": lambda n: n % 2 == 1,
    }
    keys = list(atoms)
    for _ in range(20000):
        ka, kb = rng.sample(keys, 2)
        na, nb = rng.random() < 0.5, rng.random() < 0.5
        op = rng.choice(["И", "ИЛИ"])
        nums = rng.sample(range(10, 1000), 4)

        def f(n):
            va = atoms[ka](n) != na
            vb = atoms[kb](n) != nb
            return (va and vb) if op == "И" else (va or vb)

        good = [n for n in nums if f(n)]
        if len(good) != 1:
            continue
        ta = ("НЕ " if na else "") + f"({ka})"
        tb = ("НЕ " if nb else "") + f"({kb})"
        text = (f"Дано четыре числа: {', '.join(map(str, nums))}. Для какого из приведённых чисел **истинно** "
                f"высказывание:\n\n**{ta} {op} {tb}**?\n\nВ ответ запишите это число.")
        return {"text": text, "answer": str(good[0])}
    raise RuntimeError


def t3_pick(rng):
    return g.t3_names(rng) if rng.random() < 0.4 else t3_pick_numbers(rng)


# ------------------------------------------------------------------ 4. кратчайший путь

def t4_kind(kind):
    marks = {"plain": lambda t: "проходящего" not in t, "via": lambda t: "проходящего через" in t
             and "не проходящего" not in t, "avoid": lambda t: "не проходящего" in t}

    def gen(rng):
        return retry(g.t4_roads, lambda r: marks[kind](r["text"]), rng)
    gen.__name__ = f"t4_{kind}"
    return gen


def t4_via_avoid(rng):
    return t4_kind("via")(rng) if rng.random() < 0.5 else t4_kind("avoid")(rng)


def t4_scheme(rng, image_name):
    """Граф нарисован схемой (а не таблицей)."""
    for _ in range(10000):
        names = list("ABCDEF")[:rng.choice([5, 6])]
        adj = {a: {} for a in names}
        for a, b in itertools.combinations(names, 2):
            if rng.random() < 0.5:
                w = rng.randint(1, 9)
                adj[a][b] = adj[b][a] = w
        if any(not adj[a] for a in names):
            continue
        d = g._dijkstra(adj, names[0])
        if names[-1] not in d or (names[-1] in adj[names[0]] and adj[names[0]][names[-1]] == d[names[-1]]):
            continue
        lines = [f"graph G {{ bgcolor=white; layout=neato; overlap=false; splines=true; "
                 f"node [{FONT}, shape=circle, width=0.45, fixedsize=true]; "
                 f"edge [{FONT}, fontsize=13, fontcolor=\"#1565c0\"];"]
        for a, b in itertools.combinations(names, 2):
            if b in adj[a]:
                lines.append(f'"{a}" -- "{b}" [label="{adj[a][b]}"];')
        lines.append("}")
        svg = subprocess.run(["dot", "-Tsvg", "-Kneato"], input="\n".join(lines).encode(), capture_output=True,
                             check=True).stdout.decode()
        text = ("На схеме изображены дороги между населёнными пунктами " + ", ".join(names) +
                "; числа — протяжённость дорог в километрах.\n\n"
                f"![Схема дорог](IMG/{image_name})\n\n"
                f"Определите длину кратчайшего пути между пунктами {names[0]} и {names[-1]}. "
                "Передвигаться можно только по дорогам, указанным на схеме.")
        return {"text": text, "answer": str(d[names[-1]]), "image": (image_name, svg)}
    raise RuntimeError


# ------------------------------------------------------------------ 5. исполнители

SPECIAL = [
    ("Квадратор", ["возведи в квадрат", "зачеркни справа"]),
    ("Квадратор", ["возведи в квадрат", "вычти {k}"]),
    ("Квадратор", ["возведи в квадрат", "прибавь {k}"]),
    ("Делитель", ["раздели на 2", "вычти {k}"]),
    ("Делитель", ["раздели на 3", "прибавь {k}"]),
    ("Вычислитель", ["умножь на {m}", "зачеркни справа"]),
]


def apply_cmd(cmd, x):
    """Выполнить команду исполнителя; None — если результат недопустим (не натуральный)."""
    import re as _re
    if cmd == "возведи в квадрат":
        y = x * x
    elif cmd == "зачеркни справа":
        y = x // 10
    else:
        m = _re.match(r"(прибавь|вычти|умножь на|раздели на) (\d+)", cmd)
        k = int(m.group(2))
        if m.group(1) == "прибавь":
            y = x + k
        elif m.group(1) == "вычти":
            y = x - k
        elif m.group(1) == "умножь на":
            y = x * k
        else:
            if x % k:
                return None
            y = x // k
    return y if 0 < y < 10 ** 9 else None


def t5_special(rng):
    """Нестандартные команды (квадрат, зачеркнуть цифру, деление): составить программу ≤ 5 команд."""
    for _ in range(20000):
        name, cmds = rng.choice(SPECIAL)
        k, m = rng.randint(1, 5), rng.randint(2, 5)
        cmds = [c.format(k=k, m=m) for c in cmds]
        start = rng.randint(2, 30) if "раздели" not in cmds[0] else rng.randint(40, 300)
        reach = {}
        for L in range(1, 6):
            for p in itertools.product("12", repeat=L):
                x = start
                for c in p:
                    x = apply_cmd(cmds[int(c) - 1], x)
                    if x is None:
                        break
                if x is not None:
                    reach.setdefault(x, []).append("".join(p))
        # цель: достижима не меньше чем за 4 команды, но не меньше чем за 3 и не больше чем 5
        cands = [(t, ps) for t, ps in reach.items() if min(len(p) for p in ps) >= 4 and t != start and t < 10 ** 6]
        if not cands:
            continue
        target, ps = rng.choice(cands)
        best = min(ps, key=lambda p: (len(p), p))
        text = (f"У исполнителя {name} две команды, которым присвоены номера:\n\n"
                f"1. **{cmds[0]}**\n2. **{cmds[1]}**\n\n"
                + ("Команда «зачеркни справа» удаляет крайнюю правую цифру числа. " if "зачеркни справа" in cmds
                   else "") +
                "Исполнитель работает только с натуральными числами.\n\n"
                f"Составьте алгоритм получения из числа {start} числа {target}, содержащий не более 5 команд. "
                "В ответе запишите только номера команд. Если таких алгоритмов более одного, запишите любой из них.")
        return {"text": text, "answer": best}
    raise RuntimeError


# ------------------------------------------------------------------ 6. программы

T6_MOD = [
    ("s % 9 == t", lambda s, t: s % 9 == t),
    ("s % 2 == 0 and t % 2 == 1", lambda s, t: s % 2 == 0 and t % 2 == 1),
    ("s % t == 0", lambda s, t: s % t == 0),
    ("(s + t) % 3 == 0 or s > t", lambda s, t: (s + t) % 3 == 0 or s > t),
    ("s // 10 == t % 10", lambda s, t: s // 10 == t % 10),
    ("s % 5 == 0 or t % 4 == 0", lambda s, t: s % 5 == 0 or t % 4 == 0),
    ("not (s % 3 == 0) and t > 5", lambda s, t: (not s % 3 == 0) and t > 5),
]


def t6_mod(rng):
    return retry(_t6_mod, lambda r: r["answer"] not in ("0", "1", "8", "9"), rng)


def _t6_mod(rng):
    tmpl, f = rng.choice(T6_MOD)
    lo = 1 if "s % t" in tmpl else -5
    pairs = [(rng.randint(1, 40), rng.randint(max(lo, 1) if "% t" in tmpl else 0, 12)) for _ in range(9)]
    word = rng.choice(["YES", "NO"])
    cnt = sum(1 for s, t in pairs if f(s, t))
    if word == "NO":
        cnt = 9 - cnt
    text = ("Ниже приведена программа, записанная на языке Python.\n\n" + g._prog6(tmpl) +
            "\n\nБыло проведено 9 запусков программы, при которых в качестве значений переменных s и t "
            f"вводились следующие пары чисел:\n\n{g._pairs_md(pairs)}.\n\n"
            f"Сколько было запусков, при которых программа напечатала «{word}»?")
    return {"text": text, "answer": str(cnt)}


# ------------------------------------------------------------------ 7. адреса

def t7_url_right(rng):
    """URL, где точка «приклеена» справа: `net`, `.ru`, `com`, `.pas`."""
    srv = rng.choice([("net", "ru"), ("olympiada", "ru"), ("school", "org"), ("info", "net"), ("edu", "com")])
    fil = rng.choice([("com", "pas"), ("tests", "rar"), ("http", "txt"), ("ftp", "doc"), ("list", "htm")])
    proto = rng.choice(["http", "https", "ftp"])
    parts = [proto, "://", srv[0], "." + srv[1], "/", fil[0], "." + fil[1]]
    letters = list("АБВГДЕЖ")
    order = parts[:]
    rng.shuffle(order)
    mapping = dict(zip(letters, order))
    rev = {p: L for L, p in mapping.items()}
    ans = "".join(rev[p] for p in parts)
    text = (f"Доступ к файлу **{fil[0]}.{fil[1]}**, находящемуся на сервере **{srv[0]}.{srv[1]}**, "
            f"осуществляется по протоколу **{proto}**. Фрагменты адреса файла закодированы буквами от А до Ж. "
            "Запишите последовательность этих букв, кодирующую адрес указанного файла в сети Интернет.\n\n"
            + "\n".join(f"{L}) `{mapping[L]}`" for L in letters))
    return {"text": text, "answer": ans}


def t7_url_any(rng):
    return g.t7_url(rng) if rng.random() < 0.5 else t7_url_right(rng)


def t7_email(rng):
    for _ in range(1000):
        box = rng.choice([("wait_", "for_", "mail"), ("ivan", ".", "petrov"), ("best_", "pupil", "2027"),
                          ("masha", "_", "ivanova"), ("info", "-", "school")])
        server = rng.choice([("GorodN", ".ru"), ("mail", ".ru"), ("school12", ".org"), ("yandex", ".ru")])
        parts = [box[0], box[1], box[2], "@", server[0], server[1]]
        target = "".join(parts)
        letters = list("АБВГДЕ")
        order = parts[:]
        rng.shuffle(order)
        mapping = dict(zip(letters, order))
        sols = ["".join(p) for p in itertools.permutations(letters) if "".join(mapping[x] for x in p) == target]
        if len(sols) != 1:
            continue
        text = (f"На сервере **{server[0]}{server[1]}** находится почтовый ящик **{''.join(box)}**. Фрагменты адреса "
                "электронной почты закодированы буквами от А до Е. Запишите последовательность букв, кодирующую "
                "этот адрес.\n\n" + "\n".join(f"{L}) `{mapping[L]}`" for L in letters))
        return {"text": text, "answer": sols[0]}
    raise RuntimeError


def _valid_ip(s):
    p = s.split(".")
    return len(p) == 4 and all(x.isdigit() and int(x) <= 255 and (x == "0" or x[0] != "0") for x in p)


def t7_ip(rng):
    for _ in range(100000):
        ip = ".".join(str(rng.randint(0, 255)) for _ in range(4))
        cuts = sorted(rng.sample(range(1, len(ip)), 3))
        frags = [ip[i:j] for i, j in zip([0] + cuts, cuts + [len(ip)])]
        if any(len(f) < 2 for f in frags) or len(set(frags)) < 4:
            continue
        letters = list("АБВГ")
        order = frags[:]
        rng.shuffle(order)
        mapping = dict(zip(letters, order))
        sols = ["".join(p) for p in itertools.permutations(letters) if _valid_ip("".join(mapping[x] for x in p))]
        if len(sols) != 1:
            continue
        text = ("На месте преступления были обнаружены четыре обрывка бумаги. Следствие установило, что на них "
                "записаны фрагменты одного IP-адреса. Криминалисты обозначили эти фрагменты буквами А, Б, В и Г:\n\n"
                "| А | Б | В | Г |\n|---|---|---|---|\n| " + " | ".join(f"`{mapping[L]}`" for L in letters) + " |\n\n"
                "Восстановите IP-адрес. В ответе укажите последовательность букв, обозначающих фрагменты, в порядке, "
                "соответствующем IP-адресу.")
        return {"text": text, "answer": sols[0]}
    raise RuntimeError


# ------------------------------------------------------------------ 8. запросы

TRIPLES = [("Индукция", "Поле", "Агроном"), ("Луна", "Марс", "Венера"), ("Барокко", "Классицизм", "Ампир"),
           ("Пирожное", "Выпечка", "Торт"), ("Солнце", "Ветер", "Дождь")]
# области: 1=A, 2=B, 3=C, 12, 13, 23, 123
REG = ["a", "b", "c", "ab", "ac", "bc", "abc"]


def _q_regions(q):
    """Запрос — строка вида 'A & B' / 'A | B | C' / 'A' над буквами a, b, c → множество областей."""
    if "|" in q:
        words = [w.strip() for w in q.split("|")]
        return {r for r in REG if any(w in r for w in words)}
    words = [w.strip() for w in q.split("&")]
    return {r for r in REG if all(w in r for w in words)}


def t8_three(rng):
    for _ in range(20000):
        names = rng.choice(TRIPLES)
        val = {r: rng.randint(1, 40) * 10 for r in REG}
        zero = rng.choice([("ac", "abc"), ("bc", "abc"), ("ab", "abc"), ("abc",), ()])
        for r in zero:
            val[r] = 0
        pool = ["a", "b", "c", "a & b", "a & c", "b & c", "a | b", "a | c", "b | c", "a | b | c", "a & b & c"]
        target = rng.choice([q for q in pool if "&" in q or "|" in q])
        known = [q for q in pool if q != target]
        rng.shuffle(known)
        known = known[:rng.randint(4, 6)]
        # обнулённые пересечения сообщаем явно (как в задачах ФИПИ «Индукция & Агроном = 0»)
        for q in pool:
            if q.count("&") == 1 and sum(val[r] for r in _q_regions(q)) == 0 and q not in known and q != target:
                known.append(q)
        if not _determined(known, target, val):
            continue
        sub = dict(zip("abc", names))
        fmt = lambda q: " ".join(sub.get(w, w) for w in q.split())
        rows = "\n".join("| " + fmt(q).replace("|", "\\|") + f" | {sum(val[r] for r in _q_regions(q))} |"
                         for q in known)
        text = ("В языке запросов поискового сервера для обозначения логической операции «ИЛИ» используется "
                "символ «|», а для обозначения логической операции «И» — символ «&».\n\n"
                "В таблице приведены запросы и количество найденных по ним страниц некоторого сегмента сети "
                "Интернет.\n\n| Запрос | Найдено страниц (в тысячах) |\n|---|---|\n" + rows +
                f"\n\nКакое количество страниц (в тысячах) будет найдено по запросу **{fmt(target)}**?\n\n"
                "Считается, что все запросы выполнялись практически одновременно, так что набор страниц, "
                "содержащих все искомые слова, не изменялся за время выполнения запросов.")
        return {"text": text, "answer": str(sum(val[r] for r in _q_regions(target)))}
    raise RuntimeError


def _determined(known, target, val):
    """Однозначно ли target выражается через известные запросы (с учётом неотрицательности нулевых)."""
    from fractions import Fraction
    zero_regs = set()
    for q in known:
        if sum(val[r] for r in _q_regions(q)) == 0:
            zero_regs |= _q_regions(q)
    free = [r for r in REG if r not in zero_regs]
    rows = [[Fraction(int(r in _q_regions(q))) for r in free] for q in known]
    tgt = [Fraction(int(r in _q_regions(target))) for r in free]
    # target ∈ row-space(rows) ?  Проверим ранг
    def rank(m):
        m = [row[:] for row in m]
        rk, col = 0, 0
        ncol = len(m[0]) if m else 0
        while rk < len(m) and col < ncol:
            piv = next((i for i in range(rk, len(m)) if m[i][col] != 0), None)
            if piv is None:
                col += 1
                continue
            m[rk], m[piv] = m[piv], m[rk]
            for i in range(len(m)):
                if i != rk and m[i][col] != 0:
                    f = m[i][col] / m[rk][col]
                    m[i] = [a - f * b for a, b in zip(m[i], m[rk])]
            rk += 1
            col += 1
        return rk
    return rank(rows) == rank(rows + [tgt])


# ------------------------------------------------------------------ 9. пути

def t9_kind(kind):
    def gen(rng, image_name):
        for _ in range(20000):
            n = rng.choice([9, 10, 11])
            names, edges, layers = g._dag(rng, n)
            s, t = names[0], names[-1]
            if kind == "plain":
                ans = g._count_paths(names, edges, s, t)
                q = f"Сколько существует различных путей из города {s} в город {t}?"
            elif kind == "through":
                v = rng.choice(names[2:-2])
                ans = g._count_paths(names, edges, s, t, through=v)
                q = f"Сколько существует различных путей из города {s} в город {t}, проходящих через город {v}?"
            elif kind == "avoid":
                v = rng.choice(names[2:-2])
                ans = g._count_paths(names, edges, s, t, avoid=v)
                q = f"Сколько существует различных путей из города {s} в город {t}, не проходящих через город {v}?"
            else:
                v, u = rng.sample(names[2:-1], 2)
                ans = _count_through_avoid(names, edges, s, t, v, u)
                q = (f"Сколько существует различных путей из города {s} в город {t}, проходящих через город {v}, "
                     f"но не проходящих через город {u}?")
            if not (4 <= ans <= 40):
                continue
            if kind == "through_avoid" and ans in (g._count_paths(names, edges, s, t, through=v), 0):
                continue
            svg = g._dag_svg(names, edges, layers)
            text = ("На рисунке — схема дорог, связывающих города " + ", ".join(names) +
                    ". По каждой дороге можно двигаться только в одном направлении, указанном стрелкой.\n\n"
                    f"![Схема дорог](IMG/{image_name})\n\n" + q)
            return {"text": text, "answer": str(ans), "image": (image_name, svg)}
        raise RuntimeError
    gen.__name__ = f"t9_{kind}"
    gen.needs_image = True
    return gen


def _count_through_avoid(names, edges, s, t, v, u):
    # пути s→v без u, умноженные на пути v→t без u
    def cnt(a, b):
        c = {x: 0 for x in names}
        c[a] = 1
        for x in names:
            if x == u:
                c[x] = 0
                continue
            for p, q in edges:
                if p == x:
                    c[q] += c[x]
        return c[b]
    return cnt(s, v) * cnt(v, t)


# ------------------------------------------------------------------ 10. системы счисления

def t10_to_bin(rng):
    n = rng.randint(70, 255)
    text = (f"Переведите число {n} из десятичной системы счисления в двоичную систему счисления. "
            "В ответе укажите двоичное число. Основание системы счисления указывать не нужно.")
    return {"text": text, "answer": bin(n)[2:]}


def t10_digit_sum(rng):
    for _ in range(1000):
        b = rng.choice([8, 8, 16, 2])
        nums = rng.sample(range(20, 256), 3)
        sums = [sum(int(c, 16) for c in g._to_base(n, b)) for n in nums]
        which = rng.choice(["наименьшая", "наибольшая"])
        best = min(sums) if which == "наименьшая" else max(sums)
        if sums.count(best) != 1:
            continue
        bname = {2: "двоичной", 8: "восьмеричной", 16: "шестнадцатеричной"}[b]
        text = (f"Среди приведённых ниже трёх чисел, записанных в десятичной системе счисления, найдите число, "
                f"сумма цифр которого в {bname} записи {which}. В ответе запишите сумму цифр в {bname} записи "
                f"этого числа (в десятичной системе).\n\n" + ", ".join(f"{n}<sub>10</sub>" for n in nums))
        return {"text": text, "answer": str(best)}
    raise RuntimeError


# ------------------------------------------------------------------ реестр

SUBTYPES = {
    "1.1": ("Вычеркнутое слово", g.t1_word),
    "1.2": ("Объём статьи по страницам", g.t1_volume),
    "1.3": ("Обратная задача: параметр по объёму", t1_inverse),
    "1.4": ("Перекодировка текста", t1_recode),
    "2.1": ("Какая цепочка расшифровывается однозначно", g.t2_unique),
    "2.2": ("Номера букв латинского алфавита", t2_alpha),
    "2.3": ("Буквы не повторяются", g.t2_distinct),
    "2.4": ("Сколько букв в сообщении", t2_count),
    "3.1": ("Крайнее X, высказывание истинно", t3_extreme(True)),
    "3.2": ("Крайнее X, высказывание ложно", t3_extreme(False)),
    "3.3": ("Количество чисел", t3_count),
    "3.4": ("Единственное число", t3_unique),
    "3.5": ("Выбор из списка", t3_pick),
    "4.1": ("Кратчайший путь по таблице", t4_kind("plain")),
    "4.2": ("Через пункт или в обход пункта", t4_via_avoid),
    "4.3": ("Схема вместо таблицы", t4_scheme),
    "5.1": ("Найти неизвестный параметр b", g.t5_find_b),
    "5.2": ("Составить программу: «прибавь» и «умножь»", g.t5_program),
    "5.3": ("Квадратор, Делитель и другие команды", t5_special),
    "6.1": ("Сколько раз YES / NO", lambda rng: retry(g.t6_count, lambda r: r["answer"] not in ("0", "9"), rng)),
    "6.2": ("Параметр A", g.t6_param),
    "6.3": ("Остатки и делимость в условии", t6_mod),
    "7.1": ("Адрес файла (URL)", t7_url_any),
    "7.2": ("Адрес электронной почты", t7_email),
    "7.3": ("IP-адрес из обрывков", t7_ip),
    "8.1": ("Два слова", g.t8_two),
    "8.2": ("Три слова", t8_three),
    "9.1": ("Все пути", t9_kind("plain")),
    "9.2": ("Через вершину", t9_kind("through")),
    "9.3": ("Не через вершину", t9_kind("avoid")),
    "9.4": ("Через одну вершину, но не через другую", t9_kind("through_avoid")),
    "10.1": ("Сравнение чисел в разных системах", g.t10_compare),
    "10.2": ("Перевод в двоичную систему", t10_to_bin),
    "10.3": ("Единицы и нули в двоичной записи", g.t10_ones),
    "10.4": ("Перевод в десятичную систему", g.t10_to_dec),
    "10.5": ("Сумма цифр в записи числа", t10_digit_sum),
}
t4_scheme.needs_image = True

if __name__ == "__main__":
    rng = random.Random(3)
    for key, (title, fn) in SUBTYPES.items():
        r = fn(rng, "x.svg") if getattr(fn, "needs_image", False) else fn(rng)
        print(f"=== {key} {title}\n{r['text'][:600]}\nОТВЕТ: {r['answer']}\n")
