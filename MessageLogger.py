## MessageLogger.py

class MessageLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.messages = []
        return cls._instance

    def log_message(self, message):
        self.messages.append(message)

    def get_messages(self):
        return self.messages


