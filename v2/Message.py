# Message.py
import Node
import simpy

class Message(object):
    def __init__(self, env: simpy.Environment, _type: str, _from: Node, _to: Node, content: dict = {}):
        self.env: simpy.Environment = env
        self._type = _type
        self._from = _from
        self._to = _to
        self.content = content

    def set(self, _type: str, _from: Node, _to: Node, content: str={}):
        self._type = _type
        self._from = _from
        self._to = _to
        self.content = content

    def set_to(self, _to: Node):
        self._to = _to
