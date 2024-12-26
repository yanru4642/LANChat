import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

# 設定伺服器 IP 和埠
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("聊天室")
        self.master.geometry("400x500")

        # 設定 Grid 欄位比例
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # 聊天記錄區
        self.chat_area = scrolledtext.ScrolledText(
            self.master, wrap=tk.WORD, state='disabled', font=("Arial", 16), spacing3=5
        )
        self.chat_area.tag_configure("self", foreground="blue")
        self.chat_area.tag_configure("other", foreground="black")
        self.chat_area.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 訊息輸入區
        self.input_frame = tk.Frame(self.master)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.input_frame.grid_columnconfigure(0, weight=1)  # 讓輸入框自適應寬度

        self.input_area = tk.Entry(self.input_frame, font=("Arial", 16))
        self.input_area.grid(row=0, column=0, padx=5, sticky="ew")
        self.input_area.focus_set()  # 自動聚焦輸入框

        # 發送按鈕
        self.send_button = tk.Button(self.input_frame, text="發送", command=self.send_message, font=("Arial", 14))
        self.send_button.grid(row=0, column=1, padx=5)

        # 綁定 Enter 鍵事件
        self.input_area.bind("<Return>", self.send_message_event)

        # 初始化變數
        self.client_socket = None
        self.is_connected = False
        self.nickname = None

        # 啟動時顯示主視窗並請求暱稱
        self.master.after(100, self.request_nickname_and_connect)

    def request_nickname_and_connect(self):
        while not self.nickname:
            dialog = tk.Toplevel(self.master)
            dialog.title("輸入暱稱")
            dialog.geometry("300x150")

            dialog_label = tk.Label(dialog, text="請輸入您的暱稱：", font=("Arial", 16))
            dialog_label.pack(pady=10)

            nickname_entry = tk.Entry(dialog, font=("Arial", 16))
            nickname_entry.pack(pady=5, padx=10, fill=tk.X)
            nickname_entry.focus_set()  # 自動聚焦輸入框

            def submit_nickname(event=None):
                self.nickname = nickname_entry.get().strip()
                if self.nickname:
                    dialog.destroy()
                else:
                    messagebox.showwarning("警告", "暱稱不可為空！", parent=dialog)

            def close_program():
                self.master.destroy()

            nickname_entry.bind("<Return>", submit_nickname)
            submit_button = tk.Button(dialog, text="確定", command=submit_nickname, font=("Arial", 14))
            submit_button.pack(pady=10)

            dialog.protocol("WM_DELETE_WINDOW", close_program)
            self.master.wait_window(dialog)

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            self.client_socket.send(self.nickname.encode('utf-8'))
            self.is_connected = True

            # 啟動接收訊息的執行緒
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.display_message(f"[系統訊息] 已連線到伺服器！", tag="other")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法連線到伺服器：{e}")
            self.master.destroy()

    def receive_messages(self):
        while self.is_connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message, tag="other")
            except:
                self.display_message("[系統訊息] 與伺服器斷開連線", tag="other")
                self.is_connected = False
                break

    def send_message(self, event=None):
        message = self.input_area.get()
        if message and self.is_connected:
            try:
                formatted_message = f"{self.nickname}: {message}"
                self.client_socket.send(formatted_message.encode('utf-8'))
                self.display_message(formatted_message, tag="self")
                self.input_area.delete(0, tk.END)
            except:
                self.display_message("[系統訊息] 訊息無法發送，請檢查連線", tag="other")
        elif not self.is_connected:
            messagebox.showwarning("警告", "尚未連線到伺服器！")

    def send_message_event(self, event):
        self.send_message()

    def display_message(self, message, tag="other"):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n", tag)
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

# 啟動主程式
if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()