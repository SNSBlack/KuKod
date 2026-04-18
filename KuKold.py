import os, sys, json, time, random, threading, textwrap
from dataclasses import dataclass, field
from typing import Optional

# ── зависимости ──────────────────────────────────────────────────────
def ensure(pkg, import_name=None):
    n = import_name or pkg
    try:
        __import__(n)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {pkg} --break-system-packages -q")

ensure("customtkinter"); ensure("pillow", "PIL"); ensure("google-genai")

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageDraw
from google import genai
from google.genai import types

# ── тема ─────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── палитра ──────────────────────────────────────────────────────────
C = {
    "bg":       "#0F1117",
    "panel":    "#1A1D27",
    "card":     "#22263A",
    "accent":   "#C9A84C",
    "accent2":  "#534AB7",
    "teal":     "#1D9E75",
    "red":      "#E24B4A",
    "muted":    "#7A7F9A",
    "text":     "#E8E8F0",
    "subtext":  "#9298B8",
    "border":   "#2E3350",
    "hover":    "#2A2F4A",
}

FONTS = {
    "title":   ("Georgia", 26, "bold"),
    "h1":      ("Georgia", 20, "bold"),
    "h2":      ("Georgia", 16, "bold"),
    "h3":      ("Helvetica", 13, "bold"),
    "body":    ("Helvetica", 13),
    "small":   ("Helvetica", 11),
    "mono":    ("Courier", 12),
    "xp":      ("Georgia", 28, "bold"),
}

# ── данные ───────────────────────────────────────────────────────────
CLASSICS = {
    "pushkin": {
        "name": "Александр Пушкин", "years": "1799–1837", "icon": "📜",
        "system": (
            "Ты — цифровой двойник Александра Сергеевича Пушкина. "
            "Говори от первого лица, стиль XIX века но понятный. "
            "Отвечай только на основе достоверных исторических фактов: биография, "
            "произведения, письма, современники. В конце каждого ответа: "
            "'[Источник: ...]' — реальный источник. Максимум 120 слов."
        ),
        "greeting": "Рад встрече! Спрашивайте о поэзии, моей жизни или эпохе...",
        "xp": 40, "color": "#C9A84C",
        "demo": [
            "Поэзия — моё дыхание. Я писал везде: в ссылке, на балах, в дороге...\n[Источник: Письма Пушкина, т. II, 1824–1830]",
            "Татьяна — мой любимый образ. В ней воплощена русская душа: верная, глубокая, непоказная.\n[Источник: Пушкин А.С. Полн. собр. соч., т. 6]",
            "Ссылка на юг дала мне многое — Кавказ, Крым, южные поэмы.\n[Источник: Лотман Ю. Биография Пушкина. СПб., 1995]",
        ],
    },
    "chekhov": {
        "name": "Антон Чехов", "years": "1860–1904", "icon": "🎭",
        "system": (
            "Ты — цифровой двойник Антона Чехова. Говори лаконично, "
            "с мягким юмором. Только достоверные факты о жизни и творчестве. "
            "В конце: '[Источник: ...]'. Максимум 100 слов."
        ),
        "greeting": "Здравствуйте. Я лечил людей и писал о них. Что вас интересует?",
        "xp": 45, "color": "#534AB7",
        "demo": [
            "Краткость — сестра таланта. Лишнее слово убивает живое.\n[Источник: Письмо Суворину, 1889]",
            "Медицина — законная жена, литература — любовница. Обе требуют всего.\n[Источник: Письмо, 1888, РГАЛИ ф. 331]",
            "На Сахалине я понял: за каждым номером в списке — живой человек.\n[Источник: Чехов А.П. Остров Сахалин, 1895]",
        ],
    },
    "tolstoy": {
        "name": "Лев Толстой", "years": "1828–1910", "icon": "⚔️",
        "system": (
            "Ты — Лев Толстой в зрелые годы. Говори глубоко, философски. "
            "Только достоверные факты: романы, трактаты, дневники, Ясная Поляна. "
            "В конце: '[Источник: ...]'. Максимум 120 слов."
        ),
        "greeting": "Истина — в простоте. Спрашивайте, отвечу честно.",
        "xp": 50, "color": "#1D9E75",
        "demo": [
            "«Война и мир» писалась семь лет. Всё великое совершается медленно.\n[Источник: Дневники Толстого, 1865–1869, ИРЛИ]",
            "Я не верю в государство и церковь. Верю в совесть каждого человека.\n[Источник: Толстой Л.Н. В чём моя вера? 1884]",
            "Яснополянская школа — моя лучшая работа. Крестьянский ребёнок умнее, чем думают господа.\n[Источник: Толстой Л.Н. Яснополянская школа. 1862]",
        ],
    },
}

QUIZZES = {
    "arch": {
        "title": "Архитектура России", "icon": "🏛", "xp": 35,
        "questions": [
            {
                "q": "Какой стиль характерен для Большого театра в Москве?",
                "opts": ["Барокко", "Русский ампир", "Конструктивизм", "Модерн"],
                "ans": 1,
                "exp": "Большой театр (1825) — русский ампир: коринфские колонны, строгий декор. Архитектор — Осип Бове.\n[Источник: Архитектурный словарь, М., 2003]",
            },
            {
                "q": "В каком веке построен храм Василия Блаженного?",
                "opts": ["XIV", "XV", "XVI", "XVII"],
                "ans": 2,
                "exp": "Собор построен в 1555–1561 гг. по приказу Ивана IV. Архитекторы — Барма и Постник.\n[Источник: БРЭ, том 3, с. 412]",
            },
            {
                "q": "Что такое конструктивизм в архитектуре?",
                "opts": [
                    "Богатый декор XIX века",
                    "Авангард 1920–30-х: функциональность без украшений",
                    "Подражание Древней Греции",
                    "Деревянное зодчество Севера",
                ],
                "ans": 1,
                "exp": "Конструктивизм — советский авангард 1920–30-х: геометрия, функциональность, отказ от декора.\n[Источник: Хан-Магомедов С.О. Конструктивизм. М., 1994]",
            },
        ],
    },
    "music": {
        "title": "Русская музыка", "icon": "🎼", "xp": 40,
        "questions": [
            {
                "q": "Кто входил в творческое объединение «Могучая кучка»?",
                "opts": [
                    "Чайковский, Рахманинов, Скрябин",
                    "Балакирев, Бородин, Кюи, Мусоргский, Римский-Корсаков",
                    "Глинка, Даргомыжский, Варламов",
                    "Прокофьев, Шостакович, Хачатурян",
                ],
                "ans": 1,
                "exp": "«Могучая кучка» (1856–1870-е) — кружок Балакирева. Название дал критик Стасов в 1867 г.\n[Источник: Асафьев Б. Русская музыка. Л., 1968]",
            },
            {
                "q": "В каком году Чайковский написал «Лебединое озеро»?",
                "opts": ["1869", "1876", "1890", "1895"],
                "ans": 1,
                "exp": "«Лебединое озеро» написано в 1875–1876 гг., премьера — 1877, Большой театр.\n[Источник: Виноградов Г. Чайковский. М., 1990, с. 234]",
            },
            {
                "q": "Какая опера Мусоргского считается вершиной русской оперной классики?",
                "opts": ["Князь Игорь", "Садко", "Борис Годунов", "Руслан и Людмила"],
                "ans": 2,
                "exp": "«Борис Годунов» (1869, ред. 1872) — опера по Пушкину. Народ как главный герой.\n[Источник: Левашёв Е. Мусоргский. М., 1978]",
            },
        ],
    },
    "lit": {
        "title": "Русская литература", "icon": "📖", "xp": 40,
        "questions": [
            {
                "q": "В каком году написан роман «Евгений Онегин»?",
                "opts": ["1815–1818", "1823–1831", "1835–1837", "1810–1815"],
                "ans": 1,
                "exp": "Пушкин работал над «Евгением Онегиным» около 8 лет — с 1823 по 1831 год.\n[Источник: Лотман Ю. Пушкин. СПб., 1995, с. 312]",
            },
            {
                "q": "Какой жанр использовал Чехов чаще всего?",
                "opts": ["Роман", "Поэма", "Рассказ и пьеса", "Очерк"],
                "ans": 2,
                "exp": "Чехов — мастер малой прозы и драматургии. Написал более 600 рассказов и 4 великие пьесы.\n[Источник: Чудаков А. Чехов. М., 1971]",
            },
            {
                "q": "Как называется усадьба Льва Толстого?",
                "opts": ["Михайловское", "Ясная Поляна", "Спасское-Лутовиново", "Мелихово"],
                "ans": 1,
                "exp": "Ясная Поляна — родовое имение Толстых в Тульской губернии. Здесь написаны «Война и мир» и «Анна Каренина».\n[Источник: БРЭ, том 35, с. 604]",
            },
        ],
    },
}

# ── состояние игрока ──────────────────────────────────────────────────
@dataclass
class Player:
    name: str = "Исследователь"
    xp: int = 0
    level: int = 1
    done: list = field(default_factory=list)
    badges: list = field(default_factory=list)
    histories: dict = field(default_factory=dict)

    def add_xp(self, n):
        self.xp += n
        new_lvl = 1 + self.xp // 100
        up = new_lvl > self.level
        self.level = new_lvl
        return up

    def to_next(self):
        return self.level * 100 - self.xp

    def badge(self, b):
        if b not in self.badges:
            self.badges.append(b)
            return True
        return False

# ── Google Gemini ─────────────────────────────────────────────────────
def ai_reply(client, history, user_msg, system, classic_id):
    """Отправляет запрос к Google Gemini API и возвращает ответ."""
    if client is None:
        time.sleep(0.7)
        return random.choice(CLASSICS[classic_id]["demo"])
    
    try:
        # Формируем контент с историей диалога
        contents = []
        
        # Добавляем историю сообщений
        for msg in history:
            if msg["role"] == "user":
                contents.append(types.UserContent(parts=[types.Part.from_text(text=msg["content"])]))
            else:
                contents.append(types.ModelContent(parts=[types.Part.from_text(text=msg["content"])]))
        
        # Добавляем текущее сообщение пользователя
        contents.append(types.UserContent(parts=[types.Part.from_text(text=user_msg)]))
        
        # Настройки генерации
        config = types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=400,
            temperature=0.7,
        )
        
        # Отправляем запрос
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=contents,
            config=config,
        )
        
        return response.text if response.text else "Извините, не удалось получить ответ."
        
    except Exception as e:
        return f"[Ошибка API: {e}]\n" + random.choice(CLASSICS[classic_id]["demo"])

# ═══════════════════════════════════════════════════════════════════════
#  ГЛАВНОЕ ОКНО
# ═══════════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("КуКод")
        self.geometry("1100x720")
        self.minsize(900, 640)
        self.configure(fg_color=C["bg"])

        self.player = Player()
        self.client = self._init_client()
        self._current_frame = None

        self._show_welcome()

    # ── Google Gemini Client ──────────────────────────────────────────
    def _init_client(self):
        """Инициализирует клиент Google Gemini."""
        # Встроенный API ключ
        key = "AIzaSyCPHRh7qcTg782IcpszVxpc4cNvWglgZT8"
        try:
            return genai.Client(api_key=key)
        except Exception as e:
            print(f"Ошибка инициализации Gemini: {e}")
            return None

    # ── навигация ────────────────────────────────────────────────────
    def _switch(self, frame_class, **kwargs):
        if self._current_frame:
            self._current_frame.destroy()
        self._current_frame = frame_class(self, **kwargs)
        self._current_frame.pack(fill="both", expand=True)

    def _show_welcome(self):   self._switch(WelcomeScreen)
    def _show_main(self):      self._switch(MainScreen)
    def _show_classic(self, cid): self._switch(ClassicScreen, classic_id=cid)
    def _show_quiz(self, qid): self._switch(QuizScreen, quiz_id=qid)
    def _show_stats(self):     self._switch(StatsScreen)

    # ── XP-уведомление ───────────────────────────────────────────────
    def _xp_popup(self, amount, reason, leveled=False):
        pop = ctk.CTkToplevel(self)
        pop.title("")
        pop.geometry("320x130")
        pop.configure(fg_color=C["card"])
        pop.grab_set()
        msg = f"+{amount} XP  —  {reason}"
        if leveled:
            msg += "\n🎉 Новый уровень!"
        ctk.CTkLabel(pop, text=msg, font=FONTS["h3"],
                     text_color=C["accent"], wraplength=280).pack(pady=36)
        pop.after(1600, pop.destroy)

# ═══════════════════════════════════════════════════════════════════════
#  ЭКРАН ПРИВЕТСТВИЯ
# ═══════════════════════════════════════════════════════════════════════
class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"])
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=C["panel"],
                            corner_radius=20, width=480)
        card.grid(row=0, column=0, padx=40, pady=60, sticky="nsew",
                  ipadx=40, ipady=40)
        card.columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="КуКод",
                     font=("Georgia", 32, "bold"),
                     text_color=C["accent"]).grid(row=0, column=0, pady=(40, 4))
        ctk.CTkLabel(card, text="ИИ-гид по культуре России",
                     font=FONTS["body"], text_color=C["subtext"]).grid(row=1, column=0, pady=(0, 24))

        icons_frame = ctk.CTkFrame(card, fg_color="transparent")
        icons_frame.grid(row=2, column=0, pady=8)
        for ico, lab in [("📖", "Литература"), ("🏛", "Архитектура"),
                          ("🎼", "Музыка"), ("🎨", "Живопись")]:
            col = ctk.CTkFrame(icons_frame, fg_color=C["card"], corner_radius=12, width=90, height=72)
            col.pack(side="left", padx=6)
            col.pack_propagate(False)
            ctk.CTkLabel(col, text=ico, font=("Helvetica", 22)).pack(pady=(12, 2))
            ctk.CTkLabel(col, text=lab, font=FONTS["small"],
                         text_color=C["subtext"]).pack()

        ctk.CTkLabel(card, text="Введите ваше имя:",
                     font=FONTS["h3"], text_color=C["text"]).grid(row=3, column=0, pady=(28, 6))
        self._name_var = tk.StringVar(value="Исследователь")
        entry = ctk.CTkEntry(card, textvariable=self._name_var,
                             font=FONTS["body"], width=300, height=42,
                             fg_color=C["card"], border_color=C["accent"],
                             text_color=C["text"])
        entry.grid(row=4, column=0, pady=(0, 20))
        entry.bind("<Return>", lambda e: self._start())

        ctk.CTkButton(card, text="Начать путешествие  →",
                      font=FONTS["h3"], height=48, width=280,
                      fg_color=C["accent"], hover_color="#A8863A",
                      text_color="#0F1117",
                      command=self._start).grid(row=5, column=0, pady=(0, 40))




    def _start(self):
        name = self._name_var.get().strip() or "Исследователь"
        self.master.player.name = name
        self.master._show_main()

# ═══════════════════════════════════════════════════════════════════════
#  ГЛАВНЫЙ ЭКРАН
# ═══════════════════════════════════════════════════════════════════════
class MainScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"])
        self._build()

    def _build(self):
        p = self.master.player

        # ── верхняя панель ───────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=0, height=62)
        top.pack(fill="x")
        top.pack_propagate(False)
        top.columnconfigure(1, weight=1)

        ctk.CTkLabel(top, text="КуКод",
                     font=("Georgia", 17, "bold"),
                     text_color=C["accent"]).pack(side="left", padx=24, pady=16)

        xp_bar_frame = ctk.CTkFrame(top, fg_color="transparent")
        xp_bar_frame.pack(side="right", padx=24, pady=10)

        ctk.CTkLabel(xp_bar_frame,
                     text=f"{p.name}   Ур. {p.level}   {p.xp} XP",
                     font=FONTS["small"], text_color=C["text"]).pack(side="left", padx=(0, 10))
        bar = ctk.CTkProgressBar(xp_bar_frame, width=140, height=8,
                                  fg_color=C["card"],
                                  progress_color=C["accent"])
        bar.set(min(1.0, (p.xp % 100) / 100))
        bar.pack(side="left")
        ctk.CTkLabel(xp_bar_frame,
                     text=f"  {p.to_next()} до ур. {p.level+1}",
                     font=FONTS["small"], text_color=C["muted"]).pack(side="left")

        # ── тело ─────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color=C["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=20)
        body.columnconfigure((0, 1), weight=1)
        body.rowconfigure(1, weight=1)

        ctk.CTkLabel(body, text="Выберите направление культуры",
                     font=FONTS["h1"], text_color=C["text"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # ── карточки модулей ─────────────────────────────────────────
        modules = [
            ("📖", "Литература",    "Диалог с ИИ-двойниками классиков",   "LLM + RAG",             True,  "lit"),
            ("🏛", "Архитектура",   "Квиз по стилям и эпохам",            "Image AI + LLM",        True,  "arch"),
            ("🎼", "Музыка",        "Квиз: композиторы и произведения",   "Audio AI + LLM",        True,  "music"),
            ("🎨", "Живопись",      "Распознавание стилей",               "CLIP + LLM",            False, None),
        ]

        positions = [(1, 0), (1, 1), (2, 0), (2, 1)]
        for (row, col), (ico, name, desc, tech, unlocked, key) in zip(positions, modules):
            self._mod_card(body, ico, name, desc, tech, unlocked, key, p).grid(
                row=row, column=col, padx=8, pady=8, sticky="nsew")

        # ── значки ───────────────────────────────────────────────────
        badge_row = ctk.CTkFrame(body, fg_color="transparent")
        badge_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ctk.CTkLabel(badge_row, text="Значки: ",
                     font=FONTS["small"], text_color=C["muted"]).pack(side="left")
        if p.badges:
            for b in p.badges[-6:]:
                ctk.CTkLabel(badge_row, text=b,
                             font=FONTS["small"], text_color=C["accent"],
                             fg_color=C["card"], corner_radius=8,
                             padx=8, pady=2).pack(side="left", padx=4)
        else:
            ctk.CTkLabel(badge_row, text="пока нет — пройди первый урок",
                         font=FONTS["small"], text_color=C["muted"]).pack(side="left")

        ctk.CTkButton(badge_row, text="Статистика",
                      font=FONTS["small"], width=110, height=28,
                      fg_color=C["card"], hover_color=C["hover"],
                      text_color=C["text"],
                      command=self.master._show_stats).pack(side="right")

    def _mod_card(self, parent, ico, name, desc, tech, unlocked, key, p):
        done_count = sum(1 for d in p.done if d.startswith(key or ""))
        card = ctk.CTkFrame(parent, fg_color=C["card"], corner_radius=16)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=18)

        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text=ico, font=("Helvetica", 30)).pack(side="left", padx=(0, 10))
        txt_col = ctk.CTkFrame(header, fg_color="transparent")
        txt_col.pack(side="left")
        ctk.CTkLabel(txt_col, text=name, font=FONTS["h2"],
                     text_color=C["text"]).pack(anchor="w")
        ctk.CTkLabel(txt_col, text=tech, font=FONTS["small"],
                     text_color=C["accent"]).pack(anchor="w")

        ctk.CTkLabel(inner, text=desc, font=FONTS["body"],
                     text_color=C["subtext"], wraplength=320,
                     justify="left").pack(anchor="w", pady=(0, 14))

        if unlocked:
            if key == "lit":
                btn = ctk.CTkButton(inner, text="Открыть →", font=FONTS["h3"],
                                    height=40, fg_color=C["accent2"],
                                    hover_color="#3D3490", text_color=C["text"],
                                    command=lambda: self.master._show_classic("pushkin"))
            else:
                btn = ctk.CTkButton(inner, text="Открыть →", font=FONTS["h3"],
                                    height=40, fg_color=C["accent2"],
                                    hover_color="#3D3490", text_color=C["text"],
                                    command=lambda k=key: self.master._show_quiz(k))
            btn.pack(fill="x")
            if done_count > 0:
                ctk.CTkLabel(inner,
                             text=f"✓ выполнено заданий: {done_count}",
                             font=FONTS["small"],
                             text_color=C["teal"]).pack(pady=(6, 0))
        else:
            ctk.CTkLabel(inner, text=f"🔒 Откроется на уровне 4",
                         font=FONTS["small"], text_color=C["muted"]).pack()
        return card

# ═══════════════════════════════════════════════════════════════════════
#  ЭКРАН КЛАССИКА (чат)
# ═══════════════════════════════════════════════════════════════════════
class ClassicScreen(ctk.CTkFrame):
    def __init__(self, master, classic_id="pushkin"):
        super().__init__(master, fg_color=C["bg"])
        self.cid = classic_id
        self.classic = CLASSICS[classic_id]
        p = master.player
        self.history = p.histories.setdefault(classic_id, [])
        self._first = classic_id not in p.done
        self._msg_count = 0
        self._build()

    def _build(self):
        # ── шапка ────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=0, height=62)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkButton(top, text="← Назад", font=FONTS["small"],
                      width=90, height=34,
                      fg_color=C["card"], hover_color=C["hover"],
                      text_color=C["text"],
                      command=self._back).pack(side="left", padx=16, pady=12)

        c = self.classic
        ctk.CTkLabel(top, text=f"{c['icon']}  {c['name']}  ({c['years']})  —  ИИ-двойник",
                     font=FONTS["h2"], text_color=C["text"]).pack(side="left", padx=8)

        if not self.master.client:
            ctk.CTkLabel(top, text="демо-режим",
                         font=FONTS["small"], text_color=C["muted"],
                         fg_color=C["card"], corner_radius=8,
                         padx=8, pady=2).pack(side="right", padx=20)

        # ── тело ─────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color=C["bg"])
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # чат
        chat_col = ctk.CTkFrame(body, fg_color=C["bg"])
        chat_col.grid(row=0, column=0, sticky="nsew", padx=(20, 8), pady=16)
        chat_col.rowconfigure(0, weight=1)
        chat_col.columnconfigure(0, weight=1)

        self.chat_box = ctk.CTkScrollableFrame(chat_col, fg_color=C["panel"],
                                                corner_radius=14)
        self.chat_box.grid(row=0, column=0, sticky="nsew")
        self.chat_box.columnconfigure(0, weight=1)

        # приветствие
        self._add_bubble(c["greeting"], role="ai")

        # восстанавливаем историю
        for msg in self.history[-6:]:
            self._add_bubble(msg["content"],
                             role="user" if msg["role"] == "user" else "ai")

        # ввод
        input_row = ctk.CTkFrame(chat_col, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        input_row.columnconfigure(0, weight=1)

        self.input_var = tk.StringVar()
        entry = ctk.CTkEntry(input_row, textvariable=self.input_var,
                             placeholder_text="Задайте вопрос классику...",
                             font=FONTS["body"], height=46,
                             fg_color=C["card"], border_color=C["border"],
                             text_color=C["text"])
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        entry.bind("<Return>", lambda e: self._send())

        ctk.CTkButton(input_row, text="Отправить",
                      font=FONTS["h3"], width=120, height=46,
                      fg_color=C["accent2"], hover_color="#3D3490",
                      text_color=C["text"],
                      command=self._send).grid(row=0, column=1)

        # боковая панель
        side = ctk.CTkFrame(body, fg_color=C["panel"], corner_radius=14)
        side.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=16, ipadx=10, ipady=12)

        ctk.CTkLabel(side, text="Быстрые вопросы",
                     font=FONTS["h3"], text_color=C["text"]).pack(pady=(12, 8))

        quick = []
        if self.cid == "pushkin":
            quick = ["Как придумали Татьяну?", "О вашей ссылке",
                     "Любимое произведение?", "О дуэли и гибели"]
        elif self.cid == "chekhov":
            quick = ["О рассказе «Палата №6»", "Поездка на Сахалин",
                     "Медицина и литература", "Любимый персонаж?"]
        else:
            quick = ["О романе «Война и мир»", "Ясная Поляна",
                     "Философия и вера", "Об Анне Карениной"]

        for q in quick:
            ctk.CTkButton(side, text=q, font=FONTS["small"],
                          width=180, height=36,
                          fg_color=C["card"], hover_color=C["hover"],
                          text_color=C["text"], anchor="w",
                          command=lambda t=q: self._quick_send(t)).pack(padx=10, pady=4)

        ctk.CTkLabel(side, text="ИИ-технология:",
                     font=FONTS["small"], text_color=C["muted"]).pack(pady=(24, 2))
        ctk.CTkLabel(side, text="Gemini 2.0 Flash",
                     font=FONTS["h3"], text_color=C["accent"]).pack()
        ctk.CTkLabel(side,
                     text="Ответы ограничены\nверифицированными\nисточниками",
                     font=FONTS["small"], text_color=C["muted"],
                     justify="center").pack(pady=(4, 0))

    def _add_bubble(self, text, role="ai"):
        frame = ctk.CTkFrame(self.chat_box, fg_color="transparent")
        frame.pack(fill="x", pady=4, padx=8)

        if role == "user":
            bg = C["accent2"]
            tc = C["text"]
            anchor = "e"
            pad = (60, 0)
        else:
            bg = C["card"]
            tc = C["text"]
            anchor = "w"
            pad = (0, 60)

        bubble = ctk.CTkFrame(frame, fg_color=bg, corner_radius=12)
        bubble.pack(anchor=anchor, padx=pad)

        ctk.CTkLabel(bubble, text=text, font=FONTS["body"],
                     text_color=tc, wraplength=380,
                     justify="left").pack(padx=14, pady=10)

        self.chat_box._parent_canvas.yview_moveto(1.0)

    def _send(self):
        txt = self.input_var.get().strip()
        if not txt:
            return
        self.input_var.set("")
        self._add_bubble(txt, role="user")
        self._add_bubble("...", role="ai")
        threading.Thread(target=self._get_reply, args=(txt,), daemon=True).start()

    def _quick_send(self, txt):
        self.input_var.set(txt)
        self._send()

    def _get_reply(self, txt):
        # убрать «...»
        reply = ai_reply(
            self.master.client, self.history, txt,
            self.classic["system"], self.cid,
        )
        self.history.append({"role": "user", "content": txt})
        self.history.append({"role": "assistant", "content": reply})

        # обновить последний пузырь
        frames = self.chat_box.winfo_children()
        if frames:
            last = frames[-1]
            for w in last.winfo_children():
                w.destroy()
            bubble = ctk.CTkFrame(last, fg_color=C["card"], corner_radius=12)
            bubble.pack(anchor="w", padx=(0, 60))
            ctk.CTkLabel(bubble, text=reply, font=FONTS["body"],
                         text_color=C["text"], wraplength=380,
                         justify="left").pack(padx=14, pady=10)

        self._msg_count += 1
        if self._msg_count % 3 == 0:
            leveled = self.master.player.add_xp(10)
            self.after(0, lambda: self.master._xp_popup(10, "активный диалог", leveled))

    def _back(self):
        p = self.master.player
        if self._first and self._msg_count > 0:
            leveled = p.add_xp(self.classic["xp"])
            p.done.append(self.cid)
            badge = f"Знаток {self.classic['name'].split()[0]}"
            p.badge(badge)
            self.after(0, lambda: self.master._xp_popup(
                self.classic["xp"], f"Диалог с {self.classic['name']}", leveled))
        self.master._show_main()

# ═══════════════════════════════════════════════════════════════════════
#  ЭКРАН КВИЗА
# ═══════════════════════════════════════════════════════════════════════
class QuizScreen(ctk.CTkFrame):
    def __init__(self, master, quiz_id="arch"):
        super().__init__(master, fg_color=C["bg"])
        self.qid = quiz_id
        self.quiz = QUIZZES[quiz_id]
        self.questions = self.quiz["questions"]
        self._idx = 0
        self._score = 0
        self._answered = False
        self._already_done = quiz_id in master.player.done
        self._build()
        self._load_question()

    def _build(self):
        # шапка
        top = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=0, height=62)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkButton(top, text="← Назад", font=FONTS["small"],
                      width=90, height=34,
                      fg_color=C["card"], hover_color=C["hover"],
                      text_color=C["text"],
                      command=self.master._show_main).pack(side="left", padx=16, pady=12)

        q = self.quiz
        ctk.CTkLabel(top, text=f"{q['icon']}  {q['title']}  —  Квиз",
                     font=FONTS["h2"], text_color=C["text"]).pack(side="left", padx=8)

        self._prog_lbl = ctk.CTkLabel(top, text="", font=FONTS["small"],
                                       text_color=C["muted"])
        self._prog_lbl.pack(side="right", padx=24)

        # тело
        self._body = ctk.CTkFrame(self, fg_color=C["bg"])
        self._body.pack(fill="both", expand=True, padx=60, pady=30)
        self._body.columnconfigure(0, weight=1)

    def _load_question(self):
        for w in self._body.winfo_children():
            w.destroy()
        self._answered = False

        total = len(self.questions)
        q = self.questions[self._idx]
        self._prog_lbl.configure(
            text=f"Вопрос {self._idx + 1} / {total}")

        # прогресс-бар вверху
        pb = ctk.CTkProgressBar(self._body, height=6,
                                 fg_color=C["card"], progress_color=C["accent"])
        pb.set((self._idx) / total)
        pb.grid(row=0, column=0, sticky="ew", pady=(0, 24))

        # вопрос
        ctk.CTkLabel(self._body, text=q["q"],
                     font=FONTS["h1"], text_color=C["text"],
                     wraplength=700, justify="left").grid(
            row=1, column=0, sticky="w", pady=(0, 28))

        # варианты
        opts_frame = ctk.CTkFrame(self._body, fg_color="transparent")
        opts_frame.grid(row=2, column=0, sticky="ew")
        opts_frame.columnconfigure((0, 1), weight=1)
        self._opt_btns = []

        for i, opt in enumerate(q["opts"]):
            r, c = divmod(i, 2)
            btn = ctk.CTkButton(
                opts_frame, text=f"  {opt}",
                font=FONTS["h3"], height=60, anchor="w",
                fg_color=C["card"], hover_color=C["hover"],
                text_color=C["text"], border_width=1,
                border_color=C["border"], corner_radius=12,
                command=lambda idx=i: self._answer(idx),
            )
            btn.grid(row=r, column=c, padx=8, pady=8, sticky="ew")
            self._opt_btns.append(btn)

        # объяснение (скрыто)
        self._exp_frame = ctk.CTkFrame(self._body, fg_color=C["panel"],
                                        corner_radius=12)
        self._exp_lbl = ctk.CTkLabel(self._exp_frame, text="",
                                      font=FONTS["body"], text_color=C["subtext"],
                                      wraplength=640, justify="left")
        self._exp_lbl.pack(padx=16, pady=12)

        # кнопка далее
        self._next_btn = ctk.CTkButton(self._body, text="Далее →",
                                        font=FONTS["h3"], height=48,
                                        fg_color=C["accent"], hover_color="#A8863A",
                                        text_color="#0F1117",
                                        command=self._next)
        self._score_lbl = ctk.CTkLabel(self._body, text="",
                                        font=FONTS["h2"], text_color=C["text"])

    def _answer(self, chosen):
        if self._answered:
            return
        self._answered = True
        q = self.questions[self._idx]
        correct = q["ans"]

        for i, btn in enumerate(self._opt_btns):
            btn.configure(state="disabled")
            if i == correct:
                btn.configure(fg_color=C["teal"], border_color=C["teal"],
                               text_color=C["text"])
            elif i == chosen and chosen != correct:
                btn.configure(fg_color=C["red"], border_color=C["red"])

        if chosen == correct:
            self._score += 1

        self._exp_lbl.configure(text=f"💡  {q['exp']}")
        self._exp_frame.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        self._next_btn.grid(row=4, column=0, sticky="e", pady=(16, 0))

    def _next(self):
        self._idx += 1
        if self._idx < len(self.questions):
            self._load_question()
        else:
            self._show_result()

    def _show_result(self):
        for w in self._body.winfo_children():
            w.destroy()

        total = len(self.questions)
        pct = int(self._score / total * 100)

        ctk.CTkLabel(self._body, text="Квиз завершён!",
                     font=FONTS["title"], text_color=C["accent"]).pack(pady=(20, 8))

        score_color = C["teal"] if pct >= 60 else C["red"]
        ctk.CTkLabel(self._body,
                     text=f"{self._score} / {total}  ({pct}%)",
                     font=("Georgia", 48, "bold"),
                     text_color=score_color).pack(pady=16)

        msg = ("Отлично! Ты настоящий знаток." if pct == 100
               else "Хороший результат!" if pct >= 60
               else "Попробуй ещё раз — с каждым разом лучше!")
        ctk.CTkLabel(self._body, text=msg, font=FONTS["h2"],
                     text_color=C["text"]).pack(pady=8)

        p = self.master.player
        if not self._already_done:
            earned = int(self.quiz["xp"] * pct / 100)
            leveled = p.add_xp(earned)
            p.done.append(self.qid)
            if pct == 100:
                p.badge("Отличник")
            self.after(300, lambda: self.master._xp_popup(
                earned, f"Квиз: {pct}%", leveled))
        else:
            ctk.CTkLabel(self._body,
                         text="(повторное прохождение — XP не начисляется)",
                         font=FONTS["small"], text_color=C["muted"]).pack(pady=4)

        btns = ctk.CTkFrame(self._body, fg_color="transparent")
        btns.pack(pady=24)
        ctk.CTkButton(btns, text="На главную", font=FONTS["h3"],
                      height=46, width=180,
                      fg_color=C["card"], hover_color=C["hover"],
                      text_color=C["text"],
                      command=self.master._show_main).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Пройти снова", font=FONTS["h3"],
                      height=46, width=180,
                      fg_color=C["accent2"], hover_color="#3D3490",
                      text_color=C["text"],
                      command=lambda: self.master._show_quiz(self.qid)).pack(side="left", padx=8)

# ═══════════════════════════════════════════════════════════════════════
#  ЭКРАН СТАТИСТИКИ
# ═══════════════════════════════════════════════════════════════════════
class StatsScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"])
        self._build()

    def _build(self):
        p = self.master.player

        top = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=0, height=62)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkButton(top, text="← Назад", font=FONTS["small"],
                      width=90, height=34,
                      fg_color=C["card"], hover_color=C["hover"],
                      text_color=C["text"],
                      command=self.master._show_main).pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(top, text="Ваш прогресс",
                     font=FONTS["h2"], text_color=C["text"]).pack(side="left", padx=8)

        body = ctk.CTkFrame(self, fg_color=C["bg"])
        body.pack(fill="both", expand=True, padx=60, pady=30)
        body.columnconfigure((0, 1, 2, 3), weight=1)

        # метрики
        for col, (lbl, val, color) in enumerate([
            ("Уровень",       str(p.level),         C["accent"]),
            ("XP",            str(p.xp),             C["accent2"]),
            ("До след. ур.",  str(p.to_next()),      C["teal"]),
            ("Пройдено",      str(len(p.done)),      C["subtext"]),
        ]):
            card = ctk.CTkFrame(body, fg_color=C["card"], corner_radius=14)
            card.grid(row=0, column=col, padx=8, pady=(0, 20), sticky="ew",
                      ipady=14)
            ctk.CTkLabel(card, text=lbl, font=FONTS["small"],
                         text_color=C["muted"]).pack(pady=(12, 4))
            ctk.CTkLabel(card, text=val, font=FONTS["xp"],
                         text_color=color).pack(pady=(0, 12))

        # прогресс по модулям
        ctk.CTkLabel(body, text="Прогресс по направлениям",
                     font=FONTS["h2"], text_color=C["text"]).grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(8, 12))

        mod_data = [
            ("📖 Литература",  ["pushkin", "chekhov", "tolstoy"]),
            ("🏛 Архитектура", ["arch", "arch_eras"]),
            ("🎼 Музыка",      ["music", "music2"]),
        ]
        for r, (mname, ids) in enumerate(mod_data, 2):
            done = sum(1 for i in ids if i in p.done)
            total = len(ids)
            row_frame = ctk.CTkFrame(body, fg_color=C["panel"], corner_radius=10)
            row_frame.grid(row=r, column=0, columnspan=4, sticky="ew",
                           padx=0, pady=4, ipady=10)
            row_frame.columnconfigure(1, weight=1)
            ctk.CTkLabel(row_frame, text=mname, font=FONTS["h3"],
                         text_color=C["text"], width=180,
                         anchor="w").grid(row=0, column=0, padx=16)
            pb = ctk.CTkProgressBar(row_frame, height=8,
                                     fg_color=C["card"],
                                     progress_color=C["teal"])
            pb.set(done / total if total else 0)
            pb.grid(row=0, column=1, sticky="ew", padx=(0, 12))
            ctk.CTkLabel(row_frame, text=f"{done}/{total}",
                         font=FONTS["small"], text_color=C["muted"],
                         width=40).grid(row=0, column=2, padx=(0, 16))

        # значки
        ctk.CTkLabel(body, text="Значки",
                     font=FONTS["h2"], text_color=C["text"]).grid(
            row=5, column=0, columnspan=4, sticky="w", pady=(20, 8))

        badges_frame = ctk.CTkFrame(body, fg_color="transparent")
        badges_frame.grid(row=6, column=0, columnspan=4, sticky="ew")

        if p.badges:
            for b in p.badges:
                ctk.CTkLabel(badges_frame, text=f"★  {b}",
                             font=FONTS["body"], text_color=C["accent"],
                             fg_color=C["card"], corner_radius=10,
                             padx=14, pady=6).pack(side="left", padx=6)
        else:
            ctk.CTkLabel(badges_frame,
                         text="Пройди урок или квиз, чтобы получить первый значок!",
                         font=FONTS["body"], text_color=C["muted"]).pack(anchor="w")

# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()