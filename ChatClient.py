import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# 設定伺服器 IP 和埠
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("聊天室")
        self.master.geometry("400x500")

        # 聊天記錄區
        self.chat_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, state='disabled', height=20)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 訊息輸入區
        self.input_frame = tk.Frame(self.master)
        self.input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.input_area = tk.Entry(self.input_frame, font=("Arial", 14))
        self.input_area.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 發送按鈕
        self.send_button = tk.Button(self.input_frame, text="發送", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # 連線按鈕
        self.connect_button = tk.Button(self.master, text="連線", command=self.connect_to_server)
        self.connect_button.pack(pady=(0, 10))

        # 綁定 Enter 鍵事件
        self.input_area.bind("<Return>", self.send_message_event)

        # 初始化變數
        self.client_socket = None
        self.is_connected = False

    def connect_to_server(self):
        if not self.is_connected:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((SERVER_HOST, SERVER_PORT))
                self.is_connected = True

                # 啟動接收訊息的執行緒
                threading.Thread(target=self.receive_messages, daemon=True).start()
                self.display_message("[系統訊息] 成功連線到伺服器！")
            except Exception as e:
                messagebox.showerror("錯誤", f"無法連線到伺服器：{e}")

    def receive_messages(self):
        while self.is_connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message)
            except:
                self.display_message("[系統訊息] 與伺服器斷開連線")
                self.is_connected = False
                break

    def send_message(self, event=None):
        # 確保不會對 event 參數進行強制解包
        message = self.input_area.get()
        if message and self.is_connected:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.display_message(f"[我] {message}")  # 顯示使用者發送的訊息
                self.input_area.delete(0, tk.END)
            except:
                self.display_message("[系統訊息] 訊息無法發送，請檢查連線")
        elif not self.is_connected:
            messagebox.showwarning("警告", "尚未連線到伺服器！")

    def send_message_event(self, event):
        # 當按下 Enter 鍵時觸發發送訊息
        self.send_message()

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

# 啟動主程式
if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
