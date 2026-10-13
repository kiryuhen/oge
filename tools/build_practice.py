"""Вставляет в файлы tasks/*.md блоки тренировочных задач «как на экзамене» с ответами.

Блок находится между строками
    <!-- BEGIN:generated -->
    <!-- END:generated -->
и полностью перезаписывается при каждом запуске (остальной текст файла не трогается).
Запуск:  python3 tools/build_practice.py   (из корня репозитория)
"""

import glob
import json
import os
import random
import re

import gen_tasks as g
import prog_tasks
import robot_tasks

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
IMG_DIR = os.path.join(ROOT, "images", "tasks")

BEGIN, END = "<!-- BEGIN:generated -->", "<!-- END:generated -->"

PRACTICE_ROBOT = ["r21", "r03", "r05", "r07", "r08", "r10", "r11", "r12", "r16", "r20"]
VARIANT_ROBOT = ["r02", "r04", "r06", "r09", "r13", "r14", "r15", "r17", "r18", "r19"]
PRACTICE_PROG = ["p01", "p02", "p03", "p04", "p05", "p07", "p08", "p10", "p15", "p16"]
VARIANT_PROG = ["p06", "p09", "p11", "p12", "p13", "p14", "p17", "p18", "p19", "p20"]


def split_q12(q12):
    """Делит банк вопросов к заданию 12 на тренировочные (10) и для вариантов (остальные)."""
    q12 = [q for q in q12 if q["answer"] != "0"]
    by = lambda k: [q for q in q12 if q["kind"] == k]
    ext, year, size = by("ext"), by("year"), by("size")
    practice = ext[:3] + year[0:6:2] + size[0:6:2] + by("name")
    rest = [q for q in q12 if q not in practice]
    return practice, rest


def answer_block(ans, extra=""):
    return f"<details><summary>Ответ</summary>\n\n**{ans}**{extra}\n\n</details>\n"


def gen_simple(task_no, count, rng, start_no, img_prefix, img_rel):
    """count задач по образцу ФИПИ для заданий 1–10."""
    out = []
    fs = g.GENERATORS[task_no]
    seen = set()
    k = 0
    while len(out) < count:
        f = fs[k % len(fs)]
        k += 1
        if f is g.t9_paths:
            name = f"{img_prefix}-{len(out) + 1}.svg"
            r = f(rng, name)
            os.makedirs(IMG_DIR, exist_ok=True)
            with open(os.path.join(IMG_DIR, name), "w") as fh:
                fh.write(r["image"][1])
            r["text"] = r["text"].replace("IMG/", img_rel)
        else:
            r = f(rng)
        if r["text"] in seen:
            continue
        seen.add(r["text"])
        out.append(f"### Задача {start_no + len(out)}\n\n{r['text']}\n\n" + answer_block(r["answer"]))
    return out


def robot_md(t, no, img_rel):
    return (f"### Задача {no}. {t['title']}\n\n{t['text']}\n\n{robot_tasks.COMMON}\n\n"
            f"Пример поля (размеры могут быть другими):\n\n"
            f"| Было | Нужно закрасить |\n|---|---|\n"
            f"| ![до]({img_rel}{t['id']}-before.svg) | ![после]({img_rel}{t['id']}-after.svg) |\n\n"
            f"<details><summary>Решение</summary>\n\n```\n{t['solution']}\n```\n\n"
            f"Решение проверено на 300 полях со случайными размерами стен.\n\n</details>\n")


def prog_md(t, no):
    tests = prog_tasks.make_tests(t)
    ex_in, ex_out = tests[0]
    guarantee = (" " + t["guarantee"]) if t["guarantee"] else ""
    shown_in = prog_tasks.to_input(t, ex_in).strip().replace("\n", "<br>")
    table = "| № | Входные данные | Выходные данные |\n|---|---|---|\n" + "\n".join(
        f"| {i + 1} | {prog_tasks.to_input(t, a).strip().replace(chr(10), '<br>')} | "
        f"{r.replace(chr(10), '<br>')} |" for i, (a, r) in enumerate(tests))
    return (f"### Задача {no}\n\n{t['text']}\n\n{t['fmt']}{guarantee}\n\n"
            f"**Пример работы программы:**\n\n| Входные данные | Выходные данные |\n|---|---|\n"
            f"| {shown_in} | {ex_out.replace(chr(10), '<br>')} |\n\n"
            f"<details><summary>Решение и тесты</summary>\n\n```python\n{t['solution']}\n```\n\n"
            f"Тесты для самопроверки:\n\n{table}\n\n</details>\n")


def replace_block(path, body, key=None):
    """Заменить содержимое блока. key=None — общий блок «как на экзамене», иначе блок подтипа."""
    b, e = (BEGIN, END) if key is None else (f"<!-- BEGIN:sub:{key} -->", f"<!-- END:sub:{key} -->")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if b not in text:
        return False
    new = re.sub(re.escape(b) + ".*?" + re.escape(e), lambda m: b + "\n\n" + body.strip() + "\n\n" + e, text,
                 flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)
    return True


def task_file(no):
    return glob.glob(os.path.join(ROOT, "tasks", f"{no:02d}-*.md"))[0]


def variant_picks(corpus):
    """Вопросы к заданиям 11 и 12, отданные вариантам (в гайдах их не используем)."""
    rng = random.Random(77)
    q11 = rng.sample(corpus["q11"][27:53], 10)  # [53] — в разборе
    pool12 = [q for q in corpus["q12"] if q["answer"] != "0" and q["kind"] in ("ext", "year", "size", "name")]
    q12 = rng.sample(pool12, 10)
    return q11, q12


def sub_item(key, n, text, answer, extra=""):
    return f"#### Тренировка {key}.{n}\n\n{text}\n\n" + answer_block(answer, extra)


# группы задач по подтипам для заданий 11, 12, 14, 15, 16
SUB11 = {"11.1": ("book", "chess"), "11.2": ("trip", "olymp"), "11.3": ("sport",)}
SUB12 = {"12.1": ("ext", "year"), "12.2": ("mask", "name"), "12.3": ("size", "size_lt"), "12.4": ("total",)}
SUB15 = {"15.1": ["r21", "r07", "r16"], "15.2": ["r12", "r10", "r05"], "15.3": ["r03", "r08", "r11", "r20"],
         "15.4": ["r22", "r24", "r23"]}
SUB16 = {"16.1": ["p01", "p02", "p05", "p08"], "16.2": ["p03", "p04", "p07", "p15", "p16"],
         "16.3": ["p21", "p25", "p26"], "16.4": ["p22", "p23", "p24", "p10"]}


def robot_sub(t, key, n):
    return (f"#### Тренировка {key}.{n}. {t['title']}\n\n{t['text']}\n\n{robot_tasks.COMMON}\n\n"
            f"| Пример поля | Нужно закрасить |\n|---|---|\n"
            f"| ![до](../images/robot/{t['id']}-before.svg) | ![после](../images/robot/{t['id']}-after.svg) |\n\n"
            f"<details><summary>Решение</summary>\n\n```\n{t['solution']}\n```\n\n"
            f"Решение проверено на 300 полях со случайными размерами стен.\n\n</details>\n")


def prog_sub(t, key, n):
    return prog_md(t, n).replace(f"### Задача {n}\n", f"#### Тренировка {key}.{n}\n", 1)


def main():
    import subtypes
    corpus = json.load(open(os.path.join(HERE, "corpus_questions.json"), encoding="utf-8"))
    xlsx = json.load(open(os.path.join(HERE, "xlsx_questions.json"), encoding="utf-8"))
    v11, v12 = variant_picks(corpus)

    # 1–10: общий блок «как на экзамене» (5 задач) и блоки по подтипам (по 4 задачи)
    for no in range(1, 11):
        rng = random.Random(1000 + no)
        items = gen_simple(no, 5, rng, 1, f"t{no:02d}-practice", "../images/tasks/")
        replace_block(task_file(no), "\n".join(items))
    for key, (title, fn) in subtypes.SUBTYPES.items():
        no = int(key.split(".")[0])
        rng = random.Random("sub" + key)
        items, seen = [], set()
        while len(items) < 4:
            if getattr(fn, "needs_image", False):
                name = f"sub-{key}-{len(items) + 1}.svg"
                r = fn(rng, name)
                os.makedirs(IMG_DIR, exist_ok=True)
                with open(os.path.join(IMG_DIR, name), "w") as fh:
                    fh.write(r["image"][1])
                r["text"] = r["text"].replace("IMG/", "../images/tasks/")
            else:
                r = fn(rng)
            if r["text"] in seen:
                continue
            seen.add(r["text"])
            extra = ("\n\nВозможны и другие правильные программы: проверьте свою, выполнив команды по порядку."
                     if key in ("5.2", "5.3") else "")
            items.append(sub_item(key, len(items) + 1, r["text"], r["answer"], extra))
        if not replace_block(task_file(no), "\n".join(items), key):
            print("нет блока", key)

    # 11: вопросы по архиву, разбитые по подтипам (без вопросов из вариантов и разбора)
    pool11 = [q for q in corpus["q11"][:27] if q not in v11]
    for key, kinds in SUB11.items():
        qs = [q for q in pool11 if q["kind"] in kinds][:4]
        items = [sub_item(key, i + 1, q["q"], q["answer"],
                          f"\n\nГде искать: файл `archive/{q['file']}`, поисковая фраза: «{q['search']}».")
                 for i, q in enumerate(qs)]
        replace_block(task_file(11), "\n".join(items), key)

    # 12
    pool12 = [q for q in corpus["q12"] if q["answer"] != "0" and q not in v12]
    for key, kinds in SUB12.items():
        qs = [q for q in pool12 if q["kind"] in kinds]
        qs = qs[::max(1, len(qs) // 4)][:4]
        items = [sub_item(key, i + 1, q["q"], q["answer"]) for i, q in enumerate(qs)]
        replace_block(task_file(12), "\n".join(items), key)

    # 13: пять презентаций и пять документов
    t13 = json.load(open(os.path.join(HERE, "task13.json"), encoding="utf-8"))
    items = []
    for i, pr in enumerate(t13["pres"][1:6]):
        items.append(f"### Задача {i + 1} (13.1). Презентация «{pr['topic']}»\n\n{pr['req']}\n\n"
                     "<details><summary>Как проверить</summary>\n\nПройдите по "
                     "[чек-листу 13.1](#чек-лист-самопроверки-131). Одна ошибка — минус балл, две — ноль.\n\n</details>\n")
    for i, d in enumerate(t13["docs"][1:6]):
        items.append(f"### Задача {i + 6} (13.2). Документ «{d['topic']}»\n\n{d['req']}\n\n**Образец:**\n\n"
                     f"![Образец]({'../images/task13/'}{d['id']}.png)\n\n"
                     "<details><summary>Как проверить</summary>\n\nПройдите по "
                     "[чек-листу 13.2](#чек-лист-самопроверки-132). Положите свой документ рядом с образцом "
                     "и сравните построчно.\n\n</details>\n")
    replace_block(task_file(13), "\n".join(items))

    # 14: полные задания (как на экзамене) и вопросы по подтипам
    items = []
    for i in range(1, 5):
        d = xlsx[f"practice-{i}.xlsx"]
        qtext = "\n".join(f"{j + 1}. {q}" for j, (q, _) in enumerate(d["questions"]))
        ans = "\n".join(f"{j + 1}. **{a}**" + (" (значения для диаграммы)" if j == 2 else "")
                        for j, (_, a) in enumerate(d["questions"]))
        items.append(f"### Тренировка {i}. Файл [`practice-{i}.xlsx`](../materials/task14/practice-{i}.xlsx)\n\n"
                     f"{d['intro']}\n\nПервые строки таблицы:\n\n{d['preview']}\n\n"
                     f"Выполните задание:\n\n{qtext}\n\n<details><summary>Ответы</summary>\n\n{ans}\n\n</details>\n")
    replace_block(task_file(14), "\n".join(items))
    for key in ("14.1", "14.2", "14.3"):
        items, n = [], 0
        for fname in ["practice-1.xlsx", "practice-2.xlsx", "practice-3.xlsx", "practice-4.xlsx"]:
            for e in xlsx[fname]["extra"]:
                if e["sub"] == key:
                    n += 1
                    items.append(sub_item(key, n, f"Файл [`{fname}`](../materials/task14/{fname}). {e['q']}", e["answer"]))
        replace_block(task_file(14), "\n".join(items), key)

    # 15, 16
    rb = {t["id"]: t for t in robot_tasks.TASKS}
    for key, ids in SUB15.items():
        replace_block(task_file(15), "\n".join(robot_sub(rb[r], key, i + 1) for i, r in enumerate(ids)), key)
    pb = {t["id"]: t for t in prog_tasks.TASKS}
    for key, ids in SUB16.items():
        replace_block(task_file(16), "\n".join(prog_sub(pb[p], key, i + 1) for i, p in enumerate(ids)), key)
    print("тренировочные блоки обновлены")


if __name__ == "__main__":
    main()
