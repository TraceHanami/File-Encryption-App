import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from cryptography.fernet import Fernet, InvalidToken
from PIL import Image
import json, os, hashlib, base64, mimetypes
import tkinter as tk

USER_FILE = "users.json"
LOG_DIR = "user_logs"
os.makedirs(LOG_DIR, exist_ok=True)

app = ctk.CTk()
app.geometry("520x640")
app.minsize(480, 600)
app.title("🔐 SecureAccess - Personal File Vault")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

try:
    login_bg_img = ctk.CTkImage(Image.open(r"E:\jeswin website project\secure acess\assests\cyber_bg.png"), size=(520, 640))
    signup_bg_img = ctk.CTkImage(Image.open(r"E:\jeswin website project\secure acess\assests\cyber_bg2.png"), size=(520, 640))
    dashboard_bg_img = ctk.CTkImage(Image.open(r"E:\jeswin website project\secure acess\assests\cyber_bg.png"), size=(520, 640))
except:
    login_bg_img = signup_bg_img = dashboard_bg_img = None

logged_in_user = None

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({}, f)
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_fernet_key_from_user():
    user_key = simpledialog.askstring("Enter Key", "Enter encryption/decryption key:", show='*')
    if not user_key:
        raise ValueError("Key is required!")
    hashed = hashlib.sha256(user_key.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

def get_log_file(username):
    return os.path.join(LOG_DIR, f"filelog_{username}.json")

def load_file_log(username):
    path = get_log_file(username)
    if not os.path.exists(path):
        return {"encrypted": [], "decrypted": []}
    with open(path, 'r') as f:
        return json.load(f)

def save_file_log(username, log):
    with open(get_log_file(username), 'w') as f:
        json.dump(log, f)

login_frame = ctk.CTkFrame(app)
signup_frame = ctk.CTkFrame(app)
dashboard_frame = ctk.CTkFrame(app)

if login_bg_img:
    ctk.CTkLabel(login_frame, image=login_bg_img, text="").place(x=0, y=0, relwidth=1, relheight=1)
if signup_bg_img:
    ctk.CTkLabel(signup_frame, image=signup_bg_img, text="").place(x=0, y=0, relwidth=1, relheight=1)
if dashboard_bg_img:
    ctk.CTkLabel(dashboard_frame, image=dashboard_bg_img, text="").place(x=0, y=0, relwidth=1, relheight=1)

def switch_to_frame(target):
    for frame in (login_frame, signup_frame, dashboard_frame):
        frame.pack_forget()
    target.pack(expand=True, fill="both", pady=0)

def encrypt_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        try:
            key = get_fernet_key_from_user()
            fernet = Fernet(key)
            with open(filepath, 'rb') as file:
                original = file.read()
            encrypted = fernet.encrypt(original)
            with open(filepath, 'wb') as encrypted_file:
                encrypted_file.write(encrypted)
            log = load_file_log(logged_in_user)
            log["encrypted"].append(filepath)
            save_file_log(logged_in_user, log)
            update_dashboard()
            messagebox.showinfo("Success", "File encrypted successfully!")
        except Exception as e:
            messagebox.showerror("Encryption Failed", str(e))

def decrypt_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        try:
            key = get_fernet_key_from_user()
            fernet = Fernet(key)
            with open(filepath, 'rb') as enc_file:
                encrypted = enc_file.read()
            decrypted = fernet.decrypt(encrypted)
            with open(filepath, 'wb') as dec_file:
                dec_file.write(decrypted)
            log = load_file_log(logged_in_user)
            log["decrypted"].append(filepath)
            save_file_log(logged_in_user, log)
            update_dashboard()
            messagebox.showinfo("Success", "File decrypted successfully!")
        except InvalidToken:
            messagebox.showerror("Decryption Error", "Invalid key or corrupted file.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decrypt: {e}")

def clear_logs_and_preview():
    encrypted_list.delete("1.0", "end")
    decrypted_list.delete("1.0", "end")
    preview_box.configure(state="normal")
    preview_box.delete("1.0", "end")
    preview_box.configure(state="disabled")

def clear_login_entries():
    username_entry.delete(0, "end")
    password_entry.delete(0, "end")

ctk.CTkLabel(login_frame, text="🔐 Login to SecureAccess", font=("Arial", 20)).pack(pady=10)
username_entry = ctk.CTkEntry(login_frame, placeholder_text="Username")
username_entry.pack(pady=10)
password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*")
password_entry.pack(pady=10)
ctk.CTkButton(login_frame, text="Login", command=lambda: login()).pack(pady=10)
ctk.CTkButton(login_frame, text="Create Account", command=lambda: switch_to_frame(signup_frame), fg_color="gray").pack()

ctk.CTkLabel(signup_frame, text="🛡 Create Account", font=("Arial", 20)).pack(pady=10)
new_user_entry = ctk.CTkEntry(signup_frame, placeholder_text="New Username")
new_user_entry.pack(pady=10)
new_pwd_entry = ctk.CTkEntry(signup_frame, placeholder_text="Password", show="*")
new_pwd_entry.pack(pady=10)
confirm_pwd_entry = ctk.CTkEntry(signup_frame, placeholder_text="Confirm Password", show="*")
confirm_pwd_entry.pack(pady=10)
ctk.CTkButton(signup_frame, text="Sign Up", command=lambda: signup()).pack(pady=10)
ctk.CTkButton(signup_frame, text="Back to Login", command=lambda: switch_to_frame(login_frame), fg_color="gray").pack()

def login():
    user = username_entry.get().strip()
    pwd = password_entry.get().strip()
    users = load_users()
    if user in users and users[user] == hash_password(pwd):
        global logged_in_user
        logged_in_user = user
        messagebox.showinfo("Login Successful", f"Welcome, {user}!")
        switch_to_frame(dashboard_frame)
        update_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def signup():
    user = new_user_entry.get().strip()
    pwd = new_pwd_entry.get().strip()
    confirm = confirm_pwd_entry.get().strip()
    users = load_users()
    if not user or not pwd or not confirm:
        messagebox.showwarning("Input Error", "All fields are required.")
    elif pwd != confirm:
        messagebox.showerror("Password Error", "Passwords do not match.")
    elif user in users:
        messagebox.showerror("Username Exists", "Choose a different username.")
    else:
        users[user] = hash_password(pwd)
        save_users(users)
        messagebox.showinfo("Account Created", "You can now login.")
        switch_to_frame(login_frame)

dash_split = tk.PanedWindow(dashboard_frame, orient=tk.HORIZONTAL)
dash_split.pack(fill="both", expand=True)

logs_panel = ctk.CTkFrame(dash_split, width=300)
dash_split.add(logs_panel)
control_panel = ctk.CTkFrame(dash_split)
dash_split.add(control_panel)

ctk.CTkLabel(logs_panel, text="🔒 Encrypted Files", font=("Arial", 14)).pack(pady=(10, 0), anchor="w", padx=10)
encrypted_list = ctk.CTkTextbox(logs_panel, height=150, wrap="none")
encrypted_list.pack(pady=(5, 10), padx=10, fill="x")
ctk.CTkLabel(logs_panel, text="🔓 Decrypted Files", font=("Arial", 14)).pack(pady=(10, 0), anchor="w", padx=10)
decrypted_list = ctk.CTkTextbox(logs_panel, height=150, wrap="none")
decrypted_list.pack(pady=(5, 10), padx=10, fill="x")
ctk.CTkLabel(logs_panel, text="📝 File Preview", font=("Arial", 14)).pack(pady=(10, 0), anchor="w", padx=10)
preview_box = ctk.CTkTextbox(logs_panel, height=150, wrap="word", state="disabled")
preview_box.pack(padx=10, pady=5, fill="both", expand=True)
ctk.CTkButton(logs_panel, text="🧹 Clear", command=clear_logs_and_preview, fg_color="red").pack(pady=5, padx=10)

user_label = ctk.CTkLabel(control_panel, text="", font=("Arial", 20))
user_label.pack(pady=20)
ctk.CTkButton(control_panel, text="📤 Encrypt File", command=encrypt_file, width=240).pack(pady=10)
ctk.CTkButton(control_panel, text="📥 Decrypt File", command=decrypt_file, width=240).pack(pady=10)
ctk.CTkButton(control_panel, text="🚪 Logout", command=lambda: [clear_login_entries(), clear_logs_and_preview(), switch_to_frame(login_frame)], fg_color="gray", width=240).pack(pady=20)

def preview_file_content(event):
    widget = event.widget
    index = widget.index("@%s,%s" % (event.x, event.y))
    filepath = widget.get(index + " linestart", index + " lineend").strip()
    if os.path.isfile(filepath):
        preview_box.configure(state="normal")
        preview_box.delete("1.0", "end")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(1000)
            size = os.path.getsize(filepath)
            mimetype = mimetypes.guess_type(filepath)[0]
            info = f"📄 File: {os.path.basename(filepath)}\n📦 Size: {size} bytes\n🧩 Type: {mimetype}\n\n{content}"
            preview_box.insert("1.0", info)
        except:
            preview_box.insert("1.0", "⚠️ Cannot preview this file (binary or restricted)")
        preview_box.configure(state="disabled")

def update_dashboard():
    user_label.configure(text=f"👤 Welcome {logged_in_user}")
    encrypted_list.delete("1.0", "end")
    decrypted_list.delete("1.0", "end")
    preview_box.configure(state="normal")
    preview_box.delete("1.0", "end")
    preview_box.configure(state="disabled")
    log = load_file_log(logged_in_user)
    for file in log["encrypted"]:
        encrypted_list.insert("end", file + "\n")
    for file in log["decrypted"]:
        decrypted_list.insert("end", file + "\n")

encrypted_list.bind("<ButtonRelease-1>", preview_file_content)
decrypted_list.bind("<ButtonRelease-1>", preview_file_content)

switch_to_frame(login_frame)
app.mainloop()
