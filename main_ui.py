import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from tkinter import messagebox
import pygame
from casino.games import coin_flip, HEADS, TAILS
from casino.simulation import play_coinflip_round, play_flat_bet, play_martingale
from casino.player import Player
from tkinter import simpledialog

ASSETS = Path(__file__).parent / "assets"
W, H = 960, 540


def load_png(name: str) -> ImageTk.PhotoImage:
    path = ASSETS / name
    img = Image.open(path).convert("RGBA")
    return ImageTk.PhotoImage(img)


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Casino Simulator")
        root.resizable(False, False)
        root.geometry(f"{W}x{H}")

        self.icon = load_png("logo.png")
        root.iconphoto(False, self.icon)



        self.canvas = tk.Canvas(root, width=W, height=H, highlightthickness=0)
        self.canvas.pack()

        # --- Load images (keep references on self!)
        self.bg = load_png("background.png")
        self.dealer = load_png("dealer_idle.png")

        self.player = Player(name="Max", balance=100)



        self.btn_manual = load_png("button_manual.png")
        self.btn_flat = load_png("button_flat_bet.png")
        self.btn_marti = load_png("button_martingale.png")
        self.btn_settings = load_png("button_settings.png")
        self.btn_close = load_png("button_close.png")
        self.btn_close_mini = load_png("button_close_mini.png")
        self.btn_send_logs = load_png("button_logs.png")
        self.settings_panel = load_png("settings_background.png")
        self.coin_heads = load_png("coin_heads.png")
        self.coin_tails = load_png("coin_tails.png")
        self.choice_tails = load_png("button_t_choice.png")
        self.choice_heads = load_png("button_h_choice.png")
        self.coin_choice = load_png("coin_choice.png")


        profile = self.profile_dialog()
        if profile is None:
            self.root.destroy()
            return

        name, balance = profile
        self.player = Player(name=name, balance=balance)
        self.player_name = name
        self.player_balance = balance




        # Optional panel (if you have it)
        self.log_panel = None
        self.console_panel = load_png("controls_panel.png")
        self.sign = load_png("banner.png")
        panel_path = ASSETS / "log_panel.png"
        if panel_path.exists():
            self.log_panel = load_png("log_panel.png")

        # --- Draw background
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg)

        # --- Place banner
        self.canvas.create_image(W // 2, 90, image=self.sign)  # y подстрой


        # --- Place dealer (center-ish)
        self.canvas.create_image(W // 2, H // 2 - 5, image=self.dealer)

        # --- Coin image (center, tweak coords)
        self.coin_id = None 


        self.side_win = None
        self._side_choice = None


        # --- Place control panel (LEFT SIDE)
        CONTROL_X, CONTROL_Y = 40, 130
        self.canvas.create_image(CONTROL_X, CONTROL_Y, anchor="nw", image=self.console_panel)

        # --- Place buttons INSIDE control panel
        btn_x = CONTROL_X + 95
        btn_y = CONTROL_Y + 130
        gap = 10
        btn_h = 48  # если кнопки ~48px высотой

        # --- Place buttons as image-buttons
        self._place_button(self.btn_manual,   btn_x, btn_y + 0*(btn_h + gap), self.on_manual)
        self._place_button(self.btn_flat,     btn_x, btn_y + 1*(btn_h + gap), self.on_flat)
        self._place_button(self.btn_marti,    btn_x, btn_y + 2*(btn_h + gap), self.on_martingale)

        # Settings ниже с небольшим дополнительным отступом
        self._place_button(self.btn_settings, btn_x, btn_y + 3*(btn_h + gap) + 0, self.on_settings)






        # --- Log area
        LOG_PANEL_X, LOG_PANEL_Y = 730, 130
        if self.log_panel:
            self.canvas.create_image(LOG_PANEL_X, LOG_PANEL_Y, anchor="nw", image=self.log_panel)


        self.log_lines: list[str] = []
        self._log("UI loaded. (Static preview)")

        self._draw_console_info()

        # --- Settings window state
        self.settings_win = None
        self.volume_value = tk.IntVar(value=60)  # 0..100

        # --- Start music automatically
        self._init_audio()



    def _place_button(self, img: ImageTk.PhotoImage, x: int, y: int, cmd):
        btn = tk.Button(
            self.root,
            image=img,
            command=cmd,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            activebackground="#000000",  # won't matter much with image
        )
        self.canvas.create_window(x, y, anchor="center", window=btn)


    def _fit_log_line(self, s: str, max_chars: int = 26) -> str:
        s = str(s)
        if len(s) <= max_chars:
            return s
        return s[:max_chars - 1] + "…"





    def _log(self, text: str):
        self.log_lines.append(text)
        self.log_lines = self.log_lines[-11:]
        

        self.canvas.delete("log_text")

        LOG_TEXT_X = 740
        LOG_TEXT_Y = 170
        line_h = 25

        for i, line in enumerate(self.log_lines):
            self.canvas.create_text(
                LOG_TEXT_X,
                LOG_TEXT_Y + i * line_h,
                text=self._fit_log_line(line),
                fill="#f8f8f8",
                anchor="nw",
                font=("Pixelify Sans", 8),
                tags="log_text",
            )



    def show_coin(self, side: str | None = None):
        """Показывает монету на экране. side можно не передавать."""
        if self.coin_id is None:
            img = self.coin_heads if (side is None or side == HEADS) else self.coin_tails
            self.coin_id = self.canvas.create_image(W // 2, 360, image=img)
        else:
            # если уже есть — просто обновим картинку
            if side is not None:
                self._set_coin_image(side)

    def hide_coin(self):
        """Убирает монету с экрана."""
        if self.coin_id is not None:
            self.canvas.delete(self.coin_id)
            self.coin_id = None



    def _set_coin_image(self, side: str):
        if self.coin_id is None:
            return
        img = self.coin_heads if side == HEADS else self.coin_tails
        self.canvas.itemconfig(self.coin_id, image=img)


    def _animate_flip(self, final_side: str):
        # простая анимация: быстро мигаем heads/tails 6 раз, потом итог
        seq = [self.coin_heads, self.coin_tails] * 3

        def step(i=0):
            if i < len(seq):
                self.canvas.itemconfig(self.coin_id, image=seq[i])
                self.root.after(80, lambda: step(i + 1))
            else:
                self._set_coin_image(final_side)

        step()








    def ask_bet_and_rounds(self) -> tuple[int, int] | None:
        win = tk.Toplevel(self.root)
        win.title("Simulation")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        w, h = 260, 160
        x = self.root.winfo_x() + (W - w) // 2
        y = self.root.winfo_y() + (H - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.configure(bg="#0C1028")

        c = tk.Canvas(win, width=w, height=h, highlightthickness=0, bg="#0C1028")
        c.pack()

        c.create_text(w//2, 20, text="Enter settings", fill="#f8f8f8",
                    font=("Pixelify Sans", 14), anchor="center")

        c.create_text(20, 55, text="Bet:", fill="#f8f8f8", font=("Pixelify Sans", 12), anchor="nw")
        c.create_text(20, 90, text="Rounds:", fill="#f8f8f8", font=("Pixelify Sans", 12), anchor="nw")

        bet_var = tk.StringVar(value="10")
        rounds_var = tk.StringVar(value="20")

        bet_entry = tk.Entry(win, textvariable=bet_var, bg="#141A3A", fg="#f8f8f8",
                            insertbackground="#f8f8f8", relief="flat")
        rounds_entry = tk.Entry(win, textvariable=rounds_var, bg="#141A3A", fg="#f8f8f8",
                                insertbackground="#f8f8f8", relief="flat")

        c.create_window(90, 52, anchor="nw", window=bet_entry, width=140, height=24)
        c.create_window(90, 87, anchor="nw", window=rounds_entry, width=140, height=24)

        error_id = c.create_text(w//2, 120, text="", fill="#ff6b6b",
                                font=("Pixelify Sans", 10), anchor="center")

        result = {"val": None}

        def submit():
            try:
                bet = int(bet_var.get().strip())
                rounds = int(rounds_var.get().strip())
                if bet <= 0 or rounds <= 0:
                    raise ValueError
            except ValueError:
                c.itemconfig(error_id, text="Use positive integers.")
                return

            result["val"] = (bet, rounds)
            close()

        def close():
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        btn_ok = tk.Button(win, text="OK", command=submit, bg="#141A3A", fg="#f8f8f8", relief="flat")
        btn_cancel = tk.Button(win, text="CANCEL", command=close, bg="#141A3A", fg="#f8f8f8", relief="flat")

        c.create_window(w//2 - 50, 140, anchor="center", window=btn_ok, width=70, height=22)
        c.create_window(w//2 + 50, 140, anchor="center", window=btn_cancel, width=70, height=22)

        bet_entry.focus_set()
        self.root.wait_window(win)
        return result["val"]














    def choose_side_ui(self) -> str | None:
        if self.side_win is not None and self.side_win.winfo_exists():
            self.side_win.lift()
            self.root.wait_window(self.side_win)
            return self._side_choice

        self._side_choice = None

        win = tk.Toplevel(self.root)
        self.side_win = win
        win.title("Choose Side")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        # --- fixed size + center
        w, h = 250, 130
        x = self.root.winfo_x() + (W - w) // 2
        y = self.root.winfo_y() + (H - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.configure(bg="#0C1028")

        # --- canvas for layout
        c = tk.Canvas(win, width=w, height=h, highlightthickness=0, bg="#0C1028")
        c.pack(fill="both", expand=True)

        # --- title text (top center)
        c.create_text(
            w // 2, 10,
            text="Choose side:",
            fill="#f8f8f8",
            font=("Pixelify Sans", 14),
            anchor="center",
            tags="side_text"
        )

        # --- close button (top-right)
        close_btn = tk.Button(
            win,
            image=self.btn_close_mini,   # твоя PNG кнопка закрытия
            command=lambda: pick(None),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            bg="#0C1028",
            activebackground="#0C1028",
        )
        # чуть отступаем от края
        c.create_window(w - 4, 4, anchor="ne", window=close_btn)

        # --- coin preview (center)
        # ставим чуть ниже заголовка
        c.create_image(w // 2, 67, image=self.coin_choice, anchor="center")

        # --- heads/tails buttons (bottom row)
        heads_btn = tk.Button(
            win,
            image=self.choice_heads,
            command=lambda: pick(HEADS),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            bg="#0C1028",
            activebackground="#0C1028",
        )
        tails_btn = tk.Button(
            win,
            image=self.choice_tails,
            command=lambda: pick(TAILS),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            bg="#0C1028",
            activebackground="#0C1028",
        )

        # размещение снизу: левее/правее центра
        c.create_window(w // 2 - 55, 107, anchor="center", window=heads_btn)
        c.create_window(w // 2 + 55, 107, anchor="center", window=tails_btn)

        def pick(side):
            self._side_choice = side
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()
            self.side_win = None

        win.protocol("WM_DELETE_WINDOW", lambda: pick(None))

        self.root.wait_window(win)
        return self._side_choice







    def profile_dialog(self) -> tuple[str, int] | None:
        """Окно ввода профиля. Возвращает (name, balance) или None если Cancel/закрыли."""
        win = tk.Toplevel(self.root)
        win.title("Create Profile")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        w, h = 420, 260
        x = self.root.winfo_x() + (W - w) // 2
        y = self.root.winfo_y() + (H - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.configure(bg="#0C1028")

        # состояние результата
        result = {"value": None}

        # canvas (чтобы красиво позиционировать)
        c = tk.Canvas(win, width=w, height=h, highlightthickness=0, bg="#0C1028")
        c.pack(fill="both", expand=True)

        # заголовок
        c.create_text(
            w // 2, 35,
            text="CREATE PROFILE",
            fill="#f8f8f8",
            font=("Pixelify Sans", 18),
            anchor="center"
        )

        # лейблы
        c.create_text(70, 95, text="Name:", fill="#f8f8f8", font=("Pixelify Sans", 12), anchor="nw")
        c.create_text(70, 145, text="Balance:", fill="#f8f8f8", font=("Pixelify Sans", 12), anchor="nw")

        name_var = tk.StringVar(value="")
        bal_var = tk.StringVar(value="100")

        name_entry = tk.Entry(
            win, textvariable=name_var,
            bg="#141A3A", fg="#f8f8f8",
            insertbackground="#f8f8f8",
            relief="flat",
            highlightthickness=1, highlightbackground="#2b2f55", highlightcolor="#2b2f55",
            font=("Pixelify Sans", 12)
        )
        bal_entry = tk.Entry(
            win, textvariable=bal_var,
            bg="#141A3A", fg="#f8f8f8",
            insertbackground="#f8f8f8",
            relief="flat",
            highlightthickness=1, highlightbackground="#2b2f55", highlightcolor="#2b2f55",
            font=("Pixelify Sans", 12)
        )

        c.create_window(170, 92, anchor="nw", window=name_entry, width=200, height=28)
        c.create_window(170, 142, anchor="nw", window=bal_entry, width=200, height=28)

        error_id = c.create_text(
            w // 2, 185,
            text="",
            fill="#ff6b6b",
            font=("Pixelify Sans", 10),
            anchor="center"
        )

        def validate_and_submit():
            name = name_var.get().strip()
            if not name:
                c.itemconfig(error_id, text="Name cannot be empty.")
                return

            raw_bal = bal_var.get().strip()
            try:
                balance = int(raw_bal)
            except ValueError:
                c.itemconfig(error_id, text="Balance must be an integer.")
                return

            if balance <= 0:
                c.itemconfig(error_id, text="Balance must be > 0.")
                return

            result["value"] = (name, balance)
            close()

        def close():
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        # кнопки (пока обычные, потом заменим PNG)
        start_btn = tk.Button(
            win, text="START",
            command=validate_and_submit,
            bg="#141A3A", fg="#f8f8f8",
            relief="flat",
            activebackground="#1a214a",
            font=("Pixelify Sans", 12)
        )
        cancel_btn = tk.Button(
            win, text="CANCEL",
            command=lambda: close(),
            bg="#141A3A", fg="#f8f8f8",
            relief="flat",
            activebackground="#1a214a",
            font=("Pixelify Sans", 12)
        )

        c.create_window(w // 2 - 80, 215, anchor="center", window=start_btn, width=120, height=28)
        c.create_window(w // 2 + 80, 215, anchor="center", window=cancel_btn, width=120, height=28)

        # enter = start
        win.bind("<Return>", lambda e: validate_and_submit())
        win.protocol("WM_DELETE_WINDOW", close)

        name_entry.focus_set()
        self.root.wait_window(win)
        return result["value"]













    def open_settings(self):
        if self.settings_win is not None and self.settings_win.winfo_exists():
            self.settings_win.lift()
            return

        win = tk.Toplevel(self.root)
        self.settings_win = win

        win.title("Settings")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        # размеры берем из картинки settings_panel (надежнее)
        w = self.settings_panel.width()
        h = self.settings_panel.height()

        x = self.root.winfo_x() + (W - w) // 2
        y = self.root.winfo_y() + (H - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        canvas = tk.Canvas(win, width=w, height=h, highlightthickness=0)
        canvas.pack()

        # фон-панель
        canvas.create_image(0, 0, anchor="nw", image=self.settings_panel)

        # заголовок (внутри панели)
        canvas.create_text(
            30, 22,
            text="SETTINGS",
            anchor="nw",
            fill="#f8f8f8",
            font=("Pixelify Sans", 18),
            tags="settings_text"
        )

        # подпись громкости
        canvas.create_text(
            30, 72,
            text="MUSIC VOLUME",
            anchor="nw",
            fill="#f8f8f8",
            font=("Pixelify Sans", 12),
            tags="settings_text"
        )

        # slider громкости (пока стандартный, но вписан в окно)
        vol = tk.Scale(
            win,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volume_value,
            command=self._set_volume,
            length=260,
            showvalue=False,
            troughcolor="#2b2b2b",
            bd=0,
            highlightthickness=0
        )
        canvas.create_window(30, 98, anchor="nw", window=vol)

        # цифра громкости справа (пиксельным текстом)
        self._settings_vol_text_id = canvas.create_text(
            305, 98,
            text=f"{self.volume_value.get()}%",
            anchor="nw",
            fill="#f8f8f8",
            font=("Pixelify Sans", 12),
            tags="settings_text"
        )

        # обновляем проценты при изменении
        def update_vol_label(*_):
            canvas.itemconfig(self._settings_vol_text_id, text=f"{self.volume_value.get()}%")
        self.volume_value.trace_add("write", update_vol_label)


        # --- PNG "buttons" directly on canvas
        send_id = canvas.create_image(30, 150, anchor="nw", image=self.btn_send_logs, tags="send_btn")
        close_id = canvas.create_image(175, 150, anchor="nw", image=self.btn_close, tags="close_btn")

        canvas.tag_bind("send_btn", "<Button-1>", lambda e: self.send_logs())
        canvas.tag_bind("close_btn", "<Button-1>", lambda e: self.close_settings())



        win.protocol("WM_DELETE_WINDOW", self.close_settings)











    def _init_audio(self):
        """Starts background music (autoplay)."""
        try:
            pygame.mixer.init()
            music_path = ASSETS / "soundtrack_2.mp3"  # поменяй имя если другое
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.volume_value.get() / 100)
            pygame.mixer.music.play(-1)  # loop forever
            self._log("Music: ON")
        except Exception as e:
            self._log(f"Music error: {e}")

    def _set_volume(self, value: str):
        """Called by slider, value comes as string."""
        try:
            v = int(float(value))
            pygame.mixer.music.set_volume(v / 100)
        except Exception:
            pass


    def _draw_console_info(self):
        self.canvas.delete("console_text")

        text=f"Name: {self.player.name}"
        text=f"Balance: {self.player.balance}$"

        self.canvas.create_text(
            60, 165,
            text=f"Name: {self.player.name}",
            fill="#f5f5f5",
            anchor="nw",
            font=("Pixelify Sans", 14),
            tags="console_text"
        )

        self.canvas.create_text(
            60, 195,
            text=f"Balance: {self.player.balance}$",
            fill="#f5f5f5",
            anchor="nw",
            font=("Pixelify Sans", 14),
            tags="console_text"
        )





    def close_settings(self):
        if self.settings_win is not None and self.settings_win.winfo_exists():
            try:
                self.settings_win.grab_release()
            except Exception:
                pass
            self.settings_win.destroy()
        self.settings_win = None

    def send_logs(self):
        try:
            out_path = Path(__file__).parent / "casino_logs.txt"
            with open(out_path, "w", encoding="utf-8") as f:
                for line in self.log_lines:
                    f.write(line + "\n")

            messagebox.showinfo("Logs", "Saved to casino_logs.txt")
            self._log("Logs: saved to casino_logs.txt")
        except Exception as e:
            messagebox.showerror("Logs", f"Failed: {e}")
            self._log(f"Logs error: {e}")



    def show_status(self, text: str, ms: int = 900):
        self.canvas.delete("status_text")
        self.canvas.create_text(
            W // 2, 140,   # подгони Y как нравится
            text=text,
            fill="#ffd84d",   # можно менять под стиль
            font=("Pixelify Sans", 36),
            anchor="center",
            tags="status_text",
        )
        self.root.after(ms, lambda: self.canvas.delete("status_text"))






    # --- Animation for flat bet and martingale


    def start_autoplay(self, *, mode: str, bet: int, rounds: int, side: str):
        """
        mode: "flat" | "martingale"
        """
        if getattr(self, "_auto_running", False):
            return  # чтобы не запустить два раза

        self._auto_running = True
        self._auto_mode = mode
        self._auto_side = side
        self._auto_target_rounds = rounds
        self._auto_played = 0

        self._auto_base_bet = bet
        self._auto_current_bet = bet

        self.show_coin()  # монетка появилась
        self._log(f"{mode.upper()} start: side={side}, bet={bet}, rounds={rounds}")
        self._autoplay_step()



    def _autoplay_step(self):
        # закончились раунды
        if self._auto_played >= self._auto_target_rounds:
            self._log(f"{self._auto_mode.upper()} done. Balance={self.player.balance}")
            self._draw_console_info()
            self._auto_finish()
            return

        bet = self._auto_current_bet

        # не хватает денег
        if bet > self.player.balance or bet <= 0:
            self._log(f"Stop: insufficient funds for bet={bet}. Balance={self.player.balance}")
            self._draw_console_info()
            self._auto_finish()
            return
        
        # играем один раунд
        try:
            win, result_side = play_coinflip_round(player=self.player, bet_amount=bet, chosen_side=self._auto_side)
        except ValueError as e:
            self._log(f"Bet error: {e}")
            self._draw_console_info()
            self._auto_finish()
            return

        self._auto_played += 1
        self._draw_console_info()

        # короткий лог (влезет)
        self._log(f"R{self._auto_played}: {'W' if win else 'L'} "
          f"bet={bet} got={result_side} bal={self.player.balance}")


        # статус на экран
        self.show_status("WIN!" if win else "LOSE!", ms=350)

        # логика мартингейла
        if self._auto_mode == "martingale":
            if win:
                self._auto_current_bet = self._auto_base_bet
            else:
                self._auto_current_bet *= 2

        # скорость анимации (подгони)
        self.root.after(500, self._autoplay_step)


    def _auto_finish(self):
        self._auto_running = False
        self.root.after(700, self.hide_coin)






    # --- Button handlers

    def on_manual(self):
        self.show_coin()  # теперь монетка появилась

        chosen_side = self.choose_side_ui()
        if chosen_side is None:
            self.hide_coin()
            return


        bet = 10
        try:
            win, result_side = play_coinflip_round(self.player, bet, chosen_side)
        except ValueError as e:
            self._log(f"Bet failed: {e}")
            self.hide_coin()
            return
        
        self._animate_flip(result_side)
        self.show_status("WIN!" if win else "LOSE!")
        self._log(f"Manual: chose={chosen_side}, result={result_side}, {'WIN' if win else 'LOSE'}")
        self._draw_console_info()

        # если хочешь, чтобы монета исчезала сразу после раунда:
        self.root.after(700, self.hide_coin)




    def on_flat(self):
        chosen_side = self.choose_side_ui()
        if chosen_side is None:
            return

        settings = self.ask_bet_and_rounds()
        if settings is None:
            return

        bet, rounds = settings
        self.start_autoplay(mode="flat", bet=bet, rounds=rounds, side=chosen_side)





    def on_martingale(self):
        chosen_side = self.choose_side_ui()
        if chosen_side is None:
            return

        settings = self.ask_bet_and_rounds()
        if settings is None:
            return

        base_bet, rounds = settings
        self.start_autoplay(mode="martingale", bet=base_bet, rounds=rounds, side=chosen_side)







    def on_settings(self):
        self._log("Clicked: Settings")
        self.open_settings()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
