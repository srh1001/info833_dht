# Message.py
import Node
from MessageLogger import MessageLogger
import simpy


class Message(object):
    def __init__(self, env: simpy.Environment, _type: str, _from: Node, _to: Node, content: dict = {}, tag: str = None):
        self.env: simpy.Environment = env
        self._type = _type # type du message (insertion_request, update_request, etc.)
        self._from = _from # noeud emetteur
        self._to = _to # noeud destinataire
        self.content = content # contenu
        self.tag = tag # un tag (mais pas vraiment utilisé pour le moment)

        self.archives = {} # dictionnaire les différents états du message au cours de la simulation

        MessageLogger().log_message(self) # stocker le message dans le singletion MessageLogger
        self.archive() # archiver la première version du message

    def update(self, updates: dict):
        """
        Méthode pour changer les attributs du message.
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Attribute '{key}' does not exist in Message.")  
        
        self.archive() # enregistrer le nouvel état du message

    def archive(self):
        """
        Méthode pour archiver le message en stockant ses attributs pour un temps donné dans la simulation.
        """
        self.archives[self.env.now] = vars(self).copy()

        