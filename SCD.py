import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from typing import List, Optional
import uuid
import hashlib
import os

class Database:
    def __init__(self, db_name="task_management.db"):
        self.db_name = db_name
        self.create_tables()
    
    def create_tables(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL,
                    user_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create Tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT,
                    deadline TIMESTAMP,
                    category TEXT,
                    status TEXT DEFAULT 'New',
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (user_id)
                )
            ''')
            
            # Create Task Assignments table (many-to-many relationship)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_assignments (
                    task_id TEXT,
                    user_id TEXT,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (task_id, user_id),
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Create Notes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    note_id TEXT PRIMARY KEY,
                    task_id TEXT,
                    content TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                    FOREIGN KEY (created_by) REFERENCES users (user_id)
                )
            ''')
            
            # Create Reminders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    reminder_id TEXT PRIMARY KEY,
                    task_id TEXT,
                    description TEXT,
                    reminder_time TIMESTAMP,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                    FOREIGN KEY (created_by) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    # User Management Methods
    def create_user(self, username: str, password: str, email: str, user_type: str) -> str:
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(password)
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, username, password, email, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, hashed_password, email, user_type))
            conn.commit()
        return user_id
    
    def verify_user(self, username: str, password: str) -> Optional[tuple]:
        hashed_password = self.hash_password(password)
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, email, user_type
                FROM users
                WHERE username = ? AND password = ?
            ''', (username, hashed_password))
            return cursor.fetchone()
    
    # Task Management Methods
    def create_task(self, title: str, description: str, priority: str,
                   deadline: datetime, category: str, created_by: str) -> str:
        task_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (task_id, title, description, priority,
                                 deadline, category, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_id, title, description, priority,
                 deadline, category, created_by))
            conn.commit()
        return task_id
    
    def assign_task(self, task_id: str, user_id: str):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO task_assignments (task_id, user_id)
                VALUES (?, ?)
            ''', (task_id, user_id))
            conn.commit()
    
    def get_user_tasks(self, user_id: str) -> List[tuple]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*
                FROM tasks t
                JOIN task_assignments ta ON t.task_id = ta.task_id
                WHERE ta.user_id = ?
            ''', (user_id,))
            return cursor.fetchall()
    
    def get_created_tasks(self, user_id: str) -> List[tuple]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tasks WHERE created_by = ?
            ''', (user_id,))
            return cursor.fetchall()
    
    def update_task_status(self, task_id: str, status: str):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks SET status = ? WHERE task_id = ?
            ''', (status, task_id))
            conn.commit()
    
    # Note Management Methods
    def add_note(self, task_id: str, content: str, created_by: str) -> str:
        note_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notes (note_id, task_id, content, created_by)
                VALUES (?, ?, ?, ?)
            ''', (note_id, task_id, content, created_by))
            conn.commit()
        return note_id
    
    def get_task_notes(self, task_id: str) -> List[tuple]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM notes WHERE task_id = ?
                ORDER BY created_at DESC
            ''', (task_id,))
            return cursor.fetchall()
    
    # Reminder Management Methods
    def add_reminder(self, task_id: str, description: str,
                    reminder_time: datetime, created_by: str) -> str:
        reminder_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reminders (reminder_id, task_id, description,
                                     reminder_time, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (reminder_id, task_id, description, reminder_time, created_by))
            conn.commit()
        return reminder_id
    
    def get_task_reminders(self, task_id: str) -> List[tuple]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM reminders WHERE task_id = ?
                ORDER BY reminder_time ASC
            ''', (task_id,))
            return cursor.fetchall()

# Modified User class to work with database
class User:
    def __init__(self, db: Database, user_id: str, username: str, email: str, user_type: str):
        self.db = db
        self.userID = user_id
        self.username = username
        self.email = email
        self.user_type = user_type
        self.logged_in = True
    
    @classmethod
    def login(cls, db: Database, username: str, password: str) -> Optional['User']:
        user_data = db.verify_user(username, password)
        if user_data:
            user_id, username, email, user_type = user_data
            if user_type == "Manager":
                return Manager(db, user_id, username, email)
            elif user_type == "Employee":
                return Employee(db, user_id, username, email)
            elif user_type == "Admin":
                return Admin(db, user_id, username, email)
        return None
    
    def logout(self):
        self.logged_in = False

class Employee(User):
    def __init__(self, db: Database, user_id: str, username: str, email: str):
        super().__init__(db, user_id, username, email, "Employee")
    
    def get_assigned_tasks(self) -> List[tuple]:
        return self.db.get_user_tasks(self.userID)
    
    def update_task_status(self, task_id: str, status: str):
        self.db.update_task_status(task_id, status)
    
    def add_note(self, task_id: str, note: str):
        self.db.add_note(task_id, note, self.userID)
    
    def set_reminder(self, task_id: str, description: str, reminder_time: datetime):
        self.db.add_reminder(task_id, description, reminder_time, self.userID)

class Manager(User):
    def __init__(self, db: Database, user_id: str, username: str, email: str):
        super().__init__(db, user_id, username, email, "Manager")
    
    def create_task(self, title: str, description: str, priority: str,
                   deadline: datetime, category: str) -> str:
        return self.db.create_task(title, description, priority,
                                 deadline, category, self.userID)
    
    def assign_task(self, task_id: str, employee_id: str):
        self.db.assign_task(task_id, employee_id)
    
    def get_created_tasks(self) -> List[tuple]:
        return self.db.get_created_tasks(self.userID)

class Admin(User):
    def __init__(self, db: Database, user_id: str, username: str, email: str):
        super().__init__(db, user_id, username, email, "Admin")
    
    def create_account(self, username: str, password: str, email: str, user_type: str) -> str:
        return self.db.create_user(username, password, email, user_type)

# Modified TaskManagementSystem to work with database
class TaskManagementSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Task Management System")
        self.geometry("800x600")
        
        # Initialize database
        self.db = Database()
        self.current_user = None
        
        # Create admin account if it doesn't exist
        self.initialize_admin()
        
        self.create_login_frame()
    
    def initialize_admin(self):
        # Try to verify if admin exists
        if not self.db.verify_user("admin", "admin123"):
            self.db.create_user("admin", "admin123", "admin@example.com", "Admin")
            # Create sample manager and employee accounts
            manager_id = self.db.create_user("manager", "manager123", "manager@example.com", "Manager")
            employee_id = self.db.create_user("employee", "employee123", "employee@example.com", "Employee")
    
    # Rest of the TaskManagementSystem class implementation remains similar,
    # but modified to use the database methods instead of in-memory storage

if __name__ == "__main__":
    app = TaskManagementSystem()
    app.mainloop()\
