## Node.py 
import random
import simpy
from typing_extensions import Self
from Message import Message
import time


class Node(object):
    def __init__(self, env: simpy.Environment, node_id: int):
        self.env: simpy.Environment = env
        self.node_id: int = node_id
        self.is_inserted: bool = False

        self.right_neighbour: Node = None
        self.left_neighbour: Node = None

        self.insertion_request_messages: list[Message] = []
        self.is_processing_insertion_request: bool = False
        
        self.update_request_messages: list[Message] = []
        self.is_processing_update_request: bool = False

        self.is_ready_to_update_messages: list[Message] = []

        self.new_neighbours_messages: list[Message] = []

        self.other_messages: list[Message] = []

    def __str__(self):
        return f"[ {self.env.now} ] I am node {self.node_id} and my neighbours are : left={self.left_neighbour.node_id} & right={self.right_neighbour.node_id}.\n"

    def __str__(self):
        result = f"[ {self.env.now} ] I am node {self.node_id}, my neighbours are: "
        result += f"left={self.left_neighbour.node_id if self.left_neighbour != None else None} "
        result += f"right={self.right_neighbour.node_id if self.left_neighbour != None else None}.\n"
        return result

    def receive_message(self, message: Message):
        if message._type == "update_request":
            self.update_request_messages.append(message) 
            print(f"[ {self.env.now} ] Node {self.node_id} received message of type update_request from node {message._from.node_id}.\n")

        elif message._type == "insertion_request":
            self.insertion_request_messages.append(message)
            print(f"[ {self.env.now} ] Node {self.node_id} received message of type insertion_request from node {message._from.node_id}.\n")

        elif message._type == "is_ready_to_update":
            self.is_ready_to_update_messages.append(message)
            print(f"[ {self.env.now} ] Node {self.node_id} received message of type is_ready_to_update from node {message._from.node_id}.\n")

        elif message._type == "new_neighbours":
            self.new_neighbours_messages.append(message)
            print(f"[ {self.env.now} ] Node {self.node_id} received message of type update_request from node {message._from.node_id}.\n")

        else:
            self.other_messages.append(message)
            print(f"[ {self.env.now} ] Node {self.node_id} received message of other type from node {message._from.node_id}.\n")
   

    def send_message(self, message: Message):
        print(f"[ {self.env.now} ] Node {self.node_id} sent message of type {message._type} to node {message._to.node_id}.\n")
        message._to.receive_message(message) # bon là irl se serait des sockets par exemple.


    def process_insertion_request(self, message:Message):
        self.is_processing_insertion_request = True
        self.insertion_request_messages.remove(message)

        joining_node = message._from

        print(f"[ {self.env.now} ] Node {self.node_id} started processing insertion request from node {joining_node.node_id}.\n")

        if joining_node.node_id < self.node_id:

            if  not (self.left_neighbour.node_id >= self.node_id) and joining_node.node_id < self.left_neighbour.node_id: # si le noeud joignant est inférieur à mon voisin gauche et que je ne suis pas le min
                
                # envoyer le message de demande d'insertion qui venait de joining_node, à son voisin gauche
                message.set_to(_to=self.left_neighbour)
                self.send_message(message = message)
                                

            else:
                
            # créer deux messages de demande d'update et l'envoyer à son voisin gauche et au nouveau noeud
                msg_left = Message(env = self.env,
                                        _type = 'update_request',
                                        _from = self,
                                        _to = self.left_neighbour,
                                    )
                
                msg_joining = Message(env = self.env,
                                        _type = 'update_request',
                                        _from = self,
                                        _to = joining_node,
                                    )
                
                self.send_message(message=msg_left)
                self.send_message(message=msg_joining)
                time.sleep(1)

                # attendre de recevoir ces messages dans la liste is_ready_to_update_messages
                while True:
                    if msg_left not in self.is_ready_to_update_messages or msg_joining not in self.is_ready_to_update_messages:
                        time.sleep(1)
                    else:
                        # modifier les messages pour qu'ils deviennent de type new_neighbours
                        _to = msg_left._from
                        msg_left.set(_type = 'new_neighbours', _from = self, _to = _to, content = {'new_neighbours': [joining_node]})
                        self.send_message(message = msg_left)

                        _to = msg_joining._from
                        msg_joining.set(_type = 'new_neighbours', _from = self, _to = _to, content = {'new_neighbours': [self, self.left_neighbour]})
                        self.send_message(message = msg_joining)

                        # mettre à jour ses propres voisins
                        self.update_neighbours(new_neighbours=[joining_node])

                        # supprimer ces messages de la liste
                        self.is_ready_to_update_messages.remove(msg_left)
                        self.is_ready_to_update_messages.remove(msg_left)      
                        break    
        
        elif joining_node.node_id > self.node_id:
                
                # même procédé que ci-dessus mais pour le voisin droit au lieu du voisin gauche
                
                if  joining_node.node_id > self.right_neighbour.node_id and not (self.right_neighbour.node_id <= self.node_id): # si le noeud joignant est supérieur à mon voisin droit et que je ne suis pas le max

                    # envoyer le message de demande d'insertion qui venait de joining_node, à son voisin droit
                    message.set_to(_to=self.right_neighbour)
                    self.send_message(message = message)
                                                     
                else:

                # créer deux messages de demande d'update et l'envoyer à son voisin droit et au nouveau noeud
                    msg_right = Message(env = self.env,
                                            _type = 'update_request',
                                            _from = self,
                                            _to = self.right_neighbour,
                                        )
                    
                    msg_joining = Message(env = self.env,
                                            _type = 'update_request',
                                            _from = self,
                                            _to = joining_node,
                                        )
                    
                    self.send_message(message=msg_right)
                    self.send_message(message=msg_joining)

                    # attendre de recevoir ces messages dans la liste is_ready_to_update_messages
                    while True:
                        if msg_right not in self.is_ready_to_update_messages or msg_joining not in self.is_ready_to_update_messages:
                            time.sleep(1)
                        else:
                            # modifier les messages pour qu'ils deviennent de type new_neighbours
                            _to = msg_right._from
                            msg_right.set(_type = 'new_neighbours', _from = self, _to = _to, content = {'new_neighbours': [joining_node]})
                            self.send_message(message = msg_right)

                            _to = msg_joining._from
                            msg_joining.set(_type = 'new_neighbours', _from = self, _to = _to, content = {'new_neighbours': [self, self.right_neighbour]})
                            self.send_message(message = msg_joining)

                            # mettre à jour ses propres voisins
                            self.update_neighbours(new_neighbours=[joining_node])

                            # supprimer ces messages de la liste
                            self.is_ready_to_update_messages.remove(msg_right)
                            self.is_ready_to_update_messages.remove(msg_joining)      
                            break    
                
        self.is_processing_insertion_request = False


    def process_update_request(self, message: Message):

        self.is_processing_update_request = True
        print(f"[ {self.env.now} ] Node {self.node_id} started processing update request from node {message._from.node_id}.\n")

        while True:
            # attendre qu'on ne soit plus en train de traiter l'insertion d'un noeud si c'est le cas
            if self.is_processing_insertion_request:
                time.sleep(1)

            else:
                # dès qu'on est prêt, changer le type du message en 'is_ready_to_update' et l'envoyer
                _to = message._from 
                message.set(_type = 'is_ready_to_update', _from = self, _to = _to)
                print(message._type)
                self.send_message(message=message)
                break

        while True:
            if message in self.new_neighbours_messages:
                self.update_neighbours(message.content.new_neighbours)
                self.new_neighbours_messages.remove(message)
                break
            else:
                time.sleep(1)

        # supprimer le message de la liste de demande d'update de voisins
        self.update_request_messages.remove(message)

        self.is_processing_update_request = False
        

    def update_neighbours(self, new_neighbours: list[Self]):
        for n in new_neighbours:
            if n.node_id > self.node_id:
                print(f"[ {self.env.now} ] Node {self.node_id} is updating its right neighbour : new neighbour is {n.node_id}.\n")
                self.right_neighbour = n
            else:
                print(f"[ {self.env.now} ] Node {self.node_id} is updating its left neighbour : new neighbour is {n.node_id}.\n")
                self.left_neighbour = n

    def run(self):
            while True:
                while len(self.update_request_messages) > 0:
                    print(f'Node {self.node_id} est dans la boucle de traitement des demandes d\'update.\n')
                    msg = self.update_request_messages[0]
                    self.process_update_request(msg)
                    #yield self.env.timeout(random.randint(1, 3))

                if self.is_inserted:
                    while len(self.insertion_request_messages) > 0:
                        print(f'Node {self.node_id} est dans la boucle de traitement des demandes d\'insertion.\n')
                        msg = self.insertion_request_messages[0]
                        self.process_insertion_request(message=msg)
                        #yield self.env.timeout(random.randint(1, 3))

                # Attendre un certain temps avant de continuer
                yield self.env.timeout(random.randint(3, 10))