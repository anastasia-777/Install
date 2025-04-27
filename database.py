import sqlite3
import hashlib
from typing import List, Optional

class Database:
    def __init__(self, db_file="freelance_app.db"):
        """Инициализируйте соединение с базой данных и создайте таблицы, если они не существуют."""
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Создайте все необходимые таблицы, если они не существуют."""
        # Таблица пользователей
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT NOT NULL,
            social_media TEXT,
            user_type TEXT NOT NULL,
            specialty TEXT,
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Таблица вакансий
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            client_id INTEGER NOT NULL,
            freelancer_id INTEGER,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES users (id),
            FOREIGN KEY (freelancer_id) REFERENCES users (id)
        )
        ''')

        # Таблица услуг (услуги, предлагаемые фрилансерами)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            freelancer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (freelancer_id) REFERENCES users (id)
        )
        ''')

        # Таблица сообщений
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            read INTEGER DEFAULT 0,
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (recipient_id) REFERENCES users (id)
        )
        ''')

        # Таблица рейтингов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            freelancer_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            review TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES users (id),
            FOREIGN KEY (freelancer_id) REFERENCES users (id),
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            UNIQUE (client_id, freelancer_id, job_id)
        )
        ''')

        # Таблица календаря занятости
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            freelancer_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            complexity TEXT NOT NULL,
            can_accept_more INTEGER DEFAULT 0,
            note TEXT,
            FOREIGN KEY (freelancer_id) REFERENCES users (id)
        )
        ''')

        self.conn.commit()

    def close(self):
        """Закрыть соединение с базой данных."""
        if self.conn:
            self.conn.close()

    def register_user(self, username: str, password: str, phone: str,
                      social_media: str, user_type: str, specialty: str) -> bool:
        """Зарегистрировать нового пользователя в базе данных."""
        try:
            password_hash = self._hash_password(password)
            self.cursor.execute(
                '''INSERT INTO users 
                   (username, password_hash, phone, social_media, user_type, specialty) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (username, password_hash, phone, social_media, user_type, specialty)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Имя пользователя, вероятно, уже существует
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Аутентификация пользователя."""
        self.cursor.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        )
        user = self.cursor.fetchone()

        if user and self._verify_password(password, user['password_hash']):
            return dict(user)
        return None

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля для хранения."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Проверьте сохраненный пароль на соответствие предоставленному паролю."""
        return self._hash_password(password) == stored_hash

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Получить пользователя по идентификатору."""
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = self.cursor.fetchone()
        return dict(user) if user else None

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Получить пользователя по имени пользователя."""
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()
        return dict(user) if user else None

    def add_job(self, title: str, description: str, client_id: int) -> int:
        """Добавить новую вакансию."""
        self.cursor.execute(
            '''INSERT INTO jobs (title, description, client_id, status) 
               VALUES (?, ?, ?, ?)''',
            (title, description, client_id, 'open')
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_job(self, job_id: int, title: str, description: str) -> bool:
        """Обновить сведения о вакансии."""
        try:
            self.cursor.execute(
                '''UPDATE jobs SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?''',
                (title, description, job_id)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def delete_job(self, job_id: int) -> bool:
        """Удалить вакансию."""
        try:
            self.cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_job(self, job_id: int) -> Optional[dict]:
        """Получить работу по ID."""
        self.cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job = self.cursor.fetchone()
        return dict(job) if job else None

    def get_open_jobs(self) -> List[dict]:
        """Получить все открытые вакансии."""
        self.cursor.execute("SELECT * FROM jobs WHERE status = 'open' ORDER BY created_at DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_client_jobs(self, client_id: int) -> List[dict]:
        """Получить все вакансии, опубликованные конкретным клиентом."""
        self.cursor.execute(
            "SELECT * FROM jobs WHERE client_id = ? ORDER BY created_at DESC", (client_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_freelancer_jobs(self, freelancer_id: int) -> List[dict]:
        """Получить все задания, назначенные конкретному фрилансеру."""
        self.cursor.execute(
            "SELECT * FROM jobs WHERE freelancer_id = ? ORDER BY created_at DESC",
            (freelancer_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def assign_job(self, job_id: int, freelancer_id: int) -> bool:
        """Назначение работы фрилансеру."""
        try:
            self.cursor.execute(
                '''UPDATE jobs SET freelancer_id = ?, status = 'assigned', 
                   updated_at = CURRENT_TIMESTAMP WHERE id = ?''',
                (freelancer_id, job_id)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def complete_job(self, job_id: int) -> bool:
        """Отметить вакансию как завершенную."""
        try:
            self.cursor.execute(
                '''UPDATE jobs SET status = 'completed', updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?''',
                (job_id,)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def add_service(self, freelancer_id: int, title: str, description: str) -> int:
        """Добавить новую услугу от фрилансера."""
        self.cursor.execute(
            "INSERT INTO services (freelancer_id, title, description) VALUES (?, ?, ?)",
            (freelancer_id, title, description)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_service(self, service_id: int, title: str, description: str) -> bool:
        """Обновить сведения об услуге."""
        try:
            self.cursor.execute(
                "UPDATE services SET title = ?, description = ? WHERE id = ?",
                (title, description, service_id)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def delete_service(self, service_id: int) -> bool:
        """Удалить услугу."""
        try:
            self.cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_freelancer_services(self, freelancer_id: int) -> List[dict]:
        """Получите все услуги, предлагаемые конкретным фрилансером."""
        self.cursor.execute(
            "SELECT * FROM services WHERE freelancer_id = ?", (freelancer_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def send_message(self, sender_id: int, recipient_id: int, content: str) -> int:
        """Отправить сообщение от одного пользователя другому."""
        self.cursor.execute(
            "INSERT INTO messages (sender_id, recipient_id, content) VALUES (?, ?, ?)",
            (sender_id, recipient_id, content)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_messages(self, user1_id: int, user2_id: int) -> List[dict]:
        """Получить все сообщения между двумя пользователями."""
        self.cursor.execute(
            '''SELECT * FROM messages 
               WHERE (sender_id = ? AND recipient_id = ?) 
               OR (sender_id = ? AND recipient_id = ?) 
               ORDER BY sent_at ASC''',
            (user1_id, user2_id, user2_id, user1_id)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_conversations(self, user_id: int) -> List[dict]:
        """Получить всех пользователей, с которыми текущий пользователь общается."""
        query = '''
        SELECT DISTINCT u.id, u.username, u.user_type 
        FROM users u
        JOIN messages m ON (m.sender_id = u.id OR m.recipient_id = u.id)
        WHERE (m.sender_id = ? OR m.recipient_id = ?) 
        AND u.id != ?
        '''
        self.cursor.execute(query, (user_id, user_id, user_id))
        return [dict(row) for row in self.cursor.fetchall()]

    def mark_messages_as_read(self, sender_id: int, recipient_id: int) -> bool:
        """Отметить все сообщения от отправителя к получателю как прочитанные."""
        try:
            self.cursor.execute(
                "UPDATE messages SET read = 1 WHERE sender_id = ? AND recipient_id = ?",
                (sender_id, recipient_id)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def delete_conversation(self, user1_id: int, user2_id: int) -> bool:
        """Удалить все сообщения между двумя пользователями."""
        try:
            self.cursor.execute(
                '''DELETE FROM messages 
                   WHERE (sender_id = ? AND recipient_id = ?) 
                   OR (sender_id = ? AND recipient_id = ?)''',
                (user1_id, user2_id, user2_id, user1_id)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def add_rating(self, client_id: int, freelancer_id: int, job_id: int,
                   rating: int, review: str) -> bool:
        """Добавьте оценку и отзыв о фрилансере."""
        try:
            self.cursor.execute(
                '''INSERT INTO ratings 
                   (client_id, freelancer_id, job_id, rating, review) 
                   VALUES (?, ?, ?, ?, ?)''',
                (client_id, freelancer_id, job_id, rating, review)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Рейтинг этой вакансии от этого клиента уже существует
            return False

    def get_freelancer_ratings(self, freelancer_id: int) -> List[dict]:
        """Получить все рейтинги конкретного фрилансера."""
        query = '''
        SELECT r.*, u.username as client_name, j.title as job_title
        FROM ratings r
        JOIN users u ON r.client_id = u.id
        JOIN jobs j ON r.job_id = j.id
        WHERE r.freelancer_id = ?
        ORDER BY r.created_at DESC
        '''
        self.cursor.execute(query, (freelancer_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_average_rating(self, freelancer_id: int) -> float:
        """Получить средний рейтинг конкретного фрилансера."""
        self.cursor.execute(
            "SELECT AVG(rating) as avg_rating FROM ratings WHERE freelancer_id = ?",
            (freelancer_id,)
        )
        result = self.cursor.fetchone()
        return result['avg_rating'] if result and result['avg_rating'] else 0.0

    def add_availability(self, freelancer_id: int, start_date: str, end_date: str,
                         complexity: str, can_accept_more: bool, note: str) -> int:
        """Добавьте новый период занятости для фрилансера."""
        self.cursor.execute(
            '''INSERT INTO availability 
               (freelancer_id, start_date, end_date, complexity, can_accept_more, note) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (freelancer_id, start_date, end_date, complexity, int(can_accept_more), note)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_availability(self, availability_id: int, start_date: str, end_date: str,
                            complexity: str, can_accept_more: bool, note: str) -> bool:
        """Обновить сведения о занятости."""
        try:
            self.cursor.execute(
                '''UPDATE availability 
                   SET start_date = ?, end_date = ?, complexity = ?, 
                       can_accept_more = ?, note = ? 
                   WHERE id = ?''',
                (start_date, end_date, complexity, int(can_accept_more), note, availability_id)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def delete_availability(self, availability_id: int) -> bool:
        """Удалить период занятости."""
        try:
            self.cursor.execute("DELETE FROM availability WHERE id = ?", (availability_id,))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_freelancer_availability(self, freelancer_id: int) -> List[dict]:
        """Получить все периоды занястоти для конкретного фрилансера."""
        self.cursor.execute(
            "SELECT * FROM availability WHERE freelancer_id = ? ORDER BY start_date",
            (freelancer_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_freelancers(self) -> List[dict]:
        """Получить всех пользователей-фрилансеров."""
        self.cursor.execute(
            "SELECT id, username, specialty FROM users WHERE user_type = 'freelancer'"
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_clients(self) -> List[dict]:
        """Получить всех пользователей, которые являются клиентами."""
        self.cursor.execute(
            "SELECT id, username FROM users WHERE user_type = 'client'"
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def is_username_taken(self, username: str) -> bool:
        """Проверьте, занято ли имя пользователя."""
        self.cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return bool(self.cursor.fetchone())
