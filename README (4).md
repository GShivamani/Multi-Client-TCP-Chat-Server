# 💬 Multi-Client TCP Chat Server

> A real-time terminal chat system using Python sockets and multithreading — supports rooms, direct messages, and multiple concurrent users.

---

## 📌 Description

A socket-based multi-client chat application demonstrating core networking concepts. Features multi-room chat, direct messaging, live user lists, and concurrent client handling via threads — all over raw TCP with a lightweight JSON protocol.

---

## 🛠️ Tech Stack

- Python 3.x
- Standard Library only (`socket`, `threading`, `json`)

---

## 🚀 Getting Started

```bash
git clone https://github.com/yourusername/tcp-chat-server.git
cd tcp-chat-server

# Terminal 1 — Start the server
python server.py

# Terminal 2, 3, ... — Start clients
python client.py
```

---

## 💻 Chat Commands

| Command | Description |
|---|---|
| `/rooms` | List all available rooms |
| `/join <room>` | Join or create a room |
| `/leave` | Return to #general |
| `/users` | List users in current room |
| `/list` | List all online users |
| `/dm <user> <msg>` | Send a private message |
| `/quit` | Disconnect |

---

## 📂 Project Structure

```
tcp-chat-server/
├── server.py    # Multithreaded server with room management
├── client.py    # Terminal client with colored output
└── README.md
```

---

## 🧠 Concepts Covered

- TCP socket programming
- Multithreading with thread safety (`threading.Lock`)
- Client-server architecture
- Custom application protocol (JSON over TCP)
- Broadcast and unicast messaging

---

## 🌐 Protocol Format

```json
{
  "type": "message | system | dm | error | echo",
  "sender": "username",
  "room": "general",
  "message": "Hello!",
  "time": "14:32"
}
```

---

## ⚙️ Configuration

Edit at the top of `server.py`:
```python
HOST = "127.0.0.1"
PORT = 5555
MAX_CLIENTS = 10
```

---

## 📄 License

MIT
