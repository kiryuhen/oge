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


def replace_block(path, body):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if BEGIN not in text:
        raise SystemExit(f"нет маркера в {path}")
    new = re.sub(re.escape(BEGIN) + ".*?" + re.escape(END), BEGIN + "\n\n" + body.strip() + "\n\n" + END, text,
                 flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


def task_file(no):
    return glob.glob(os.path.join(ROOT, "tasks", f"{no:02d}-*.md"))[0]


def main():
    corpus = json.load(open(os.path.join(HERE, "corpus_questions.json"), encoding="utf-8"))
    xlsx = json.load(open(os.path.join(HERE, "xlsx_questions.json"), encoding="utf-8"))

    # 1–10: по 5 задач «как на экзамене», нумерация с 6 (1–5 — авторские в самом файле)
    for no in range(1, 11):
        rng = random.Random(1000 + no)
        items = gen_simple(no, 5, rng, 6, f"t{no:02d}-practice", "../images/tasks/")
        replace_block(task_file(no), "\n".join(items))

    # 11: 10 вопросов по архиву
    rng = random.Random(11)
    qs = rng.sample(corpus["q11"][:27], 10)  # первая половина банка — для тренировки, вторая — для вариантов
    items = [f"### Задача {i + 1}\n\n{q['q']}\n\n" + answer_block(
        q["answer"], f"\n\nГде искать: файл `archive/{q['file']}`, поисковая фраза: «{q['search']}».")
        for i, q in enumerate(qs)]
    replace_block(task_file(11), "\n".join(items))

    # 12: 10 вопросов разных типов (остальные — для вариантов, см. split_q12)
    qs = split_q12(corpus["q12"])[0]
    items = [f"### Задача {i + 1}\n\n{q['q']}\n\n" + answer_block(q["answer"]) for i, q in enumerate(qs)]
    replace_block(task_file(12), "\n".join(items))

    # 13: пять презентаций и пять документов
    t13 = json.load(open(os.path.join(HERE, "task13.json"), encoding="utf-8"))
    items = []
    for i, pr in enumerate(t13["pres"][1:6]):
        items.append(f"### Задача {i + 1} (13.1). Презентация «{pr['topic']}»\n\n{pr['req']}\n\n"
                     "<details><summary>Как проверить</summary>\n\nПройдите по "
                     "[чек-листу 13.1](#чек-лист-самопроверки-131). Каждый пункт — обязателен.\n\n</details>\n")
    for i, d in enumerate(t13["docs"][1:6]):
        items.append(f"### Задача {i + 6} (13.2). Документ «{d['topic']}»\n\n{d['req']}\n\n**Образец:**\n\n"
                     f"![Образец]({'../images/task13/'}{d['id']}.png)\n\n"
                     "<details><summary>Как проверить</summary>\n\nПройдите по "
                     "[чек-листу 13.2](#чек-лист-самопроверки-132). Положите свой документ рядом с образцом "
                     "и сравните построчно.\n\n</details>\n")
    replace_block(task_file(13), "\n".join(items))

    # 14: 4 тренировочных файла × 3 вопроса
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

    # 15: 10 задач на Робота
    by_id = {t["id"]: t for t in robot_tasks.TASKS}
    items = [robot_md(by_id[r], i + 1, "../images/robot/") for i, r in enumerate(PRACTICE_ROBOT)]
    replace_block(task_file(15), "\n".join(items))

    # 16: 10 задач на программирование
    by_id = {t["id"]: t for t in prog_tasks.TASKS}
    items = [prog_md(by_id[p], i + 1) for i, p in enumerate(PRACTICE_PROG)]
    replace_block(task_file(16), "\n".join(items))
    print("тренировочные блоки обновлены")


if __name__ == "__main__":
    main()
