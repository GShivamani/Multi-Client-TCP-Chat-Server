"""
Chat Client
Connect to the chat server. Run after starting server.py.
Usage: python client.py [host] [port]
"""

import socket
import threading
import json
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5555

COLORS = {
    "message": "\033[97m",
    "system":  "\033[93m",
    "error":   "\033[91m",
    "dm":      "\033[95m",
    "echo":    "\033[90m",
    "reset":   "\033[0m"
}


def receive(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("\n[Disconnected from server]")
                break
            packet = json.loads(data.decode())
            msg_type = packet.get("type", "message")
            color = COLORS.get(msg_type, COLORS["message"])
            reset = COLORS["reset"]

            if msg_type == "message":
                print(f"\r{color}[{packet['time']}] {packet['sender']}: {packet['message']}{reset}")
            elif msg_type == "echo":
                print(f"\r{color}{packet['message']}{reset}")
            elif msg_type == "dm":
                print(f"\r{color}[DM from {packet['sender']}]: {packet['message']}{reset}")
            elif msg_type in ("system", "error"):
                print(f"\r{color}>>> {packet['message']}{reset}")

            print("> ", end="", flush=True)
        except json.JSONDecodeError:
            pass
        except Exception:
            break


def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print(f"✅ Connected to {HOST}:{PORT}")
    except ConnectionRefusedError:
        print(f"❌ Could not connect to {HOST}:{PORT}. Is the server running?")
        sys.exit(1)

    threading.Thread(target=receive, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input("> ").strip()
            if msg:
                sock.sendall(msg.encode())
                if msg == "/quit":
                    break
    except (KeyboardInterrupt, EOFError):
        sock.sendall(b"/quit")
    finally:
        sock.close()
        print("\n👋 Disconnected.")


if __name__ == "__main__":
    main()
