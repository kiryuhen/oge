"""Банк задач для задания 16 (программа на Python): условие, эталонное решение, тесты.

Проверка: каждое эталонное решение запускается как отдельная программа на тестах,
а правильный ответ считается независимой функцией `ref`.
Запуск:  python3 tools/prog_tasks.py
"""

import random
import subprocess
import sys

N_FMT = ("Программа получает на вход количество чисел в последовательности, а затем сами числа. "
         "Количество чисел не превышает 1000. Введённые числа по модулю не превышают 30 000.")
N_FMT_NAT = ("Программа получает на вход количество чисел в последовательности, а затем сами числа. "
             "Количество чисел не превышает 1000. Введённые числа — натуральные, не превышают 30 000.")
Z_FMT = ("Программа получает на вход натуральные числа, количество введённых чисел неизвестно, "
         "последовательность чисел заканчивается числом 0 (0 — признак окончания ввода, не входит "
         "в последовательность). Количество чисел не превышает 1000. Введённые числа не превышают 30 000.")

TASKS = []


def nonempty_sum(xs):
    """Сумма с гарантией «хотя бы одно такое число есть» (иначе — тест недопустим)."""
    if not xs:
        raise ValueError
    return sum(xs)


def task(tid, text, fmt, mode, ref, solution, gen, guarantee=None):
    TASKS.append({"id": tid, "text": text, "fmt": fmt, "mode": mode, "ref": ref,
                  "solution": solution.strip("\n"), "gen": gen, "guarantee": guarantee})


def nums(lo, hi):
    return lambda rng: [rng.randint(lo, hi) for _ in range(rng.randint(1, 12))]


task("p01", "Напишите программу, которая в последовательности натуральных чисел определяет количество чисел, "
     "кратных 4. Программа должна вывести одно число — количество чисел, кратных 4.",
     N_FMT_NAT, "n", lambda a: sum(1 for x in a if x % 4 == 0), """
n = int(input())
count = 0
for i in range(n):
    x = int(input())
    if x % 4 == 0:
        count += 1
print(count)
""", nums(1, 100))

task("p02", "Напишите программу, которая в последовательности натуральных чисел определяет сумму чисел, "
     "кратных 6 и оканчивающихся на 4. Программа должна вывести одно число — сумму таких чисел.",
     N_FMT_NAT, "n", lambda a: nonempty_sum([x for x in a if x % 6 == 0 and x % 10 == 4]), """
n = int(input())
s = 0
for i in range(n):
    x = int(input())
    if x % 6 == 0 and x % 10 == 4:
        s += x
print(s)
""", nums(1, 200), "В последовательности всегда имеется хотя бы одно число, кратное 6 и оканчивающееся на 4.")

task("p03", "Напишите программу, которая в последовательности натуральных чисел определяет максимальное "
     "число, кратное 5. Программа должна вывести одно число — максимальное число, кратное 5.",
     N_FMT_NAT, "n", lambda a: max(x for x in a if x % 5 == 0), """
n = int(input())
mx = 0
for i in range(n):
    x = int(input())
    if x % 5 == 0 and x > mx:
        mx = x
print(mx)
""", nums(1, 300), "В последовательности всегда имеется хотя бы одно число, кратное 5.")

task("p04", "Напишите программу, которая в последовательности натуральных чисел определяет минимальное "
     "число, оканчивающееся на 3. Программа должна вывести одно число — минимальное число, оканчивающееся на 3.",
     Z_FMT, "zero", lambda a: min(x for x in a if x % 10 == 3), """
mn = 30001
x = int(input())
while x != 0:
    if x % 10 == 3 and x < mn:
        mn = x
    x = int(input())
print(mn)
""", nums(1, 30000), "В последовательности всегда имеется хотя бы одно число, оканчивающееся на 3.")

task("p05", "Напишите программу, которая в последовательности натуральных чисел определяет количество "
     "чисел, оканчивающихся на 7. Программа должна вывести одно число — количество таких чисел.",
     Z_FMT, "zero", lambda a: sum(1 for x in a if x % 10 == 7), """
count = 0
x = int(input())
while x != 0:
    if x % 10 == 7:
        count += 1
    x = int(input())
print(count)
""", nums(1, 500))

task("p06", "Напишите программу, которая в последовательности натуральных чисел вычисляет среднее "
     "арифметическое чётных чисел. Программа должна вывести среднее арифметическое с точностью до десятых.",
     Z_FMT, "zero", lambda a: f"{sum(x for x in a if x % 2 == 0) / len([x for x in a if x % 2 == 0]):.1f}", """
s = 0
count = 0
x = int(input())
while x != 0:
    if x % 2 == 0:
        s += x
        count += 1
    x = int(input())
print(f"{s / count:.1f}")
""", nums(1, 100), "В последовательности всегда имеется хотя бы одно чётное число.")

task("p07", "Напишите программу, которая в последовательности натуральных чисел определяет количество чисел, "
     "кратных 3, и максимальное из них. Программа должна вывести два числа: сначала количество чисел, "
     "кратных 3, затем максимальное число, кратное 3 (каждое число — в отдельной строке).",
     N_FMT_NAT, "n", lambda a: f"{sum(1 for x in a if x % 3 == 0)}\n{max(x for x in a if x % 3 == 0)}", """
n = int(input())
count = 0
mx = 0
for i in range(n):
    x = int(input())
    if x % 3 == 0:
        count += 1
        if x > mx:
            mx = x
print(count)
print(mx)
""", nums(1, 300), "В последовательности всегда имеется хотя бы одно число, кратное 3.")

task("p08", "Напишите программу, которая в последовательности натуральных чисел определяет количество чисел, "
     "которые кратны 3, но не кратны 9. Программа должна вывести одно число.",
     N_FMT_NAT, "n", lambda a: sum(1 for x in a if x % 3 == 0 and x % 9 != 0), """
n = int(input())
count = 0
for i in range(n):
    x = int(input())
    if x % 3 == 0 and x % 9 != 0:
        count += 1
print(count)
""", nums(1, 200))

task("p09", "Напишите программу, которая в последовательности натуральных чисел определяет сумму всех "
     "двузначных чисел. Программа должна вывести одно число — сумму двузначных чисел.",
     Z_FMT, "zero", lambda a: sum(x for x in a if 10 <= x <= 99), """
s = 0
x = int(input())
while x != 0:
    if 10 <= x <= 99:
        s += x
    x = int(input())
print(s)
""", nums(1, 400))

task("p10", "Напишите программу, которая для последовательности целых чисел определяет, сколько чисел больше "
     "предыдущего числа последовательности. Первое число не учитывается (у него нет предыдущего). "
     "Программа должна вывести одно число.",
     N_FMT, "n", lambda a: sum(1 for i in range(1, len(a)) if a[i] > a[i - 1]), """
n = int(input())
prev = int(input())
count = 0
for i in range(n - 1):
    x = int(input())
    if x > prev:
        count += 1
    prev = x
print(count)
""", nums(-50, 50))

task("p11", "Напишите программу, которая в последовательности натуральных чисел определяет минимальное "
     "чётное число. Программа должна вывести одно число — минимальное чётное число.",
     N_FMT_NAT, "n", lambda a: min(x for x in a if x % 2 == 0), """
n = int(input())
mn = 30001
for i in range(n):
    x = int(input())
    if x % 2 == 0 and x < mn:
        mn = x
print(mn)
""", nums(1, 1000), "В последовательности всегда имеется хотя бы одно чётное число.")

task("p12", "Напишите программу, которая в последовательности натуральных чисел определяет количество чисел, "
     "оканчивающихся на 4 и кратных 3. Программа должна вывести одно число.",
     Z_FMT, "zero", lambda a: sum(1 for x in a if x % 10 == 4 and x % 3 == 0), """
count = 0
x = int(input())
while x != 0:
    if x % 10 == 4 and x % 3 == 0:
        count += 1
    x = int(input())
print(count)
""", nums(1, 120))

task("p13", "Напишите программу, которая в последовательности натуральных чисел определяет количество чисел, "
     "кратных 7, и их сумму. Программа должна вывести два числа: сначала количество, затем сумму "
     "(каждое число — в отдельной строке).",
     Z_FMT, "zero", lambda a: f"{sum(1 for x in a if x % 7 == 0)}\n{sum(x for x in a if x % 7 == 0)}", """
count = 0
s = 0
x = int(input())
while x != 0:
    if x % 7 == 0:
        count += 1
        s += x
    x = int(input())
print(count)
print(s)
""", nums(1, 100))

task("p14", "Напишите программу, которая в последовательности натуральных чисел определяет максимальное число, "
     "оканчивающееся на 6. Программа должна вывести одно число — максимальное число, оканчивающееся на 6.",
     Z_FMT, "zero", lambda a: max(x for x in a if x % 10 == 6), """
mx = 0
x = int(input())
while x != 0:
    if x % 10 == 6 and x > mx:
        mx = x
    x = int(input())
print(mx)
""", nums(1, 30000), "В последовательности всегда имеется хотя бы одно число, оканчивающееся на 6.")

task("p15", "Напишите программу, которая для последовательности целых чисел определяет разность между "
     "максимальным и минимальным числом. Программа должна вывести одно число.",
     N_FMT, "n", lambda a: max(a) - min(a), """
n = int(input())
x = int(input())
mx = x
mn = x
for i in range(n - 1):
    x = int(input())
    if x > mx:
        mx = x
    if x < mn:
        mn = x
print(mx - mn)
""", nums(-30000, 30000))

task("p16", "Напишите программу, которая в последовательности натуральных чисел определяет, сколько раз "
     "в ней встречается максимальное число. Программа должна вывести одно число.",
     N_FMT_NAT, "n", lambda a: a.count(max(a)), """
n = int(input())
mx = 0
count = 0
for i in range(n):
    x = int(input())
    if x > mx:
        mx = x
        count = 1
    elif x == mx:
        count += 1
print(count)
""", lambda rng: [rng.randint(1, 6) for _ in range(rng.randint(1, 12))])

task("p17", "Напишите программу, которая в последовательности натуральных чисел определяет количество "
     "двузначных чисел, кратных 5. Программа должна вывести одно число.",
     N_FMT_NAT, "n", lambda a: sum(1 for x in a if 10 <= x <= 99 and x % 5 == 0), """
n = int(input())
count = 0
for i in range(n):
    x = int(input())
    if 10 <= x <= 99 and x % 5 == 0:
        count += 1
print(count)
""", nums(1, 150))

task("p18", "Напишите программу, которая в последовательности натуральных чисел определяет, есть ли в ней "
     "число, кратное 13. Программа должна вывести «YES», если такое число есть, и «NO» в противном случае.",
     Z_FMT, "zero", lambda a: "YES" if any(x % 13 == 0 for x in a) else "NO", """
found = False
x = int(input())
while x != 0:
    if x % 13 == 0:
        found = True
    x = int(input())
if found:
    print("YES")
else:
    print("NO")
""", nums(1, 60))

task("p19", "Напишите программу, которая в последовательности натуральных чисел определяет сумму чисел, "
     "оканчивающихся на 2 или на 5. Программа должна вывести одно число — сумму таких чисел.",
     N_FMT_NAT, "n", lambda a: sum(x for x in a if x % 10 in (2, 5)), """
n = int(input())
s = 0
for i in range(n):
    x = int(input())
    if x % 10 == 2 or x % 10 == 5:
        s += x
print(s)
""", nums(1, 100))

task("p20", "Напишите программу, которая в последовательности натуральных чисел определяет минимальное число, "
     "кратное 4, и количество чисел, кратных 4. Программа должна вывести два числа: сначала минимальное число, "
     "кратное 4, затем количество таких чисел (каждое — в отдельной строке).",
     Z_FMT, "zero", lambda a: f"{min(x for x in a if x % 4 == 0)}\n{sum(1 for x in a if x % 4 == 0)}", """
mn = 30001
count = 0
x = int(input())
while x != 0:
    if x % 4 == 0:
        count += 1
        if x < mn:
            mn = x
    x = int(input())
print(mn)
print(count)
""", nums(1, 30000), "В последовательности всегда имеется хотя бы одно число, кратное 4.")


# ---------------------------------------------------------------- тесты

def to_input(t, a):
    if t["mode"] == "n":
        return "\n".join(map(str, [len(a)] + a)) + "\n"
    return "\n".join(map(str, a + [0])) + "\n"


def valid(t, a):
    try:
        t["ref"](a)
        return True
    except (ValueError, ZeroDivisionError):
        return False


def make_tests(t, k=4, seed=0):
    """k тестов: детерминированно, с гарантией выполнения условия задачи."""
    rng = random.Random(int(t["id"][1:]) * 7919 + seed)
    tests = []
    tries = 0
    while len(tests) < k:
        tries += 1
        a = t["gen"](rng)[:6] if len(tests) < k - 1 else t["gen"](rng)
        if len(a) < 3:
            continue
        if not valid(t, a):
            continue
        if tries < 500 and any(str(t["ref"](a)) == str(t["ref"](b)) for b in tests):
            continue
        tests.append(a)
    return [(a, str(t["ref"](a))) for a in tests]


def run_solution(t, a):
    r = subprocess.run([sys.executable, "-c", t["solution"]], input=to_input(t, a), capture_output=True,
                       text=True, timeout=10)
    return r.stdout.strip()


def check(t, extra=200):
    rng = random.Random(1)
    cases = [a for a, _ in make_tests(t)]
    while len(cases) < extra:
        a = t["gen"](rng)
        if valid(t, a):
            cases.append(a)
    # один процесс на все случаи — быстрее
    code = ("import sys, io\nSRC = " + repr(t["solution"]) + "\n"
            "for inp in " + repr([to_input(t, a) for a in cases]) + ":\n"
            "    sys.stdin = io.StringIO(inp)\n    exec(SRC, {})\n    print('#END')\n")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60).stdout
    got = [x.strip() for x in out.split("#END")[:-1]]
    for a, g in zip(cases, got):
        if g != str(t["ref"](a)):
            raise AssertionError(f"{t['id']}: на {a} получено {g!r}, ожидалось {t['ref'](a)!r}")


if __name__ == "__main__":
    for t in TASKS:
        check(t)
        print("OK", t["id"], [r for _, r in make_tests(t)])
