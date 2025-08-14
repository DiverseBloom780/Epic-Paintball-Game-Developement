import socket, json, threading, queue

class NetClient:
    def __init__(self, host, port, name="Player"):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.inbox = queue.Queue()
        hello = json.dumps({"type":"hello","name":name}) + "\n"
        self.sock.sendall(hello.encode("utf-8"))
        self._start_reader()

    def _start_reader(self):
        def _reader():
            buf = b""
            try:
                while True:
                    data = self.sock.recv(4096)
                    if not data: break
                    buf += data
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            msg = json.loads(line.decode("utf-8"))
                            self.inbox.put(msg)
                        except: pass
            finally:
                self.sock.close()
        threading.Thread(target=_reader, daemon=True).start()

    def send_snapshot(self, name, x, y):
        msg = json.dumps({"type":"snapshot","name":name,"x":x,"y":y}) + "\n"
        try:
            self.sock.sendall(msg.encode("utf-8"))
        except:
            pass

    def poll(self):
        items = []
        while not self.inbox.empty():
            items.append(self.inbox.get())
        return items
