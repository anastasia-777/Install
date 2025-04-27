import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from database import Database
from ui_components_fixed import (
    ScrollableFrame, CalendarView, ChatView, Validators, ProfileView,
    JobListingView, ServiceListingView, RatingsView
)


class FreelanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FreeWorker")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        self.root.configure(bg='#d4dbe2')  # Основной цвет интерфейса

        # Настройка стилей
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Используем тему, поддерживающую кастомизацию

        # Конфигурация стилей
        self.style.configure('.', background='#d4dbe2', foreground='black')
        self.style.configure('TFrame', background='#d4dbe2')
        self.style.configure('TLabel', background='#d4dbe2', foreground='black')
        self.style.configure('TButton',
                             background='#ceb5ce',
                             foreground='black',
                             padding=6,
                             font=('TkDefaultFont', 10),
                             bordercolor='#9c8a9c',
                             relief='raised')

        self.style.map('TButton',
                       background=[('active', '#baa4ba'), ('pressed', '#a693a6')],
                       foreground=[('active', 'black'), ('pressed', 'black')])

        self.style.configure('TEntry',
                             fieldbackground='white',
                             foreground='black',
                             bordercolor='#d4dbe2',
                             insertcolor='black')

        self.style.configure('Treeview',
                             background='white',
                             fieldbackground='white',
                             foreground='black')

        self.style.configure('Treeview.Heading',
                             background='#d4dbe2',
                             foreground='black',
                             relief='raised')

        self.style.configure('TLabelframe',
                             background='#d4dbe2',
                             foreground='black')

        self.style.configure('TLabelframe.Label',
                             background='#d4dbe2',
                             foreground='black')

        # Добавляем обработчик изменения размера окна
        self.root.bind("<Configure>", self._check_window_position)

        # Инициализируем базу данных
        self.db = Database()

        # Текущие данные пользователя
        self.current_user = None

        # Создаем пользовательский интерфейс приложения
        self.create_ui()

        # Начинать с экрана входа в систему
        self.show_login_screen()

    def create_ui(self):
        # Основной контейнер
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # Контейнер для экранов авторизации (вход/регистрация)
        self.auth_container = ttk.Frame(self.main_container)

        # Контейнер для основного приложения (после входа в систему)
        self.app_container = ttk.Frame(self.main_container)

        # Боковая панель и области контента для основного приложения.
        self.sidebar = ttk.Frame(self.app_container, width=220)
        self.sidebar.pack_propagate(False)
        self.content = ttk.Frame(self.app_container)

        # Создание кнопки навигации
        self.nav_buttons = {}

    def show_login_screen(self):
        # Скрыть контейнер приложения и показать контейнер аутентификации
        self.app_container.pack_forget()
        self.auth_container.pack(fill="both", expand=True)

        # Очистим контейнер аутентификации
        for widget in self.auth_container.winfo_children():
            widget.destroy()

        # Создание формы входа
        frame = ttk.Frame(self.auth_container, padding=20)
        frame.pack(expand=True)

        # Добавляем отступы вверху
        ttk.Label(frame, text="").pack(pady=20)

        # Название приложения
        title = ttk.Label(frame, text="FreeWorker", font=("TkDefaultFont", 16, "bold"))
        title.pack(pady=10)

        subtitle = ttk.Label(frame, text="Войдите в свою учетную запись", font=("TkDefaultFont", 12))
        subtitle.pack(pady=(0, 20))

        # Имя пользователя
        username_frame = ttk.Frame(frame)
        username_frame.pack(fill="x", pady=5)
        username_label = ttk.Label(username_frame, text="Имя пользователя:", width=19, anchor="w")
        username_label.pack(side="left")
        self.username_entry = ttk.Entry(username_frame, width=30)
        self.username_entry.pack(side="left", padx=5)

        # Пароль
        password_frame = ttk.Frame(frame)
        password_frame.pack(fill="x", pady=5)
        password_label = ttk.Label(password_frame, text="Пароль:", width=19, anchor="w")
        password_label.pack(side="left")
        self.password_entry = ttk.Entry(password_frame, width=30, show="*")
        self.password_entry.pack(side="left", padx=5)

        # Кнопка входа
        login_btn = ttk.Button(frame, text="Войти", command=self.handle_login, width=20)
        login_btn.pack(pady=10)

        # Ссылка на регистрацию
        register_link = ttk.Label(
            frame,
            text="У вас нет учетной записи? Зарегистрируйтесь здесь",
            foreground="blue",
            cursor="hand2"
        )
        register_link.pack(pady=5)
        register_link.bind("<Button-1>", lambda e: self.show_register_screen())

    def show_register_screen(self):
        # Очистка контейнера аутентификации
        for widget in self.auth_container.winfo_children():
            widget.destroy()

        # Создание регистрационной формы
        frame = ttk.Frame(self.auth_container, padding=20)
        frame.pack(expand=True)

        # Название приложения
        title = ttk.Label(frame, text="FreeWorker", font=("TkDefaultFont", 16, "bold"))
        title.pack(pady=10)

        subtitle = ttk.Label(frame, text="Создать новый аккаунт", font=("TkDefaultFont", 12))
        subtitle.pack(pady=(0, 20))

        # Имя пользователя
        username_frame = ttk.Frame(frame)
        username_frame.pack(fill="x", pady=5)
        username_label = ttk.Label(username_frame, text="Имя пользователя:", width=25, anchor="w")
        username_label.pack(side="left")
        self.reg_username_entry = ttk.Entry(username_frame, width=30)
        self.reg_username_entry.pack(side="left", padx=5)

        # Пароль
        password_frame = ttk.Frame(frame)
        password_frame.pack(fill="x", pady=5)
        password_label = ttk.Label(password_frame, text="Пароль:", width=25, anchor="w")
        password_label.pack(side="left")
        self.reg_password_entry = ttk.Entry(password_frame, width=30, show="*")
        self.reg_password_entry.pack(side="left", padx=5)

        # Подтвердите пароль
        confirm_frame = ttk.Frame(frame)
        confirm_frame.pack(fill="x", pady=5)
        confirm_label = ttk.Label(confirm_frame, text="Подтвердить пароль:", width=25, anchor="w")
        confirm_label.pack(side="left")
        self.reg_confirm_entry = ttk.Entry(confirm_frame, width=30, show="*")
        self.reg_confirm_entry.pack(side="left", padx=5)

        # Номер телефона
        phone_frame = ttk.Frame(frame)
        phone_frame.pack(fill="x", pady=5)
        phone_label = ttk.Label(phone_frame, text="Номер телефона:", width=25, anchor="w")
        phone_label.pack(side="left")
        self.reg_phone_entry = ttk.Entry(phone_frame, width=30)
        self.reg_phone_entry.pack(side="left", padx=5)

        # Социальные сети
        social_frame = ttk.Frame(frame)
        social_frame.pack(fill="x", pady=5)
        social_label = ttk.Label(social_frame, text="Социальные сети:", width=25, anchor="w")
        social_label.pack(side="left")
        self.reg_social_entry = ttk.Entry(social_frame, width=30)
        self.reg_social_entry.pack(side="left", padx=5)

        # Тип пользователя
        type_frame = ttk.Frame(frame)
        type_frame.pack(fill="x", pady=5)
        type_label = ttk.Label(type_frame, text="Кто я:", width=25, anchor="w")
        type_label.pack(side="left")

        self.user_type_var = tk.StringVar(value="freelancer")
        freelancer_radio = ttk.Radiobutton(
            type_frame, text="Фрилансер", variable=self.user_type_var, value="freelancer"
        )
        freelancer_radio.pack(side="left", padx=(0, 10))

        client_radio = ttk.Radiobutton(
            type_frame, text="Клиент", variable=self.user_type_var, value="client"
        )
        client_radio.pack(side="left")

        # Специальность (для фрилансера)
        specialty_frame = ttk.Frame(frame)
        specialty_frame.pack(fill="x", pady=5)
        specialty_label = ttk.Label(specialty_frame, text="Специальность:", width=25, anchor="w")
        specialty_label.pack(side="left")
        self.reg_specialty_entry = ttk.Entry(specialty_frame, width=30)
        self.reg_specialty_entry.pack(side="left", padx=5)

        # Кнопка регистрации
        register_btn = ttk.Button(frame, text="Зарегистрироваться", command=self.handle_registration, width=20)
        register_btn.pack(pady=10)

        # Ссылка для входа
        login_link = ttk.Label(
            frame,
            text="У вас уже есть аккаунт? Войти здесь",
            foreground="blue",
            cursor="hand2"
        )
        login_link.pack(pady=5)
        login_link.bind("<Button-1>", lambda e: self.show_login_screen())

    def handle_login(self):
        """Обработка отправки формы входа."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Проверка входных данных
        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, введите имя пользователя и пароль")
            return

        # Попытка аутентификации
        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.show_main_app()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")

    def handle_registration(self):
        """Обработка отправки регистрационной формы."""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()
        phone = self.reg_phone_entry.get().strip()
        social = self.reg_social_entry.get().strip()
        user_type = self.user_type_var.get()
        specialty = self.reg_specialty_entry.get().strip()

        # Проверка входных данных
        valid_username, username_msg = Validators.validate_username(username)
        if not valid_username:
            messagebox.showerror("Ошибка", username_msg)
            return

        valid_password, password_msg = Validators.validate_password(password)
        if not valid_password:
            messagebox.showerror("Ошибка", password_msg)
            return

        if password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        valid_phone, phone_msg = Validators.validate_phone(phone)
        if not valid_phone:
            messagebox.showerror("Ошибка", phone_msg)
            return

        # Проверка существования имени пользователя
        if self.db.is_username_taken(username):
            messagebox.showerror("Ошибка", "Имя пользователя уже существует. Пожалуйста, введите другое имя")
            return

        # Зарегистрируйте пользователя
        success = self.db.register_user(
            username, password, phone, social, user_type, specialty
        )

        if success:
            messagebox.showinfo("Успех", "Регистрация прошла успешно! Теперь вы можете войти.")
            self.show_login_screen()
        else:
            messagebox.showerror("Ошибка", "Не удалось зарегистрироваться. Пожалуйста, попробуйте еще раз.")

    def _check_window_position(self, event=None):
        """Проверяет, чтобы окно не выходило за пределы экрана"""
        if not self.root.winfo_viewable():
            return

        # Получаем размеры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Получаем текущие размеры и положение окна
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        # Корректируем положение, если окно выходит за границы
        new_x = max(0, min(x, screen_width - window_width))
        new_y = max(0, min(y, screen_height - window_height))

        if x != new_x or y != new_y:
            self.root.geometry(f"+{new_x}+{new_y}")

    def _position_dialog(self, dialog):
        dialog.configure(bg='#6b8e9e')
        """Позиционирует диалоговое окно относительно главного окна"""
        if not self.root.winfo_viewable():
            return

        # Получаем размеры главного окна
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # Получаем размеры диалогового окна
        dialog.update_idletasks()  # Обновляем геометрию окна
        width = dialog.winfo_width()
        height = dialog.winfo_height()

        # Вычисляем положение по центру главного окна
        x = root_x + (root_width - width) // 2
        y = root_y + (root_height - height) // 2

        # Проверяем, чтобы не выходило за границы экрана
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()

        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))

        dialog.geometry(f"+{x}+{y}")

    def show_main_app(self):
        # Скрыть контейнер аутентификации и показать контейнер приложения
        self.auth_container.pack_forget()
        self.app_container.pack(fill="both", expand=True)

        # Настройка боковой панели и области контента
        self.sidebar.pack(side="left", fill="y")
        self.content.pack(side="right", fill="both", expand=True)
        # Настройка цвета разделителей
        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", pady=10)
        self.style.configure('TSeparator', background='#5a7a8c')
        # Очистить боковую панель и контент
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        for widget in self.content.winfo_children():
            widget.destroy()

        # Добавляем информацию о пользователе на боковую панель
        user_frame = ttk.Frame(self.sidebar, padding=10)
        user_frame.pack(fill="x")

        username_label = ttk.Label(
            user_frame,
            text=f"Здравствуйте, {self.current_user['username']}",
            font=("TkDefaultFont", 12, "bold"),
            wraplength=180
        )
        username_label.pack(fill="x", pady=5)

        user_type = self.current_user['user_type'].capitalize()
        type_label = ttk.Label(user_frame, text=f"Роль: {user_type}")
        type_label.pack(fill="x")

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", pady=10)

        # Создать меню навигации на основе типа пользователя
        self.create_navigation()

        # Показать панель инструментов по умолчанию
        self.show_dashboard()

    def create_navigation(self):
        nav_frame = ttk.Frame(self.sidebar, padding=5)
        nav_frame.pack(fill="x")

        # Общие пункты меню для обоих типов пользователей
        menu_items = [
            ("Панель информации", self.show_dashboard),
            ("Профиль", self.show_profile),
            ("Сообщения", self.show_messaging)
        ]

        # Добавляем пункты меню, специфичные для пользователя
        if self.current_user['user_type'] == 'freelancer':
            menu_items.extend([
                ("Мои услуги", self.show_freelancer_services),
                ("Доступные вакансии", self.show_available_jobs),
                ("Мои работы", self.show_freelancer_jobs),
                ("Календарь занятости", self.show_availability_calendar)
            ])
        else:  # клиент
            menu_items.extend([
                ("Мои опубликованные вакансии", self.show_client_jobs),
                ("Поиск фрилансеров", self.show_find_freelancers)
            ])

        # Добавляем выход в конце
        menu_items.append(("Выход", self.handle_logout))

        # Создание кнопки
        for i, (text, command) in enumerate(menu_items):
            btn = ttk.Button(nav_frame, text=text, command=command, width=25)
            btn.pack(fill="x", pady=2)
            self.nav_buttons[text] = btn

    def highlight_active_nav(self, active_item):
        """Выделить активный элемент навигации."""
        try:
            for text, btn in self.nav_buttons.items():
                if text == active_item:
                    btn.state(['pressed'])
                else:
                    btn.state(['!pressed'])
        except Exception:
            # Игнорируем ошибки, если кнопка уже не существует
            pass

    def clear_content(self):
        """Очистите область содержимого."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def handle_logout(self):
        """Выйти из текущего пользователя."""
        self.current_user = None
        self.app_container.pack_forget()
        self.show_login_screen()

    def show_dashboard(self):
        """Показать панель управления/главный экран."""
        self.clear_content()
        self.highlight_active_nav("Dashboard")

        # Создание содержимого панели мониторинга
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Панель информации",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Содержимое информационной панели в зависимости от типа пользователя
        if self.current_user['user_type'] == 'freelancer':
            self.show_freelancer_dashboard(frame)
        else:
            self.show_client_dashboard(frame)

    def show_freelancer_dashboard(self, parent_frame):
        """Показать содержимое информационной панели фрилансера."""
        # Обзор статистики
        stats_frame = ttk.LabelFrame(parent_frame, text="Важная информация", padding=10)
        stats_frame.pack(fill="x", pady=10)

        # Получить текущее количество вакансий
        current_jobs = self.db.get_freelancer_jobs(self.current_user['id'])
        active_jobs = sum(1 for job in current_jobs if job['status'] == 'assigned')

        # Получить средний рейтинг
        avg_rating = self.db.get_average_rating(self.current_user['id'])
        if avg_rating is None:
            avg_rating = 0

        # Текущие вакансии
        job_frame = ttk.Frame(stats_frame)
        job_frame.pack(side="left", expand=True, fill="x", padx=10, pady=5)

        job_label = ttk.Label(job_frame, text="В работе", font=("TkDefaultFont", 11, "bold"))
        job_label.pack()

        job_count = ttk.Label(job_frame, text=str(active_jobs), font=("TkDefaultFont", 20))
        job_count.pack()

        # Средний рейтинг
        rating_frame = ttk.Frame(stats_frame)
        rating_frame.pack(side="left", expand=True, fill="x", padx=10, pady=5)

        rating_label = ttk.Label(rating_frame, text="Средний рейтинг", font=("TkDefaultFont", 11, "bold"))
        rating_label.pack()

        rating_val = ttk.Label(rating_frame, text=f"{avg_rating:.1f}/5.0", font=("TkDefaultFont", 20))
        rating_val.pack()

        # Быстрые действия
        quick_frame = ttk.LabelFrame(parent_frame, text="Быстрые действия", padding=10)
        quick_frame.pack(fill="x", pady=10)

        # Кнопка обновления занятости
        avail_btn = ttk.Button(
            quick_frame,
            text="Обновить занятость",
            command=self.show_availability_calendar
        )
        avail_btn.pack(side="left", padx=10, pady=5)

        # Просмотреть доступные вакансии
        jobs_btn = ttk.Button(
            quick_frame,
            text="Просмотреть доступные вакансии",
            command=self.show_available_jobs
        )
        jobs_btn.pack(side="left", padx=10, pady=5)

        # Управление услугами
        services_btn = ttk.Button(
            quick_frame,
            text="Управлять услугами",
            command=self.show_freelancer_services
        )
        services_btn.pack(side="left", padx=10, pady=5)

        # Недавняя активность — показать несколько недавних вакансий.
        recent_frame = ttk.LabelFrame(parent_frame, text="Недавние вакансии", padding=10)
        recent_frame.pack(fill="both", expand=True, pady=10)

        if not current_jobs:
            no_jobs = ttk.Label(recent_frame, text="У вас пока нет вакансий.")
            no_jobs.pack(pady=20)
        else:
            # Показать последние 3 вакансии
            for job in current_jobs[:3]:
                job_item = ttk.Frame(recent_frame, padding=5)
                job_item.pack(fill="x", pady=2)

                job_title = ttk.Label(
                    job_item,
                    text=job['title'],
                    font=("TkDefaultFont", 11, "bold")
                )
                job_title.pack(side="left")

                status_translation = {
                    "Open": "Открыта",
                    "Assigned": "Назначена",
                    "Completed": "Завершена"
                }

                status_text = status_translation.get(job['status'].capitalize(), job['status'])
                status_colors = {
                    "Открыта": "green",
                    "Назначена": "orange",
                    "Завершена": "blue"
                }
                status_color = status_colors.get(status_text, "black")

                status = ttk.Label(job_item, text=f"Статус: {status_text}", foreground=status_color)
                status.pack(side="right")

                ttk.Separator(recent_frame, orient="horizontal").pack(fill="x", pady=2)

            view_all = ttk.Button(
                recent_frame,
                text="Просмотреть все вакансии",
                command=self.show_freelancer_jobs
            )
            view_all.pack(pady=10)

    def show_client_dashboard(self, parent_frame):
        """Показать содержимое панели управления клиента."""
        # Обзор статистики
        stats_frame = ttk.LabelFrame(parent_frame, text="Важная информация", padding=10)
        stats_frame.pack(fill="x", pady=10)

        # Получить статистику вакансий
        client_jobs = self.db.get_client_jobs(self.current_user['id'])
        open_jobs = sum(1 for job in client_jobs if job['status'] == 'open')
        in_progress = sum(1 for job in client_jobs if job['status'] == 'assigned')
        completed = sum(1 for job in client_jobs if job['status'] == 'completed')

        # Открытые вакансии
        open_frame = ttk.Frame(stats_frame)
        open_frame.pack(side="left", expand=True, fill="x", padx=10, pady=5)

        open_label = ttk.Label(open_frame, text="Доступные вакансии", font=("TkDefaultFont", 11, "bold"))
        open_label.pack()

        open_count = ttk.Label(open_frame, text=str(open_jobs), font=("TkDefaultFont", 20))
        open_count.pack()

        # В работе
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(side="left", expand=True, fill="x", padx=10, pady=5)

        progress_label = ttk.Label(progress_frame, text="В ходе выполнения", font=("TkDefaultFont", 11, "bold"))
        progress_label.pack()

        progress_count = ttk.Label(progress_frame, text=str(in_progress), font=("TkDefaultFont", 20))
        progress_count.pack()

        # Завершенных работ
        completed_frame = ttk.Frame(stats_frame)
        completed_frame.pack(side="left", expand=True, fill="x", padx=10, pady=5)

        completed_label = ttk.Label(completed_frame, text="Завершенные", font=("TkDefaultFont", 11, "bold"))
        completed_label.pack()

        completed_count = ttk.Label(completed_frame, text=str(completed), font=("TkDefaultFont", 20))
        completed_count.pack()

        # Быстрые действия
        quick_frame = ttk.LabelFrame(parent_frame, text="Быстрые действия", padding=10)
        quick_frame.pack(fill="x", pady=10)

        # Кнопка публикации новой вакансии
        post_btn = ttk.Button(
            quick_frame,
            text="Создать новую вакансию",
            command=self.show_post_job_dialog
        )
        post_btn.pack(side="left", padx=10, pady=5)

        # Поиск фрилансеров
        find_btn = ttk.Button(
            quick_frame,
            text="Поиск фрилансеров",
            command=self.show_find_freelancers
        )
        find_btn.pack(side="left", padx=10, pady=5)

        # Управление заданиями
        manage_btn = ttk.Button(
            quick_frame,
            text="Управление вакансиями",
            command=self.show_client_jobs
        )
        manage_btn.pack(side="left", padx=10, pady=5)

        # Недавняя активность — показать несколько недавних вакансий.
        recent_frame = ttk.LabelFrame(parent_frame, text="Недавние вакансии", padding=10)
        recent_frame.pack(fill="both", expand=True, pady=10)

        if not client_jobs:
            no_jobs = ttk.Label(recent_frame, text="Вы еще не разместили ни одной вакансии.")
            no_jobs.pack(pady=20)
        else:
            # Показать последние 3 вакансии
            for job in client_jobs[:3]:
                job_item = ttk.Frame(recent_frame, padding=5)
                job_item.pack(fill="x", pady=2)

                job_title = ttk.Label(
                    job_item,
                    text=job['title'],
                    font=("TkDefaultFont", 11, "bold")
                )
                job_title.pack(side="left")

                status_translation = {
                    "Open": "Открыта",
                    "Assigned": "Назначена",
                    "Completed": "Завершена"
                }

                status_text = status_translation.get(job['status'].capitalize(), job['status'])
                status_colors = {
                    "Открыта": "green",
                    "Назначена": "orange",
                    "Завершена": "blue"
                }
                status_color = status_colors.get(status_text, "black")

                status = ttk.Label(job_item, text=f"Статус: {status_text}", foreground=status_color)
                status.pack(side="right")

                ttk.Separator(recent_frame, orient="horizontal").pack(fill="x", pady=2)

            view_all = ttk.Button(
                recent_frame,
                text="Просмотреть все вакансии",
                command=self.show_client_jobs
            )
            view_all.pack(pady=10)

    def show_profile(self):
        """Показать экран профиля пользователя."""
        self.clear_content()
        self.highlight_active_nav("Profile")

        # Создать контент профиля
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Просмотр профиля
        profile_view = ProfileView(
            frame,
            self.current_user,
            is_own_profile=True
        )
        profile_view.pack(fill="x", pady=10)

        # Если пользователь фрилансер, показывать рейтинги и услуги
        if self.current_user['user_type'] == 'freelancer':
            # Получайте рейтинги
            ratings = self.db.get_freelancer_ratings(self.current_user['id'])
            avg_rating = self.db.get_average_rating(self.current_user['id'])

            # Раздел рейтингов
            ratings_view = RatingsView(frame, ratings, avg_rating)
            ratings_view.pack(fill="both", expand=True, pady=10)

    def show_messaging(self):
        """Показать экран сообщений/чата."""
        self.clear_content()
        self.highlight_active_nav("Messaging")

        # Создать контент для обмена сообщениямиt
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Сообщения",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Просмотр чата
        chat_view = ChatView(
            frame,
            user_id=self.current_user['id'],
            get_messages_callback=self.db.get_messages,
            send_message_callback=self.db.send_message,
            get_users_callback=self.db.get_conversations,
            delete_chat_callback=self.db.delete_conversation
        )
        chat_view.pack(fill="both", expand=True)

    def show_freelancer_services(self):
        """Показать экран услуг фрилансера."""
        self.clear_content()
        self.highlight_active_nav("My Services")

        # Создание контента услуг
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Мои услуги",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Получить услуги
        services = self.db.get_freelancer_services(self.current_user['id'])

        # Список услуг
        services_view = ServiceListingView(
            frame,
            services_data=services,
            is_own_services=True,
            on_create=self.show_create_service_dialog,
            on_edit=self.show_edit_service_dialog,
            on_delete=self.handle_delete_service
        )
        services_view.pack(fill="both", expand=True)

    def show_create_service_dialog(self):
        """Показать диалог для создания новой услуги."""
        # Создаем окно верхнего уровня
        dialog = tk.Toplevel(self.root)
        dialog.title("Создание новой услуги")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        # Позиционируем окно
        self._position_dialog(dialog)
        # Создать форму
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill="x", pady=10)
        title_label = ttk.Label(title_frame, text="Название услуги:", width=20, anchor="w")
        title_label.pack(side="left")
        title_entry = ttk.Entry(title_frame, width=40)
        title_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Описание
        desc_frame = ttk.Frame(frame)
        desc_frame.pack(fill="x", pady=10)
        desc_label = ttk.Label(desc_frame, text="Описание:", width=20, anchor="nw")
        desc_label.pack(side="left", anchor="n")
        desc_text = tk.Text(desc_frame, width=40, height=10)
        desc_text.pack(side="left", fill="both", expand=True, padx=5)

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Отмена",
            command=dialog.destroy
        )
        cancel_btn.pack(side="right", padx=5)

        def save_service():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", "end-1c").strip()

            # Подтвердить
            if not title or not description:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля", parent=dialog)
                return

            # Сохранить услугу
            service_id = self.db.add_service(
                self.current_user['id'], title, description
            )

            if service_id:
                messagebox.showinfo("Успех", "Услуга успешно добавлена", parent=dialog)
                dialog.destroy()
                # Refresh services view
                self.show_freelancer_services()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить услугу", parent=dialog)

        save_btn = ttk.Button(
            btn_frame,
            text="Сохранить",
            command=save_service
        )
        save_btn.pack(side="right", padx=5)

    def show_edit_service_dialog(self, service):
        """Показать диалог для редактирования существующей услуги."""
        # Создаем окно верхнего уровня
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование услуги")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        # Позиционируем окно
        self._position_dialog(dialog)
        # Создание формы
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill="x", pady=10)
        title_label = ttk.Label(title_frame, text="Название услуги:", width=20, anchor="w")
        title_label.pack(side="left")
        title_entry = ttk.Entry(title_frame, width=40)
        title_entry.insert(0, service['title'])
        title_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Описание
        desc_frame = ttk.Frame(frame)
        desc_frame.pack(fill="x", pady=10)
        desc_label = ttk.Label(desc_frame, text="Описание:", width=20, anchor="nw")
        desc_label.pack(side="left", anchor="n")
        desc_text = tk.Text(desc_frame, width=40, height=10)
        desc_text.insert("1.0", service['description'])
        desc_text.pack(side="left", fill="both", expand=True, padx=5)

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Отмена",
            command=dialog.destroy
        )
        cancel_btn.pack(side="right", padx=5)

        def update_service():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", "end-1c").strip()

            # Подтвердить
            if not title or not description:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля", parent=dialog)
                return

            # Сохранить услугу
            success = self.db.update_service(
                service['id'], title, description
            )

            if success:
                messagebox.showinfo("Успех", "Услуга успешно добавлена", parent=dialog)
                dialog.destroy()
                # Обновить вид услуг
                self.show_freelancer_services()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить услугу", parent=dialog)

        save_btn = ttk.Button(
            btn_frame,
            text="Сохранить",
            command=update_service
        )
        save_btn.pack(side="right", padx=5)

    def handle_delete_service(self, service):
        """Обработка удаления службы."""
        # Подтверждаем удаление
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить '{service['title']}'?"):
            success = self.db.delete_service(service['id'])

            if success:
                messagebox.showinfo("Успех", "Услуга успешно удалена")
                # Обновить вид услуг
                self.show_freelancer_services()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить услугу")

    def show_available_jobs(self):
        """Показать доступные вакансии для фрилансеров."""
        self.clear_content()
        self.highlight_active_nav("Available Jobs")

        # Создание контента о вакансиях
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Доступные вакансии",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Получите открытые вакансии
        jobs = self.db.get_open_jobs()

        # Списки вакансий
        job_view = JobListingView(
            frame,
            jobs_data=jobs,
            is_client=False,
            user_id=self.current_user['id'],
            on_assign=self.handle_apply_for_job,
            on_view_details=self.show_job_details
        )
        job_view.pack(fill="both", expand=True)

    def handle_apply_for_job(self, job):
        """Обработка отклика на вакансии."""
        if messagebox.askyesno("Подтверждение", f"Откликнуться на вакансию: '{job['title']}'?"):
            success = self.db.assign_job(job['id'], self.current_user['id'])

            if success:
                messagebox.showinfo("Успех", "Вы успешно откликнулись на вакансию")
                # Обновить просмотр вакансий
                self.show_available_jobs()
            else:
                messagebox.showerror("Ошибка", "Не удалось откликнуться на вакансию")

    def show_freelancer_jobs(self):
        """Показать задания, назначенные фрилансеру."""
        self.clear_content()
        self.highlight_active_nav("My Jobs")

        # Создание контента о вакансиях
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Мои работы",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Получите работу фрилансера
        jobs = self.db.get_freelancer_jobs(self.current_user['id'])

        # Списки вакансий
        job_view = JobListingView(
            frame,
            jobs_data=jobs,
            is_client=False,
            user_id=self.current_user['id'],
            on_view_details=self.show_job_details
        )
        job_view.pack(fill="both", expand=True)

    def show_availability_calendar(self):
        """Показывать календарь доступности фрилансеров и управлять им."""
        self.clear_content()
        self.highlight_active_nav("Availability Calendar")

        # Создание содержимого календаря
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Календарь занятости",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Инструкция
        instructions = ttk.Label(
            frame,
            text="Нажмите на день, чтобы указать доступность. Это будет видно клиентам."
        )
        instructions.pack(pady=(0, 10))

        # Получить данные о доступности
        availability = self.db.get_freelancer_availability(self.current_user['id'])

        # Просмотр календаря
        self.calendar_view = CalendarView(
            frame,
            freelancer_id=self.current_user['id'],
            availability_data=availability,
            callback=self.show_availability_dialog
        )
        self.calendar_view.pack(fill="both", expand=True)


    def show_availability_dialog(self, date):
        """Показать диалог, чтобы установить доступность на определенную дату."""
        # Создаем окно верхнего уровня
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Установка занятости - {date.strftime('%Y-%m-%d')}")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        # Позиционируем окно
        self._position_dialog(dialog)
        # Проверьте, есть ли свободные места на эту дату
        existing = None
        availability = self.db.get_freelancer_availability(self.current_user['id'])
        for avail in availability:
            start = datetime.datetime.strptime(avail["start_date"], "%Y-%m-%d").date()
            end = datetime.datetime.strptime(avail["end_date"], "%Y-%m-%d").date()
            if start <= date <= end:
                existing = avail
                break

        # Создать форму
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Диапазон дат
        date_frame = ttk.Frame(frame)
        date_frame.pack(fill="x", pady=10)

        from_label = ttk.Label(date_frame, text="Начало периода:", width=20, anchor="w")
        from_label.pack(side="left")

        from_var = tk.StringVar(value=date.strftime("%Y-%m-%d"))
        from_entry = ttk.Entry(date_frame, textvariable=from_var, width=15)
        from_entry.pack(side="left", padx=5)

        to_label = ttk.Label(date_frame, text="Конец периода:", width=20, anchor="w")
        to_label.pack(side="left", padx=(10, 0))

        # Дата окончания по умолчанию совпадает с датой начала
        to_var = tk.StringVar(value=date.strftime("%Y-%m-%d"))
        to_entry = ttk.Entry(date_frame, textvariable=to_var, width=15)
        to_entry.pack(side="left", padx=5)

        # Если данные уже существуют, предварительно заполните
        if existing:
            from_var.set(existing["start_date"])
            to_var.set(existing["end_date"])

        # Сложность
        complexity_frame = ttk.Frame(frame)
        complexity_frame.pack(fill="x", pady=10)

        complexity_label = ttk.Label(complexity_frame, text="Сложность:", width=20, anchor="w")
        complexity_label.pack(side="left")

        complexity_var = tk.StringVar(value="medium")
        if existing:
            complexity_var.set(existing["complexity"].lower())

        low_radio = ttk.Radiobutton(
            complexity_frame, text="Низкая", variable=complexity_var, value="low"
        )
        low_radio.pack(side="left", padx=(0, 10))

        medium_radio = ttk.Radiobutton(
            complexity_frame, text="Средняя", variable=complexity_var, value="medium"
        )
        medium_radio.pack(side="left", padx=(0, 10))

        high_radio = ttk.Radiobutton(
            complexity_frame, text="Высокая", variable=complexity_var, value="high"
        )
        high_radio.pack(side="left")

        # Занятость
        avail_frame = ttk.Frame(frame)
        avail_frame.pack(fill="x", pady=10)

        avail_label = ttk.Label(avail_frame, text="Доступен для заказов:", width=20, anchor="w")
        avail_label.pack(side="left")

        can_accept_var = tk.BooleanVar(value=False)
        if existing:
            can_accept_var.set(bool(existing["can_accept_more"]))

        can_accept_check = ttk.Checkbutton(avail_frame, variable=can_accept_var)
        can_accept_check.pack(side="left")

        # Примечание
        note_frame = ttk.Frame(frame)
        note_frame.pack(fill="x", pady=10)

        note_label = ttk.Label(note_frame, text="Примечание:", width=20, anchor="nw")
        note_label.pack(side="left", anchor="n")

        note_text = tk.Text(note_frame, width=40, height=5)
        if existing and existing["note"]:
            note_text.insert("1.0", existing["note"])
        note_text.pack(side="left", fill="x", expand=True, padx=5)

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Отмена",
            command=dialog.destroy
        )
        cancel_btn.pack(side="right", padx=5)

        def save_availability():
            try:
                start_date = from_var.get()
                end_date = to_var.get()
                complexity = complexity_var.get()
                can_accept_more = can_accept_var.get()
                note = note_text.get("1.0", "end-1c").strip()

                # Подтвердить даты
                try:
                    datetime.datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД", parent=dialog)
                    return

                if existing:
                    # Обновить существующие
                    success = self.db.update_availability(
                        existing["id"], start_date, end_date, complexity,
                        can_accept_more, note
                    )
                else:
                    # Создать новые
                    avail_id = self.db.add_availability(
                        self.current_user['id'], start_date, end_date,
                        complexity, can_accept_more, note
                    )
                    success = avail_id is not None

                if success:
                    messagebox.showinfo("Успех", "Занятость обновлена", parent=dialog)
                    dialog.destroy()

                    # Обновить календарь
                    availability = self.db.get_freelancer_availability(self.current_user['id'])
                    self.calendar_view.set_availability_data(availability)
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить занятость.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}", parent=dialog)

        save_btn = ttk.Button(
            btn_frame,
            text="Сохранить",
            command=save_availability
        )
        save_btn.pack(side="right", padx=5)

        # Добавить кнопку удаления при редактировании существующих
        if existing:
            def delete_availability():
                if messagebox.askyesno("Подтверждение", "Удалить этот период занятости?", parent=dialog):
                    success = self.db.delete_availability(existing["id"])

                    if success:
                        messagebox.showinfo("Успех", "Занятость удалена", parent=dialog)
                        dialog.destroy()

                        # Обновить календарь
                        availability = self.db.get_freelancer_availability(self.current_user['id'])
                        self.calendar_view.set_availability_data(availability)
                    else:
                        messagebox.showerror("Ошибка", "Не удалось удалить занятость.", parent=dialog)

            delete_btn = ttk.Button(
                btn_frame,
                text="Удалить",
                command=delete_availability
            )
            delete_btn.pack(side="left")

    def show_client_jobs(self):
        """Показать вакансии, опубликованные клиентом."""
        self.clear_content()
        self.highlight_active_nav("My Posted Jobs")

        # Создание контента о вакансиях
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Мои опубликованные вакансии",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Получите работу клиента
        jobs = self.db.get_client_jobs(self.current_user['id'])

        # Списки вакансий
        job_view = JobListingView(
            frame,
            jobs_data=jobs,
            is_client=True,
            user_id=self.current_user['id'],
            on_create=self.show_post_job_dialog,
            on_edit=self.show_edit_job_dialog,
            on_delete=self.handle_delete_job,
            on_complete=self.handle_complete_job,
            on_view_details=self.show_job_details
        )
        job_view.pack(fill="both", expand=True)

    def show_post_job_dialog(self):
        """Показать диалог для публикации новой вакансии."""
        # Создаем окно верхнего уровня
        dialog = tk.Toplevel(self.root)
        dialog.title("Опубликовать новую вакансию")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        # Позиционируем диалоговое окно
        self._position_dialog(dialog)

        # Создание формы
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill="x", pady=10)
        title_label = ttk.Label(title_frame, text="Название вакансии:", width=20, anchor="w")
        title_label.pack(side="left")
        title_entry = ttk.Entry(title_frame, width=50)
        title_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Описание
        desc_frame = ttk.Frame(frame)
        desc_frame.pack(fill="both", expand=True, pady=10)
        desc_label = ttk.Label(desc_frame, text="Описание:", width=20, anchor="nw")
        desc_label.pack(side="left", anchor="n")
        desc_text = tk.Text(desc_frame, width=50, height=15)
        desc_text.pack(side="left", fill="both", expand=True, padx=5)

        #Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Отмена",
            command=dialog.destroy
        )
        cancel_btn.pack(side="right", padx=5)

        def post_job():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", "end-1c").strip()

            # Подтвердить
            if not title or not description:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля", parent=dialog)
                return

            # Опубликовать вакансию
            job_id = self.db.add_job(
                title, description, self.current_user['id']
            )

            if job_id:
                messagebox.showinfo("Успех", "Вакансия успешно опубликована", parent=dialog)
                dialog.destroy()
                # Обновить просмотр вакансий
                self.show_client_jobs()
            else:
                messagebox.showerror("Ошибка", "Не удалось опубликовать вакансию", parent=dialog)

        post_btn = ttk.Button(
            btn_frame,
            text="Опубликовать вакансию",
            command=post_job
        )
        post_btn.pack(side="right", padx=5)

    def show_edit_job_dialog(self, job):
        """Показать диалог для редактирования существующего задания."""
        # Создаем окно верхнего уровня
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать вакансию")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        # Позиционируем окно
        self._position_dialog(dialog)
        # Создание формы
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill="x", pady=10)
        title_label = ttk.Label(title_frame, text="Название вакансии:", width=20, anchor="w")
        title_label.pack(side="left")
        title_entry = ttk.Entry(title_frame, width=50)
        title_entry.insert(0, job['title'])
        title_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Описание
        desc_frame = ttk.Frame(frame)
        desc_frame.pack(fill="both", expand=True, pady=10)
        desc_label = ttk.Label(desc_frame, text="Описание:", width=20, anchor="nw")
        desc_label.pack(side="left", anchor="n")
        desc_text = tk.Text(desc_frame, width=50, height=15)
        desc_text.insert("1.0", job['description'])
        desc_text.pack(side="left", fill="both", expand=True, padx=5)

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Отмена",
            command=dialog.destroy
        )
        cancel_btn.pack(side="right", padx=5)

        def update_job():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", "end-1c").strip()

            # Подтвердить
            if not title or not description:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля", parent=dialog)
                return

            # Обновить вакансию
            success = self.db.update_job(
                job['id'], title, description
            )

            if success:
                messagebox.showinfo("Успех", "Вакансия успешно обновлена", parent=dialog)
                dialog.destroy()
                # Обновить просмотр вакансий
                self.show_client_jobs()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить вакансию", parent=dialog)

        save_btn = ttk.Button(
            btn_frame,
            text="Сохранить изменения",
            command=update_job
        )
        save_btn.pack(side="right", padx=5)

    def handle_delete_job(self, job):
        """Обработка удаления вакансии."""
        # Подтверждаем удаление
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить вакансию? '{job['title']}'?"):
            success = self.db.delete_job(job['id'])

            if success:
                messagebox.showinfo("Успех", "Вакансия успешно удалена")
                # Обновить просмотр вакансий
                self.show_client_jobs()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить задание")

    def handle_complete_job(self, job):
        """Обработка отметки вакансии как завершенной и запроса оценки."""
        # Подтверждаем завершение
        if messagebox.askyesno("Подтверждение", f"Отметить работу '{job['title']}' как завершенную?"):
            # Показать диалог оценки
            self.show_rating_dialog(job)

    def show_rating_dialog(self, job):
        """Показать диалог для оценки фрилансера после завершения работы."""
        # Создаем окно верхнего уровня
        dialog = tk.Toplevel(self.root)
        dialog.title("Оценить Фрилансера")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        # Позиционируем окно
        self._position_dialog(dialog)

        # Получите информацию о фрилансере
        freelancer = self.db.get_user_by_id(job['freelancer_id'])

        if not freelancer:
            messagebox.showerror("Ошибка", "Информация о фрилансере не найдена", parent=dialog)
            dialog.destroy()
            return

        # Создание формы
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text=f"Оценить фрилансера {freelancer['username']}",
            font=("TkDefaultFont", 14, "bold")
        )
        header.pack(pady=(0, 20))

        job_title = ttk.Label(
            frame,
            text=f"Работа: {job['title']}",
            font=("TkDefaultFont", 10, "italic")
        )
        job_title.pack(pady=(0, 10))

        # Рейтинг
        rating_frame = ttk.Frame(frame)
        rating_frame.pack(fill="x", pady=10)

        rating_label = ttk.Label(rating_frame, text="Рейтинг:", width=10, anchor="w")
        rating_label.pack(side="left")

        rating_var = tk.IntVar(value=5)
        for i in range(1, 6):
            ttk.Radiobutton(
                rating_frame,
                text=str(i),
                variable=rating_var,
                value=i
            ).pack(side="left", padx=10)

        # Отзыв
        review_frame = ttk.Frame(frame)
        review_frame.pack(fill="x", pady=10)

        review_label = ttk.Label(review_frame, text="Отзыв:", width=10, anchor="nw")
        review_label.pack(side="left", anchor="n")

        review_text = tk.Text(review_frame, width=40, height=5)
        review_text.pack(side="left", fill="x", expand=True, padx=5)

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Отмена",
            command=dialog.destroy
        )
        cancel_btn.pack(side="right", padx=5)

        def submit_rating():
            rating = rating_var.get()
            review = review_text.get("1.0", "end-1c").strip()

            # Добавить оценку
            success_rating = self.db.add_rating(
                self.current_user['id'], freelancer['id'], job['id'],
                rating, review
            )

            # Завершить задание
            success_job = self.db.complete_job(job['id'])

            if success_rating and success_job:
                messagebox.showinfo(
                    "Успех",
                    "Работа отмечена как завершенная, оценка отправлена.",
                    parent=dialog
                )
                dialog.destroy()
                # Обновить просмотр вакансий
                self.show_client_jobs()
            else:
                message = ""
                if not success_rating:
                    message += "Не удалось отправить оценку."
                if not success_job:
                    message += "Не удалось завершить задание."
                messagebox.showerror("Ошибка", message, parent=dialog)

        submit_btn = ttk.Button(
            btn_frame,
            text="Отправить оценку",
            command=submit_rating
        )
        submit_btn.pack(side="right", padx=5)

    def show_job_details(self, job):
        """Показать подробное представление о задании."""
        # Создаем окно верхнего уровня
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Детали работы: {job['title']}")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        # Позиционируем окно
        self._position_dialog(dialog)
        # Создание контента
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Название работы
        title = ttk.Label(
            frame,
            text=job['title'],
            font=("TkDefaultFont", 16, "bold"),
            wraplength=550
        )
        title.pack(fill="x", pady=(0, 10))

        # Статус
        status_translation = {
            "Open": "Открыта",
            "Assigned": "Назначена",
            "Completed": "Завершена"
        }

        status_text = status_translation.get(job['status'].capitalize(), job['status'])
        status_colors = {
             "Открыта": "green",
             "Назначена": "orange",
             "Завершена": "blue"
        }
        status_color = status_colors.get(status_text, "black")

        status = ttk.Label(
            frame,
            text=f"Статус: {status_text}",
            foreground=status_color,
            font=("TkDefaultFont", 10, "bold")
        )
        status.pack(fill="x")

        # Даты
        dates_frame = ttk.Frame(frame)
        dates_frame.pack(fill="x", pady=5)

        created_date = job['created_at'].split(' ')[0] # Просто получить часть даты
        created = ttk.Label(dates_frame, text=f"Создано: {created_date}")
        created.pack(side="left")

        if job['updated_at'] != job['created_at']:
            updated_date = job['updated_at'].split(' ')[0]  # Just get date part
            updated = ttk.Label(dates_frame, text=f"Обновлено: {updated_date}")
            updated.pack(side="left", padx=(20, 0))

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        # Информация о клиенте
        client = self.db.get_user_by_id(job['client_id'])
        if client:
            client_frame = ttk.Frame(frame)
            client_frame.pack(fill="x", pady=5)

            client_label = ttk.Label(client_frame, text="Автор:", width=12, anchor="w")
            client_label.pack(side="left")

            client_name = ttk.Label(client_frame, text=client['username'])
            client_name.pack(side="left")

        # Информация о фрилансере (если назначен)
        if job['freelancer_id']:
            freelancer = self.db.get_user_by_id(job['freelancer_id'])
            if freelancer:
                freelancer_frame = ttk.Frame(frame)
                freelancer_frame.pack(fill="x", pady=5)

                freelancer_label = ttk.Label(freelancer_frame, text="Назначено:", width=12, anchor="w")
                freelancer_label.pack(side="left")

                freelancer_name = ttk.Label(freelancer_frame, text=freelancer['username'])
                freelancer_name.pack(side="left")

                # Если пользователь является клиентом, добавьте кнопку для просмотра профиля фрилансера
                if self.current_user['user_type'] == 'client' and self.current_user['id'] == job['client_id']:
                    view_profile_btn = ttk.Button(
                        freelancer_frame,
                        text="Просмотреть профиль",
                        command=lambda f=freelancer: self.show_freelancer_profile(f)
                    )
                    view_profile_btn.pack(side="right")

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        # Описание
        desc_label = ttk.Label(frame, text="Описание:", font=("TkDefaultFont", 11, "bold"))
        desc_label.pack(anchor="w", pady=(0, 5))

        desc_frame = ttk.Frame(frame)
        desc_frame.pack(fill="both", expand=True)

        desc_text = tk.Text(desc_frame, wrap="word", height=12)
        desc_text.insert("1.0", job['description'])
        desc_text.config(state="disabled")  # Make it read-only
        desc_text.pack(fill="both", expand=True)

        # Кнопка «Добавить сообщение», если задание назначено
        if job['status'] == 'assigned':
            if (self.current_user['user_type'] == 'client' and job['client_id'] == self.current_user['id'] and job[
                'freelancer_id']) or \
                    (self.current_user['user_type'] == 'freelancer' and job['freelancer_id'] == self.current_user[
                        'id']):

                btn_frame = ttk.Frame(frame)
                btn_frame.pack(fill="x", pady=10)

                other_user_id = job['freelancer_id'] if self.current_user['user_type'] == 'client' else job['client_id']
                other_user = self.db.get_user_by_id(other_user_id)

                if other_user:
                    message_btn = ttk.Button(
                        btn_frame,
                        text=f"Написать пользователю {other_user['username']}",
                        command=lambda: self.show_messaging_with_user(other_user)
                    )
                    message_btn.pack(side="left")

        # Кнопка закрытия
        close_btn = ttk.Button(
            frame,
            text="Закрыть",
            command=dialog.destroy
        )
        close_btn.pack(pady=10)

    def show_messaging_with_user(self, other_user):
        """Показать экран сообщений с выбранным конкретным пользователем."""
        self.clear_content()
        self.highlight_active_nav("Messaging")

        # Создать контент для обмена сообщениями
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Сообщения",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Отправьте первоначальное сообщение, если это новый разговор
        conversations = self.db.get_conversations(self.current_user['id'])
        user_exists = False

        for user in conversations:
            if user['id'] == other_user['id']:
                user_exists = True
                break

        if not user_exists:
            # Отправьте приветственное сообщение, чтобы начать разговор
            welcome_msg = f"Привет {other_user['username']}, Я хотел бы связаться с вами."
            self.db.send_message(self.current_user['id'], other_user['id'], welcome_msg)

        # Просмотр чата с предварительно выбранным пользователем
        chat_view = ChatView(
            frame,
            user_id=self.current_user['id'],
            current_chat_user=other_user,  # Передаем пользователя для предварительного выбора
            get_messages_callback=self.db.get_messages,
            send_message_callback=self.db.send_message,
            get_users_callback=self.db.get_conversations,
            delete_chat_callback=self.db.delete_conversation
        )
        chat_view.pack(fill="both", expand=True)

    def show_find_freelancers(self):
        """Покажите экран, чтобы найти и просмотреть фрилансеров."""
        self.clear_content()
        self.highlight_active_nav("Find Freelancers")

        # Создание контента
        frame = ttk.Frame(self.content, padding=20)
        frame.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Label(
            frame,
            text="Поиск фрилансеров",
            font=("TkDefaultFont", 16, "bold")
        )
        header.pack(pady=(0, 20))

        # Получить всех фрилансеров
        freelancers = self.db.get_all_freelancers()

        if not freelancers:
            no_freelancers = ttk.Label(
                frame,
                text="Фрилансеры не найдены",
                font=("TkDefaultFont", 12, "italic")
            )
            no_freelancers.pack(pady=50)
            return

        # Список фрилансеров
        freelancers_frame = ScrollableFrame(frame)
        freelancers_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for freelancer in freelancers:
            # Создать карточку фрилансера
            card = ttk.Frame(freelancers_frame.scrollable_frame, relief="solid", borderwidth=1)
            card.pack(fill="x", padx=5, pady=5, ipadx=5, ipady=5)

            # Имя фрилансера
            name = ttk.Label(
                card,
                text=freelancer['username'],
                font=("TkDefaultFont", 12, "bold")
            )
            name.pack(anchor="w", padx=10, pady=5)

            # Специальность
            if freelancer['specialty']:
                specialty = ttk.Label(
                    card,
                    text=f"Специальность: {freelancer['specialty']}"
                )
                specialty.pack(anchor="w", padx=10)

            # Получить средний рейтинг
            avg_rating = self.db.get_average_rating(freelancer['id'])

            if avg_rating:
                rating_frame = ttk.Frame(card)
                rating_frame.pack(anchor="w", padx=10, pady=5)

                rating_label = ttk.Label(rating_frame, text="Рейтинг: ")
                rating_label.pack(side="left")

                for i in range(5):
                    if i < int(avg_rating):
                        star = ttk.Label(rating_frame, text="★")  # Full star
                    elif i == int(avg_rating) and avg_rating % 1 >= 0.5:
                        star = ttk.Label(rating_frame, text="✯")  # Half star
                    else:
                        star = ttk.Label(rating_frame, text="☆")  # Empty star
                    star.pack(side="left")

                rating_val = ttk.Label(rating_frame, text=f" ({avg_rating:.1f})")
                rating_val.pack(side="left")

            # Кнопка просмотра профиля
            btn_frame = ttk.Frame(card)
            btn_frame.pack(fill="x", padx=10, pady=5)

            view_btn = ttk.Button(
                btn_frame,
                text="Просмотреть профиль",
                command=lambda f=freelancer: self.show_freelancer_profile(f)
            )
            view_btn.pack(side="left")

            message_btn = ttk.Button(
                btn_frame,
                text="Сообщение",
                command=lambda f=freelancer: self.show_messaging_with_user(f)
            )
            message_btn.pack(side="left", padx=(10, 0))

    def show_freelancer_profile(self, freelancer):
        """Показать профиль фрилансера в диалоговом окне."""
        # Получить полные данные пользователя
        user_data = self.db.get_user_by_id(freelancer['id'])

        if not user_data:
            messagebox.showerror("Ошибка", "Данные фрилансера не найдены")
            return

        # Создать окно верхнего уровня
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Профиль фрилансера: {user_data['username']}")
        dialog.geometry("700x800")
        dialog.transient(self.root)
        # Позиционируем окно
        self._position_dialog(dialog)
        # Создание контента
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True)

        # Создайте блокнот (интерфейс с вкладками)
        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка «Профиль»
        profile_tab = ttk.Frame(notebook)
        notebook.add(profile_tab, text="Профиль")

        profile_view = ProfileView(
            profile_tab,
            user_data,
            is_own_profile=False
        )
        profile_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка «Услуги»
        services_tab = ttk.Frame(notebook)
        notebook.add(services_tab, text="Услуги")

        services = self.db.get_freelancer_services(user_data['id'])
        services_view = ServiceListingView(
            services_tab,
            services_data=services,
            is_own_services=False
        )
        services_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка занятости
        avail_tab = ttk.Frame(notebook)
        notebook.add(avail_tab, text="Занятость")

        avail_frame = ttk.Frame(avail_tab, padding=10)
        avail_frame.pack(fill="both", expand=True)

        avail_label = ttk.Label(
            avail_frame,
            text="Календарь занятости",
            font=("TkDefaultFont", 14, "bold")
        )
        avail_label.pack(pady=(0, 10))

        availability = self.db.get_freelancer_availability(user_data['id'])
        calendar_view = CalendarView(
            avail_frame,
            freelancer_id=None,  # View-only mode
            availability_data=availability
        )
        calendar_view.pack(fill="both", expand=True)
        # Рейтинг
        ratings_tab = ttk.Frame(notebook)
        notebook.add(ratings_tab, text="Рейтинги и отзывы")

        ratings = self.db.get_freelancer_ratings(user_data['id'])
        avg_rating = self.db.get_average_rating(user_data['id'])

        ratings_view = RatingsView(
            ratings_tab,
            ratings_data=ratings,
            average_rating=avg_rating
        )
        ratings_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Рамка для кнопок
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=10, pady=10)

        # Кнопка сообщения
        message_btn = ttk.Button(
            btn_frame,
            text=f"Написать пользователю {user_data['username']}",
            command=lambda: self.show_messaging_with_user(user_data)
        )
        message_btn.pack(side="left", padx=5)

        # Кнопка закрытия
        close_btn = ttk.Button(
            btn_frame,
            text="Закрыть",
            command=dialog.destroy
        )
        close_btn.pack(side="right", padx=5)


def main():
    root = tk.Tk()
    app = FreelanceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
