import socket
import threading

# 設定伺服器參數
HOST = '0.0.0.0'  # 綁定到所有本地 IP
PORT = 12345      # 任意未被佔用的埠
clients = []      # 儲存所有連接的用戶端

def handle_client(client_socket, client_address):
    print(f"[新連線] {client_address} 已連接")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"[收到訊息] {client_address}: {message}")
                broadcast(message, client_socket)
            else:
                remove_client(client_socket)
                break
        except:
            remove_client(client_socket)
            break

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove_client(client)

def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)
        client_socket.close()

# 啟動伺服器
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"[伺服器啟動] 在 {HOST}:{PORT} 等待連線...")

while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
