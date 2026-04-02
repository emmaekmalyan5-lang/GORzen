import sys
import random
import socket
import threading
import json
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QDialog, QLineEdit, QLabel, 
                             QFileDialog, QMessageBox, QStackedWidget, QInputDialog, 
                             QFrame, QGridLayout, QScrollArea, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

# --- КОНСТАНТЫ СЕТИ ---
UDP_PORT = 55555  
TCP_PORT = 55556  
MSG_SEP = "|END|" 

# --- ЛОКАЛИЗАЦИЯ GORZEN ---
LANGUAGES = {
    "RU": {
        "menu_logo": "GOR\nZEN",
        "scan": "🔎 СКАНИРОВАНИЕ ЛОКАЛЬНОЙ СЕТИ GORZEN...",
        "create_srv": "СОЗДАТЬ СЕРВЕР GORZEN",
        "score": "Очки",
        "wait_start": "ОЖИДАНИЕ ЗАПУСКА GORZEN...",
        "next_step": "СЛЕДУЮЩИЙ ШАГ ➡️",
        "start_game": "🚀 НАЧАТЬ СЕССИЮ",
        "admin_label": "АДМИНИСТРАТОР GORZEN",
        "room_pin": "ROOM PIN",
        "arena_name": "Название вашей арены GORZEN:",
        "select_json": "📂 ВЫБРАТЬ СПИСОК ВОПРОСОВ",
        "json_ok": "✅ ФАЙЛ ЗАГРУЖЕН",
        "launch_srv": "ЗАПУСТИТЬ СЕРВЕР",
        "rating_title": "📊 РЕЙТИНГ РАУНДА",
        "correct_ans": "Правильный ответ:",
        "btn_next": "ДАЛЕЕ",
        "players": "👥 ИГРОКИ",
        "answers": "🎯 ОТВЕТЫ",
        "joined": "ПРИСОЕДИНИЛСЯ К GORZEN",
        "draw": "🤝 НИЧЬЯ!",
        "champ": "🏆 ЧЕМПИОН GORZEN",
        "final_score": "🔥 СЧЁТ",
        "back_menu": "🔄 ВЕРНУТЬСЯ В МЕНЮ",
        "nick_error": "Этот никнейм уже занят!",
        "srv_error": "Сервер GORZEN недоступен!",
        "input_nick": "Ваш ник для",
        "enter": "ВХОД",
        "lang_btn": "🌐 ЯЗЫК (RU)"
    },
    "AM": {
        "menu_logo": "GOR\nZEN",
        "scan": "🔎 ՓՆՏՐՈՒՄ Է GORZEN ՑԱՆՑՈՒՄ...",
        "create_srv": "ՍՏԵՂԾԵԼ GORZEN ՍԵՐՎԵՐ",
        "score": "Միավորներ",
        "wait_start": "ՍՊԱՍԵՔ GORZEN ՄԵԿՆԱՐԿԻՆ...",
        "next_step": "ՀԱՋՈՐԴ ՔԱՅԼԸ ➡️",
        "start_game": "🚀 ՍԿՍԵԼ ԽԱՂԸ",
        "admin_label": "ԱԴՄԻՆԻՍՏՐԱՏՈՐ",
        "room_pin": "ՍԵՆՅԱԿԻ PIN",
        "arena_name": "Ձեր GORZEN արենայի անունը:",
        "select_json": "📂 ԸՆՏՐԵԼ ՀԱՐՑԱՇԱՐԸ (JSON)",
        "json_ok": "✅ ՖԱՅԼԸ ԲԵՌՆՎԱԾ Է",
        "launch_srv": "ՄԻԱՑՆԵԼ ՍԵՐՎԵՐԸ",
        "rating_title": "📊 ՌԱՈՒՆԴԻ ԱՐԴՅՈՒՆՔՆԵՐԸ",
        "correct_ans": "Ճիշտ պատասխանը՝",
        "btn_next": "ՀԱՋՈՐԴԸ",
        "players": "👥 ԽԱՂԱՑՈՂՆԵՐ",
        "answers": "🎯 ՊԱՏԱՍԽԱՆՆԵՐ",
        "joined": "ՄԻԱՑԱՎ GORZEN-ԻՆ",
        "draw": "🤝 ՈՉ-ՈՔԻ!",
        "champ": "🏆 GORZEN ՀԱՂԹՈՂ",
        "final_score": "🔥 ՄԻԱՎՈՐ",
        "back_menu": "🔄 ՎԵՐԱԴԱՌՆԱԼ ՄԵՆՅՈՒ",
        "nick_error": "Այս անունն արդեն զբաղված է:",
        "srv_error": "GORZEN սերվերն անհասանելի է:",
        "input_nick": "Մուտքագրեք ձեր անունը",
        "enter": "ՄՈՒՏՔ",
        "lang_btn": "🌐 ԼԵԶՈՒ (AM)"
    },
    "EN": {
        "menu_logo": "GOR\nZEN",
        "scan": "🔎 SCANNING GORZEN NETWORK...",
        "create_srv": "CREATE GORZEN SERVER",
        "score": "Score",
        "wait_start": "WAITING FOR GORZEN START...",
        "next_step": "NEXT STEP ➡️",
        "start_game": "🚀 START SESSION",
        "admin_label": "GORZEN ADMINISTRATOR",
        "room_pin": "ROOM PIN",
        "arena_name": "Your GORZEN Arena Name:",
        "select_json": "📂 SELECT QUESTIONS (JSON)",
        "json_ok": "✅ FILE LOADED",
        "launch_srv": "START SERVER",
        "rating_title": "📊 ROUND RATING",
        "correct_ans": "Correct answer:",
        "btn_next": "NEXT",
        "players": "👥 PLAYERS",
        "answers": "🎯 ANSWERS",
        "joined": "JOINED GORZEN",
        "draw": "🤝 DRAW!",
        "champ": "🏆 GORZEN CHAMPION",
        "final_score": "🔥 SCORE",
        "back_menu": "🔄 BACK TO MENU",
        "nick_error": "Nickname already taken!",
        "srv_error": "GORZEN server unreachable!",
        "input_nick": "Your nick for",
        "enter": "LOGIN",
        "lang_btn": "🌐 LANGUAGE (EN)"
    }
}

CUR_LANG = "RU"

def T(key):
    return LANGUAGES[CUR_LANG].get(key, key)

# --- СТИЛИ GORZEN UI ---
STYLE_SHEET = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget#MenuWidget, QWidget#GameWidget {
    background-color: #1a1a2e;
}
QLabel {
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
QLineEdit {
    padding: 15px;
    border-radius: 12px;
    border: 2px solid #30475e;
    background: #16213e;
    color: white;
    font-size: 16px;
}
QLineEdit:focus {
    border: 2px solid #e94560;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #16213e;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #e94560;
    border-radius: 5px;
}
"""

class Communicate(QObject):
    server_found = pyqtSignal(str, str)
    new_player = pyqtSignal(str)
    receive_question = pyqtSignal(dict)
    show_results = pyqtSignal(int, dict) 
    tick_timer = pyqtSignal(int)
    update_score_signal = pyqtSignal(int)
    admin_update_stats = pyqtSignal(dict) 
    game_over_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

class LanguageSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GORZEN - LANGUAGE")
        self.setFixedSize(320, 420)
        self.setStyleSheet("background-color: #1a1a2e; border: 3px solid #e94560; border-radius: 15px;")
        layout = QVBoxLayout(self)
        
        lbl = QLabel("SELECT LANGUAGE\nԸՆՏՐԵՔ ԼԵԶՈՒՆ")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-weight: 900; color: white; font-size: 20px; border: none; margin: 10px;")
        layout.addWidget(lbl)

        buttons = [("🇷🇺 РУССКИЙ", "RU"), ("🇦🇲 ՀԱՅԵՐԵՆ", "AM"), ("🇺🇸 ENGLISH", "EN")]

        for text, code in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(70)
            btn.setStyleSheet("""
                QPushButton { 
                    background: #0f3460; color: white; border-radius: 15px; 
                    font-weight: bold; font-size: 18px; border: 1px solid #30475e;
                }
                QPushButton:hover { background: #e94560; border: 1px solid white; }
            """)
            btn.clicked.connect(lambda _, c=code: self.set_lang(c))
            layout.addWidget(btn)
    
    def set_lang(self, code):
        global CUR_LANG
        CUR_LANG = code
        self.accept()

class StatsDialog(QDialog):
    def __init__(self, scores, correct_idx, options, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GORZEN - ROUND RESULTS")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("background-color: #1a1a2e; border: 2px solid #e94560;")
        layout = QVBoxLayout(self)

        title = QLabel(T("rating_title"))
        title.setStyleSheet("font-size: 28px; font-weight: 900; color: #e94560; margin: 15px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        ans_text = options[correct_idx] if correct_idx < len(options) else "---"
        res_lbl = QLabel(f"{T('correct_ans')}\n{ans_text}")
        res_lbl.setStyleSheet("""
            color: white; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #27ae60, stop:1 #2ecc71); 
            font-size: 20px; padding: 20px; border-radius: 15px; font-weight: bold;
        """)
        res_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        res_lbl.setWordWrap(True)
        layout.addWidget(res_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll_layout = QVBoxLayout(content)
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for i, (nick, score) in enumerate(sorted_scores):
            p_box = QFrame()
            p_box.setStyleSheet("background: #16213e; border-radius: 15px; margin-bottom: 5px;")
            p_lay = QHBoxLayout(p_box)
            rank_str = "👑" if i == 0 and score > 0 else f"#{i+1}"
            rank = QLabel(rank_str)
            rank.setStyleSheet("font-size: 22px; font-weight: bold; color: #fbc02d;")
            name = QLabel(str(nick))
            name.setStyleSheet("font-size: 18px; color: white; font-weight: 600;")
            pts = QLabel(f"{score} PT")
            pts.setStyleSheet("font-weight: 900; color: #e94560; font-size: 18px;")
            p_lay.addWidget(rank); p_lay.addWidget(name); p_lay.addStretch(); p_lay.addWidget(pts)
            scroll_layout.addWidget(p_box)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

        btn_close = QPushButton(T("btn_next"))
        btn_close.setMinimumHeight(65)
        btn_close.setStyleSheet("""
            QPushButton { 
                background: #e94560; color: white; font-size: 22px; font-weight: bold; 
                border-radius: 15px; border-bottom: 5px solid #950740;
            }
            QPushButton:hover { background: #ff4d6d; }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

class AdminSetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GORZEN - SETUP")
        self.setFixedSize(450, 550)
        self.setStyleSheet("background-color: #1a1a2e;")
        layout = QVBoxLayout(self)

        self.pin = random.randint(1000, 9999)
        header = QLabel(f"{T('room_pin')}\n{self.pin}")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #673AB7, stop:1 #512DA8); 
            color: white; font-size: 36px; font-weight: 900; padding: 30px; border-radius: 20px;
        """)
        layout.addWidget(header)
        
        layout.addWidget(QLabel(f"<b style='color: #e94560;'>{T('arena_name')}</b>"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("GORZEN_ARENA_1")
        layout.addWidget(self.name_input)

        self.json_path = ""
        self.btn_file = QPushButton(T("select_json"))
        self.btn_file.setMinimumHeight(60)
        self.btn_file.setStyleSheet("""
            QPushButton { background: #30475e; color: white; border-radius: 12px; font-weight: bold; }
            QPushButton:hover { background: #3e5c7a; }
        """)
        self.btn_file.clicked.connect(self.select_file)
        layout.addWidget(self.btn_file)

        layout.addStretch()
        self.btn_start = QPushButton(T("launch_srv"))
        self.btn_start.setMinimumHeight(75)
        self.btn_start.setStyleSheet("""
            QPushButton { background: #0f3460; color: white; font-size: 22px; font-weight: bold; border-radius: 20px; border: 2px solid #e94560; }
            QPushButton:hover { background: #16213e; border: 2px solid #ff4d6d; }
        """)
        self.btn_start.clicked.connect(self.validate)
        layout.addWidget(self.btn_start)

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "JSON", "", "JSON Files (*.json)")
        if file:
            self.json_path = file
            self.btn_file.setText(T("json_ok"))
            self.btn_file.setStyleSheet("background: #0f3460; color: #2ecc71; border-radius: 12px; font-weight: bold; border: 1px solid #2ecc71;")

    def validate(self):
        if self.name_input.text().strip() and self.json_path: self.accept()
        else: QMessageBox.warning(self, "GORZEN SYSTEM", "EMPTY FIELDS!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GORZEN - ULTIMATE LAN")
        self.resize(800, 950)
        self.setStyleSheet(STYLE_SHEET)

        self.comm = Communicate()
        self.comm.server_found.connect(self.add_server_button)
        self.comm.new_player.connect(self.display_new_player)
        self.comm.receive_question.connect(self.display_question_ui)
        self.comm.show_results.connect(self.reveal_results_and_stats)
        self.comm.tick_timer.connect(self.update_timer_label)
        self.comm.update_score_signal.connect(self.update_ui_score)
        self.comm.admin_update_stats.connect(self.update_admin_stats_ui)
        self.comm.game_over_signal.connect(self.show_final_leaderboard)
        self.comm.error_signal.connect(lambda m: QMessageBox.critical(self, "GORZEN SYSTEM", m))

        self.reset_game_state()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.init_main_menu()
        self.init_game_ui()
        
        self.discovery_thread = threading.Thread(target=self.listen_for_broadcasts, daemon=True)
        self.discovery_thread.start()

    def reset_game_state(self):
        self.is_admin = False; self.is_active = False; self.my_socket = None
        self.my_nick = ""; self.my_score = 0; self.current_q_index = 0
        self.questions = []; self.player_clients = {}; self.player_scores = {}
        self.current_votes = {}; self.discovered_servers = {}; self.current_q_data = None

    def init_main_menu(self):
        self.menu_widget = QWidget(); self.menu_widget.setObjectName("MenuWidget")
        layout = QVBoxLayout(self.menu_widget); layout.setContentsMargins(30, 30, 30, 30)
        
        lang_bar = QHBoxLayout()
        self.btn_lang_toggle = QPushButton(T("lang_btn"))
        self.btn_lang_toggle.setFixedSize(200, 50)
        self.btn_lang_toggle.setStyleSheet("""
            QPushButton { 
                background: #16213e; color: #4ecca3; font-weight: bold; 
                border: 2px solid #4ecca3; border-radius: 12px; font-size: 14px;
            }
            QPushButton:hover { background: #4ecca3; color: #16213e; }
        """)
        self.btn_lang_toggle.clicked.connect(self.open_language_selector)
        lang_bar.addStretch(); lang_bar.addWidget(self.btn_lang_toggle)
        layout.addLayout(lang_bar)

        self.logo_label = QLabel(T("menu_logo"))
        self.logo_label.setStyleSheet("font-size: 85px; font-weight: 900; color: #e94560; margin: 20px; letter-spacing: 5px;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)

        self.scroll_servers = QScrollArea(); self.scroll_servers.setWidgetResizable(True)
        self.server_list_container = QWidget(); self.server_list_layout = QVBoxLayout(self.server_list_container)
        self.server_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop); self.server_list_layout.setSpacing(15)
        self.scroll_servers.setWidget(self.server_list_container)
        layout.addWidget(self.scroll_servers)

        self.search_status = QLabel(T("scan"))
        self.search_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_status.setStyleSheet("color: #4ecca3; font-size: 16px; font-weight: bold;")
        self.server_list_layout.addWidget(self.search_status)

        layout.addStretch()
        self.btn_create = QPushButton(T("create_srv"))
        self.btn_create.setMinimumHeight(90)
        self.btn_create.setStyleSheet("""
            QPushButton { 
                background: #0f3460; color: #e94560; font-size: 24px; font-weight: bold; 
                border-radius: 20px; border: 4px solid #e94560; 
            }
            QPushButton:hover { background: #e94560; color: white; }
        """)
        self.btn_create.clicked.connect(self.setup_as_admin)
        layout.addWidget(self.btn_create)
        self.stack.addWidget(self.menu_widget)

    def open_language_selector(self):
        if LanguageSelector(self).exec(): self.refresh_ui_language()

    def refresh_ui_language(self):
        self.btn_lang_toggle.setText(T("lang_btn")); self.logo_label.setText(T("menu_logo"))
        self.search_status.setText(T("scan")); self.btn_create.setText(T("create_srv"))
        self.score_lbl.setText(f"{T('score')}: {self.my_score}")
        if self.is_admin: self.score_lbl.setText(T("admin_label"))
        self.btn_admin_control.setText(T("next_step"))
        if self.stack.currentIndex() == 1 and not self.current_q_data: self.question_box.setText(T("wait_start"))

    def init_game_ui(self):
        self.game_widget = QWidget(); self.game_widget.setObjectName("GameWidget")
        layout = QVBoxLayout(self.game_widget); layout.setContentsMargins(25, 25, 25, 25)
        
        top_bar = QHBoxLayout()
        self.score_lbl = QLabel(f"{T('score')}: 0")
        self.timer_lbl = QLabel("⏱️ --")
        self.score_lbl.setStyleSheet("font-size: 26px; font-weight: 900; color: #4ecca3;")
        self.timer_lbl.setStyleSheet("font-size: 30px; font-weight: 900; color: white; background: #e94560; padding: 15px 30px; border-radius: 20px;")
        top_bar.addWidget(self.score_lbl); top_bar.addStretch(); top_bar.addWidget(self.timer_lbl)
        layout.addLayout(top_bar)

        self.game_info_bar = QLabel("")
        self.game_info_bar.setStyleSheet("color: #95a5a6; font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.game_info_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.game_info_bar)

        self.question_box = QLabel(T("wait_start"))
        self.question_box.setStyleSheet("font-size: 34px; background: #16213e; border: 4px solid #e94560; padding: 50px; border-radius: 30px; color: white; font-weight: bold;")
        self.question_box.setWordWrap(True); self.question_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.question_box)

        self.ans_container = QWidget(); self.ans_grid = QGridLayout(self.ans_container); self.ans_grid.setSpacing(20)
        layout.addWidget(self.ans_container)

        self.btn_admin_control = QPushButton(T("next_step"))
        self.btn_admin_control.setMinimumHeight(85)
        self.btn_admin_control.setStyleSheet("QPushButton { background: #30475e; color: #1a1a2e; font-size: 26px; font-weight: bold; border-radius: 25px; } QPushButton:enabled { background: #e94560; color: white; border: 2px solid #ff4d6d; }")
        self.btn_admin_control.clicked.connect(self.admin_trigger_next); self.btn_admin_control.hide()
        layout.addWidget(self.btn_admin_control)
        self.stack.addWidget(self.game_widget)

    # --- СЕРВЕРНАЯ ЛОГИКА ---
    def setup_as_admin(self):
        dialog = AdminSetupDialog()
        if dialog.exec():
            self.reset_game_state(); self.is_admin = True; self.is_active = True
            try:
                with open(dialog.json_path, 'r', encoding='utf-8') as f: self.questions = json.load(f)
                self.stack.setCurrentIndex(1); self.btn_admin_control.show(); self.btn_admin_control.setText(T("start_game")); self.btn_admin_control.setEnabled(False)
                self.score_lbl.setText(T("admin_label"))
                threading.Thread(target=self.start_broadcast, args=(dialog.name_input.text(),), daemon=True).start()
                threading.Thread(target=self.start_tcp_engine, daemon=True).start()
            except Exception as e: QMessageBox.critical(self, "GORZEN Error", f"File error: {e}")

    def start_tcp_engine(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', TCP_PORT)); s.listen(32)
        while self.is_active:
            try:
                c, _ = s.accept()
                threading.Thread(target=self.client_handler, args=(c,), daemon=True).start()
            except: break
        s.close()

    def client_handler(self, c):
        nick = ""
        while self.is_active:
            try:
                data = c.recv(4096).decode('utf-8')
                if not data: break
                for raw in data.strip().split(MSG_SEP):
                    if not raw: continue
                    if raw.startswith("JOIN:"):
                        name = raw.split(":")[1]
                        if name in self.player_scores: c.send(f"ERR_NICK{MSG_SEP}".encode('utf-8'))
                        else:
                            nick = name; c.send(f"OK_JOIN{MSG_SEP}".encode('utf-8'))
                            self.player_clients[c] = nick; self.player_scores[nick] = 0; self.comm.new_player.emit(nick)
                    elif raw.startswith("VOTE:"):
                        self.current_votes[nick] = int(raw.split(":")[1])
                        self.comm.admin_update_stats.emit({"total": len(self.player_clients), "voted": len(self.current_votes)})
                        if len(self.current_votes) >= len(self.player_clients): self.time_left = 0
            except: break

    def admin_trigger_next(self):
        if self.current_q_index < len(self.questions):
            self.current_votes = {}; q = self.questions[self.current_q_index]; self.current_q_data = q
            pkt = json.dumps({"type": "QUES", "data": q}) + MSG_SEP
            for c in list(self.player_clients.keys()):
                try: c.send(pkt.encode('utf-8'))
                except: self.player_clients.pop(c)
            self.current_q_index += 1; self.btn_admin_control.setEnabled(False); self.comm.receive_question.emit(q)
            # Берем время напрямую из JSON файла для каждого вопроса
            threading.Thread(target=self.admin_timer_loop, args=(q.get("time", 20), q["correct"]), daemon=True).start()
        else: self.server_finish_game()

    def admin_timer_loop(self, sec, cor):
        self.time_left = sec
        while self.time_left >= 0:
            # СИНХРОНИЗАЦИЯ: сервер отправляет ТЕКУЩЕЕ число всем клиентам
            sync = json.dumps({"type": "TIME", "val": self.time_left}) + MSG_SEP
            for c in list(self.player_clients.keys()):
                try: c.send(sync.encode('utf-8'))
                except: pass
            self.comm.tick_timer.emit(self.time_left)
            time.sleep(1); self.time_left -= 1
        
        # Обработка очков после конца таймера
        for c, n in self.player_clients.items():
            if self.current_votes.get(n) == cor: self.player_scores[n] += 1000
        res_pkt = json.dumps({"type": "ROUND_END", "cor": cor, "scores": self.player_scores}) + MSG_SEP
        for c in list(self.player_clients.keys()):
            try: c.send(res_pkt.encode('utf-8'))
            except: pass
        self.comm.show_results.emit(cor, self.player_scores)

    def server_finish_game(self):
        self.is_active = False; leaders = sorted(self.player_scores.items(), key=lambda x: x[1], reverse=True)
        end_pkt = json.dumps({"type": "FINAL_STATS", "leaders": leaders}) + MSG_SEP
        for c in list(self.player_clients.keys()):
            try: c.send(end_pkt.encode('utf-8'))
            except: pass
        self.comm.game_over_signal.emit(leaders)

    # --- ЛОГИКА КЛИЕНТА ---
    def player_receiver(self):
        buf = ""
        while True:
            try:
                data = self.my_socket.recv(8192).decode('utf-8')
                if not data: break
                buf += data
                while MSG_SEP in buf:
                    msg, buf = buf.split(MSG_SEP, 1)
                    if msg == "ERR_NICK": self.comm.error_signal.emit(T("nick_error")); return
                    if msg == "OK_JOIN": continue
                    obj = json.loads(msg); t = obj["type"]
                    if t == "QUES": self.current_q_data = obj["data"]; self.comm.receive_question.emit(obj["data"])
                    elif t == "TIME": 
                        # Клиент просто берет цифру от сервера
                        self.comm.tick_timer.emit(obj["val"])
                    elif t == "ROUND_END": 
                        self.my_score = obj["scores"].get(self.my_nick, 0); self.comm.update_score_signal.emit(self.my_score)
                        self.comm.show_results.emit(obj["cor"], obj["scores"])
                    elif t == "FINAL_STATS": self.comm.game_over_signal.emit(obj["leaders"])
            except: break

    def display_question_ui(self, q):
        self.stack.setCurrentIndex(1); self.question_box.setText(q["question"])
        # При получении вопроса сразу ставим время из JSON
        self.timer_lbl.setText(str(q.get('time', 15)))
        while self.ans_grid.count():
            w = self.ans_grid.takeAt(0).widget()
            if w: w.deleteLater()
        colors = ["#e94560", "#0f3460", "#fbc02d", "#4ecca3"]; coords = [(0,0), (0,1), (1,0), (1,1)]
        for i, opt in enumerate(q["options"]):
            btn = QPushButton(opt); btn.setMinimumHeight(180); color = colors[i%4]
            btn.setStyleSheet(f"QPushButton {{ background: {color}; color: white; font-size: 26px; font-weight: 900; border-radius: 25px; border-bottom: 8px solid rgba(0,0,0,0.25); padding: 10px; }} QPushButton:hover {{ margin-top: 4px; border-bottom: 4px solid rgba(0,0,0,0.25); }}")
            if self.is_admin: btn.setEnabled(False)
            else: btn.clicked.connect(lambda _, x=i: self.player_send_vote(x))
            r, c = coords[i%4]; self.ans_grid.addWidget(btn, r, c)

    def player_send_vote(self, idx):
        for i in range(self.ans_grid.count()):
            b = self.ans_grid.itemAt(i).widget()
            b.setEnabled(False)
            if i != idx: b.setStyleSheet("background: #30475e; color: #1a1a2e; border-radius: 25px;")
        try: self.my_socket.send(f"VOTE:{idx}{MSG_SEP}".encode('utf-8'))
        except: pass

    def reveal_results_and_stats(self, cor, all_scores):
        for i in range(self.ans_grid.count()):
            btn = self.ans_grid.itemAt(i).widget()
            if i == cor: btn.setStyleSheet("background: #27ae60; color: white; border: 6px solid #fbc02d; border-radius: 25px; font-weight: 900;"); btn.setText("CORRECT ✅\n" + btn.text())
            else: btn.setStyleSheet("background: #950740; color: rgba(255,255,255,0.3); border-radius: 25px;")
        dlg = StatsDialog(all_scores, cor, self.current_q_data["options"], self)
        dlg.exec()
        if self.is_admin: self.btn_admin_control.setEnabled(True); self.btn_admin_control.setText(T("next_step"))

    def show_final_leaderboard(self, leaders):
        while self.ans_grid.count(): self.ans_grid.takeAt(0).widget().deleteLater()
        is_draw = len(leaders) > 1 and leaders[0][1] == leaders[1][1] or not leaders or (len(leaders) == 1 and leaders[0][1] == 0)
        if is_draw: self.question_box.setText(T("draw")); self.question_box.setStyleSheet("font-size: 45px; background: #0f3460; border: 6px solid #4ecca3; padding: 50px; border-radius: 35px; color: #4ecca3;")
        else:
            win_n, win_s = leaders[0]; self.question_box.setText(f"{T('champ')}: {win_n}\n{T('final_score')}: {win_s}"); self.question_box.setStyleSheet("font-size: 45px; background: #1a1a2e; border: 6px solid #fbc02d; padding: 50px; border-radius: 35px; color: #fbc02d;")
        final_text = "RANKING:\n" + "\n".join([f"{i+1}. {n} — {s}" for i, (n, s) in enumerate(leaders[:5])])
        lbl = QLabel(final_text); lbl.setStyleSheet("font-size: 24px; color: white; font-weight: bold; margin: 20px;"); lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.ans_grid.addWidget(lbl, 0, 0)
        btn_restart = QPushButton(T("back_menu")); btn_restart.setMinimumHeight(80); btn_restart.setStyleSheet("QPushButton { background: #e94560; color: white; font-size: 22px; font-weight: bold; border-radius: 20px; } QPushButton:hover { background: #ff4d6d; }")
        btn_restart.clicked.connect(self.go_to_main_menu); self.ans_grid.addWidget(btn_restart, 1, 0)

    def go_to_main_menu(self):
        if self.my_socket:
            try: self.my_socket.close()
            except: pass
        self.reset_game_state()
        for i in reversed(range(self.server_list_layout.count())): 
            widget = self.server_list_layout.itemAt(i).widget()
            if widget: widget.setParent(None)
        self.server_list_layout.addWidget(self.search_status); self.search_status.setText(T("scan")); self.search_status.show(); self.stack.setCurrentIndex(0); self.refresh_ui_language()

    def update_admin_stats_ui(self, s): self.game_info_bar.setText(f"{T('players')}: {s['total']}    |    {T('answers')}: {s['voted']}")

    def update_timer_label(self, v): 
        # Прямая установка текста из сообщения сервера
        self.timer_lbl.setText(str(v))
        if v <= 5: self.timer_lbl.setStyleSheet("font-size: 30px; font-weight: 900; color: white; background: #ff0000; padding: 15px 30px; border-radius: 20px;")
        else: self.timer_lbl.setStyleSheet("font-size: 30px; font-weight: 900; color: white; background: #e94560; padding: 15px 30px; border-radius: 20px;")

    def update_ui_score(self, v): 
        self.my_score = v
        if not self.is_admin: self.score_lbl.setText(f"{T('score')}: {v} PT")

    def display_new_player(self, n):
        self.search_status.hide(); self.btn_admin_control.setEnabled(True)
        lbl = QLabel(f"⚡ {n.upper()} {T('joined')}")
        lbl.setStyleSheet("color: #4ecca3; font-weight: 900; font-size: 18px; background: #16213e; padding: 20px; border-radius: 15px; border-left: 5px solid #4ecca3;")
        self.server_list_layout.addWidget(lbl)

    def add_server_button(self, name, ip):
        self.search_status.hide()
        for i in range(self.server_list_layout.count()):
            w = self.server_list_layout.itemAt(i).widget()
            if isinstance(w, QPushButton) and w.accessibleName() == ip: return
        b = QPushButton(f"🎮 {name.upper()}\n📍 IP: {ip}"); b.setAccessibleName(ip); b.setMinimumHeight(110); b.setStyleSheet("QPushButton { background: #0f3460; color: white; font-weight: 900; font-size: 20px; border-radius: 20px; border-left: 8px solid #e94560; text-align: left; padding-left: 25px; } QPushButton:hover { background: #16213e; border-left: 8px solid #4ecca3; }")
        b.clicked.connect(lambda: self.connect_to_server(name, ip)); self.server_list_layout.insertWidget(0, b)

    def connect_to_server(self, n, ip):
        nick, ok = QInputDialog.getText(self, T("enter"), f"{T('input_nick')} {n}:")
        if ok and nick.strip():
            try:
                self.reset_game_state(); self.my_nick = nick.strip(); self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.my_socket.connect((ip, TCP_PORT)); self.my_socket.send(f"JOIN:{self.my_nick}{MSG_SEP}".encode('utf-8'))
                self.stack.setCurrentIndex(1); self.btn_admin_control.hide(); threading.Thread(target=self.player_receiver, daemon=True).start()
            except: QMessageBox.critical(self, "GORZEN SYSTEM", T("srv_error"))

    def start_broadcast(self, n):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        m = f"GORZEN_SRV:{n}".encode('utf-8')
        while self.is_active:
            try: sock.sendto(m, ('<broadcast>', UDP_PORT)); time.sleep(2)
            except: break
        sock.close()

    def listen_for_broadcasts(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); sock.bind(('', UDP_PORT))
        while True:
            try:
                data, addr = sock.recvfrom(1024); msg = data.decode('utf-8')
                if msg.startswith("GORZEN_SRV:"):
                    name = msg.split(":")[1]
                    if addr[0] not in self.discovered_servers: self.discovered_servers[addr[0]] = name; self.comm.server_found.emit(name, addr[0])
            except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    font = QFont("Segoe UI", 10); app.setFont(font)
    lang_dlg = LanguageSelector()
    if lang_dlg.exec():
        main_win = MainWindow(); main_win.show(); sys.exit(app.exec())
    else: sys.exit()