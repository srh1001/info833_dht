# Message.py
import simpy



class Message(object):
    def __init__(self, env: simpy.Environment, _type: str, _from, _to, content: dict = {}):
        self.env: simpy.Environment = env
        self._type = _type
        self._from = _from
        self._to = _to
        self.content = content

    def set(self, _type: str, _from, _to, content: str={}):
        self._type = _type
        self._from = _from
        self._to = _to
        self.content = content

    def set_to(self, _to):
        self._to = _to

    def update(self, changes: dict):
        for key, value in changes.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Attribute '{key}' does not exist in Message.")        
