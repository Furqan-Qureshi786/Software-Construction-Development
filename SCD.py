import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from typing import List, Optional
import uuid
import hashlib
import os

class Database:
    def __init__(self, db_path=r"C:\Users\Haris Khan\Desktop\Software-Construction-Development\task_management.db"):
        self.db_name = db_path
        # self.create_tables()

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
    app.mainloop()
