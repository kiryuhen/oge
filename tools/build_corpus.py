"""Строит учебный каталог materials/archive для заданий 11 и 12 и банк вопросов к нему.

Каталог — «архив школьной газеты»: статьи (.txt, .htm), фотографии (.jpg), графики (.png),
таблицы (.csv). Ответы на вопросы проверяются по самим файлам, поэтому они однозначны.

Запуск:  python3 tools/build_corpus.py   (из корня репозитория)
Результат: materials/archive/ и tools/corpus_questions.json
"""

import json
import os
import random
import shutil

from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "materials", "archive")
rng = random.Random(2027)

MALE = ["Артём", "Максим", "Иван", "Егор", "Тимофей", "Матвей", "Илья", "Кирилл", "Михаил", "Даниил",
        "Роман", "Глеб", "Фёдор", "Савелий", "Платон", "Лев", "Марк", "Никита", "Ярослав", "Арсений"]
FEMALE = ["Анна", "Мария", "Софья", "Алиса", "Ева", "Полина", "Варвара", "Вероника", "Дарья", "Ксения",
          "Ульяна", "Милана", "Таисия", "Василиса", "Арина", "Злата", "Кира", "Есения", "Алёна", "Елизавета"]
SURN = ["Соколов", "Морозов", "Волков", "Лебедев", "Козлов", "Новиков", "Зайцев", "Павлов", "Голубев",
        "Виноградов", "Богданов", "Воробьёв", "Фёдоров", "Михайлов", "Беляев", "Тарасов", "Белов", "Комаров",
        "Орлов", "Киселёв", "Макаров", "Андреев", "Ковалёв", "Ильин", "Гусев", "Титов", "Кузьмин", "Кудрявцев",
        "Баранов", "Куликов", "Алексеев", "Степанов", "Яковлев", "Сорокин", "Сергеев", "Романов", "Захаров",
        "Борисов", "Королёв", "Герасимов", "Пономарёв", "Григорьев", "Лазарев", "Медведев", "Ершов",
        "Никитин", "Соболев", "Рябов", "Поляков", "Цветков", "Данилов", "Жуков", "Фролов", "Журавлёв",
        "Николаев", "Крылов", "Максимов", "Сидоров", "Осипов", "Белоусов", "Федотов", "Дорофеев", "Егоров",
        "Матвеев", "Бобров", "Дмитриев", "Калинин", "Анисимов", "Петухов", "Антонов", "Тимофеев", "Никифоров",
        "Веселов", "Филиппов", "Марков", "Большаков", "Суханов", "Миронов", "Ширяев", "Александров", "Коновалов"]
LETTERS = "АБВГ"
SUBJECTS = ["математике", "физике", "химии", "биологии", "истории", "географии", "литературе",
            "информатике", "английскому языку", "астрономии", "экологии", "обществознанию"]
SPORTS = [("лыжных гонках", "на дистанции 5 километров"), ("лёгкой атлетике", "в беге на 100 метров"),
          ("плаванию", "на дистанции 50 метров вольным стилем"), ("лёгкой атлетике", "в прыжках в длину"),
          ("лыжных гонках", "на дистанции 3 километра"), ("лёгкой атлетике", "в беге на 400 метров"),
          ("плаванию", "на дистанции 100 метров брассом"), ("лёгкой атлетике", "в метании мяча")]
CITIES = ["Казань", "Великий Новгород", "Псков", "Суздаль", "Калининград", "Ярославль", "Тобольск",
          "Кострома", "Нижний Новгород", "Смоленск", "Тула", "Выборг", "Коломну", "Владимир", "Рязань"]
BOOKS = [("Л. Н. Толстого", "«Война и мир»"), ("Ф. М. Достоевского", "«Преступление и наказание»"),
         ("А. С. Пушкина", "«Капитанская дочка»"), ("Н. В. Гоголя", "«Мёртвые души»"),
         ("М. А. Булгакова", "«Собачье сердце»"), ("И. С. Тургенева", "«Отцы и дети»"),
         ("А. П. Чехова", "«Каштанка»"), ("М. Ю. Лермонтова", "«Герой нашего времени»"),
         ("Жюля Верна", "«Таинственный остров»"), ("Р. Брэдбери", "«451 градус по Фаренгейту»"),
         ("А. Грина", "«Алые паруса»"), ("В. Каверина", "«Два капитана»")]
FILLER = [
    "Редакция газеты поздравляет всех участников и благодарит учителей за подготовку.",
    "Фотографии с мероприятия можно посмотреть на стенде у входа в библиотеку.",
    "Следующее подобное мероприятие планируется провести уже в следующем учебном году.",
    "Многие ребята признались, что ждали этого события с самого начала четверти.",
    "Отдельное спасибо родительскому комитету за помощь в организации.",
    "Как всегда, не обошлось без сюрпризов и неожиданных поворотов.",
    "Зрители поддерживали участников громкими аплодисментами.",
    "По традиции в конце всех участников угостили чаем с пирогами.",
    "Подробный отчёт будет опубликован на сайте школы.",
    "Мы попросили участников поделиться впечатлениями, и вот что они рассказали.",
]

used_people = set()


def person():
    while True:
        if rng.random() < 0.5:
            first, last = rng.choice(MALE), rng.choice(SURN)
            g = "m"
        else:
            first, last = rng.choice(FEMALE), rng.choice(SURN) + "а"
            g = "f"
        if (first, last) not in used_people:
            used_people.add((first, last))
            return first, last, g


def balls(n):
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} балл"
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return f"{n} балла"
    return f"{n} баллов"


def cls():
    return f"{rng.randint(5, 11)} «{rng.choice(LETTERS)}»"


def v(g, m, f):
    return m if g == "m" else f


def article_olymp():
    p = person()
    subj = rng.choice(SUBJECTS)
    c = cls()
    score = rng.randint(61, 99)
    stage = rng.choice(["школьном", "муниципальном", "региональном"])
    title = f"Олимпиада по {subj}"
    body = [f"В этом году на {stage} этапе олимпиады по {subj} нашу школу представляли двенадцать человек.",
            f"Лучший результат показал{v(p[2], '', 'а')} {v(p[2], 'ученик', 'ученица')} {c} класса "
            f"{p[0]} {p[1]}, набравш{v(p[2], 'ий', 'ая')} {balls(score)} из 100.",
            rng.choice(FILLER),
            f"«Больше всего мне понравилась последняя задача, — рассказал{v(p[2], '', 'а')} {p[0]}. — "
            f"Над ней пришлось думать почти час»."]
    facts = {"type": "olymp", "g": p[2], "first": p[0], "last": p[1], "class": c, "subject": subj, "score": score,
             "stage": stage}
    return title, body, facts


def article_sport():
    p = person()
    kind, dist = rng.choice(SPORTS)
    c = cls()
    place = rng.choice(["первое", "второе", "третье"])
    t = f"{rng.randint(10, 59)},{rng.randint(0, 9)}"
    title = f"Соревнования по {kind}"
    body = [f"В прошлую субботу прошли районные соревнования по {kind}.",
            f"{p[0]} {p[1]} из {c} класса занял{v(p[2], '', 'а')} {place} место {dist}.",
            rng.choice(FILLER),
            f"Тренер команды отметил, что результат можно улучшить, если тренироваться не реже трёх раз в неделю."]
    facts = {"type": "sport", "g": p[2], "first": p[0], "last": p[1], "class": c, "kind": kind, "dist": dist,
             "place": place, "time": t}
    return title, body, facts


def article_trip():
    city = rng.choice(CITIES)
    c = cls()
    p = person()
    days = rng.randint(2, 6)
    title = "Путешествие класса"
    body = [f"Ученики {c} класса вернулись из поездки в {city}.",
            f"Поездка длилась {days} {'дня' if days < 5 else 'дней'}, за это время ребята побывали в музеях, "
            f"на экскурсии по старому городу и даже на мастер-классе гончаров.",
            f"Организовал{v(p[2], '', 'а')} поездку классный руководитель — {p[0]} {p[1]}.",
            rng.choice(FILLER)]
    facts = {"type": "trip", "g": p[2], "city": city, "class": c, "days": days, "first": p[0], "last": p[1]}
    return title, body, facts


def article_book():
    p = person()
    author, book = rng.choice(BOOKS)
    c = cls()
    title = "Книжная полка"
    body = [f"В рубрике «Книжная полка» мы рассказываем о книгах, которые советуют читать наши ученики.",
            f"В этом выпуске свою любимую книгу представляет {p[0]} {p[1]} ({c} класс). "
            f"Это роман {author} {book}.",
            f"«Эту книгу я перечитывал{v(p[2], '', 'а')} три раза и каждый раз находил{v(p[2], '', 'а')} в ней "
            f"что-то новое», — говорит {p[0]}.",
            rng.choice(FILLER)]
    facts = {"type": "book", "g": p[2], "first": p[0], "last": p[1], "class": c, "author": author, "book": book}
    return title, body, facts


def article_chess():
    p = person()
    q = person()
    c = cls()
    rounds = rng.randint(5, 9)
    title = "Шахматный турнир"
    body = [f"В актовом зале прошёл традиционный шахматный турнир, в нём участвовали {rng.randint(14, 40)} человек.",
            f"Турнир проходил в {rounds} туров по швейцарской системе.",
            f"Победителем стал{v(p[2], '', 'а')} {p[0]} {p[1]} ({c}), {v(p[2], 'который', 'которая')} "
            f"в последнем туре обыграл{v(p[2], '', 'а')} {q[0]} {q[1]}.",
            rng.choice(FILLER)]
    facts = {"type": "chess", "g": p[2], "first": p[0], "last": p[1], "class": c, "rounds": rounds,
             "loser_first": q[0], "loser_last": q[1]}
    return title, body, facts


def article_project():
    p = person()
    c = cls()
    topic = rng.choice(["умная теплица", "робот-сортировщик мусора", "метеостанция на микроконтроллере",
                        "приложение для изучения английских слов", "очистка воды с помощью угля",
                        "модель солнечной системы", "сайт школьного музея", "кормушка с камерой",
                        "игра про историю родного города", "датчик качества воздуха"])
    title = "Ярмарка проектов"
    body = ["На ежегодной ярмарке проектов было представлено более тридцати работ.",
            f"Гран-при жюри получил проект «{topic[0].upper() + topic[1:]}», автор — {p[0]} {p[1]}, {c} класс.",
            rng.choice(FILLER),
            "Проекты-победители отправятся на городской конкурс весной."]
    facts = {"type": "project", "g": p[2], "first": p[0], "last": p[1], "class": c, "topic": topic}
    return title, body, facts


MAKERS = [article_olymp, article_sport, article_trip, article_book, article_chess, article_project]


def write_txt(path, title, body):
    with open(path, "w", encoding="utf-8") as f:
        f.write(title + "\n\n" + "\n\n".join(body) + "\n")


def write_htm(path, title, body):
    paras = "\n".join(f"<p>{b}</p>" for b in body)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"<!DOCTYPE html>\n<html lang=\"ru\">\n<head><meta charset=\"utf-8\"><title>{title}</title></head>\n"
                f"<body>\n<h1>{title}</h1>\n{paras}\n</body>\n</html>\n")


def write_img(path, kb_target):
    """Картинка «шум» нужного примерного размера — для вопросов про объём файлов."""
    side = max(8, int((kb_target * 1024 / 3) ** 0.5))
    img = Image.effect_noise((side, side), rng.randint(30, 90)).convert("RGB")
    if path.endswith(".png"):
        img.save(path)
    else:
        img.save(path, quality=rng.randint(60, 95))


def build():
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    articles = []
    for year in range(2018, 2026):
        for issue in range(1, rng.randint(3, 5)):
            d = os.path.join(ROOT, str(year), f"issue-{issue:02d}")
            os.makedirs(d)
            for k in range(rng.randint(2, 4)):
                maker = rng.choice(MAKERS)
                title, body, facts = maker()
                ext = rng.choice([".txt", ".txt", ".htm"])
                name = f"article-{k + 1}{ext}"
                path = os.path.join(d, name)
                (write_txt if ext == ".txt" else write_htm)(path, title, body)
                facts["file"] = os.path.relpath(path, ROOT)
                facts["year"] = year
                articles.append(facts)
            for k in range(rng.randint(0, 3)):
                write_img(os.path.join(d, f"photo-{k + 1}.jpg"), rng.randint(3, 60))
            if rng.random() < 0.4:
                write_img(os.path.join(d, "chart.png"), rng.randint(5, 50))
            if rng.random() < 0.3:
                with open(os.path.join(d, "schedule.csv"), "w", encoding="utf-8") as f:
                    f.write("день;урок;кабинет\n" + "\n".join(
                        f"{rng.choice(['пн', 'вт', 'ср', 'чт', 'пт'])};{rng.randint(1, 7)};{rng.randint(101, 320)}"
                        for _ in range(rng.randint(5, 15))) + "\n")
    # отдельная папка с фотоархивом
    pd = os.path.join(ROOT, "photo")
    for sub in ["events", "sport", "graduation"]:
        os.makedirs(os.path.join(pd, sub))
        for k in range(rng.randint(3, 8)):
            ext = rng.choice([".jpg", ".jpg", ".png"])
            write_img(os.path.join(pd, sub, f"img-{k + 1:02d}{ext}"), rng.randint(3, 80))
    with open(os.path.join(ROOT, "readme.txt"), "w", encoding="utf-8") as f:
        f.write("Архив школьной газеты «Перемена». Материалы разложены по годам и выпускам.\n")
    return articles


# ------------------------------------------------------------------ банк вопросов

def all_files():
    res = []
    for dp, _, fns in os.walk(ROOT):
        for fn in fns:
            res.append(os.path.join(dp, fn))
    return res


def texts():
    return {p: open(p, encoding="utf-8").read() for p in all_files() if p.endswith((".txt", ".htm"))}


def unique_phrase(phrase):
    hits = [p for p, t in texts().items() if phrase in t]
    return len(hits) == 1


def make_q11(articles):
    qs = []
    for a in articles:
        t = a["type"]
        if t == "olymp":
            who = "ученице, набравшей" if a["g"] == "f" else "ученике, набравшем"
            q = (f"В одной из статей архива рассказывается об {who} на олимпиаде "
                 f"{balls(a['score'])} из 100. По какому предмету проходила эта олимпиада? "
                 f"Ответ запишите так, как он указан в тексте (например: «химии»).")
            ans = a["subject"]
            key = f"{balls(a['score'])} из 100"
        elif t == "sport":
            q = (f"В одной из статей архива упоминается {'спортсменка' if a['g'] == 'f' else 'спортсмен'} "
                 f"по фамилии {a['last']}. Какое место {'она заняла' if a['g'] == 'f' else 'он занял'}? "
                 f"В ответе запишите слово (например: «первое»).")
            ans, key = a["place"], a["last"] + " из"
        elif t == "trip":
            q = (f"Ученики одного из классов ездили в город, поездка длилась {a['days']} "
                 f"{'дня' if a['days'] < 5 else 'дней'} и её {'организовала' if a['g'] == 'f' else 'организовал'} {a['first']} {a['last']}. "
                 f"В какой город ездили ребята? Запишите название так, как оно указано в тексте.")
            ans, key = a["city"], f"{a['first']} {a['last']}"
        elif t == "book":
            q = (f"В рубрике «Книжная полка» {'ученица' if a['g'] == 'f' else 'ученик'} {a['class']} класса "
                 f"по имени {a['first']} рассказывает о любимой книге. Назовите {'её' if a['g'] == 'f' else 'его'} фамилию.")
            ans, key = a["last"], f"{a['first']} {a['last']} ({a['class']} класс)"
            # проверим, что пара имя+класс в рубрике уникальна
            same = [b for b in articles if b["type"] == "book" and b["first"] == a["first"]
                    and b["class"] == a["class"]]
            if len(same) != 1:
                continue
        elif t == "chess":
            q = (f"В одной из статей рассказывается о шахматном турнире, в последнем туре которого "
                 f"победитель обыграл(а) соперника по фамилии {a['loser_last']}. Назовите фамилию победителя.")
            ans, key = a["last"], f"{a['loser_first']} {a['loser_last']}"
        else:
            q = (f"Проект «{a['topic'][0].upper() + a['topic'][1:]}» получил гран-при на ярмарке проектов. "
                 f"Назовите фамилию автора проекта.")
            ans, key = a["last"], a["topic"][0].upper() + a["topic"][1:]
        if unique_phrase(key):
            qs.append({"q": q, "answer": ans, "file": a["file"], "search": key})
    return qs


def make_q12():
    files = all_files()
    rel = lambda p: os.path.relpath(p, ROOT)
    qs = []
    years = sorted({rel(p).split(os.sep)[0] for p in files if rel(p)[0].isdigit()})
    for ext in [".txt", ".htm", ".jpg", ".png", ".csv"]:
        n = sum(1 for p in files if p.endswith(ext))
        qs.append({"q": f"Сколько файлов с расширением **{ext}** содержится в каталоге **archive** "
                        f"и всех его подкаталогах? В ответе укажите только число.", "answer": str(n)})
    for y in years:
        for ext in [".txt", ".jpg"]:
            n = sum(1 for p in files if p.endswith(ext) and rel(p).startswith(y + os.sep))
            if n:
                qs.append({"q": f"Сколько файлов с расширением **{ext}** содержится в подкаталогах каталога "
                                f"**archive/{y}**? В ответе укажите только число.", "answer": str(n)})
    for lim in [10, 20, 30, 40]:
        for ext in [".jpg", ".png"]:
            n = sum(1 for p in files if p.endswith(ext) and os.path.getsize(p) > lim * 1024)
            qs.append({"q": f"Сколько файлов с расширением **{ext}** объёмом **более {lim} Кбайт** содержится "
                            f"в каталоге **archive** и всех его подкаталогах? В ответе укажите только число.",
                       "answer": str(n)})
    n = sum(1 for p in files if os.path.basename(p).startswith("article-1."))
    qs.append({"q": "Сколько файлов, имя которых (без расширения) — **article-1**, содержится в каталоге "
                    "**archive** и всех его подкаталогах?", "answer": str(n)})
    tot = sum(os.path.getsize(p) for p in files if rel(p).startswith("photo" + os.sep))
    qs.append({"q": "Каков общий объём (в Кбайтах) всех файлов в каталоге **archive/photo** и его подкаталогах? "
                    "Ответ округлите до целого числа.", "answer": str(round(tot / 1024))})
    return qs


if __name__ == "__main__":
    arts = build()
    q11 = make_q11(arts)
    q12 = make_q12()
    with open(os.path.join(os.path.dirname(__file__), "corpus_questions.json"), "w", encoding="utf-8") as f:
        json.dump({"q11": q11, "q12": q12}, f, ensure_ascii=False, indent=1)
    print(len(arts), "статей;", len(q11), "вопросов к 11;", len(q12), "вопросов к 12")
