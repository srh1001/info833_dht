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

        #self.insertion_request_messages: list[Message] = []
        self.insertion_request_messages = simpy.FilterStore(env)
        self.is_processing_insertion_request: bool = False
        
        #self.update_request_messages: list[Message] = []
        self.update_request_messages: simpy.Store = simpy.FilterStore(env)
        self.is_processing_update_request: bool = False

        #self.is_ready_to_update_messages: list[Message] = []
        self.is_ready_to_update_messages: simpy.Store = simpy.FilterStore(env)

        #self.new_neighbours_messages: list[Message] = []
        self.update_messages: simpy.Store = simpy.FilterStore(env)

        self.other_messages: simpy.Store = simpy.Store(env)

    def __str__(self):
        return f"[ {self.env.now} ] I am node {self.node_id} and my neighbours are : left={self.left_neighbour.node_id} & right={self.right_neighbour.node_id}.\n"

    def __str__(self):
        result = f"[ {self.env.now} ] I am node {self.node_id}, my neighbours are: "
        result += f"left={self.left_neighbour.node_id if self.left_neighbour != None else None} "
        result += f"right={self.right_neighbour.node_id if self.left_neighbour != None else None}.\n"
        return result

    def receive_message(self, message: Message):
        if message._type == "update_request":
            self.update_request_messages.put(message) 
            print(f"[ {self.env.now} ] Node {self.node_id} received message of type update_request from node {message._from.node_id}.\n")

        elif message._type == "insertion_request":
            self.insertion_request_messages.put(message)
            print(f"[ {self.env.now} ] Node {self.node_id} received message of type insertion_request from node {message._from.node_id}.\n")

        elif message._type == "is_ready_to_update":
            self.is_ready_to_update_messages.put(message)
            print(f"[ {self.env.now} ] Node {self.node_id} received message of type is_ready_to_update from node {message._from.node_id}.\n")

        elif message._type == "update":
            self.update_messages.put(message)
            print(f"[ {self.env.now} ] Node {self.node_id} received message of type update from node {message._from.node_id}.\n")

        else:
            self.other_messages.put(message)
            print(f"[ {self.env.now} ] Node {self.node_id} received message of other type from node {message._from.node_id}.\n")
   

    def send_message(self, message: Message):
        print(f"[ {self.env.now} ] Node {self.node_id} sent message of type {message._type} to node {message._to.node_id}.\n")
        message._to.receive_message(message) # bon là irl se serait des sockets par exemple.


    def process_insertion_request(self, message:Message):
        self.is_processing_insertion_request = True

        joining_node = message._from

        print(f"[ {self.env.now} ] Node {self.node_id} started processing insertion request from node {joining_node.node_id}.\n")
       
        if joining_node.node_id < self.node_id:

            if  not (self.left_neighbour.node_id >= self.node_id) and joining_node.node_id < self.left_neighbour.node_id: # si le noeud joignant est inférieur à mon voisin gauche et que je ne suis pas le min
                
                # envoyer le message de demande d'insertion qui venait de joining_node, à son voisin gauche
                message.update({'_to': self.left_neighbour})
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

                yield self.env.timeout(1)

                # attendre de recevoir ces messages dans la liste is_ready_to_update_messages
                #yield self.is_ready_to_update_messages.get()
                yield from self.wait_for_is_ready_to_update([msg_left, msg_joining])

                # modifier les messages pour qu'ils deviennent de type update
                _to = msg_left._from
                msg_left.update(
                                {
                                    '_type': 'update', 
                                    '_from': self, 
                                    '_to' : _to, 
                                    'content': {'updates': {'right_neighbour': joining_node}} 
                                    }
                                )

                self.send_message(message = msg_left)

                _to = msg_joining._from
                msg_joining.update(
                                    {
                                        '_type': 'update', 
                                        '_from': self, 
                                        '_to': _to, 
                                        'content': {'updates': {'left_neighbour': self.left_neighbour, 'right_neighbour': self, 'is_inserted': True }}
                                    }
                                )
                self.send_message(message = msg_joining)

                # mettre à jour ses propres voisins
                self.update(updates={'left_neighbour': joining_node})

                yield self.env.timeout(1)    

        
        elif joining_node.node_id > self.node_id:
                
                # même procédé que ci-dessus mais pour le voisin droit au lieu du voisin gauche
                
                if  joining_node.node_id > self.right_neighbour.node_id and not (self.right_neighbour.node_id <= self.node_id): # si le noeud joignant est supérieur à mon voisin droit et que je ne suis pas le max

                    # envoyer le message de demande d'insertion qui venait de joining_node, à son voisin droit
                    message.update({'_to': self.right_neighbour})
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

                    yield self.env.timeout(1)

                    # attendre de recevoir ces messages dans la liste is_ready_to_update_messages
                    yield from self.wait_for_is_ready_to_update([msg_right, msg_joining])

                    # modifier les messages pour qu'ils deviennent de type update
                    _to = msg_right._from
                    msg_right.update(
                                        {
                                            '_type': 'update', 
                                            '_from': self, 
                                            '_to': _to, 
                                            'content': {'updates': {'left_neighbour': joining_node}}
                                        }
                                    )
                    self.send_message(message = msg_right)

                    _to = msg_joining._from
                    msg_joining.update(
                                        {
                                            '_type': 'update', 
                                            '_from': self, 
                                            '_to': _to, 
                                            'content': {'updates': {'left_neighbour': self, 'right_neighbour': self.right_neighbour, 'is_inserted': True} }
                                        }
                                    )
                    
                    self.send_message(message = msg_joining)

                    # mettre à jour ses propres voisins
                    self.update(updates={'right_neighbour': joining_node})

                    yield self.env.timeout(1)    
                
        self.is_processing_insertion_request = False


    def process_update_request(self, message: Message):

        self.is_processing_update_request = True
        print(f"[ {self.env.now} ] Node {self.node_id} started processing update request from node {message._from.node_id}.\n")

        while True:
            # attendre qu'on ne soit plus en train de traiter l'insertion d'un noeud si c'est le cas
            if self.is_processing_insertion_request:
                yield self.env.timeout(1)

            else:
                # dès qu'on est prêt, changer le type du message en 'is_ready_to_update' et l'envoyer
                _to = message._from 
                message.update(
                                {
                                    '_type': 'is_ready_to_update',
                                    '_from': self,
                                      '_to': _to
                                } 
                            )
                self.send_message(message=message)
                yield self.env.timeout(1)
                break
        
        yield self.update_messages.get(lambda x: x == message)
        
        self.update(message.content.get('updates'))
    
        yield self.env.timeout(1)

        self.is_processing_update_request = False


    def leave_dht(self):
        
        print(f"[ {self.env.now} ] Node {self.node_id} preparing to leave dht.\n")

        while True:
                # attendre qu'on ne soit plus en train de traiter l'insertion d'un noeud ou d'updater
                if self.is_processing_insertion_request or self.is_processing_update_request:
                    yield self.env.timeout(1)
                
                else:
                    break
        # créer deux messages de demande d'update et l'envoyer à son voisin gauche et droit
        msg_left = Message(env = self.env,
                                _type = 'update_request',
                                _from = self,
                                _to = self.left_neighbour,
                            )
        
        msg_right = Message(env = self.env,
                                _type = 'update_request',
                                _from = self,
                                _to = self.right_neighbour,
                            )
        
        
        self.send_message(message=msg_right)
        self.send_message(message=msg_left)

        yield self.env.timeout(1)

        # attendre de recevoir ces messages dans la liste is_ready_to_update_messages
        yield from self.wait_for_is_ready_to_update([msg_left, msg_right])

        # modifier les messages pour qu'ils deviennent de type update
        _to = msg_left._from
        msg_left.update(
                        {
                            '_type': 'update', 
                            '_from': self, 
                            '_to': _to, 
                            'content': {'updates': {'right_neighbour': self.right_neighbour}}
                        }
                    )
        self.send_message(message = msg_left)

        msg_right.update(
                            {
                                '_type': 'update', 
                                '_from': self, 
                                '_to': _to, 
                                'content': {'updates': {'left_neighbour': self.left_neighbour}}
                            }
                        )
        self.send_message(message = msg_right)

        yield self.env.timeout(1)

        print(f"[ {self.env.now} ] Node {self.node_id} has finished warning its neighbours of its departure.\n")


    def update(self, updates: dict):
        for key, value in updates.items():
            if hasattr(self, key):
                print(f"{[ self.env.now ]} node {self.node_id} is updating {key}.\n")  
                setattr(self, key, value)
            else:
                print(f"{[ self.env.now ]} node {self.node_id} does not have attribute {key} to be updated.\n")  


    def wait_for_is_ready_to_update(self, messages: list):
        print(f"[ {self.env.now} ] wait_for_is_ready_to_update called.\n")

        # Attendre que chaque message soit reçu
        for msg in messages:
            yield self.is_ready_to_update_messages.get(lambda x: x == msg)

        print(f"[ {self.env.now} ] All is_ready messages received for node {self.node_id}.\n")

    def run(self):
        while True:

            while self.update_request_messages.items:
                yield from self.process_update_request(self.update_request_messages.get().value)

            if self.is_inserted:
                if self.insertion_request_messages.items:
                    yield from self.process_insertion_request(self.insertion_request_messages.get().value)
            
        
            yield self.env.timeout(1)
