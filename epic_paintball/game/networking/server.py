import socket, threading, argparse, json, time

# Simple newline-delimited JSON protocol: {type:'snapshot', name:'...', x:..., y:...}
# This is intentionally minimal for a local LAN test only.

def handle_client(conn, addr, clients):
    buf = b""
    name = f"{addr[0]}:{addr[1]}"
    try:
        while True:
            data = conn.recv(4096)
            if not data: break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                try:
                    msg = json.loads(line.decode("utf-8"))
                    if msg.get("type") == "hello":
                        name = msg.get("name", name)
                    # broadcast to others
                    wire = (json.dumps(msg) + "\n").encode("utf-8")
                    for c in list(clients):
                        if c is not conn:
                            try: c.sendall(wire)
                            except: pass
                except Exception:
                    pass
    finally:
        try: conn.close()
        except: pass
        if conn in clients:
            clients.remove(conn)
        print("Disconnected:", name)

def run_server(host, port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(16)
    print(f"Server listening on {host}:{port}")
    clients = []
    try:
        while True:
            conn, addr = srv.accept()
            print("Connected:", addr)
            clients.append(conn)
            threading.Thread(target=handle_client, args=(conn, addr, clients), daemon=True).start()
    finally:
        srv.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=5050)
    args = ap.parse_args()
    run_server(args.host, args.port)
