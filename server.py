import socket
import threading
import time

store = {}
expiry = {}
lock = threading.RLock()


def process(cmd):
    parts = cmd.split()
    op = parts[0].upper()

    with lock:
        if op == "SET" and len(parts) == 3:
            store[parts[1]] = parts[2]
            expiry.pop(parts[1], None)
            return "OK"
        elif op == "GET" and len(parts) == 2:
            key = parts[1]
            if key in expiry and time.time() > expiry[key]:
                store.pop(key, None)
                expiry.pop(key, None)
                return "nil"
            return store.get(key, "nil")
        elif op == "DEL" and len(parts) == 2:
            store.pop(parts[1], None)
            expiry.pop(parts[1], None)
            return "OK"
        elif op == "EXPIRE" and len(parts) == 3:
            key = parts[1]
            if key in store:
                expiry[key] = time.time() + int(parts[2])
                return "OK"
            return "nil"
        else:
            return "ERR unknown command"


def cleanup():
    while True:
        time.sleep(1)
        with lock:
            now = time.time()
            expired = [k for k, t in expiry.items() if now > t]
            for k in expired:
                store.pop(k, None)
                expiry.pop(k, None)
                print(f"Expired key: {k}")


def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            print(f"Received: {data}")
            response = process(data)
            conn.send((response + "\n").encode())
        except:
            break
    print(f"Client disconnected: {addr}")
    conn.close()


threading.Thread(target=cleanup, daemon=True).start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 6379))
server.listen(5)
print("mini-redis running on port 6379...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
