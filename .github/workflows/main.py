import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
import json
import os
from datetime import datetime

# Устанавливаем размер окна для мобильных устройств
Window.size = (360, 640)

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.contacts = []
        self.messages = {}

class Message:
    def __init__(self, sender, receiver, content, timestamp=None):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = timestamp or datetime.now()

class Database:
    def __init__(self):
        self.users_file = "users.json"
        self.messages_file = "messages.json"
        self.users = self.load_users()
        self.messages = self.load_messages()
        
    def load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    users = {}
                    for username, user_data in data.items():
                        user = User(username, user_data['password'])
                        user.contacts = user_data.get('contacts', [])
                        users[username] = user
                    return users
            except:
                return {}
        return {}
    
    def load_messages(self):
        if os.path.exists(self.messages_file):
            try:
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        data = {}
        for username, user in self.users.items():
            data[username] = {
                'password': user.password,
                'contacts': user.contacts
            }
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_messages(self):
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
    
    def register_user(self, username, password):
        if username in self.users:
            return False, "Пользователь с таким ником уже существует"
        
        if len(username) < 3:
            return False, "Ник должен быть не менее 3 символов"
        
        if len(password) < 4:
            return False, "Пароль должен быть не менее 4 символов"
        
        self.users[username] = User(username, password)
        self.save_users()
        return True, "Регистрация успешна!"
    
    def login_user(self, username, password):
        if username in self.users and self.users[username].password == password:
            return True, "Вход выполнен!"
        return False, "Неверный ник или пароль"
    
    def search_users(self, query, current_user):
        results = []
        for username in self.users:
            if query.lower() in username.lower() and username != current_user:
                results.append(username)
        return results
    
    def add_contact(self, username, contact_username):
        if contact_username in self.users and contact_username != username:
            if contact_username not in self.users[username].contacts:
                self.users[username].contacts.append(contact_username)
                self.save_users()
                return True, f"{contact_username} добавлен в контакты!"
        return False, "Пользователь не найден"
    
    def get_conversation_key(self, user1, user2):
        return f"{min(user1, user2)}_{max(user1, user2)}"
    
    def send_message(self, sender, receiver, content):
        if receiver not in self.users:
            return False, "Пользователь не найден"
        
        conv_key = self.get_conversation_key(sender, receiver)
        message = {
            'sender': sender,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        if conv_key not in self.messages:
            self.messages[conv_key] = []
        
        self.messages[conv_key].append(message)
        self.save_messages()
        return True, "Сообщение отправлено!"
    
    def get_messages(self, user1, user2):
        conv_key = self.get_conversation_key(user1, user2)
        if conv_key in self.messages:
            return self.messages[conv_key]
        return []

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = App.get_running_app().db
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Заголовок с названием Шилиграм
        title = Label(
            text='[b]Шилиграм[/b]',
            font_size='30sp', 
            size_hint_y=0.3,
            markup=True,
            color=(0.2, 0.6, 1, 1)
        )
        layout.add_widget(title)
        
        subtitle = Label(
            text='Быстрый и удобный мессенджер',
            font_size='14sp',
            size_hint_y=0.1,
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(subtitle)
        
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.4)
        
        self.username_input = TextInput(
            hint_text='Введите ваш ник',
            multiline=False,
            size_hint_y=None,
            height=50,
            background_color=(0.95, 0.95, 0.95, 1)
        )
        form_layout.add_widget(self.username_input)
        
        self.password_input = TextInput(
            hint_text='Введите пароль',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=50,
            background_color=(0.95, 0.95, 0.95, 1)
        )
        form_layout.add_widget(self.password_input)
        
        layout.add_widget(form_layout)
        
        button_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)
        
        login_btn = Button(
            text='Войти в Шилиграм',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        login_btn.bind(on_press=self.login)
        button_layout.add_widget(login_btn)
        
        register_btn = Button(
            text='Создать аккаунт',
            size_hint_y=None,
            height=50,
            background_color=(0.4, 0.8, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        register_btn.bind(on_press=self.go_to_register)
        button_layout.add_widget(register_btn)
        
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_popup("Ошибка", "Заполните все поля")
            return
        
        success, message = self.db.login_user(username, password)
        if success:
            app = App.get_running_app()
            app.current_user = username
            self.manager.current = 'main'
            self.username_input.text = ''
            self.password_input.text = ''
        else:
            self.show_popup("Ошибка входа", message)
    
    def go_to_register(self, instance):
        self.manager.current = 'register'
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title, 
            content=Label(text=message), 
            size_hint=(0.8, 0.4),
            separator_color=(0.2, 0.6, 1, 1)
        )
        popup.open()

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = App.get_running_app().db
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='[b]Регистрация в Шилиграм[/b]',
            font_size='24sp', 
            size_hint_y=0.2,
            markup=True,
            color=(0.2, 0.6, 1, 1)
        )
        layout.add_widget(title)
        
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        
        self.username_input = TextInput(
            hint_text='Придумайте ник',
            multiline=False,
            size_hint_y=None,
            height=50,
            background_color=(0.95, 0.95, 0.95, 1)
        )
        form_layout.add_widget(self.username_input)
        
        self.password_input = TextInput(
            hint_text='Придумайте пароль',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=50,
            background_color=(0.95, 0.95, 0.95, 1)
        )
        form_layout.add_widget(self.password_input)
        
        self.confirm_password_input = TextInput(
            hint_text='Повторите пароль',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=50,
            background_color=(0.95, 0.95, 0.95, 1)
        )
        form_layout.add_widget(self.confirm_password_input)
        
        layout.add_widget(form_layout)
        
        button_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)
        
        register_btn = Button(
            text='Создать аккаунт',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        register_btn.bind(on_press=self.register)
        button_layout.add_widget(register_btn)
        
        back_btn = Button(
            text='Назад',
            size_hint_y=None,
            height=50
        )
        back_btn.bind(on_press=self.go_back)
        button_layout.add_widget(back_btn)
        
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    
    def register(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()
        
        if not username or not password or not confirm_password:
            self.show_popup("Ошибка", "Заполните все поля")
            return
        
        if password != confirm_password:
            self.show_popup("Ошибка", "Пароли не совпадают")
            return
        
        success, message = self.db.register_user(username, password)
        if success:
            self.show_popup("Успех!", "Аккаунт создан! Теперь войдите в систему.")
            self.go_back(instance)
        else:
            self.show_popup("Ошибка регистрации", message)
    
    def go_back(self, instance):
        self.manager.current = 'login'
        self.username_input.text = ''
        self.password_input.text = ''
        self.confirm_password_input.text = ''
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title, 
            content=Label(text=message), 
            size_hint=(0.8, 0.4),
            separator_color=(0.2, 0.6, 1, 1)
        )
        popup.open()

class MessageBubble(BoxLayout):
    message_text = StringProperty()
    is_my_message = BooleanProperty()
    timestamp = StringProperty()

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_user = None
        self.db = App.get_running_app().db
        
        layout = BoxLayout(orientation='vertical')
        
        # Header с брендом Шилиграм
        header = BoxLayout(size_hint_y=0.08, padding=5)
        back_btn = Button(
            text='←', 
            size_hint_x=0.15,
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        self.chat_title = Label(
            text='Шилиграм - Чат',
            size_hint_x=0.85,
            color=(0.2, 0.6, 1, 1)
        )
        header.add_widget(self.chat_title)
        
        layout.add_widget(header)
        
        # Messages area
        self.messages_layout = ScrollView()
        self.messages_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=5,
            padding=10
        )
        self.messages_container.bind(minimum_height=self.messages_container.setter('height'))
        self.messages_layout.add_widget(self.messages_container)
        layout.add_widget(self.messages_layout)
        
        # Input area
        input_layout = BoxLayout(size_hint_y=0.12, spacing=10, padding=10)
        self.message_input = TextInput(
            hint_text='Напишите сообщение...',
            multiline=False,
            size_hint_x=0.7
        )
        self.message_input.bind(on_text_validate=self.send_message_from_enter)
        input_layout.add_widget(self.message_input)
        
        send_btn = Button(
            text='➤',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        send_btn.bind(on_press=self.send_message)
        input_layout.add_widget(send_btn)
        
        layout.add_widget(input_layout)
        
        self.add_widget(layout)
    
    def set_target_user(self, username):
        self.target_user = username
        self.chat_title.text = f"Шилиграм - {username}"
        self.load_messages()
    
    def load_messages(self):
        self.messages_container.clear_widgets()
        
        if not self.target_user:
            return
        
        messages = self.db.get_messages(App.get_running_app().current_user, self.target_user)
        
        for msg_data in messages:
            message_widget = MessageBubble(
                message_text=msg_data['content'],
                is_my_message=msg_data['sender'] == App.get_running_app().current_user,
                timestamp=msg_data['timestamp'][11:16]
            )
            self.messages_container.add_widget(message_widget)
        
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def scroll_to_bottom(self, dt):
        self.messages_layout.scroll_y = 0
    
    def send_message(self, instance):
        message = self.message_input.text.strip()
        if message and self.target_user:
            success, _ = self.db.send_message(
                App.get_running_app().current_user,
                self.target_user,
                message
            )
            if success:
                self.message_input.text = ''
                self.load_messages()
    
    def send_message_from_enter(self, instance):
        self.send_message(instance)
    
    def go_back(self, instance):
        self.manager.current = 'main'
        self.target_user = None

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = App.get_running_app().db
        self.current_tab = 'chats'
        
        layout = BoxLayout(orientation='vertical')
        
        # Header с брендом
        header = BoxLayout(size_hint_y=0.08, padding=5)
        self.header_label = Label(
            text='[b]Шилиграм[/b] - Мои чаты',
            size_hint_x=0.6,
            markup=True,
            color=(0.2, 0.6, 1, 1)
        )
        header.add_widget(self.header_label)
        
        search_btn = Button(
            text='🔍 Поиск',
            size_hint_x=0.2,
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        search_btn.bind(on_press=self.show_search)
        header.add_widget(search_btn)
        
        logout_btn = Button(
            text='Выйти',
            size_hint_x=0.2,
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        logout_btn.bind(on_press=self.logout)
        header.add_widget(logout_btn)
        
        layout.add_widget(header)
        
        # Content area
        self.content_layout = BoxLayout()
        
        # Chats tab
        self.chats_tab = BoxLayout(orientation='vertical')
        
        self.contacts_scroll = ScrollView()
        self.contacts_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=5
        )
        self.contacts_layout.bind(minimum_height=self.contacts_layout.setter('height'))
        self.contacts_scroll.add_widget(self.contacts_layout)
        self.chats_tab.add_widget(self.contacts_scroll)
        
        # Search tab
        self.search_tab = BoxLayout(orientation='vertical')
        
        search_input_layout = BoxLayout(size_hint_y=0.1, spacing=10, padding=10)
        self.search_input = TextInput(
            hint_text='Поиск пользователей Шилиграм...',
            multiline=False
        )
        self.search_input.bind(text=self.on_search_text)
        search_input_layout.add_widget(self.search_input)
        self.search_tab.add_widget(search_input_layout)
        
        self.search_results_scroll = ScrollView()
        self.search_results_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=5
        )
        self.search_results_layout.bind(minimum_height=self.search_results_layout.setter('height'))
        self.search_results_scroll.add_widget(self.search_results_layout)
        self.search_tab.add_widget(self.search_results_scroll)
        
        self.content_layout.add_widget(self.chats_tab)
        layout.add_widget(self.content_layout)
        
        self.add_widget(layout)
        
        Clock.schedule_interval(self.refresh_chats, 2)
    
    def on_enter(self):
        self.refresh_chats()
    
    def refresh_chats(self, dt=None):
        if self.current_tab == 'chats':
            self.load_contacts()
    
    def load_contacts(self):
        self.contacts_layout.clear_widgets()
        
        current_user = self.db.users.get(App.get_running_app().current_user)
        if not current_user:
            return
        
        if not current_user.contacts:
            no_contacts_label = Label(
                text='Нет контактов\nНайдите друзей через поиск!',
                text_size=(300, None),
                halign='center'
            )
            self.contacts_layout.add_widget(no_contacts_label)
            return
        
        for contact in current_user.contacts:
            btn = Button(
                text=f'💬 {contact}',
                size_hint_y=None,
                height=70,
                background_color=(0.9, 0.95, 1, 1),
                color=(0.2, 0.2, 0.2, 1)
            )
            btn.bind(on_press=lambda instance, username=contact: self.open_chat(username))
            self.contacts_layout.add_widget(btn)
    
    def on_search_text(self, instance, value):
        if value.strip():
            results = self.db.search_users(value.strip(), App.get_running_app().current_user)
            self.show_search_results(results)
        else:
            self.search_results_layout.clear_widgets()
    
    def show_search_results(self, results):
        self.search_results_layout.clear_widgets()
        
        if not results:
            no_results_label = Label(
                text='Пользователи не найдены',
                text_size=(300, None),
                halign='center'
            )
            self.search_results_layout.add_widget(no_results_label)
            return
        
        for username in results:
            user_layout = BoxLayout(size_hint_y=None, height=70, spacing=10, padding=10)
            
            username_label = Label(
                text=f'👤 {username}',
                size_hint_x=0.6,
                color=(0.2, 0.2, 0.2, 1)
            )
            user_layout.add_widget(username_label)
            
            add_btn = Button(
                text='Добавить',
                size_hint_x=0.4,
                background_color=(0.2, 0.6, 1, 1),
                color=(1, 1, 1, 1)
            )
            add_btn.bind(on_press=lambda instance, u=username: self.add_contact(u))
            user_layout.add_widget(add_btn)
            
            self.search_results_layout.add_widget(user_layout)
    
    def add_contact(self, username):
        success, message = self.db.add_contact(App.get_running_app().current_user, username)
        self.show_popup("Шилиграм", message)
        if success:
            self.search_input.text = ''
            self.show_chats_tab()
    
    def show_search(self, instance):
        if self.current_tab == 'search':
            self.show_chats_tab()
        else:
            self.show_search_tab()
    
    def show_chats_tab(self):
        self.current_tab = 'chats'
        self.header_label.text = '[b]Шилиграм[/b] - Мои чаты'
        self.content_layout.clear_widgets()
        self.content_layout.add_widget(self.chats_tab)
        self.refresh_chats()
    
    def show_search_tab(self):
        self.current_tab = 'search'
        self.header_label.text = '[b]Шилиграм[/b] - Поиск'
        self.content_layout.clear_widgets()
        self.content_layout.add_widget(self.search_tab)
        self.search_input.text = ''
        self.search_results_layout.clear_widgets()
    
    def open_chat(self, username):
        chat_screen = self.manager.get_screen('chat')
        chat_screen.set_target_user(username)
        self.manager.current = 'chat'
    
    def logout(self, instance):
        App.get_running_app().current_user = None
        self.manager.current = 'login'
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title, 
            content=Label(text=message), 
            size_hint=(0.8, 0.4),
            separator_color=(0.2, 0.6, 1, 1)
        )
        popup.open()

class ShiliGramApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.current_user = None
    
    def build(self):
        self.title = "Шилиграм - Мессенджер"
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ChatScreen(name='chat'))
        
        return sm

if __name__ == '__main__':
    ShiliGramApp().run()
