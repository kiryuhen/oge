"""Собирает 10 тренировочных вариантов ОГЭ (variants/variant-NN.md) и сводную таблицу ответов.

Задания 1–10 генерируются (ответы считаются программно), 11–12 — по каталогу materials/archive,
13 — образцы из tools/task13.json, 14 — файлы materials/task14/variant-NN.xlsx,
15–16 — банки задач с проверенными решениями.
Запуск:  python3 tools/build_variants.py   (из корня репозитория)
"""

import json
import os
import random

import gen_tasks as g
import prog_tasks
import robot_tasks
from build_practice import VARIANT_PROG, VARIANT_ROBOT, split_q12

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "variants")
IMG = os.path.join(ROOT, "images", "variants")

N_VARIANTS = 10


def spoiler(title, body):
    return f"<details><summary>{title}</summary>\n\n{body}\n\n</details>\n"


def build_variant(v, q11, q12, t13, xlsx):
    rng = random.Random(5000 + v)
    parts, answers = [], {}

    parts.append(f"# Вариант {v}\n\n"
                 "| Время | Заданий | Максимум |\n|---|---|---|\n| 2 ч 30 мин (150 минут) | 16 | 21 балл |\n\n"
                 "**Как выполнять.** Задания 1–10 решайте без компьютера и записывайте ответы на листок. "
                 "Задания 11–16 выполняйте на компьютере. Ответы — в самом конце файла, под спойлером. "
                 "Не подглядывайте до конца работы!\n\n"
                 "**Материалы:** каталог [`materials/archive`](../materials/archive) (задания 11, 12), "
                 f"файл [`materials/task14/variant-{v:02d}.xlsx`](../materials/task14/variant-{v:02d}.xlsx) "
                 "(задание 14). Для задания 15 нужна среда КуМир, для 16 — Python.\n\n"
                 "Если времени мало (1 час), сделайте за одно занятие задания 1–12, а 13–16 — за следующее.\n")

    # ---- часть 1
    parts.append("## Часть 1\n")
    for no in range(1, 11):
        fs = g.GENERATORS[no]
        f = fs[(v + no) % len(fs)]
        if f is g.t9_paths:
            name = f"v{v:02d}-t09.svg"
            r = f(rng, name)
            os.makedirs(IMG, exist_ok=True)
            with open(os.path.join(IMG, name), "w") as fh:
                fh.write(r["image"][1])
            r["text"] = r["text"].replace("IMG/", "../images/variants/")
        else:
            r = f(rng)
        parts.append(f"### Задание {no}\n\n{r['text']}\n")
        answers[no] = r["answer"]

    # ---- часть 2
    parts.append("## Часть 2\n\nЗадания этой части выполняются на компьютере.\n")
    q = q11[v - 1]
    parts.append(f"### Задание 11\n\n{q['q']}\n\nИщите в каталоге `materials/archive`.\n")
    answers[11] = q["answer"]
    q = q12[v - 1]
    parts.append(f"### Задание 12\n\n{q['q']}\n")
    answers[12] = q["answer"]

    pr, doc = t13["pres"][5 + v], t13["docs"][5 + v]
    parts.append("### Задание 13\n\nВыберите **одно** из заданий: 13.1 или 13.2.\n\n"
                 f"#### 13.1. Презентация «{pr['topic']}»\n\n{pr['req']}\n\n"
                 f"#### 13.2. Документ «{doc['topic']}»\n\n{doc['req']}\n\n**Образец:**\n\n"
                 f"![Образец](../images/task13/{doc['id']}.png)\n")
    answers[13] = ("Проверка по чек-листам: [13.1](../tasks/13-presentation-text.md#чек-лист-самопроверки-131), "
                   "[13.2](../tasks/13-presentation-text.md#чек-лист-самопроверки-132).")

    d = xlsx[f"variant-{v:02d}.xlsx"]
    qtext = "\n".join(f"{j + 1}. {qq}" for j, (qq, _) in enumerate(d["questions"]))
    parts.append(f"### Задание 14\n\nОткройте файл [`variant-{v:02d}.xlsx`](../materials/task14/variant-{v:02d}.xlsx).\n\n"
                 f"{d['intro']}\n\nПервые строки таблицы:\n\n{d['preview']}\n\nВыполните задание:\n\n{qtext}\n\n"
                 "Полученную таблицу сохраните в формате `.ods`.\n")
    answers[14] = d["questions"]

    rt = {t["id"]: t for t in robot_tasks.TASKS}[VARIANT_ROBOT[v - 1]]
    parts.append(f"### Задание 15\n\nИсполнитель Робот умеет перемещаться по лабиринту, начерченному на плоскости, "
                 f"разбитой на клетки. Система команд и проверок — [в теории](../theory/08-kumir.md).\n\n"
                 f"{rt['text']}\n\n{robot_tasks.COMMON}\n\n"
                 f"| Пример поля | Нужно закрасить |\n|---|---|\n"
                 f"| ![до](../images/robot/{rt['id']}-before.svg) | ![после](../images/robot/{rt['id']}-after.svg) |\n\n"
                 "Алгоритм может быть выполнен в среде КуМир или записан в текстовом редакторе.\n")
    answers[15] = rt["solution"]

    pt = {t["id"]: t for t in prog_tasks.TASKS}[VARIANT_PROG[v - 1]]
    tests = prog_tasks.make_tests(pt)
    ex_in, ex_out = tests[0]
    guarantee = (" " + pt["guarantee"]) if pt["guarantee"] else ""
    shown = prog_tasks.to_input(pt, ex_in).strip().replace("\n", "<br>")
    parts.append(f"### Задание 16\n\n{pt['text']}\n\n{pt['fmt']}{guarantee}\n\n**Пример работы программы:**\n\n"
                 f"| Входные данные | Выходные данные |\n|---|---|\n| {shown} | {ex_out.replace(chr(10), '<br>')} |\n")
    answers[16] = (pt["solution"], tests)

    # ---- ответы
    tbl = "| № | Ответ |\n|---|---|\n" + "\n".join(f"| {k} | {answers[k]} |" for k in range(1, 13))
    a14 = "\n".join(f"{j + 1}. **{a}**" + (" (значения для диаграммы)" if j == 2 else "")
                    for j, (_, a) in enumerate(answers[14]))
    sol16, tests16 = answers[16]
    t16 = "| № | Вход | Выход |\n|---|---|---|\n" + "\n".join(
        f"| {i + 1} | {prog_tasks.to_input(pt, a).strip().replace(chr(10), '<br>')} | {r.replace(chr(10), '<br>')} |"
        for i, (a, r) in enumerate(tests16))
    body = (f"**Задания 1–12** (по 1 баллу):\n\n{tbl}\n\n"
            f"**Задание 13** (2 балла): {answers[13]}\n\n"
            f"**Задание 14** (3 балла):\n\n{a14}\n\n"
            f"**Задание 15** (2 балла), один из возможных алгоритмов:\n\n```\n{answers[15]}\n```\n\n"
            f"**Задание 16** (2 балла), один из возможных вариантов программы:\n\n```python\n{sol16}\n```\n\n"
            f"Тесты для проверки:\n\n{t16}\n\n"
            "**Перевод в оценку:** 0–4 → «2», 5–10 → «3», 11–16 → «4», 17–21 → «5».")
    parts.append("---\n\n## Ответы\n\n" + spoiler("Показать ответы и решения", body))
    parts.append("\n[← Все варианты](README.md) · [К оглавлению](../README.md)\n")
    with open(os.path.join(OUT, f"variant-{v:02d}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return answers


def main():
    os.makedirs(OUT, exist_ok=True)
    corpus = json.load(open(os.path.join(HERE, "corpus_questions.json"), encoding="utf-8"))
    xlsx = json.load(open(os.path.join(HERE, "xlsx_questions.json"), encoding="utf-8"))
    t13 = json.load(open(os.path.join(HERE, "task13.json"), encoding="utf-8"))
    rng = random.Random(77)
    q11 = rng.sample(corpus["q11"][27:53], N_VARIANTS)  # [53] — в разборе, [:27] — в тренировке
    rest12 = split_q12(corpus["q12"])[1]
    q12 = rng.sample(rest12, N_VARIANTS)
    all_answers = {v: build_variant(v, q11, q12, t13, xlsx) for v in range(1, N_VARIANTS + 1)}

    # сводная таблица для учителя
    head = "| Задание | " + " | ".join(f"В{v}" for v in all_answers) + " |\n|---|" + "---|" * N_VARIANTS + "\n"
    rows = "\n".join(f"| {k} | " + " | ".join(str(all_answers[v][k]) for v in all_answers) + " |" for k in range(1, 13))
    r14 = "\n".join(f"| 14.{j + 1} | " + " | ".join(str(all_answers[v][14][j][1]) for v in all_answers) + " |"
                    for j in range(2))
    with open(os.path.join(OUT, "answers.md"), "w", encoding="utf-8") as f:
        f.write("# Ответы ко всем вариантам\n\n> Для учителя или для проверки после выполнения варианта. "
                "Решения заданий 13, 15, 16 и данные для диаграммы в задании 14 — в конце каждого варианта.\n\n"
                + head + rows + "\n" + r14 + "\n\n[← Все варианты](README.md)\n")
    print("варианты собраны:", N_VARIANTS)


if __name__ == "__main__":
    main()
