# Message.py
from Node import Node
import simpy

class Message(object):
    def __init__(self, env: simpy.Environment, _from: Node, _to: Node, content: dict = {}):
        self.env: simpy.Environment = env
        self._from = _from
        self._to = _to
        self.content = content

