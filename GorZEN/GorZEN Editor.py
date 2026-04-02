import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                             QSpinBox, QFileDialog, QMessageBox, QFrame, 
                             QScrollArea, QGraphicsDropShadowEffect, QDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor

# --- СИСТЕМА ЛОКАЛИЗАЦИИ (3 ЯЗЫКА) ---
LANGUAGES = {
    "RU": {
        "logo": "GORZEN\nEDITOR",
        "edit_title": "РЕДАКТИРОВАНИЕ СЛАЙДА",
        "export_btn": "💾 ЭКСПОРТ В .JSON",
        "q_label": "ТЕКСТ ВОПРОСА",
        "q_placeholder": "Напишите ваш вопрос здесь...",
        "ans_label": "ВАРИАНТЫ ОТВЕТОВ (ВЫБЕРИТЕ ПРАВИЛЬНЫЙ)",
        "ans_placeholder": "Вариант ответа",
        "correct_tag": "✓ ПРАВИЛЬНЫЙ",
        "time_label": "ТАЙМЕР (СЕК)",
        "del_btn": "🗑️ УДАЛИТЬ СЛАЙД",
        "add_btn": "＋ ДОБАВИТЬ СЛАЙД",
        "prev_btn": "❮ НАЗАД",
        "next_btn": "ВПЕРЕД ❯",
        "page_info": "СЛАЙД {} ИЗ {}",
        "err_empty": "Ошибка: Слайд №{} не заполнен!",
        "err_last": "Нельзя удалить последний слайд!",
        "save_success": "Успешно сохранено {} слайдов!",
        "empty_text": "Пустой вопрос",
        "lang_name": "🌐 ЯЗЫК (RU)"
    },
    "AM": {
        "logo": "GORZEN\nEDITOR",
        "edit_title": "ՍԼԱՅԴԻ ԽՄԲԱԳՐՈՒՄ",
        "export_btn": "💾 ԱՐՏԱՀԱՆԵԼ .JSON",
        "q_label": "ՀԱՐՑԻ ՏԵՔՍՏԸ",
        "q_placeholder": "Գրեք ձեր հարցը այստեղ...",
        "ans_label": "ՊԱՏԱՍԽԱՆՆԵՐ (ԸՆՏՐԵՔ ՃԻՇՏԸ)",
        "ans_placeholder": "Պատասխան",
        "correct_tag": "✓ ՃԻՇՏ Է",
        "time_label": "ԺԱՄԱՆԱԿ (ՎԱՅՐԿ.)",
        "del_btn": "🗑️ ՀԵՌԱՑՆԵԼ ՍԼԱՅԴԸ",
        "add_btn": "＋ ԱՎԵԼԱՑՆԵԼ ՍԼԱՅԴ",
        "prev_btn": "❮ ԵՏ",
        "next_btn": "ԱՌԱՋ ❯",
        "page_info": "ՍԼԱՅԴ {} / {}",
        "err_empty": "Սխալ: Սլայդ №{} լրացված չէ:",
        "err_last": "Չի կարելի հեռացնել վերջին սլայդը:",
        "save_success": "Հաջողությամբ պահպանվեց {} սլայդ:",
        "empty_text": "Դատարկ հարց",
        "lang_name": "🌐 ԼԵԶՈՒ (AM)"
    },
    "EN": {
        "logo": "GORZEN\nEDITOR",
        "edit_title": "EDIT SLIDE",
        "export_btn": "💾 EXPORT TO .JSON",
        "q_label": "QUESTION TEXT",
        "q_placeholder": "Write your question here...",
        "ans_label": "ANSWERS (SELECT CORRECT ONE)",
        "ans_placeholder": "Answer option",
        "correct_tag": "✓ CORRECT",
        "time_label": "TIMER (SEC)",
        "del_btn": "🗑️ DELETE SLIDE",
        "add_btn": "＋ ADD NEW SLIDE",
        "prev_btn": "❮ BACK",
        "next_btn": "NEXT ❯",
        "page_info": "SLIDE {} OF {}",
        "err_empty": "Error: Slide #{} is empty!",
        "err_last": "Cannot delete the only remaining slide!",
        "save_success": "Successfully saved {} slides!",
        "empty_text": "Empty question",
        "lang_name": "🌐 LANGUAGE (EN)"
    }
}

class LanguageSelector(QDialog):
    """Окно выбора языка при запуске или смене"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Language")
        self.setFixedSize(320, 320)
        self.choice = "RU"
        self.setStyleSheet("background-color: #0f172a; color: white;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        label = QLabel("CHOOSE LANGUAGE / ԸՆՏՐԵԼ ԼԵԶՈՒՆ")
        label.setStyleSheet("font-weight: bold; color: #38bdf8;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        for lang_code, name in [("RU", "🇷🇺 Русский"), ("AM", "🇦🇲 Հայերեն"), ("EN", "🇺🇸 English")]:
            btn = QPushButton(name)
            btn.setFixedHeight(55)
            btn.setStyleSheet("""
                QPushButton { background: #1e293b; border: 1px solid #334155; border-radius: 12px; font-weight: bold; font-size: 14px; }
                QPushButton:hover { background: #38bdf8; color: #0f172a; }
            """)
            btn.clicked.connect(lambda _, c=lang_code: self.done_with_choice(c))
            layout.addWidget(btn)
            
    def done_with_choice(self, code):
        self.choice = code
        self.accept()

class GorzenEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "RU"
        self.setWindowTitle("GORZEN - PROFESSIONAL SLIDE EDITOR")
        self.resize(1200, 820)
        
        # Данные проекта
        self.slides = [self.create_empty_slide_data()]
        self.current_index = 0

        self.setup_ui()
        self.refresh_ui()

    def create_empty_slide_data(self):
        return {
            "question": "",
            "options": ["", "", "", ""],
            "correct": 0,
            "time": 15
        }

    def t(self, key):
        """Функция перевода текста по ключу"""
        return LANGUAGES[self.lang].get(key, key)

    def setup_ui(self):
        # Глобальный современный стиль
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QWidget#MainContent { background-color: #1e293b; border-radius: 25px; }
            QFrame#SideBar { background-color: #0f172a; border-right: 1px solid #1e293b; }
            
            QLabel { color: #f1f5f9; font-family: 'Segoe UI', sans-serif; }
            
            QLineEdit { 
                background: #0f172a; border: 2px solid #334155; 
                border-radius: 12px; color: white; padding: 14px; font-size: 16px;
            }
            QLineEdit:focus { border-color: #38bdf8; background: #111827; }
            
            QPushButton#NavBtn { 
                background: #334155; color: white; border-radius: 15px; 
                font-size: 16px; font-weight: bold; height: 55px;
            }
            QPushButton#NavBtn:hover { background: #38bdf8; color: #0f172a; }
            
            QPushButton#SlideItem { 
                background: #1e293b; color: #94a3b8; border-radius: 10px; 
                text-align: left; padding: 12px; border: 1px solid #334155; font-size: 13px;
                margin-bottom: 2px;
            }
            QPushButton#SlideItem[active="true"] { 
                background: #38bdf8; color: #0f172a; font-weight: bold; border: 2px solid white;
            }
            
            QPushButton#CorrectBtn { 
                background: #334155; color: white; border-radius: 12px; font-weight: bold; font-size: 13px;
            }
            QPushButton#CorrectBtn:checked { 
                background: #10b981; border: 2px solid white; color: white;
            }
            
            QSpinBox { 
                background: #0f172a; color: white; border: 2px solid #334155; 
                padding: 8px; border-radius: 10px; font-size: 16px; font-weight: bold;
            }
            
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: #0f172a; width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #334155; border-radius: 4px; min-height: 20px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        outer_layout = QHBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # --- ЛЕВАЯ ПАНЕЛЬ (SIDEBAR) ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("SideBar")
        self.sidebar.setFixedWidth(300)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(15, 20, 15, 20)
        
        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("font-size: 34px; font-weight: 900; color: #38bdf8; margin: 15px 0;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(self.logo_label)

        # Список слайдов с прокруткой
        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.slides_layout = QVBoxLayout(self.scroll_content)
        self.slides_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        side_layout.addWidget(self.scroll_area)

        # Кнопка смены языка
        self.btn_lang = QPushButton()
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.setStyleSheet("""
            QPushButton { background: transparent; color: #38bdf8; border: 2px solid #38bdf8; 
            border-radius: 12px; padding: 12px; font-weight: bold; margin-bottom: 8px; }
            QPushButton:hover { background: #38bdf8; color: #0f172a; }
        """)
        self.btn_lang.clicked.connect(self.change_language)
        side_layout.addWidget(self.btn_lang)

        # Кнопка добавить слайд в сайдбаре
        self.btn_add_sidebar = QPushButton()
        self.btn_add_sidebar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_sidebar.setStyleSheet("""
            QPushButton { 
                background: #10b981; color: white; border-radius: 15px; 
                padding: 18px; font-weight: bold; font-size: 15px;
            }
            QPushButton:hover { background: #059669; }
        """)
        self.btn_add_sidebar.clicked.connect(self.add_new_slide)
        side_layout.addWidget(self.btn_add_sidebar)

        outer_layout.addWidget(self.sidebar)

        # --- ПРАВАЯ ПАНЕЛЬ (EDITOR) ---
        self.main_content_container = QWidget()
        self.main_content_container.setContentsMargins(20, 20, 20, 20)
        main_box = QVBoxLayout(self.main_content_container)

        self.main_content = QWidget()
        self.main_content.setObjectName("MainContent")
        right_layout = QVBoxLayout(self.main_content)
        right_layout.setContentsMargins(45, 45, 45, 45)

        # Тень для основного контента
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.main_content.setGraphicsEffect(shadow)

        # Header: Заголовок и Кнопка Экспорта
        header_row = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #94a3b8;")
        
        self.btn_export = QPushButton()
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setFixedSize(220, 50)
        self.btn_export.setStyleSheet("""
            QPushButton { background: #e11d48; color: white; border-radius: 12px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background: #be123c; }
        """)
        self.btn_export.clicked.connect(self.export_json)
        
        header_row.addWidget(self.title_label)
        header_row.addStretch()
        header_row.addWidget(self.btn_export)
        right_layout.addLayout(header_row)

        right_layout.addSpacing(35)

        # Поле ввода вопроса
        self.label_question_title = QLabel()
        self.label_question_title.setStyleSheet("font-weight: bold; color: #38bdf8; font-size: 14px;")
        right_layout.addWidget(self.label_question_title)
        self.q_input = QLineEdit()
        self.q_input.setStyleSheet("font-size: 24px; font-weight: 500; padding: 22px;")
        right_layout.addWidget(self.q_input)

        right_layout.addSpacing(35)

        # Варианты ответов
        self.label_options_title = QLabel()
        self.label_options_title.setStyleSheet("font-weight: bold; color: #38bdf8; font-size: 14px;")
        right_layout.addWidget(self.label_options_title)
        
        self.ans_edits = []
        self.ans_checks = []
        ans_layout_container = QVBoxLayout()
        ans_layout_container.setSpacing(12)
        
        for i in range(4):
            row = QHBoxLayout()
            edit = QLineEdit()
            
            check = QPushButton()
            check.setCursor(Qt.CursorShape.PointingHandCursor)
            check.setCheckable(True)
            check.setFixedSize(150, 52)
            check.setObjectName("CorrectBtn")
            check.clicked.connect(lambda _, idx=i: self.set_correct_ans(idx))
            
            self.ans_edits.append(edit)
            self.ans_checks.append(check)
            row.addWidget(edit)
            row.addWidget(check)
            ans_layout_container.addLayout(row)
        right_layout.addLayout(ans_layout_container)

        right_layout.addSpacing(35)

        # Нижние настройки (Таймер и Удаление)
        bottom_settings = QHBoxLayout()
        
        time_vbox = QVBoxLayout()
        self.label_timer_title = QLabel()
        self.label_timer_title.setStyleSheet("font-weight: bold; color: #64748b;")
        time_vbox.addWidget(self.label_timer_title)
        self.time_spin = QSpinBox()
        self.time_spin.setRange(5, 600)
        self.time_spin.setFixedSize(130, 50)
        time_vbox.addWidget(self.time_spin)
        bottom_settings.addLayout(time_vbox)
        
        bottom_settings.addStretch()
        
        self.btn_delete_slide = QPushButton()
        self.btn_delete_slide.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete_slide.setFixedSize(240, 50)
        self.btn_delete_slide.setStyleSheet("""
            QPushButton { background: #1e293b; color: #fda4af; border: 1px solid #450a0a; border-radius: 12px; font-weight: bold; } 
            QPushButton:hover { background: #450a0a; color: white; }
        """)
        self.btn_delete_slide.clicked.connect(self.delete_current_slide)
        bottom_settings.addWidget(self.btn_delete_slide, alignment=Qt.AlignmentFlag.AlignBottom)

        right_layout.addLayout(bottom_settings)
        right_layout.addStretch()

        # Панель навигации
        nav_panel = QHBoxLayout()
        self.btn_prev = QPushButton()
        self.btn_prev.setObjectName("NavBtn")
        self.btn_prev.setFixedWidth(180)
        self.btn_prev.clicked.connect(self.go_prev)

        self.page_indicator = QLabel()
        self.page_indicator.setStyleSheet("font-size: 18px; font-weight: 900; color: #38bdf8;")

        self.btn_next = QPushButton()
        self.btn_next.setObjectName("NavBtn")
        self.btn_next.setFixedWidth(180)
        self.btn_next.clicked.connect(self.go_next)

        nav_panel.addWidget(self.btn_prev)
        nav_panel.addStretch()
        nav_panel.addWidget(self.page_indicator)
        nav_panel.addStretch()
        nav_panel.addWidget(self.btn_next)
        right_layout.addLayout(nav_panel)

        main_box.addWidget(self.main_content)
        outer_layout.addWidget(self.main_content_container)

    # --- ЛОГИКА ПРИЛОЖЕНИЯ ---

    def change_language(self):
        """Смена языка через диалог"""
        selector = LanguageSelector(self)
        if selector.exec():
            self.lang = selector.choice
            self.refresh_ui()

    def save_current(self):
        """Сохранение введенных данных в список слайдов"""
        if 0 <= self.current_index < len(self.slides):
            self.slides[self.current_index] = {
                "question": self.q_input.text(),
                "options": [e.text() for e in self.ans_edits],
                "correct": next((i for i, b in enumerate(self.ans_checks) if b.isChecked()), 0),
                "time": self.time_spin.value()
            }

    def refresh_ui(self):
        """Полная синхронизация интерфейса с данными"""
        # Обновление текстов локализации
        self.logo_label.setText(self.t("logo"))
        self.title_label.setText(self.t("edit_title"))
        self.btn_export.setText(self.t("export_btn"))
        self.label_question_title.setText(self.t("q_label"))
        self.q_input.setPlaceholderText(self.t("q_placeholder"))
        self.label_options_title.setText(self.t("ans_label"))
        self.label_timer_title.setText(self.t("time_label"))
        self.btn_delete_slide.setText(self.t("del_btn"))
        self.btn_add_sidebar.setText(self.t("add_btn"))
        self.btn_prev.setText(self.t("prev_btn"))
        self.btn_next.setText(self.t("next_btn"))
        self.btn_lang.setText(self.t("lang_name"))
        
        for i, edit in enumerate(self.ans_edits):
            edit.setPlaceholderText(f"{self.t('ans_placeholder')} {i+1}")
        for check in self.ans_checks:
            check.setText(self.t("correct_tag"))

        # Перерисовка списка слайдов в сайдбаре
        for i in reversed(range(self.slides_layout.count())): 
            item = self.slides_layout.itemAt(i).widget()
            if item: item.setParent(None)

        for i, slide in enumerate(self.slides):
            short_text = slide['question'][:18] if slide['question'].strip() else self.t('empty_text')
            btn = QPushButton(f"{i+1}. {short_text}...")
            btn.setObjectName("SlideItem")
            btn.setProperty("active", i == self.current_index)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self.jump_to_slide(idx))
            self.slides_layout.addWidget(btn)

        # Загрузка данных текущего слайда в поля ввода
        data = self.slides[self.current_index]
        self.q_input.setText(data["question"])
        for i, text in enumerate(data["options"]):
            self.ans_edits[i].setText(text)
        self.set_correct_ans(data["correct"])
        self.time_spin.setValue(data["time"])

        # Индикатор страниц
        self.page_indicator.setText(self.t("page_info").format(self.current_index + 1, len(self.slides)))
        self.btn_prev.setEnabled(self.current_index > 0)
        
        # Обновление стилей (для динамического свойства active)
        self.sidebar.style().unpolish(self.sidebar)
        self.sidebar.style().polish(self.sidebar)

    def set_correct_ans(self, index):
        """Установка правильного ответа (только один чекбокс активен)"""
        for i, btn in enumerate(self.ans_checks):
            btn.setChecked(i == index)

    def jump_to_slide(self, index):
        """Переход к конкретному слайду"""
        self.save_current()
        self.current_index = index
        self.refresh_ui()

    def add_new_slide(self):
        """Создание нового слайда"""
        self.save_current()
        self.slides.append(self.create_empty_slide_data())
        self.current_index = len(self.slides) - 1
        self.refresh_ui()

    def delete_current_slide(self):
        """Удаление слайда с проверкой на последний оставшийся"""
        if len(self.slides) > 1:
            self.slides.pop(self.current_index)
            self.current_index = max(0, self.current_index - 1)
            self.refresh_ui()
        else:
            QMessageBox.warning(self, "GORZEN", self.t("err_last"))

    def go_prev(self):
        """Назад"""
        if self.current_index > 0:
            self.save_current()
            self.current_index -= 1
            self.refresh_ui()

    def go_next(self):
        """Вперед (если последний — создает новый)"""
        self.save_current()
        if self.current_index < len(self.slides) - 1:
            self.current_index += 1
        else:
            self.slides.append(self.create_empty_slide_data())
            self.current_index += 1
        self.refresh_ui()

    def export_json(self):
        """Экспорт всех слайдов в файл JSON"""
        self.save_current()
        # Проверка на пустые вопросы перед сохранением
        for i, s in enumerate(self.slides):
            if not s["question"].strip():
                QMessageBox.critical(self, "GORZEN", self.t("err_empty").format(i+1))
                self.jump_to_slide(i)
                return

        path, _ = QFileDialog.getSaveFileName(self, "Export GORZEN Quiz", "quiz.json", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.slides, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "GORZEN SYSTEM", self.t("save_success").format(len(self.slides)))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Плавный стиль Fusion для всех платформ
    app.setStyle("Fusion")
    
    # Стартовый шрифт
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    editor = GorzenEditor()
    editor.show()
    sys.exit(app.exec())