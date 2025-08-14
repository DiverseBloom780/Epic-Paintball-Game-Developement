# core/team_communication.py
class TeamCommunication:
    def __init__(self, max_msgs=8):
        self.max_msgs = max_msgs
        self.messages = []

    def send(self, who, msg):
        line = f"[{who}] {msg}"
        self.messages.append(line)
        self.messages = self.messages[-self.max_msgs:]

    def list(self):
        return list(self.messages)
