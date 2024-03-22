## Node.py 
import random
import simpy
from Message import Message
from typing_extensions import Self

class Node(object):
    def __init__(self, env: simpy.Environment, node_id: int):
        self.env: simpy.Environment = env
        self.node_id: int = node_id
        self.is_inserted: bool = False

        self.right_neighbour: Node = None
        self.left_neighbour: Node = None

        self.insertion_requests: list[Node] = []
        self.is_processing_insertion_request: bool = False
        
        self.update_requests: list[Message] = []
        self.is_processing_update_request: bool = False

        self.is_ready_to_update_messages: list[Message] = []

        self.update_neighbours_messages: list[Message] = []

        self.other_messages: list[Message] = []


    def __str__(self):
        return f"[ {self.env.now} ] I am node {self.node_id} and my neighbours are : left={self.left_neighbour.node_id} & right={self.right_neighbour.node_id}.\n"

    def receive_message(self, message: Message):
        if message.type == "update_request":
            self.update_requests.add(message)
    

            print(f"[ {self.env.now} ] Node {message._from.node_id} requested update to node {self.message._to.node_id}.\n")

        elif message.type == "insertion_request"
            self.insertion_requests.add(message)
            print(f"[ {self.env.now} ] Node {message._from.node_id} requested insertion to node {self.message._to.node_id}.\n")

        elif message.type == "is_ready_to_update":
            self.is_ready_to_update_message.add(message)
            print(f"[ {self.env.now} ] Node {message._from.node_id} told node {self.message._to.node_id} it is ready to update.\n")

        elif message.type == "update_neighbours":
            self.update_neighbours_messages.add(message)
            print(f"[ {self.env.now} ] Node {message._from.node_id} informed {self.message._to.node_id} about the neighbours it has to update.\n")

        else:
            self.other_messages.add(message)
            print(f"[ {self.env.now} ] Node {message._from.node_id} sent other message to {self.message._to.node_id}.\n")
   

    def send_message(recipient: Node, message: Message):
        recipient.receive_message(message)
    

    def process_insertion_request(self, message:Message):

        self.is_processing_insertion_request = True

        joining_node = message._from

        print(f"[ {self.env.now} ] Node {self.node_id} started processing insertion request from node {joining_node.node_id}.\n")

        if joining_node.node_id < self.node_id:

             # créer deux messages de demande d'update et l'envoyer à son voisin gauche et au nouveau noeud
             # attendre de recevoir ces messages dans la liste is_ready_to_update_messages
             # supprimer ces messages de la liste

            if  not (self.left_neighbour.node_id >= self.node_id) and joining_node.node_id < self.left_neighbour.node_id: # si le noeud joignant est inférieur à mon voisin gauche et que je ne suis pas le min
                

                # changer le type du message à destination de du voisin gauche en "update_neighbours"
                # ajouter dans ce message à destination du voisin gauche node, qui sont ces nouveaux voisins : il n'y en a pas

                # changer le type du message à destination de joining_node en "update_neighbours"
                # ajouter dans ce message à destination de joining node, qui sont ces nouveaux voisins : il n'y en a pas

                # attendre une seconde

                # envoyer le message de demande d'insertion qui venait de joining_node, à son voisin gauche
                                

            else:
                
                # changer le type de message à destination de joining_node en "update_neighbours"
                # ajouter dans le message à destination de joining node, qui sont ces nouveaux voisins : self et self.left_neighbour

                
                # changer le type de message à destination de self.left_neighbour en "update_neighbours"
                # ajouter dans le message à destination de joining node, qui sont ces nouveaux voisins : joining_node

                # envoyer les messages

                # mettre à jour ses propres voisins : self.left_neighbour = joining_node

                # attendre une ou deux secondes

                
        elif joining_node.node_id > self.node_id:
                
                # même procédé que ci-dessus mais pour le voisin droit au lieu du voisin gauche
                
                if  not (self.right_neighbour.node_id <= self.node_id) and joining_node.node_id > self.right_neighbour.node_id: # si le noeud joignant est supérieur à mon voisin droit et que je ne suis pas le max

                    # ...
                     
                else:

                    # ...
                     
        self.is_processing_insertion_request = False

    # def process_update_request(message: Message):

        # is_processing_update_request == True
        print(f"[ {self.env.now} ] Node {self.node_id} started processing update request from node {message._from.node_id}.\n")
 
        # supprimer le message de la liste update_request_messages

        # attendre qu'on ne soit plus en train de traiter l'insertion d'un noeud si c'est le cas

        # dès qu'on est prêt, changer le type du message en 'is_ready_to_update' et l'envoyer 

        # attendre de recevoir le message envoyé, dans sa liste update_neighbours_messages

        print(f"[ {self.env.now} ] Node {self.node_id} is about to update its neighbours.\n")
        # supprimer le message de sa liste update_neighbours_messages

        # updater ces voisins selon le contenu du message
        # is_processing_update_request == False
        

    def run(self):
            while True:
                if len(self.insertion_requests) > 0 and self.is_inserted==True and self.is_processing_insertion_request==False and self.is_processing_update_request==False:
                    joining_node = self.insertion_requests.pop(0)
                    self.process_insertion_request(joining_node)

                # Attendre un certain temps avant de continuer
                yield self.env.timeout(random.randint(10, 100))