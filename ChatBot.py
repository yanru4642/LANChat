import socket
import threading
import requests
import json

# Ollama 配置
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "gemma:2b"

# 伺服器配置
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12345

# 客戶端名稱
BOT_NAME = "ChatBot"

# 與 Ollama 交互的函數
def get_ollama_response(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt},
            stream=True  # 啟用流式回應
        )
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    part = json.loads(line)
                    full_response += part.get("response", "")
                    if part.get("done", False):
                        break
            return full_response
        else:
            return f"錯誤: {response.status_code}, {response.text}"
    except Exception as e:
        return f"無法連接到 Ollama: {e}"

# 接收訊息的執行緒
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"[收到訊息]: {message}")
                # 如果訊息不是來自 ChatBot 自己，則處理
                if not message.startswith(f"{BOT_NAME}:"):
                    response = get_ollama_response(message)
                    send_message(client_socket, f"{BOT_NAME}: {response}")
        except Exception as e:
            print(f"[錯誤] 與伺服器斷開連線: {e}")
            client_socket.close()
            break

# 發送訊息的函數
def send_message(client_socket, message):
    try:
        client_socket.send(message.encode('utf-8'))
    except Exception as e:
        print(f"[錯誤] 無法發送訊息: {e}")

# 主函數
def main():
    # 連接到伺服器
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[連線成功] 已連接到伺服器 {SERVER_HOST}:{SERVER_PORT}")

        # 啟動接收訊息的執行緒
        threading.Thread(target=receive_messages, args=(client_socket,)).start()

        # ChatBot 不需要主動發送訊息，讓執行緒持續運行
        while True:
            pass

    except Exception as e:
        print(f"[錯誤] 無法連接到伺服器: {e}")
        client_socket.close()

if __name__ == "__main__":
    main()
