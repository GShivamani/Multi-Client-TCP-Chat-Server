"""
Multi-Client TCP Chat Server
A terminal chat application using Python sockets and threading.
Run server.py first, then connect multiple clients via client.py.
"""

# ─── server.py ────────────────────────────────────────────────
import socket
import threading
import json
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5555
MAX_CLIENTS = 10

clients = {}       # socket -> username
rooms = {"general": set(), "tech": set(), "random": set()}  # room -> set of sockets
lock = threading.Lock()


def broadcast(message, room="general", sender=None, msg_type="message"):
    packet = json.dumps({
        "type": msg_type,
        "room": room,
        "sender": sender or "Server",
        "message": message,
        "time": datetime.now().strftime("%H:%M")
    }).encode()

    with lock:
        targets = rooms.get(room, set()).copy()

    for client in targets:
        if client != sender:
            try:
                client.sendall(packet)
            except:
                pass


def dm(target_user, from_user, message):
    with lock:
        target_sock = next((s for s, u in clients.items() if u == target_user), None)
    if target_sock:
        packet = json.dumps({
            "type": "dm",
            "sender": from_user,
            "message": message,
            "time": datetime.now().strftime("%H:%M")
        }).encode()
        try:
            target_sock.sendall(packet)
            return True
        except:
            pass
    return False


def send_to(sock, msg_type, message, sender="Server"):
    try:
        sock.sendall(json.dumps({
            "type": msg_type,
            "sender": sender,
            "message": message,
            "time": datetime.now().strftime("%H:%M")
        }).encode())
    except:
        pass


def handle_client(conn, addr):
    username = None
    current_room = "general"

    try:
        # Get username
        send_to(conn, "system", "Enter your username: ")
        username = conn.recv(1024).decode().strip()

        with lock:
            if username in clients.values():
                send_to(conn, "error", f"Username '{username}' is taken. Disconnecting.")
                conn.close()
                return
            clients[conn] = username
            rooms["general"].add(conn)

        send_to(conn, "system",
                f"Welcome, {username}! You're in #general\n"
                f"Commands: /join <room> | /leave | /list | /users | /dm <user> <msg> | /rooms | /quit")
        broadcast(f"{username} joined the chat!", room="general", msg_type="system")
        print(f"[+] {username} connected from {addr}")

        while True:
            data = conn.recv(2048)
            if not data:
                break

            message = data.decode().strip()
            if not message:
                continue

            # Commands
            if message.startswith("/"):
                parts = message.split(" ", 2)
                cmd = parts[0].lower()

                if cmd == "/quit":
                    break

                elif cmd == "/rooms":
                    room_list = ", ".join(f"#{r} ({len(v)} users)" for r, v in rooms.items())
                    send_to(conn, "system", f"Available rooms: {room_list}")

                elif cmd == "/users":
                    with lock:
                        room_users = [clients[s] for s in rooms.get(current_room, set()) if s in clients]
                    send_to(conn, "system", f"Users in #{current_room}: {', '.join(room_users)}")

                elif cmd == "/list":
                    with lock:
                        all_users = list(clients.values())
                    send_to(conn, "system", f"Online users: {', '.join(all_users)}")

                elif cmd == "/join" and len(parts) > 1:
                    new_room = parts[1].lower()
                    if new_room not in rooms:
                        rooms[new_room] = set()
                    with lock:
                        rooms[current_room].discard(conn)
                        rooms[new_room].add(conn)
                    old_room = current_room
                    current_room = new_room
                    broadcast(f"{username} left", room=old_room, msg_type="system")
                    broadcast(f"{username} joined #{current_room}", room=current_room, msg_type="system")
                    send_to(conn, "system", f"Joined #{current_room}")

                elif cmd == "/leave":
                    with lock:
                        rooms[current_room].discard(conn)
                        rooms["general"].add(conn)
                    broadcast(f"{username} left #{current_room}", room=current_room, msg_type="system")
                    current_room = "general"
                    broadcast(f"{username} returned to #general", room="general", msg_type="system")
                    send_to(conn, "system", "Returned to #general")

                elif cmd == "/dm" and len(parts) >= 3:
                    target = parts[1]
                    msg = parts[2]
                    if dm(target, username, msg):
                        send_to(conn, "system", f"DM sent to {target}")
                    else:
                        send_to(conn, "error", f"User '{target}' not found or offline.")

                else:
                    send_to(conn, "error", "Unknown command.")
            else:
                broadcast(message, room=current_room, sender=conn, msg_type="message")
                # Also echo back to sender
                send_to(conn, "echo", f"[You → #{current_room}]: {message}")

    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        with lock:
            if conn in clients:
                gone_user = clients.pop(conn)
                for room in rooms.values():
                    room.discard(conn)
                if username:
                    broadcast(f"{gone_user} left the chat.", msg_type="system")
                    print(f"[-] {gone_user} disconnected.")
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)
    print(f"🚀 Chat Server started on {HOST}:{PORT}")
    print(f"   Max clients: {MAX_CLIENTS}")
    print(f"   Default rooms: {', '.join(rooms.keys())}")
    print("   Press Ctrl+C to stop\n")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
