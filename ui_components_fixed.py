import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import datetime
import re


class ScrollableFrame(ttk.Frame):
    """Виджет прокручиваемой рамки."""

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # Создаем холст и полосу прокрутки
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем события колеса мыши
        self.bind_mousewheel()

    def bind_mousewheel(self):
        """Привяжите события колеса мыши к холсту для прокрутки."""

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def unbind_mousewheel(self):
        """Отменить привязку событий колеса мыши, когда рамка не видна."""
        self.canvas.unbind_all("<MouseWheel>")


class CalendarView(tk.Frame):
    """Пользовательский виджет календаря для отображения и управления занятостью."""

    def __init__(self, parent, freelancer_id=None, availability_data=None, callback=None):
        super().__init__(parent, bg="#c1b7df")
        self.freelancer_id = freelancer_id
        self.availability_data = availability_data or []
        self.callback = callback
        self.current_date = datetime.datetime.now()
        self.selected_date = None
        self.editable = freelancer_id is not None

        self.init_ui()

    def init_ui(self):
        """Инициализировать пользовательский интерфейс календаря."""
        control_frame = tk.Frame(self, bg="#c1b7df")
        control_frame.pack(fill="x", padx=5, pady=5)

        prev_btn = ttk.Button(control_frame, text="<", command=self.prev_month)
        prev_btn.pack(side="left")

        self.month_label = tk.Label(control_frame, text="", font=("TkDefaultFont", 10, "bold"), bg="#c1b7df")
        self.month_label.pack(side="left", expand=True)

        next_btn = ttk.Button(control_frame, text=">", command=self.next_month)
        next_btn.pack(side="right")

        # Дни календаря
        days_frame = tk.Frame(self, bg="#d5cfe9")
        days_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Названия дней
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            label = tk.Label(days_frame, text=day, anchor="center", bg="#d5cfe9")
            label.grid(row=0, column=i, sticky="nsew")

        # Сетка календаря
        self.calendar_days = []
        for row in range(6):
            for col in range(7):
                frame = tk.Frame(days_frame, borderwidth=1, relief="solid", width=60, height=60, bg="#f0f0f0")
                frame.grid(row=row + 1, column=col, sticky="nsew", padx=1, pady=1)
                frame.grid_propagate(False)

                date_label = tk.Label(frame, text="", anchor="ne", bg="#f0f0f0")
                date_label.place(x=2, y=2)

                content_frame = tk.Frame(frame, bg="#f0f0f0")
                content_frame.place(x=2, y=18, width=56, height=40)

                self.calendar_days.append({
                    "frame": frame,
                    "date_label": date_label,
                    "content_frame": content_frame,
                    "date": None
                })

        # Настраиваем веса сетки
        for i in range(7):
            days_frame.columnconfigure(i, weight=1)
        for i in range(7):
            days_frame.rowconfigure(i, weight=1)

        # Обновление календаря
        self.update_calendar()

        # Рамка легенды
        legend_frame = tk.Frame(self, bg="#c1b7df", pady=10)
        legend_frame.pack(fill="x", padx=5, pady=5)

        # Название легенды
        legend_title = tk.Label(legend_frame, text="Легенда:", font=("TkDefaultFont", 9, "bold"), bg="#c1b7df")
        legend_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Легенда сложности
        complexity_frame = tk.Frame(legend_frame, bg="#c1b7df")
        complexity_frame.grid(row=1, column=0, sticky="nw", padx=(0, 10))

        complexity_title = tk.Label(complexity_frame, text="Сложность:", bg="#c1b7df")
        complexity_title.pack(anchor="w")

        # Низкая
        low_frame = tk.Frame(complexity_frame, bg="#c1b7df")
        low_frame.pack(fill="x", pady=2)
        low_color = tk.Label(low_frame, bg="#d4f7d4", width=3, height=1)
        low_color.pack(side="left", padx=(10, 5))
        low_text = tk.Label(low_frame, text="Низкая", bg="#c1b7df")
        low_text.pack(side="left")

        # Средняя
        medium_frame = tk.Frame(complexity_frame, bg="#c1b7df")
        medium_frame.pack(fill="x", pady=2)
        medium_color = tk.Label(medium_frame, bg="#ffffcc", width=3, height=1)
        medium_color.pack(side="left", padx=(10, 5))
        medium_text = tk.Label(medium_frame, text="Средняя", bg="#c1b7df")
        medium_text.pack(side="left")

        # Высокая
        high_frame = tk.Frame(complexity_frame, bg="#c1b7df")
        high_frame.pack(fill="x", pady=2)
        high_color = tk.Label(high_frame, bg="#ffcccc", width=3, height=1)
        high_color.pack(side="left", padx=(10, 5))
        high_text = tk.Label(high_frame, text="Высокая", bg="#c1b7df")
        high_text.pack(side="left")

        # Легенда статуса
        status_frame = tk.Frame(legend_frame, bg="#c1b7df")
        status_frame.grid(row=1, column=1, sticky="nw")

        status_title = tk.Label(status_frame, text="Статус:", bg="#c1b7df")
        status_title.pack(anchor="w")

        # Доступен
        available_frame = tk.Frame(status_frame, bg="#c1b7df")
        available_frame.pack(fill="x", pady=2)
        available_label = tk.Label(available_frame, text="Доступен", bg="#d4f7d4", padx=5, relief="ridge")
        available_label.pack(side="left", padx=(10, 5))
        available_text = tk.Label(available_frame, text="Могу принять новую работу", bg="#c1b7df")
        available_text.pack(side="left")

        # Занят
        busy_frame = tk.Frame(status_frame, bg="#c1b7df")
        busy_frame.pack(fill="x", pady=2)
        busy_label = tk.Label(busy_frame, text="Занят", bg="#b0e0b0", padx=5, relief="ridge")
        busy_label.pack(side="left", padx=(10, 5))
        busy_text = tk.Label(busy_frame, text="Не могу принять новую работу", bg="#c1b7df")
        busy_text.pack(side="left")

        if self.editable:
            instruction = tk.Label(self, text="Нажмите на день, чтобы добавить/изменить занятость", bg="#c1b7df")
            instruction.pack(pady=5)

    def update_calendar(self):
        """Обновить представление календаря на основе текущего месяца."""
        month_name = self.current_date.strftime("%B %Y")
        self.month_label.config(text=month_name)

        year = self.current_date.year
        month = self.current_date.month

        # Очистить предыдущий контент
        for day in self.calendar_days:
            day["date_label"].config(text="")
            for widget in day["content_frame"].winfo_children():
                widget.destroy()
            day["date"] = None
            day["frame"].config(bg="#f0f0f0")
            day["date_label"].config(bg="#f0f0f0")
            day["content_frame"].config(bg="#f0f0f0")

        # Получить дни месяца
        cal = calendar.monthcalendar(year, month)

        # Заполняем календарь
        day_index = 0
        for week in cal:
            for day_num in week:
                if day_index >= len(self.calendar_days):
                    break

                day_data = self.calendar_days[day_index]

                if day_num == 0:
                    day_data["date"] = None
                else:
                    date = datetime.date(year, month, day_num)
                    day_data["date"] = date
                    day_data["date_label"].config(text=str(day_num))

                    # Проверьте, есть ли у даты данные о доступности
                    self.render_availability(day_data, date)

                    # Привязать событие клика, если оно доступно для редактирования
                    if self.editable:
                        day_data["frame"].bind("<Button-1>",
                                               lambda e, d=date: self.on_date_click(d))

                day_index += 1

    def render_availability(self, day_data, date):
        """Отображение данных о доступности на определенную дату."""
        content_frame = day_data["content_frame"]

        # Проверьте наличие записей о доступности, которые включают эту дату
        for avail in self.availability_data:
            start = datetime.datetime.strptime(avail["start_date"], "%Y-%m-%d").date()
            end = datetime.datetime.strptime(avail["end_date"], "%Y-%m-%d").date()

            if start <= date <= end:
                # Определить цвет в зависимости от сложности
                colors = {
                    "low": "#d4f7d4",  # Светло зеленый
                    "medium": "#ffffcc",  # Светло желтый
                    "high": "#ffcccc"  # Светло красный
                }
                color = colors.get(avail["complexity"].lower(), "#d4d4d4")  # По умолчанию светло-серый

                # Изменить фон дня
                day_data["frame"].config(bg=color)
                day_data["date_label"].config(bg=color)
                day_data["content_frame"].config(bg=color)

                # Показать статус доступности с четкой визуальной индикацией
                if avail["can_accept_more"]:
                    status = "Доступен"
                    status_color = color
                else:
                    status = "Занят"
                    # Немного более темный оттенок статуса, чем фон
                    if color == "#d4f7d4":  # Светло зеленый
                        status_color = "#b0e0b0"
                    elif color == "#ffffcc":  # Светло желтый
                        status_color = "#e0e0aa"
                    elif color == "#ffcccc":  # Светло красный
                        status_color = "#e0b0b0"
                    else:
                        status_color = "#c0c0c0"  # По умолчанию светло-серый

                status_label = tk.Label(content_frame, text=status, bg=status_color, padx=2, relief="ridge")
                status_label.pack(fill="x")

                # Показать заметку, если она существует и есть место
                if avail["note"] and len(avail["note"]) > 0:
                    note = avail["note"]
                    if len(note) > 10:
                        note = note[:8] + "..."
                    note_label = tk.Label(content_frame, text=note, bg=color)
                    note_label.pack(fill="x")

                # Мы нашли запись на эту дату, нет необходимости проверять другие
                break

    def on_date_click(self, date):
        """Обработка щелчка по дате, чтобы добавить или изменить доступность."""
        self.selected_date = date
        if self.callback:
            self.callback(date)

    def prev_month(self):
        """Перейти к предыдущему месяцу."""
        year = self.current_date.year
        month = self.current_date.month - 1

        if month < 1:
            month = 12
            year -= 1

        self.current_date = self.current_date.replace(year=year, month=month)
        self.update_calendar()

    def next_month(self):
        """Перейти к следующему месяцу."""
        year = self.current_date.year
        month = self.current_date.month + 1

        if month > 12:
            month = 1
            year += 1

        self.current_date = self.current_date.replace(year=year, month=month)
        self.update_calendar()

    def set_availability_data(self, availability_data):
        """Обновите данные о занятости и обновите календарь."""
        self.availability_data = availability_data
        self.update_calendar()


class ChatView(ttk.Frame):
    """Пользовательский виджет чата для обмена сообщениями между пользователями."""
    def __init__(self, parent, user_id, current_chat_user=None,
                 get_messages_callback=None, send_message_callback=None,
                 get_users_callback=None, delete_chat_callback=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_chat_user = current_chat_user
        self.get_messages_callback = get_messages_callback
        self.send_message_callback = send_message_callback
        self.get_users_callback = get_users_callback
        self.delete_chat_callback = delete_chat_callback

        self.init_ui()
        self.refresh_users()

    def init_ui(self):
        """Инициализировать пользовательский интерфейс чата."""
        # Разделить на левую боковую панель (пользователи) и правый контент (сообщения)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # Боковая панель пользователей
        users_frame = ttk.Frame(self)
        users_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        users_label = ttk.Label(users_frame, text="Диалоги", font=("TkDefaultFont", 10, "bold"))
        users_label.pack(fill="x", pady=(0, 5))

        self.users_listbox = tk.Listbox(users_frame, height=15)
        self.users_listbox.pack(fill="both", expand=True)
        self.users_listbox.bind("<<ListboxSelect>>", self.on_user_select)

        delete_chat_btn = ttk.Button(users_frame, text="Удалить диалог",
                                     command=self.delete_current_chat)
        delete_chat_btn.pack(fill="x", pady=(5, 0))

        # Рамка содержимого чата
        chat_frame = ttk.Frame(self)
        chat_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Заголовок чата
        self.chat_header = ttk.Label(chat_frame, text="Выберите диалог",
                                     font=("TkDefaultFont", 10, "bold"))
        self.chat_header.pack(fill="x", pady=(0, 5))

        # Область отображения сообщений
        self.messages_frame = ScrollableFrame(chat_frame)
        self.messages_frame.pack(fill="both", expand=True, pady=5)

        # Ввод сообщения
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill="x", pady=(5, 0))

        self.message_input = ttk.Entry(input_frame)
        self.message_input.pack(side="left", fill="x", expand=True, padx=(0, 5))

        send_button = ttk.Button(input_frame, text="Отправить", command=self.send_message)
        send_button.pack(side="right")

        # Привязать клавишу ввода для отправки сообщения
        self.message_input.bind("<Return>", lambda e: self.send_message())

    def refresh_users(self):
        """Обновить список пользователей с беседами."""
        if self.get_users_callback:
            users = self.get_users_callback(self.user_id)
            self.users_listbox.delete(0, tk.END)

            self.user_list = []
            for user in users:
                self.user_list.append(user)
                display_name = f"{user['username']} ({user['user_type'].capitalize()})"
                self.users_listbox.insert(tk.END, display_name)

            # Если в чате есть текущий пользователь и он все еще в списке, выберите его
            if self.current_chat_user:
                for i, user in enumerate(self.user_list):
                    if user['id'] == self.current_chat_user['id']:
                        self.users_listbox.selection_set(i)
                        break

    def on_user_select(self, event):
        """Обработка выбора пользователя для загрузки сообщений чата."""
        selection = self.users_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_chat_user = self.user_list[index]
            self.chat_header.config(text=f"Чат с {self.current_chat_user['username']}")
            self.load_messages()

    def load_messages(self):
        """Загрузка и отображение сообщений для текущего чата."""
        if not self.current_chat_user or not self.get_messages_callback:
            return

        messages = self.get_messages_callback(self.user_id, self.current_chat_user['id'])

        # Очистить предыдущие сообщения
        for widget in self.messages_frame.scrollable_frame.winfo_children():
            widget.destroy()

        for message in messages:
            # Создать пузырь сообщения
            is_own = message['sender_id'] == self.user_id
            bubble = ttk.Frame(self.messages_frame.scrollable_frame, padding=5)
            bubble.pack(fill="x", pady=2, padx=10, anchor="e" if is_own else "w")

            # Содержание сообщения
            content = message['content']
            message_label = ttk.Label(bubble, text=content, wraplength=300)
            message_label.pack(anchor="e" if is_own else "w")

            # Временная метка
            timestamp = message['sent_at'].split(" ")[0]  # Просто получите часть даты для простоты
            time_label = ttk.Label(bubble, text=timestamp, font=("TkDefaultFont", 7))
            time_label.pack(anchor="e" if is_own else "w")

        # Прокрутите вниз
        self.messages_frame.canvas.update_idletasks()
        self.messages_frame.canvas.yview_moveto(1.0)

    def send_message(self):
        """Отправить сообщение текущему пользователю чата."""
        if not self.current_chat_user or not self.send_message_callback:
            messagebox.showinfo("Информация", "Пожалуйста, выберите пользователя для общения")
            return

        message = self.message_input.get().strip()
        if not message:
            return

        success = self.send_message_callback(
            self.user_id, self.current_chat_user['id'], message
        )

        if success:
            self.message_input.delete(0, tk.END)
            self.load_messages()

    def delete_current_chat(self):
        """Удалить текущий разговор."""
        if not self.current_chat_user or not self.delete_chat_callback:
            messagebox.showinfo("Информация", "Пожалуйста, выберите диалог, который хотите удалить")
            return

        if messagebox.askyesno("Подтвердить удаление",
                               f"Вы уверены, что хотите удалить диалог с "
                               f"{self.current_chat_user['username']}?"):
            success = self.delete_chat_callback(self.user_id, self.current_chat_user['id'])

            if success:
                for widget in self.messages_frame.scrollable_frame.winfo_children():
                    widget.destroy()
                self.chat_header.config(text="Выберите диалог")
                self.current_chat_user = None
                self.refresh_users()
                messagebox.showinfo("Успех", " Диалог удален")


class Validators:
    """Утилитный класс с методами проверки входных данных формы."""

    @staticmethod
    def validate_username(username):
        """
        Подтвердите имя пользователя:
        - Минимум 3 символа
        - Только буквы, цифры и подчеркивания
        """
        if not username or len(username) < 3:
            return False, "Имя пользователя должно быть не менее 3 символов"

        if not re.match(r'^[a-zA-Z0-9_а-яА-Я]+$', username):
            return False, "Имя пользователя должно содержать только буквы, цифры и символы подчеркивания."

        return True, ""

    @staticmethod
    def validate_password(password):
        """
        Подтвердите пароль:
        - Минимум 6 символов
        - Хотя бы одна буква и одна цифра
        """
        if not password or len(password) < 6:
            return False, "Пароль должен быть не менее 6 символов"

        if not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password):
            return False, "Пароль должен содержать хотя бы одну букву или одну цифру"

        return True, ""

    @staticmethod
    def validate_phone(phone):
        """
        Подтвердите номер телефона:
        - Только цифры и опционально + в начале
        - От 11 до 16 символов.
        """
        if not phone:
            return False, "Введите номер телефона"

        if not re.match(r'^\+?[0-9]{11,16}$', phone):
            return False, "Неверный формат номера телефона"

        return True, ""

    @staticmethod
    def validate_required(value, field_name="Field"):
        """Проверьте, что поле не пусто."""
        if not value or value.strip() == "":
            return False, f"{field_name} обязательно для заполнения"

        return True, ""


class ProfileView(ttk.Frame):
    """Виджет для отображения и редактирования профилей пользователей."""

    def __init__(self, parent, user_data, is_own_profile=False, update_callback=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_own_profile = is_own_profile
        self.update_callback = update_callback

        self.init_ui()

    def init_ui(self):
        """Инициализировать пользовательский интерфейс профиля."""
        # Шапка профиля
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        profile_label = ttk.Label(header_frame,
                                  text=f"{self.user_data['username']}",
                                  font=("TkDefaultFont", 16, "bold"))
        profile_label.pack(side="left")

        user_type = self.user_data['user_type'].capitalize()
        type_label = ttk.Label(header_frame, text=f"({user_type})",
                               font=("TkDefaultFont", 12))
        type_label.pack(side="left", padx=(5, 0))

        # Информация о профиле
        info_frame = ttk.LabelFrame(self, text="Информация о профиле")
        info_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Имя пользователя
        username_frame = ttk.Frame(info_frame)
        username_frame.pack(fill="x", padx=10, pady=5)
        username_label = ttk.Label(username_frame, text="Имя пользователя:", width=25, anchor="w")
        username_label.pack(side="left")
        username_value = ttk.Label(username_frame, text=self.user_data['username'])
        username_value.pack(side="left", fill="x", expand=True)

        # Номер телефона
        phone_frame = ttk.Frame(info_frame)
        phone_frame.pack(fill="x", padx=10, pady=5)
        phone_label = ttk.Label(phone_frame, text="Номер телефона:", width=25, anchor="w")
        phone_label.pack(side="left")
        phone_value = ttk.Label(phone_frame, text=self.user_data['phone'])
        phone_value.pack(side="left", fill="x", expand=True)

        # Социальные сети
        social_frame = ttk.Frame(info_frame)
        social_frame.pack(fill="x", padx=10, pady=5)
        social_label = ttk.Label(social_frame, text="Социальные сети:", width=25, anchor="w")
        social_label.pack(side="left")
        social_value = ttk.Label(social_frame, text=self.user_data.get('social_media', 'Not provided'))
        social_value.pack(side="left", fill="x", expand=True)

        # Специальномть (для фрилансера)
        if self.user_data['user_type'] == 'freelancer' and self.user_data.get('specialty'):
            specialty_frame = ttk.Frame(info_frame)
            specialty_frame.pack(fill="x", padx=10, pady=5)
            specialty_label = ttk.Label(specialty_frame, text="Специальность:", width=25, anchor="w")
            specialty_label.pack(side="left")
            specialty_value = ttk.Label(specialty_frame, text=self.user_data['specialty'])
            specialty_value.pack(side="left", fill="x", expand=True)

        # Дата регистрации
        if self.user_data.get('registration_date'):
            reg_date_frame = ttk.Frame(info_frame)
            reg_date_frame.pack(fill="x", padx=10, pady=5)
            reg_date_label = ttk.Label(reg_date_frame, text="Зарегистрирован:", width=25, anchor="w")
            reg_date_label.pack(side="left")

            # Форматируем дату для лучшей читаемости
            reg_date = self.user_data['registration_date'].split(' ')[0]  # Just get the date part
            reg_date_value = ttk.Label(reg_date_frame, text=reg_date)
            reg_date_value.pack(side="left", fill="x", expand=True)


class JobListingView(ttk.Frame):
    """Виджет для отображения и управления списками вакансий."""

    def __init__(self, parent, jobs_data=None, is_client=False, user_id=None,
                 on_create=None, on_edit=None, on_delete=None,
                 on_assign=None, on_complete=None, on_view_details=None):
        super().__init__(parent)
        self.jobs_data = jobs_data or []
        self.is_client = is_client
        self.user_id = user_id
        self.on_create = on_create
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_assign = on_assign
        self.on_complete = on_complete
        self.on_view_details = on_view_details

        self.init_ui()

    def init_ui(self):
        """Инициализировать пользовательский интерфейс списков вакансий."""
        # Заголовок с кнопками действий
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        title_label = ttk.Label(header_frame, text="Списки вакансий", font=("TkDefaultFont", 14, "bold"))
        title_label.pack(side="left")

        # Если пользователь является клиентом, показать кнопку создания
        if self.is_client:
            create_btn = ttk.Button(header_frame, text="Создать вакансию", command=self.create_job)
            create_btn.pack(side="right")

        # Список вакансий
        self.jobs_frame = ScrollableFrame(self)
        self.jobs_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Обновить списки
        self.refresh_listings()

    def refresh_listings(self):
        """Обновите список вакансий."""
        # Очистить предыдущие списки
        for widget in self.jobs_frame.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.jobs_data:
            empty_label = ttk.Label(self.jobs_frame.scrollable_frame,
                                    text="Вакансий не найдено", font=("TkDefaultFont", 10, "italic"))
            empty_label.pack(pady=20)
            return

        # Создание карточек заданий
        for job in self.jobs_data:
            self.create_job_card(job)

    def create_job_card(self, job):
        """Создайте визуальную карточку для списка вакансий."""
        card = ttk.Frame(self.jobs_frame.scrollable_frame, relief="solid", borderwidth=1)
        card.pack(fill="x", padx=5, pady=5, ipadx=5, ipady=5)

        # Заголовок задания
        header_frame = ttk.Frame(card)
        header_frame.pack(fill="x", padx=5, pady=5)

        job_title = ttk.Label(header_frame, text=job['title'], font=("TkDefaultFont", 12, "bold"))
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

        status_label = ttk.Label(header_frame, text=f"Статус: {status_text}", foreground=status_color)
        status_label.pack(side="right")

        # Описание вакансии (сокращенно)
        desc = job['description']
        if len(desc) > 100:
            desc = desc[:97] + "..."

        desc_frame = ttk.Frame(card)
        desc_frame.pack(fill="x", padx=5, pady=5)
        desc_label = ttk.Label(desc_frame, text=desc, wraplength=400)
        desc_label.pack(fill="x", anchor="w")

        # Информация о дате
        date_frame = ttk.Frame(card)
        date_frame.pack(fill="x", padx=5, pady=5)

        created_date = job['created_at'].split(' ')[0]  # Просто получить часть даты
        date_label = ttk.Label(date_frame, text=f"Создано: {created_date}", font=("TkDefaultFont", 8))
        date_label.pack(side="left")

        # Кнопки действий
        actions_frame = ttk.Frame(card)
        actions_frame.pack(fill="x", padx=5, pady=5)

        # Кнопка «Просмотреть подробности» (доступна всем)
        view_btn = ttk.Button(actions_frame, text="Просмотреть детали",
                              command=lambda j=job: self.view_job_details(j))
        view_btn.pack(side="left", padx=(0, 5))

        # Действия, специфичные для клиента
        if self.is_client and job['client_id'] == self.user_id:
            # Кнопка редактирования (только для открытых вакансий)
            if job['status'].lower() == 'open':
                edit_btn = ttk.Button(actions_frame, text="Редактировать",
                                      command=lambda j=job: self.edit_job(j))
                edit_btn.pack(side="left", padx=(0, 5))

                delete_btn = ttk.Button(actions_frame, text="Удалить",
                                        command=lambda j=job: self.delete_job(j))
                delete_btn.pack(side="left", padx=(0, 5))

            # Кнопка «Завершить» (только для назначенных заданий)
            if job['status'].lower() == 'assigned':
                complete_btn = ttk.Button(actions_frame, text="Отметить как завершенное",
                                          command=lambda j=job: self.complete_job(j))
                complete_btn.pack(side="left", padx=(0, 5))

        # Действия, специфичные для фрилансера
        elif not self.is_client and job['status'].lower() == 'open':
            assign_btn = ttk.Button(actions_frame, text="Откликнуться",
                                    command=lambda j=job: self.assign_job(j))
            assign_btn.pack(side="left", padx=(0, 5))

    def create_job(self):
        """Обработка действия создания услуги."""
        if self.on_create:
            self.on_create()

    def edit_job(self, job):
        """Обработка действия редактирования услуги."""
        if self.on_edit:
            self.on_edit(job)

    def delete_job(self, job):
        """Обработка действия удаления услуги."""
        if self.on_delete:
            self.on_delete(job)

    def assign_job(self, job):
        """Обработка действия назначения услуги."""
        if self.on_assign:
            self.on_assign(job)

    def complete_job(self, job):
        """Обработка полной услуги."""
        if self.on_complete:
            self.on_complete(job)

    def view_job_details(self, job):
        """Обработка действия просмотра сведений о услуге."""
        if self.on_view_details:
            self.on_view_details(job)

    def set_jobs_data(self, jobs_data):
        """Обновите данные о вакансиях и обновите список."""
        self.jobs_data = jobs_data
        self.refresh_listings()


class ServiceListingView(ttk.Frame):
    """Виджет для отображения и управления услугами фрилансера."""

    def __init__(self, parent, services_data=None, is_own_services=False,
                 on_create=None, on_edit=None, on_delete=None):
        super().__init__(parent)
        self.services_data = services_data or []
        self.is_own_services = is_own_services
        self.on_create = on_create
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.init_ui()

    def init_ui(self):
        """Инициализировать пользовательский интерфейс списка служб."""
        # Заголовок с кнопками действий
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        title_label = ttk.Label(header_frame, text="Услуги", font=("TkDefaultFont", 14, "bold"))
        title_label.pack(side="left")

        # Если это собственные службы пользователя, показать кнопку создания
        if self.is_own_services:
            create_btn = ttk.Button(header_frame, text="Создать услугу", command=self.create_service)
            create_btn.pack(side="right")

        # Список услуг
        self.services_frame = ScrollableFrame(self)
        self.services_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Обновить списки
        self.refresh_listings()

    def refresh_listings(self):
        """Обновить список услуг."""
        # Очистить предыдущие списки
        for widget in self.services_frame.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.services_data:
            empty_label = ttk.Label(self.services_frame.scrollable_frame,
                                    text="Услуги не найдены", font=("TkDefaultFont", 10, "italic"))
            empty_label.pack(pady=20)
            return

        # Создание карточек услуг
        for service in self.services_data:
            self.create_service_card(service)

    def create_service_card(self, service):
        """Создайте визуальную карточку для списка услуг."""
        card = ttk.Frame(self.services_frame.scrollable_frame, relief="solid", borderwidth=1)
        card.pack(fill="x", padx=5, pady=5, ipadx=5, ipady=5)

        # Название услуги
        header_frame = ttk.Frame(card)
        header_frame.pack(fill="x", padx=5, pady=5)

        service_title = ttk.Label(header_frame, text=service['title'],
                                  font=("TkDefaultFont", 12, "bold"))
        service_title.pack(side="left")

        # Описание услуги
        desc_frame = ttk.Frame(card)
        desc_frame.pack(fill="x", padx=5, pady=5)
        desc_label = ttk.Label(desc_frame, text=service['description'], wraplength=400)
        desc_label.pack(fill="x", anchor="w")

        # Кнопки действий (только для собственных услуг)
        if self.is_own_services:
            actions_frame = ttk.Frame(card)
            actions_frame.pack(fill="x", padx=5, pady=5)

            edit_btn = ttk.Button(actions_frame, text="Редактировать",
                                  command=lambda s=service: self.edit_service(s))
            edit_btn.pack(side="left", padx=(0, 5))

            delete_btn = ttk.Button(actions_frame, text="Удалить",
                                    command=lambda s=service: self.delete_service(s))
            delete_btn.pack(side="left", padx=(0, 5))

    def create_service(self):
        """Обработка действия создания службы."""
        if self.on_create:
            self.on_create()

    def edit_service(self, service):
        """Обработка действия редактирования службы."""
        if self.on_edit:
            self.on_edit(service)

    def delete_service(self, service):
        """Обработка действия удаления службы."""
        if self.on_delete:
            self.on_delete(service)

    def set_services_data(self, services_data):
        """Обновите данные об услугах и обновите список."""
        self.services_data = services_data
        self.refresh_listings()


class RatingsView(ttk.Frame):
    """Виджет для отображения оценок и отзывов."""

    def __init__(self, parent, ratings_data=None, average_rating=0.0):
        super().__init__(parent)
        self.ratings_data = ratings_data or []
        self.average_rating = float(average_rating) if average_rating is not None else 0.0

        self.init_ui()

    def init_ui(self):
        """Инициализировать пользовательский интерфейс рейтингов."""
        # Заголовок с общим рейтингом
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        title_label = ttk.Label(header_frame, text="Рейтинги и отзывы",
                                font=("TkDefaultFont", 14, "bold"))
        title_label.pack(side="left")

        # Отображение среднего рейтинга
        avg_frame = ttk.Frame(self)
        avg_frame.pack(fill="x", padx=10, pady=(0, 10))

        avg_text = f"Средний рейтинг: {self.average_rating:.1f}/5.0"
        avg_label = ttk.Label(avg_frame, text=avg_text, font=("TkDefaultFont", 12))
        avg_label.pack(side="left")

        # Представление звезд
        stars_frame = ttk.Frame(avg_frame)
        stars_frame.pack(side="left", padx=(10, 0))

        # Создать звездное представление
        full_stars = int(self.average_rating)
        has_half_star = (self.average_rating - full_stars) >= 0.5

        for i in range(5):
            if i < full_stars:
                star_label = ttk.Label(stars_frame, text="★")  # Full star
            elif i == full_stars and has_half_star:
                star_label = ttk.Label(stars_frame, text="✯")  # Half star
            else:
                star_label = ttk.Label(stars_frame, text="☆")  # Empty star
            star_label.pack(side="left")

        # Список отзывов
        self.reviews_frame = ScrollableFrame(self)
        self.reviews_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Показать отзывы
        self.refresh_ratings()

    def refresh_ratings(self):
        """Обновить отображение рейтингов."""
        # Очистить предыдущие рейтинги
        for widget in self.reviews_frame.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.ratings_data:
            empty_label = ttk.Label(self.reviews_frame.scrollable_frame,
                                    text="Отзывов пока нет", font=("TkDefaultFont", 10, "italic"))
            empty_label.pack(pady=20)
            return

        # Создание карточек отзывов
        for rating in self.ratings_data:
            self.create_rating_card(rating)

    def create_rating_card(self, rating):
        """Создайте визуальную карточку для оценки/обзора."""
        card = ttk.Frame(self.reviews_frame.scrollable_frame, relief="solid", borderwidth=1)
        card.pack(fill="x", padx=5, pady=5, ipadx=5, ipady=5)

        # Заголовок рейтинга с именем клиента и звездами
        header_frame = ttk.Frame(card)
        header_frame.pack(fill="x", padx=5, pady=5)

        client_name = rating.get('client_name', 'Client')
        client_label = ttk.Label(header_frame, text=f"Отзыв от {client_name}",
                                 font=("TkDefaultFont", 10, "bold"))
        client_label.pack(side="left")

        # Звезды рейтинга
        stars_frame = ttk.Frame(header_frame)
        stars_frame.pack(side="right")

        for i in range(5):
            star_text = "★" if i < rating['rating'] else "☆"
            star_label = ttk.Label(stars_frame, text=star_text)
            star_label.pack(side="left")

        # Название работы
        if rating.get('job_title'):
            job_frame = ttk.Frame(card)
            job_frame.pack(fill="x", padx=5, pady=(0, 5))
            job_label = ttk.Label(job_frame, text=f"Название работы: {rating['job_title']}",
                                  font=("TkDefaultFont", 9, "italic"))
            job_label.pack(side="left")

        # Текст отзыва
        if rating.get('review'):
            review_frame = ttk.Frame(card)
            review_frame.pack(fill="x", padx=5, pady=5)
            review_label = ttk.Label(review_frame, text=rating['review'], wraplength=400)
            review_label.pack(fill="x", anchor="w")

        # Дата
        if rating.get('created_at'):
            date_frame = ttk.Frame(card)
            date_frame.pack(fill="x", padx=5, pady=(5, 0))

            date = rating['created_at'].split(' ')[0]  # Just get date part
            date_label = ttk.Label(date_frame, text=f"Опубликовано: {date}",
                                   font=("TkDefaultFont", 8))
            date_label.pack(side="right")

    def set_ratings_data(self, ratings_data, average_rating):
        """Обновите данные рейтингов и обновите отображение."""
        self.ratings_data = ratings_data
        self.average_rating = float(average_rating) if average_rating is not None else 0.0
        self.refresh_ratings()
