import socket
import threading

# 設定伺服器 IP 和埠
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"[訊息]: {message}")
        except:
            print("[錯誤] 與伺服器斷開連線")
            client_socket.close()
            break

# 連接到伺服器
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

print("[連線成功] 輸入訊息開始聊天，輸入 'exit' 離開")

# 啟動接收訊息的執行緒
threading.Thread(target=receive_messages, args=(client_socket,)).start()

while True:
    message = input()
    if message.lower() == 'exit':
        client_socket.close()
        break
    client_socket.send(message.encode('utf-8'))
