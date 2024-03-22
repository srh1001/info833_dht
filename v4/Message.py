# Message.py
import Node
from MessageLogger import MessageLogger
import simpy



class Message(object):
    def __init__(self, env: simpy.Environment, _type: str, _from: Node, _to: Node, content: dict = {}):
        self.env: simpy.Environment = env
        self._type = _type
        self._from = _from
        self._to = _to
        self.content = content

        self.archives = {}

        MessageLogger().log_message(self)
        self.archive()

    def update(self, updates: dict):

        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Attribute '{key}' does not exist in Message.")  
        
        self.archive()

    def archive(self):
        self.archives[self.env.now] = vars(self).copy()

        