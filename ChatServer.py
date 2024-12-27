import socket
import threading
import sys
import signal

# 設定伺服器參數
HOST = '127.0.0.1'
PORT = 12345
clients = {}  # 儲存客戶端 socket 與暱稱的對應關係

def handle_client(client_socket, client_address):
    print(f"[新連線] {client_address} 已連接")

    # 要求暱稱
    # client_socket.send("請輸入暱稱：".encode('utf-8'))
    try:
        nickname = client_socket.recv(1024).decode('utf-8')
        if not nickname:
            raise ValueError("暱稱不可為空")
    except Exception as e:
        print(f"[錯誤] {client_address} 暱稱設定失敗：{e}")
        client_socket.close()
        return

    # 儲存暱稱並通知其他使用者
    clients[client_socket] = nickname
    print(f"[暱稱設定] {nickname} 已加入聊天室")
    broadcast(f"[系統訊息] {nickname} 加入聊天室！")

    # 處理訊息
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"[收到訊息] {nickname}: {message}")
                broadcast(message, client_socket)
            else:
                remove_client(client_socket)
                break
        except:
            remove_client(client_socket)
            break

def broadcast(message, sender_socket=None):
    """
    廣播訊息給所有連接的客戶端。
    sender_socket: 發送訊息的客戶端 socket，若為 None，則不排除任何人。
    """
    if sender_socket == None: # 廣播
        for client in clients:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove_client(client)
    else: # 私訊
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(f"{clients[sender_socket]}: {message}".encode('utf-8'))
                except:
                    remove_client(client)

def remove_client(client_socket):
    """
    移除已斷開的客戶端並通知其他使用者。
    """
    if client_socket in clients:
        nickname = clients[client_socket]
        print(f"[斷線] {nickname} 離開聊天室")
        broadcast(f"[系統訊息] {nickname} 離開聊天室！")
        del clients[client_socket]
    client_socket.close()

def server_cleanup(signum, frame):
    """
    當伺服器收到終止信號時，進行清理工作。
    """
    print("\n[伺服器關閉] 接收到終止信號，正在進行清理工作...")
    for client in clients:
        try:
            client.close()
        except Exception as e:
            print(f"[錯誤] 關閉客戶端連線時出現問題: {e}")
    try:
        server_socket.close()
    except Exception as e:
        print(f"[錯誤] 關閉伺服器連線時出現問題: {e}")
    sys.exit(0)

# 設定處理 SIGINT 信號，並執行 server_cleanup 函數
signal.signal(signal.SIGINT, server_cleanup)
# 啟動伺服器
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"[伺服器啟動] 在 {HOST}:{PORT} 等待連線...")

while True:
    client_socket, client_address = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
