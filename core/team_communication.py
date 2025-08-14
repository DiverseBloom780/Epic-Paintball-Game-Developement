from collections import deque

class TeamCommunication:
    def __init__(self, max_msgs=8):
        self.messages = deque(maxlen=max_msgs)

    def send(self, sender, message):
        s = f"{sender}: {message}"
        self.messages.appendleft(s)
        print(s)  # also print to console

    def list(self):
        return list(self.messages)
