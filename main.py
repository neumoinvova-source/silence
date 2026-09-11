from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import requests

Window.size = (360, 640)

# ==========================================
# НАСТРОЙКИ УСТРОЙСТВА — МЕНЯЙТЕ ИХ ТУТ ⚙️
# ==========================================
IS_ADMIN_PULTE = True   # Поставьте False для телефонов-приемников
MY_PHONE_NUMBER = "1"   # Номер приемника (от 1 до 5)
# ==========================================

class AmongUsMessengerApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Константы и настройки
        self.admin_password = "AdminVova#999"
        self.database_url = "https://firebaseio.com"
        self.current_volume = 1.0
        self.selected_phone = None  # Изначально телефон не выбран
        self.selected_sound = "Сирена"
        
        self.sound_files = {"Сирена": "sirena.mp3", "Звонок": "zvonok.mp3", "Гудок": "gudok.mp3"}
        
        # Списки для хранения кнопок (чтобы менять им цвета при активации)
        self.phone_buttons = {}
        self.sound_buttons = {}
        
        # Состояние крышки кнопки (0 - закрыта, 1 - крышка открыта, ждем второго нажатия)
        self.button_stage = 0

        if IS_ADMIN_PULTE:
            self.build_admin_ui()
        else:
            self.build_receiver_ui()
            
        return self.main_layout

    # 🎛️ ИНТЕРФЕЙС ПУЛЬТА
    def build_admin_ui(self):
        self.status_label = Label(text="🎮 РЕЖИМ ПУЛЬТА\nВыделите цель", font_size="18sp", halign="center", size_hint_y=0.1)
        self.main_layout.add_widget(self.status_label)
        
        # Ползунок громкости (изначально скрыт: size_hint_y=0)
        self.volume_label = Label(text="Удаленная громкость цели:", font_size="12sp", size_hint_y=0, opacity=0)
        self.volume_slider = Slider(min=0, max=1, value=1, step=0.1, size_hint_y=0, opacity=0)
        self.volume_slider.bind(value=self.change_volume)
        
        self.main_layout.add_widget(self.volume_label)
        self.main_layout.add_widget(self.volume_slider)
        
        # Выбор телефона
        self.main_layout.add_widget(Label(text="Кому отправить:", font_size="14sp", size_hint_y=0.05))
        phones_layout = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=0.08)
        for i in range(1, 6):
            btn = Button(text=str(i), background_color=(0.3, 0.3, 0.3, 1))
            btn.bind(on_press=self.select_phone)
            self.phone_buttons[str(i)] = btn
            phones_layout.add_widget(btn)
        self.main_layout.add_widget(phones_layout)
        
        # Выбор звука
        self.main_layout.add_widget(Label(text="Выбор звука:", font_size="14sp", size_hint_y=0.05))
        sounds_layout = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=0.08)
        for sound in self.sound_files.keys():
            # По умолчанию подсветим Сирену
            bg_color = (0.6, 0.3, 0.8, 1) if sound == "Сирена" else (0.4, 0.4, 0.5, 1)
            btn = Button(text=sound, background_color=bg_color)
            btn.bind(on_press=self.select_sound_func)
            self.sound_buttons[sound] = btn
            sounds_layout.add_widget(btn)
        self.main_layout.add_widget(sounds_layout)
        
        # Пароль
        self.main_layout.add_widget(Label(text="Пароль администратора:", font_size="14sp", size_hint_y=0.05))
        self.password_input = TextInput(text="", password=True, multiline=False, size_hint_y=0.08, font_size="16sp")
        self.password_input.bind(text=self.check_password)
        main_layout = self.main_layout.add_widget(self.password_input)
        
        # Двухэтапная главная кнопка
        self.send_btn = Button(
            text="🔒 ДОСТУП ОГРАНИЧЕН\n(Введите пароль)", font_size="16sp", halign="center",
            background_color=(0.2, 0.2, 0.2, 1), disabled=True, size_hint_y=0.3
        )
        self.send_btn.bind(on_press=self.handle_double_click_button)
        self.main_layout.add_widget(self.send_btn)

    # 📡 ИНТЕРФЕЙС ПРИЕМНИКА
    def build_receiver_ui(self):
        self.status_label = Label(
            text=f"📡 РЕЖИМ ПРИЕМНИКА\nУстройство: №{MY_PHONE_NUMBER}\nОжидание сигнала из сети...", 
            font_size="20sp", halign="center", size_hint_y=0.4
        )
        self.main_layout.add_widget(self.status_label)
        
        self.main_layout.add_widget(Label(text="Локальная громкость:", font_size="14sp", size_hint_y=0.1))
        volume_slider = Slider(min=0, max=1, value=1, step=0.1, size_hint_y=0.2)
        volume_slider.bind(value=self.change_volume)
        self.main_layout.add_widget(volume_slider)
        self.main_layout.add_widget(Label(size_hint_y=0.3))
        
        Clock.schedule_interval(self.check_internet_signals, 2.0)

    # 🕹️ ЛОГИКА КНОПОК И ПОДСВЕТКИ
    def select_phone(self, instance):
        self.selected_phone = instance.text
        
        # Сбрасываем цвета всех кнопок телефонов и красим выбранную в синий
        for btn in self.phone_buttons.values():
            btn.background_color = (0.3, 0.3, 0.3, 1)
        instance.background_color = (0.2, 0.5, 0.9, 1) # Ярко-синий
        
        # Показываем ползунок громкости, раз телефон выбран!
        self.volume_label.size_hint_y = 0.05
        self.volume_label.opacity = 1
        self.volume_slider.size_hint_y = 0.08
        self.volume_slider.opacity = 1
        
        self.update_status()

    def select_sound_func(self, instance):
        self.selected_sound = instance.text
        
        # Сбрасываем цвета кнопок звуков и красим выбранную в фиолетовый
        for btn in self.sound_buttons.values():
            btn.background_color = (0.4, 0.4, 0.5, 1)
        instance.background_color = (0.6, 0.3, 0.8, 1) # Фиолетовый
        
        self.update_status()

    def update_status(self):
        phone_text = f"Телефон №{self.selected_phone}" if self.selected_phone else "Не выбран"
        self.status_label.text = f"🎮 РЕЖИМ ПУЛЬТА\nЦель: {phone_text} ({self.selected_sound})"

    def change_volume(self, instance, value):
        self.current_volume = value

    def check_password(self, instance, text):
        if text == self.admin_password:
            if self.button_stage == 0:
                self.send_btn.disabled = False
                self.send_btn.text = "🔴 ОТКРЫТЬ КРЫШКУ КНОПКИ"
                self.send_btn.background_color = (0.4, 0.4, 0.4, 1)
        else:
            self.send_btn.disabled = True
            self.send_btn.text = "🔒 ДОСТУП ОГРАНИЧЕН\n(Введите пароль)"
            self.send_btn.background_color = (0.2, 0.2, 0.2, 1)
            self.button_stage = 0

    # 🛡️ СИСТЕМА ДВОЙНОГО НАЖАТИЯ (AMONG US)
    def handle_double_click_button(self, instance):
        if not self.selected_phone:
            self.status_label.text = "❌ ОШИБКА: Сначала выберите номер телефона!"
            return

        if self.button_stage == 0:
            # Этап 1: Откидываем крышку
            self.button_stage = 1
            self.send_btn.text = "⚠️ ПОДТВЕРДИТЬ ОТПРАВКУ!\n(Нажмите еще раз)"
            self.send_btn.background_color = (1, 0.2, 0.2, 1) # Становится угрожающе красной
            
            # Включаем таймер: если за 4 секунды не нажал второй раз — крышка закроется обратно
            Clock.schedule_once(self.reset_cover, 4.0)
            
        elif self.button_stage == 1:
            # Этап 2: Кнопка нажата повторно, отправляем в сеть!
            self.button_stage = 0
            self.send_to_internet()

    def reset_cover(self, dt):
        # Функция сброса крышки, если пользователь передумал нажимать второй раз
        if self.button_stage == 1 and self.password_input.text == self.admin_password:
            self.button_stage = 0
            self.send_btn.text = "🔴 ОТКРЫТЬ КРЫШКУ КНОПКИ"
            self.send_btn.background_color = (0.4, 0.4, 0.4, 1)

    # 🌐 ОТПРАВКА СИГНАЛА И ОТЧЕТ
    def send_to_internet(self):
        self.send_btn.text = "⏳ ОТПРАВКА..."
        self.send_btn.background_color = (0.8, 0.6, 0.2, 1)
        
        data = {
            "target_phone": self.selected_phone, 
            "sound_type": self.selected_sound,
            "volume": self.current_volume
        }
        try:
            response = requests.patch(self.database_url, json=data)
            if response.status_code == 200:
                self.send_btn.text = "✅ ОТПРАВЛЕНО УСПЕШНО!"
                self.send_btn.background_color = (0.2, 0.8, 0.2, 1) # Зелёная
            else:
                self.send_btn.text = "❌ СБОЙ СЕРВЕРА!"
                self.send_btn.background_color = (0.8, 0.2, 0.2, 1)
        except Exception:
            self.send_btn.text = "❌ СБОЙ СЕТИ (НЕТ ИНТЕРНЕТА)!"
            self.send_btn.background_color = (0.8, 0.2, 0.2, 1) # Красная
            
        # Через 3 секунды возвращаем кнопку в режим ожидания клика
        Clock.schedule_once(self.restore_button_after_report, 3.0)

    def restore_button_after_report(self, dt):
        if self.password_input.text == self.admin_password:
            self.send_btn.text = "🔴 ОТКРЫТЬ КРЫШКУ КНОПКИ"
            self.send_btn.background_color = (0.4, 0.4, 0.4, 1)

    # 📡 ФОНОВАЯ РАБОТА ПРИЕМНИКА
    def check_internet_signals(self, dt):
        try:
            response = requests.get(self.database_url)
            if response.status_code == 200:
                data = response.json()
                if data and "target_phone" in data and "sound_type" in data:
                    if data["target_phone"] == MY_PHONE_NUMBER:
                        sound_name = data["sound_type"]
                        remote_volume = data.get("volume", 1.0) # Считываем громкость, присланную админом
                        
