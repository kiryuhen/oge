"""Генераторы заданий 1–10 ОГЭ по информатике в формате ФИПИ.

Каждая функция tN_*(rng) возвращает словарь:
    text   — условие (Markdown),
    answer — правильный ответ (строка),
    image  — (необязательно) имя SVG-файла и его содержимое.
Ответы вычисляются программно, поэтому им можно доверять.
"""

import itertools
import random
import subprocess

RU_LETTERS = "АБВГДЕЖ"

# ------------------------------------------------------------------ задание 1

T1_LISTS = [
    ("дикие животные", ["ёж", "лев", "як", "слон", "зубр", "олень", "тюлень", "жираф", "носорог", "гепард",
                        "крокодил", "бегемот", "аллигатор", "муравьед", "дикобраз", "барсук"]),
    ("города России", ["Орёл", "Тула", "Тверь", "Пенза", "Казань", "Москва", "Воронеж", "Кострома",
                       "Ярославль", "Владивосток", "Омск", "Самара", "Смоленск", "Новосибирск"]),
    ("реки России", ["Обь", "Дон", "Лена", "Ока", "Волга", "Ангара", "Енисей", "Иртыш", "Печора", "Кама",
                     "Амур", "Нева", "Урал"]),
    ("овощи", ["лук", "репа", "свёкла", "огурец", "морковь", "капуста", "картофель", "патиссон", "редис",
               "томат", "баклажан", "кабачок"]),
    ("птицы", ["сыч", "грач", "дрозд", "иволга", "синица", "снегирь", "соловей", "трясогузка", "дятел",
               "ласточка", "зяблик", "журавль"]),
    ("музыкальные инструменты", ["арфа", "лютня", "гитара", "скрипка", "балалайка", "контрабас",
                                 "виолончель", "флейта", "орган", "барабан", "саксофон"]),
    ("деревья", ["ель", "дуб", "клён", "сосна", "осина", "рябина", "лиственница", "берёза", "тополь",
                 "кедр", "ясень", "черёмуха"]),
    ("языки программирования", ["C", "Go", "Java", "Lisp", "Python", "Pascal", "Haskell", "JavaScript",
                                "Kotlin", "Ruby", "Swift", "Fortran"]),
]

T1_ENC = [
    ("В кодировке КОИ-8 каждый символ кодируется 8 битами.", 8),
    ("В кодировке Windows-1251 каждый символ кодируется 8 битами.", 8),
    ("В одной из кодировок Unicode каждый символ кодируется 16 битами.", 16),
    ("В кодировке UTF-16 каждый символ кодируется 16 битами.", 16),
    ("В кодировке UTF-32 каждый символ кодируется 32 битами.", 32),
]

NAMES = ["Вова", "Миша", "Лена", "Катя", "Петя", "Аня", "Дима", "Оля", "Ваня", "Таня", "Костя", "Маша"]
FEMALE = {"Лена", "Катя", "Аня", "Оля", "Таня", "Маша"}


def plural(n, one, few, many):
    """plural(5, 'байт', 'байта', 'байт') -> '5 байт'"""
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        w = one
    elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        w = few
    else:
        w = many
    return w


def wrote(name):
    return "написала" if name in FEMALE else "написал"


def _cap(s):
    return s[0].upper() + s[1:]


def t1_word(rng):
    title, words = rng.choice(T1_LISTS)
    enc_text, bits = rng.choice(T1_ENC)
    while True:
        k = rng.randint(6, 8)
        chosen = rng.sample(words, k)
        chosen.sort(key=len)  # как в ФИПИ: по возрастанию длины
        target_i = rng.randrange(1, k)  # не первое слово
        target = chosen[target_i]
        if sum(1 for w in chosen if len(w) == len(target)) == 1:
            break
    sentence = ", ".join([_cap(chosen[0])] + chosen[1:]) + " – " + title
    delta_bits = (len(target) + 2) * bits
    delta = delta_bits // 8
    unit = plural(delta, "байт", "байта", "байт")
    if rng.random() < 0.25:
        delta = delta_bits
        unit = plural(delta, "бит", "бита", "бит")
    name = rng.choice(NAMES)
    one, what = {"дикие животные": ("одного", "животного"), "города России": ("одного", "города"),
                 "реки России": ("одной", "реки"), "овощи": ("одного", "овоща"), "птицы": ("одной", "птицы"),
                 "музыкальные инструменты": ("одного", "инструмента"), "деревья": ("одного", "дерева"),
                 "языки программирования": ("одного", "языка")}[title]
    text = (f"{enc_text} {name} {wrote(name)} текст (в нём нет лишних пробелов):\n\n"
            f"«{sentence}».\n\n"
            f"Ученик вычеркнул из списка название {one} {what}. Заодно он вычеркнул ставшие лишними "
            f"запятую и пробел — два пробела не должны идти подряд.\n\n"
            f"При этом размер нового предложения в данной кодировке оказался на {delta} {unit} меньше, "
            f"чем размер исходного предложения. Напишите в ответе вычеркнутое название {what}.")
    return {"text": text, "answer": target}


def t1_volume(rng):
    while True:
        pages = rng.choice([4, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64])
        lines = rng.choice([30, 32, 40, 48, 56, 64])
        chars = rng.choice([32, 40, 48, 50, 56, 60, 64])
        bits = rng.choice([8, 16])
        total_bits = pages * lines * chars * bits
        if total_bits % (8 * 1024) == 0:
            break
    kb = total_bits // 8 // 1024
    doc = rng.choice(["Статья", "Реферат", "Рассказ", "Доклад"])
    text = (f"{doc}, набранный на компьютере, содержит {pages} {plural(pages, 'страницу', 'страницы', 'страниц')}, "
            f"на каждой странице {lines} {plural(lines, 'строка', 'строки', 'строк')}, "
            f"в каждой строке {chars} {plural(chars, 'символ', 'символа', 'символов')}. Определите информационный объём текста в кодировке, "
            f"в которой каждый символ кодируется {bits} битами. Ответ дайте в килобайтах.")
    text = text.replace("Статья, набранный", "Статья, набранная")
    return {"text": text, "answer": str(kb)}


# ------------------------------------------------------------------ задание 2

T2_TABLES = [
    ({"А": "01", "Д": "100", "К": "101", "Н": "10", "О": "111", "С": "000"},
     ["ДОК", "СОК", "НОС", "СОН", "КОН", "ДОН", "САД", "ОКНО", "ДОСКА", "КОСА", "НАСОС", "СОДА", "КАНОН",
      "ДОНОС", "СНОС", "АНОД", "КОДА", "НАКОС"]),
    ({"А": "10", "Б": "110", "В": "011", "Е": "0", "Р": "01", "Т": "111"},
     ["БЕТА", "ВЕРА", "ТАРА", "АРБА", "БАРТЕР", "ВАТА", "РАБ", "ТЕАТР", "ВЕТЕР", "ВЕРБА", "БРА", "ТРАВА"]),
    ({"Л": "11", "И": "0", "С": "101", "А": "100", "П": "1", "Т": "010"},
     ["ЛИСА", "ПИЛА", "ЛАПА", "ЛИСТ", "СТАЛ", "ПЛАСТ", "СИЛА", "ТАЛИСТ", "СЛАЛИ", "ПАСТИЛА", "ПИТА"]),
    ({"М": "00", "О": "011", "Р": "1", "Е": "010", "К": "11", "А": "0"},
     ["МОРЕ", "КОРМА", "РЕКА", "МЕРА", "КАРМА", "МАК", "КОМА", "АРКА", "МОРОКА", "ОКЕАН"]),
]


def _decodings(s, table, limit=50, distinct=False):
    res = []

    def go(i, acc):
        if len(res) >= limit:
            return
        if i == len(s):
            res.append("".join(acc))
            return
        for letter, code in table.items():
            if distinct and letter in acc:
                continue
            if s.startswith(code, i):
                acc.append(letter)
                go(i + len(code), acc)
                acc.pop()

    go(0, [])
    return res


def _enc(word, table):
    return "".join(table[c] for c in word)


def _table_md(table):
    letters = list(table)
    return ("| " + " | ".join(letters) + " |\n|" + "---|" * len(letters) + "\n| " +
            " | ".join(f"`{table[c]}`" for c in letters) + " |")


def t2_unique(rng):
    """Три цепочки, только одна расшифровывается однозначно."""
    for _ in range(5000):
        table, words = rng.choice(T2_TABLES)
        good = [w for w in words if all(c in table for c in w) and len(_decodings(_enc(w, table), table)) == 1]
        bad = [w for w in words if all(c in table for c in w) and len(_decodings(_enc(w, table), table)) > 1]
        if good and len(bad) >= 2:
            ans = rng.choice(good)
            others = rng.sample(bad, 2)
            codes = [_enc(w, table) for w in [ans] + others]
            rng.shuffle(codes)
            name = rng.choice(NAMES)
            text = (f"{name} {'шифрует'} русские слова, записывая вместо каждой буквы её код:\n\n"
                    f"{_table_md(table)}\n\n"
                    "Некоторые цепочки можно расшифровать не одним способом. Даны три кодовые цепочки:\n\n"
                    + "\n".join(f"- `{c}`" for c in codes) +
                    "\n\nНайдите среди них ту, которая имеет только одну расшифровку, "
                    "и запишите в ответе расшифрованное слово.")
            return {"text": text, "answer": ans}
    raise RuntimeError


T2_SYMBOL_TABLES = [
    {"А": "•–", "Б": "–•••", "В": "•––", "Г": "––•", "Д": "–••", "Е": "•", "Ж": "•••–", "З": "––••"},
    {"А": "~", "Б": "*~", "В": "~~*", "Г": "*", "Д": "~*", "Е": "**~", "Ж": "*~~"},
    {"К": "#", "Л": "+#", "М": "##+", "Н": "+", "О": "#+", "П": "+##", "Р": "++#"},
]


def t2_distinct(rng):
    """Сообщение из неповторяющихся букв, нужно восстановить его."""
    for _ in range(20000):
        table = rng.choice(T2_SYMBOL_TABLES)
        letters = list(table)
        msg = "".join(rng.sample(letters, rng.randint(4, 6)))
        s = _enc(msg, table)
        decs = _decodings(s, table, limit=100, distinct=True)
        if decs == [msg]:
            text = ("Мальчики играли в шпионов и закодировали сообщение придуманным шифром. "
                    "В сообщении присутствуют только буквы из приведённого фрагмента кодовой таблицы:\n\n"
                    f"{_table_md(table)}\n\n"
                    f"Определите, какое сообщение закодировано в строчке\n\n`{s}`\n\n"
                    "Известно, что буквы в сообщении не повторяются. В ответе запишите сообщение.")
            return {"text": text, "answer": msg}
    raise RuntimeError


# ------------------------------------------------------------------ задание 3

def _cond_eval(atom, x):
    kind, v = atom
    if kind == "div":
        return x % v == 0
    return {"<": x < v, ">": x > v, "<=": x <= v, ">=": x >= v,
            "even": x % 2 == 0, "odd": x % 2 == 1}[kind]


def _cond_text(atom):
    kind, v = atom
    return {"<": f"X < {v}", ">": f"X > {v}", "<=": f"X <= {v}", ">=": f"X >= {v}",
            "even": "X чётное", "odd": "X нечётное", "div": f"X делится на {v}"}[kind]


def t3_number(rng):
    for _ in range(10000):
        a = (rng.choice(["<", ">"]), rng.randint(5, 60))
        b = rng.choice([(rng.choice(["<", ">"]), rng.randint(5, 60)), ("even", 0), ("odd", 0)])
        na, nb = rng.random() < 0.5, rng.random() < 0.5
        op = rng.choice(["И", "ИЛИ"])
        want = rng.choice([True, False])
        extreme = rng.choice(["наименьшее", "наибольшее"])

        def f(x):
            va = not _cond_eval(a, x) if na else _cond_eval(a, x)
            vb = not _cond_eval(b, x) if nb else _cond_eval(b, x)
            return (va and vb) if op == "И" else (va or vb)

        dom = range(1, 1001)  # натуральные числа (достаточно далеко вправо, чтобы увидеть неограниченность)
        xs = [x for x in dom if f(x) == want]
        if not xs or len(xs) == len(dom):
            continue
        # отбрасываем вырожденные случаи, когда одна из частей ни на что не влияет
        sa = {x for x in dom if (not _cond_eval(a, x) if na else _cond_eval(a, x)) == want}
        sb = {x for x in dom if (not _cond_eval(b, x) if nb else _cond_eval(b, x)) == want}
        if set(xs) in (sa, sb):
            continue
        if extreme == "наименьшее":
            ans = min(xs)
            if ans == 1:
                continue  # слишком очевидно
        else:
            ans = max(xs)
            if ans > 900:
                continue  # множество не ограничено сверху — наибольшего нет
        ta = ("НЕ " if na else "") + f"({_cond_text(a)})"
        tb = ("НЕ " if nb else "") + f"({_cond_text(b)})"
        text = (f"Напишите {extreme} натуральное число X, для которого {'истинно' if want else 'ложно'} "
                f"высказывание:\n\n**{ta} {op} {tb}**")
        return {"text": text, "answer": str(ans)}
    raise RuntimeError


T3_NAMES = ["Анна", "Борис", "Вера", "Глеб", "Денис", "Ева", "Игорь", "Ирина", "Кирилл", "Олег", "Ольга",
            "Павел", "Роман", "Софья", "Тимур", "Ульяна", "Эмма", "Юлия", "Яна", "Антон", "Егор", "Илья",
            "Максим", "Никита", "Арина", "Алиса", "Остап", "Ульяна", "Эльдар", "Мария"]
VOWELS = set("АЕЁИОУЫЭЮЯаеёиоуыэюя")


def t3_names(rng):
    atoms = {
        "Первая буква гласная": lambda s: s[0] in VOWELS,
        "Последняя буква гласная": lambda s: s[-1] in VOWELS,
        "Количество букв чётное": lambda s: len(s) % 2 == 0,
        "Вторая буква гласная": lambda s: s[1] in VOWELS,
    }
    keys = list(atoms)
    for _ in range(10000):
        ka, kb = rng.sample(keys, 2)
        na, nb = rng.random() < 0.5, rng.random() < 0.5
        op = rng.choice(["И", "ИЛИ"])

        def f(s):
            va = atoms[ka](s) != na
            vb = atoms[kb](s) != nb
            return (va and vb) if op == "И" else (va or vb)

        names = rng.sample(sorted(set(T3_NAMES)), 4)
        good = [n for n in names if f(n)]
        if len(good) != 1:
            continue
        ta = ("НЕ " if na else "") + f"({ka})"
        tb = ("НЕ " if nb else "") + f"({kb})"
        text = (f"Для какого из приведённых имён **истинно** высказывание:\n\n**{ta} {op} {tb}**?\n\n"
                + "\n".join(f"{i + 1}) {n}" for i, n in enumerate(names))
                + "\n\nВ ответе запишите имя.")
        return {"text": text, "answer": good[0]}
    raise RuntimeError


# ------------------------------------------------------------------ задание 4

def _dijkstra(adj, s, banned=()):
    import heapq
    dist = {s: 0}
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u].items():
            if v in banned:
                continue
            if d + w < dist.get(v, 10 ** 9):
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return dist


def _roads_md(names, adj):
    head = "|   | " + " | ".join(names) + " |\n|---|" + "---|" * len(names) + "\n"
    rows = []
    for a in names:
        rows.append(f"| **{a}** | " + " | ".join(str(adj[a][b]) if b in adj[a] else "" for b in names) + " |")
    return head + "\n".join(rows)


def t4_roads(rng):
    for _ in range(10000):
        n = rng.choice([5, 6])
        names = list("ABCDEF")[:n]
        adj = {a: {} for a in names}
        for a, b in itertools.combinations(names, 2):
            if rng.random() < 0.55:
                w = rng.randint(1, 9)
                adj[a][b] = adj[b][a] = w
        src, dst = names[0], names[-1]
        kind = rng.choice(["plain", "plain", "via", "avoid"])
        if any(len(adj[a]) == 0 for a in names):
            continue
        d = _dijkstra(adj, src)
        if dst not in d:
            continue
        if kind == "plain":
            ans = d[dst]
            if dst in adj[src] and adj[src][dst] == ans:
                continue  # прямая дорога — неинтересно
            q = f"Определите длину кратчайшего пути между пунктами {src} и {dst}."
        elif kind == "via":
            via = rng.choice(names[1:-1])
            d2 = _dijkstra(adj, via)
            if via not in d or dst not in d2:
                continue
            ans = d[via] + d2[dst]
            if ans == d[dst]:
                continue
            q = f"Определите длину кратчайшего пути между пунктами {src} и {dst}, проходящего через пункт {via}."
        else:
            av = rng.choice(names[1:-1])
            d3 = _dijkstra(adj, src, banned={av})
            if dst not in d3 or d3[dst] == d[dst]:
                continue
            ans = d3[dst]
            q = (f"Определите длину кратчайшего пути между пунктами {src} и {dst}, "
                 f"не проходящего через пункт {av}.")
        text = ("Между населёнными пунктами " + ", ".join(names) +
                " построены дороги, протяжённость которых (в километрах) приведена в таблице.\n\n"
                + _roads_md(names, adj) + "\n\n" + q +
                " Передвигаться можно только по дорогам, протяжённость которых указана в таблице.")
        return {"text": text, "answer": str(ans)}
    raise RuntimeError


# ------------------------------------------------------------------ задание 5

def t5_find_b(rng):
    for _ in range(10000):
        name = rng.choice(["Альфа", "Бета", "Вычислитель", "Гамма", "Омега"])
        mode = rng.choice(["mul", "div", "sub"])
        k = rng.randint(1, 5)
        b = rng.randint(2, 9)
        prog = "".join(rng.choice("12") for _ in range(5))
        if "2" not in prog or "1" not in prog:
            continue
        if mode == "mul":
            c1, c2 = f"прибавь {k}", "умножь на b"
            op1, op2 = (lambda x: x + k), (lambda x, bb: x * bb)
        elif mode == "div":
            c1, c2 = f"прибавь {k}", "раздели на b"
            op1, op2 = (lambda x: x + k), (lambda x, bb: x / bb)
        else:
            c1, c2 = f"вычти {k}", "умножь на b"
            op1, op2 = (lambda x: x - k), (lambda x, bb: x * bb)
        start = rng.randint(2, 70)

        def runp(bb):
            x = start
            for c in prog:
                x = op1(x) if c == "1" else op2(x, bb)
                if x != int(x):
                    return None
            return int(x)

        res = runp(b)
        if res is None or res <= 0 or res > 5000:
            continue
        sols = [bb for bb in range(2, 200) if runp(bb) == res]
        if sols != [b]:
            continue
        text = (f"У исполнителя {name} две команды, которым присвоены номера:\n\n"
                f"1. **{c1}**\n2. **{c2}**\n\n"
                f"(b — неизвестное натуральное число; b ≥ 2).\n\n"
                f"Выполняя первую из них, {name} {'увеличивает' if mode != 'sub' else 'уменьшает'} число "
                f"на экране на {k}, а выполняя вторую, {'умножает' if mode != 'div' else 'делит'} это число "
                f"на b. Программа для исполнителя {name} — это последовательность номеров команд.\n\n"
                f"Известно, что программа **{prog}** переводит число {start} в число {res}. "
                f"Определите значение b.")
        return {"text": text, "answer": str(b)}
    raise RuntimeError


def t5_program(rng):
    """Составить программу не длиннее 5 команд; ответ проверяется перебором (выдаём один вариант)."""
    for _ in range(10000):
        a = rng.randint(2, 6)
        m = rng.choice([2, 3])
        start = rng.randint(1, 9)
        progs = {}
        for L in range(1, 6):
            for p in itertools.product("12", repeat=L):
                x = start
                for c in p:
                    x = x + a if c == "1" else x * m
                progs.setdefault(x, []).append("".join(p))
        cands = [(t, ps) for t, ps in progs.items() if len(ps) == 1 and len(ps[0]) == 5 and t > 40]
        if not cands:
            continue
        target, ps = rng.choice(cands)
        text = (f"У исполнителя Удвоитель (или Утроитель) две команды:\n\n"
                f"1. **прибавь {a}**\n2. **умножь на {m}**\n\n"
                f"Запишите порядок команд в программе, которая преобразует число {start} в число {target} "
                f"и содержит не более пяти команд, указывая лишь номера команд.")
        text = text.replace("Удвоитель (или Утроитель)", "Удвоитель" if m == 2 else "Утроитель")
        return {"text": text, "answer": ps[0]}
    raise RuntimeError


# ------------------------------------------------------------------ задание 6

def _pairs_md(pairs):
    return ", ".join(f"({s}, {t})" for s, t in pairs)


T6_CONDS = [
    ("s > A or t > {c}", lambda s, t, A, c: s > A or t > c),
    ("s > A and t < {c}", lambda s, t, A, c: s > A and t < c),
    ("s < A or t < {c}", lambda s, t, A, c: s < A or t < c),
    ("s > {c} or t > A", lambda s, t, A, c: s > c or t > A),
    ("s < {c} and t > A", lambda s, t, A, c: s < c and t > A),
    ("not (s > A) or t > {c}", lambda s, t, A, c: (not s > A) or t > c),
    ("s + t > A", lambda s, t, A, c: s + t > A),
    ("s > A and not (t > {c})", lambda s, t, A, c: s > A and not t > c),
]


def _prog6(cond):
    return ("```python\ns = int(input())\nt = int(input())\n"
            f"if {cond}:\n    print(\"YES\")\nelse:\n    print(\"NO\")\n```")


def t6_count(rng):
    tmpl, f = rng.choice(T6_CONDS)
    c = rng.randint(3, 12)
    A = rng.randint(3, 12)
    cond = tmpl.format(c=c).replace("A", str(A))
    pairs = [(rng.randint(-5, 15), rng.randint(-5, 15)) for _ in range(9)]
    cnt = sum(1 for s, t in pairs if f(s, t, A, c))
    word = rng.choice(["YES", "NO"])
    if word == "NO":
        cnt = 9 - cnt
    text = ("Ниже приведена программа, записанная на языке Python.\n\n" + _prog6(cond) +
            f"\n\nБыло проведено 9 запусков программы, при которых в качестве значений переменных s и t "
            f"вводились следующие пары чисел:\n\n{_pairs_md(pairs)}.\n\n"
            f"Сколько было запусков, при которых программа напечатала «{word}»?")
    return {"text": text, "answer": str(cnt)}


def t6_param(rng):
    for _ in range(10000):
        tmpl, f = rng.choice(T6_CONDS)
        c = rng.randint(3, 12)
        cond = tmpl.format(c=c)
        pairs = [(rng.randint(-5, 15), rng.randint(-5, 15)) for _ in range(9)]
        word = rng.choice(["YES", "NO"])
        k = rng.randint(2, 7)
        kind = rng.choice(["min", "max", "count"])
        good = []
        for A in range(-100, 101):
            cnt = sum(1 for s, t in pairs if f(s, t, A, c))
            if word == "NO":
                cnt = 9 - cnt
            if cnt == k:
                good.append(A)
        if not good or len(good) > 40 or -100 in good or 100 in good:
            continue
        if kind == "min":
            ans, q = min(good), "Укажите наименьшее целое значение параметра A"
        elif kind == "max":
            ans, q = max(good), "Укажите наибольшее целое значение параметра A"
        else:
            ans, q = len(good), "Укажите количество целых значений параметра A"
        text = ("Ниже приведена программа, записанная на языке Python.\n\n" + _prog6(cond) +
                f"\n\nБыло проведено 9 запусков программы, при которых в качестве значений переменных s и t "
                f"вводились следующие пары чисел:\n\n{_pairs_md(pairs)}.\n\n"
                f"{q}, при котором для указанных входных данных программа напечатает «{word}» {k} раз"
                + ("а." if k in (2, 3, 4) else "."))
        if kind == "count":
            text = text.replace("при котором", "при которых")
        return {"text": text, "answer": str(ans)}
    raise RuntimeError


# ------------------------------------------------------------------ задание 7

T7_SERVERS = [("obr", "org"), ("www", "ru"), ("edu", "net"), ("lib", "ru"), ("ftp", "com"), ("sch", "info"),
              ("rus", "ru"), ("map", "su"), ("news", "org"), ("home", "net")]
T7_FILES = [("rus", "doc"), ("htm", "txt"), ("math", "pdf"), ("img", "png"), ("www", "htm"), ("net", "xls"),
            ("list", "txt"), ("ftp", "jpg"), ("song", "mp3"), ("org", "odt")]


def t7_url(rng):
    srv = rng.choice(T7_SERVERS)
    fil = rng.choice(T7_FILES)
    proto = rng.choice(["http", "https", "ftp"])
    parts = [proto, "://", srv[0] + ".", srv[1], "/", fil[0] + ".", fil[1]]
    letters = list("АБВГДЕЖ")
    order = parts[:]
    rng.shuffle(order)
    mapping = dict(zip(letters, order))
    rev = {}
    for L, p in mapping.items():
        rev.setdefault(p, []).append(L)
    ans = "".join(rev[p].pop(0) for p in parts)
    text = (f"Доступ к файлу **{fil[0]}.{fil[1]}**, находящемуся на сервере **{srv[0]}.{srv[1]}**, "
            f"осуществляется по протоколу **{proto}**. Фрагменты адреса файла закодированы буквами от А до Ж. "
            "Запишите последовательность этих букв, кодирующую адрес указанного файла в сети Интернет.\n\n"
            + "\n".join(f"{L}) `{mapping[L]}`" for L in letters))
    return {"text": text, "answer": ans}


# ------------------------------------------------------------------ задание 8

T8_PAIRS = [("Крейсер", "Линкор"), ("Пушкин", "Лермонтов"), ("Сирень", "Жасмин"), ("Фрегат", "Эсминец"),
            ("Канарейка", "Щегол"), ("Рыбка", "Рыбак"), ("Шахматы", "Шашки"), ("Москва", "Петербург")]


def t8_two(rng):
    a, b = rng.choice(T8_PAIRS)
    ab = rng.randint(1, 60) * 10
    only_a = rng.randint(10, 300) * 10
    only_b = rng.randint(10, 300) * 10
    A, B, OR, AND = only_a + ab, only_b + ab, only_a + only_b + ab, ab
    known = {f"{a} | {b}": OR, f"{a} & {b}": AND, a: A, b: B}
    target = rng.choice(list(known))
    rows = [k for k in known if k != target]
    rng.shuffle(rows)
    table = "| Запрос | Найдено страниц (в тысячах) |\n|---|---|\n" + \
            "\n".join("| " + r.replace("|", "\\|") + f" | {known[r]} |" for r in rows)
    text = ("В языке запросов поискового сервера для обозначения логической операции «ИЛИ» используется "
            "символ «|», а для обозначения логической операции «И» — символ «&».\n\n"
            "В таблице приведены запросы и количество найденных по ним страниц некоторого сегмента сети "
            "Интернет.\n\n" + table +
            f"\n\nКакое количество страниц (в тысячах) будет найдено по запросу **{target}**?\n\n"
            "Считается, что все запросы выполнялись практически одновременно, так что набор страниц, "
            "содержащих все искомые слова, не изменялся за время выполнения запросов.")
    return {"text": text, "answer": str(known[target])}


# ------------------------------------------------------------------ задание 9

def _dag(rng, n):
    names = list("АБВГДЕЖИКЛМН")[:n]
    # слои
    layers = [[names[0]]]
    rest = names[1:-1]
    i = 0
    while i < len(rest):
        sz = rng.choice([2, 2, 3])
        layers.append(rest[i:i + sz])
        i += sz
    layers.append([names[-1]])
    layer_of = {v: li for li, L in enumerate(layers) for v in L}
    edges = set()
    for li in range(len(layers) - 1):
        for v in layers[li]:
            outs = rng.sample(layers[li + 1], min(len(layers[li + 1]), rng.choice([1, 2, 2])))
            for u in outs:
                edges.add((v, u))
            if li + 2 < len(layers) and rng.random() < 0.35:
                edges.add((v, rng.choice(layers[li + 2])))
        # связи внутри слоя (стрелка в сторону следующего по алфавиту)
        L = layers[li + 1]
        if len(L) >= 2 and rng.random() < 0.5:
            x, y = sorted(rng.sample(L, 2), key=names.index)
            edges.add((x, y))
    # у каждой вершины должен быть вход и выход
    for v in names[1:]:
        if not any(e[1] == v for e in edges):
            prev = layers[layer_of[v] - 1]
            edges.add((rng.choice(prev), v))
    for v in names[:-1]:
        if not any(e[0] == v for e in edges):
            nxt = layers[layer_of[v] + 1]
            edges.add((v, rng.choice(nxt)))
    return names, sorted(edges), layers


def _count_paths(names, edges, s, t, through=None, avoid=None):
    order = names  # имена расставлены в топологическом порядке
    cnt = {v: 0 for v in names}
    cnt[s] = 1
    for v in order:
        if v == avoid:
            cnt[v] = 0
            continue
        for a, b in edges:
            if a == v:
                cnt[b] += cnt[v]
    if through:
        c1 = _count_paths(names, edges, s, through)
        c2 = _count_paths(names, edges, through, t)
        return c1 * c2
    return cnt[t]


def _dag_svg(names, edges, layers):
    lines = ["digraph G {", "rankdir=LR; bgcolor=white; nodesep=0.5; ranksep=0.7;",
             'node [shape=circle, fontname="DejaVu Sans", fontsize=14, width=0.45, fixedsize=true];',
             'edge [arrowsize=0.7];']
    for L in layers:
        lines.append("{rank=same; " + " ".join(f'"{v}"' for v in L) + "}")
    for a, b in edges:
        lines.append(f'"{a}" -> "{b}";')
    lines.append("}")
    return subprocess.run(["dot", "-Tsvg"], input="\n".join(lines).encode(), capture_output=True,
                          check=True).stdout.decode()


def t9_paths(rng, image_name):
    for _ in range(10000):
        n = rng.choice([9, 10, 11])
        names, edges, layers = _dag(rng, n)
        s, t = names[0], names[-1]
        kind = rng.choice(["plain", "plain", "through", "avoid"])
        if kind == "plain":
            ans = _count_paths(names, edges, s, t)
            q = f"Сколько существует различных путей из города {s} в город {t}?"
        elif kind == "through":
            v = rng.choice(names[2:-2])
            ans = _count_paths(names, edges, s, t, through=v)
            q = f"Сколько существует различных путей из города {s} в город {t}, проходящих через город {v}?"
        else:
            v = rng.choice(names[2:-2])
            ans = _count_paths(names, edges, s, t, avoid=v)
            q = f"Сколько существует различных путей из города {s} в город {t}, не проходящих через город {v}?"
        if not (6 <= ans <= 40):
            continue
        svg = _dag_svg(names, edges, layers)
        text = ("На рисунке — схема дорог, связывающих города " + ", ".join(names) +
                ". По каждой дороге можно двигаться только в одном направлении, указанном стрелкой.\n\n"
                f"![Схема дорог](IMG/{image_name})\n\n" + q)
        return {"text": text, "answer": str(ans), "image": (image_name, svg)}
    raise RuntimeError


# ------------------------------------------------------------------ задание 10

def _to_base(n, b):
    digits = "0123456789ABCDEF"
    s = ""
    while n:
        s = digits[n % b] + s
        n //= b
    return s or "0"


def t10_compare(rng):
    while True:
        vals = rng.sample(range(20, 256), 3)
        if len({v // 10 for v in vals}) < 2:
            continue
        bases = rng.sample([2, 8, 16], 3)
        break
    which = rng.choice(["максимальное", "минимальное"])
    nums = [f"{_to_base(v, b)}<sub>{b}</sub>" for v, b in zip(vals, bases)]
    ans = max(vals) if which == "максимальное" else min(vals)
    text = ("Среди приведённых ниже трёх чисел, записанных в различных системах счисления, найдите "
            f"{which} и запишите его в ответе в десятичной системе счисления. В ответе запишите только "
            "число, основание системы счисления указывать не нужно.\n\n" + ", ".join(nums))
    return {"text": text, "answer": str(ans)}


def t10_ones(rng):
    n = rng.randint(70, 255)
    q = rng.choice(["единиц", "значащих нулей"])
    b = bin(n)[2:]
    ans = b.count("1") if q == "единиц" else b.count("0")
    text = (f"Переведите число {n} из десятичной системы счисления в двоичную систему счисления. "
            f"Сколько {q} содержит полученное число? В ответе укажите одно число.")
    return {"text": text, "answer": str(ans)}


def t10_to_dec(rng):
    b = rng.choice([2, 8, 16])
    n = rng.randint(40, 255) if b == 2 else rng.randint(60, 900)
    text = (f"Переведите число {_to_base(n, b)}<sub>{b}</sub> в десятичную систему счисления. "
            "В ответе запишите полученное число.")
    return {"text": text, "answer": str(n)}


GENERATORS = {
    1: [t1_word, t1_word, t1_volume],
    2: [t2_unique, t2_distinct],
    3: [t3_number, t3_number, t3_names],
    4: [t4_roads],
    5: [t5_find_b, t5_find_b, t5_program],
    6: [t6_count, t6_param],
    7: [t7_url],
    8: [t8_two],
    9: [t9_paths],
    10: [t10_compare, t10_compare, t10_ones, t10_to_dec],
}

if __name__ == "__main__":
    rng = random.Random(1)
    for k, fs in GENERATORS.items():
        for f in fs:
            r = f(rng, "test.svg") if f is t9_paths else f(rng)
            print(f"--- {k} {f.__name__}\n{r['text']}\nОТВЕТ: {r['answer']}\n")
