# team_communication.py

class TeamCommunication:
    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)

    def receive_messages(self):
        return self.messages

def main():
    team_communication = TeamCommunication()
    team_communication.send_message("Enemy spotted!")
    print(team_communication.receive_messages())

if __name__ == "__main__":
    main()
