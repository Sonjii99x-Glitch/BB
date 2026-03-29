import tkinter as tk
import requests
import time
import threading
import json
import os
import winsound
from tkinter import messagebox, simpledialog

class PisoNetClient:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg='black')

        self.state = 'LOCKED'
        self.server_ip = '192.168.1.100'  # Load from settings
        self.client_id = 'client1'
        self.session_time = 0
        self.logged_in_user = None

        self.load_settings()

        self.create_ui()

        # Block keys
        self.root.bind('<Alt-Tab>', lambda e: 'break')
        self.root.bind('<Alt-F4>', lambda e: 'break')
        self.root.bind('<KeyPress>', self.on_key_press)

        # Start polling
        threading.Thread(target=self.poll_server, daemon=True).start()

    def load_settings(self):
        settings_path = r'C:\Program Files\PisoNetClient\settings.json'
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                self.server_ip = settings.get('server_ip', self.server_ip)

    def create_ui(self):
        self.label = tk.Label(self.root, text="INSERT COIN", font=("Arial", 48), fg="white", bg="black")
        self.label.pack(expand=True)

        self.login_button = tk.Button(self.root, text="LOGIN", command=self.show_login, bg="gray", fg="white")
        self.login_button.pack(side=tk.BOTTOM, pady=20)

        self.start_button = tk.Button(self.root, text="START PLAYING", command=self.start_session, bg="green", fg="white")
        self.start_button.pack_forget()

    def on_key_press(self, event):
        if event.keysym == 'F10':
            self.show_admin_panel()
        return 'break'

    def poll_server(self):
        while True:
            try:
                response = requests.get(f'http://{self.server_ip}:5000/coin_status')
                data = response.json()
                if data['coins'] > 0 and self.state == 'INSERT_MODE':
                    self.state = 'CREDIT_READY'
                    self.root.after(0, self.show_start_button)
                if self.state == 'ACTIVE_SESSION':
                    requests.post(f'http://{self.server_ip}:5000/heartbeat', json={'client_id': self.client_id})
            except:
                pass
            time.sleep(1)

    def insert_coin(self):
        if self.state == 'LOCKED':
            self.state = 'INSERT_MODE'
            self.label.config(text="INSERTING COIN...")
            try:
                response = requests.post(f'http://{self.server_ip}:5000/start_coin_session', json={'client_id': self.client_id, 'user': self.logged_in_user})
                if response.json()['status'] == 'started':
                    pass  # Wait for coins
            except:
                messagebox.showerror("Error", "Cannot connect to server")

    def show_start_button(self):
        self.start_button.pack()

    def start_session(self):
        self.state = 'ACTIVE_SESSION'
        self.label.config(text="SESSION ACTIVE")
        self.start_button.pack_forget()
        # Start timer popup
        self.show_timer_popup()

    def show_timer_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Timer")
        popup.geometry("200x100")
        timer_label = tk.Label(popup, text="00:00", font=("Arial", 24))
        timer_label.pack(expand=True)
        # Simple countdown, in real app sync with server
        def countdown():
            nonlocal timer_label
            for i in range(3600, 0, -1):  # 1 hour example
                timer_label.config(text=f"{i//60:02d}:{i%60:02d}")
                time.sleep(1)
            popup.destroy()
            self.end_session()
        threading.Thread(target=countdown, daemon=True).start()

    def end_session(self):
        self.state = 'LOCKED'
        self.label.config(text="INSERT COIN")
        try:
            requests.post(f'http://{self.server_ip}:5000/stop_coin_session', json={'client_id': self.client_id})
        except:
            pass

    def show_login(self):
        username = simpledialog.askstring("Login", "Username:")
        password = simpledialog.askstring("Login", "Password:", show='*')
        if username and password:
            try:
                response = requests.post(f'http://{self.server_ip}:5000/user_login', json={'username': username, 'password': password})
                if response.json()['valid']:
                    self.logged_in_user = username
                    self.session_time = response.json()['time_remaining']
                    messagebox.showinfo("Login", f"Logged in as {username}. Time remaining: {self.session_time} min")
                else:
                    messagebox.showerror("Error", "Invalid credentials")
            except:
                messagebox.showerror("Error", "Cannot connect to server")

    def show_admin_panel(self):
        # Simple admin panel, in real app more features
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel")
        tk.Button(admin_window, text="Force Unlock", command=self.force_unlock).pack()
        tk.Button(admin_window, text="Add Time", command=self.add_time).pack()

    def force_unlock(self):
        self.end_session()

    def add_time(self):
        # Add time logic
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PisoNetClient(root)
    root.mainloop()