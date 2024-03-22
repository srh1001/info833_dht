## Node.py 
import random
import simpy
from typing_extensions import Self
from Message import Message
import time

class Node:
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.neighbour = None
        self.is_processing_insertion = False

        self.insertion_request_messages = simpy.FilterStore(env)
        self.update_request_messages = simpy.FilterStore(env)
        self.is_ready_to_update_messages = simpy.FilterStore(env)
        self.new_neighbours_messages = simpy.FilterStore(env)

    def process_insertion_request(self, insert_request_msg):
        print(f"{[ self.env.now ]} {self.id} is processing request insertion.")

        joining_node = insert_request_msg._from

        # Envoyer une demande d'update
        msg_1 = Message(env=self.env, _type='update_request', _from=self, _to=self.neighbour)
        self.send_message(msg_1)

        msg_2 = Message(env=self.env, _type='update_request', _from=self, _to=joining_node)
        self.send_message(msg_2)

        #yield self.env.timeout(3)
        # Attendre de recevoir le message 'is_ready_to_update'
        #yield self.is_ready_to_update_messages.get()

        yield self.env.timeout(2)

        ready = yield from self.wait_for_is_ready_to_update([msg_1, msg_2])
        print(f"{[ self.env.now ]} {self.id} : are they ready for update ? : ", ready)

        # Renvoyer un message de type 'new_neighbours'
        new_neighbours_msg = Message(env=self.env, _type='new_neighbours', _from=self, _to=self.neighbour, content=insert_request_msg._from)
        self.send_message(new_neighbours_msg)

        # Renvoyer un message de type 'new_neighbours'
        new_neighbours_msg = Message(env=self.env, _type='new_neighbours', _from=self, _to=joining_node, content=self)
        self.send_message(new_neighbours_msg)

    def process_update_request(self, msg):
        print(f"{[ self.env.now ]} {self.id} is processing update request.")

        # Attendre que self.is_processing_insertion soit False
        while self.is_processing_insertion:
            self.env.timeout(2)  # Attente très courte

        yield self.env.timeout(10)
        _to = msg._from
        msg.update({'_type': 'is_ready_to_update', '_from': self, '_to': _to})
        
        #ready_msg = Message(env=self.env, _type = 'is_ready_to_update', _from=self, _to=update_request_msg._from)
        
        # Envoyer un message de type 'is_ready_to_update'
        self.send_message(msg)

        # Attendre de recevoir le message 'new_neighbours'
        yield self.new_neighbours_messages.get()

        # Mettre à jour ses voisins
        print(f"{[ self.env.now ]} {self.id} met à jour ses voisins")

    def send_message(self, message):
        print(f'{[ self.env.now ]} {self.id} sent message of type {message._type} to {message._to.id}')
        message._to.receive_message(message)

    def receive_message(self, message):
        if message._type == 'update_request':
            print(f"{[ self.env.now ]} {self.id} received update request message.")
            self.update_request_messages.put(message)

        elif message._type == 'is_ready_to_update':
            print(f"{[ self.env.now ]} {self.id} received is ready to update message.")
            self.is_ready_to_update_messages.put(message)
            print(f"{[self.env.now]} receive : is_ready_to_update_messages : ", self.is_ready_to_update_messages.items)

        elif message._type == 'new_neighbours':
            print(f"{[self.env.now]} {self.id} received new neighbours message.")
            self.new_neighbours_messages.put(message)
    

    def wait_for_is_ready_to_update(self, messages: list):
        print("---- wait_for_is_ready_to_update called")
        print("messages list given to wait_for_is_ready_to_update: ", messages)
        
        # Attendre que chaque message soit reçu
        for msg in messages:
            yield self.is_ready_to_update_messages.get(lambda x: x == msg)
            print(f"Message {msg} received")

        print("All messages received")


    def wait_for_is_ready_to_update_bis(self, messages: list):
        print(f"{[self.env.now]} wait_for_is_ready_to_update called")
        print(f"{[self.env.now]} wait_for  : is_ready_to_update_messages : ", self.is_ready_to_update_messages.items)

        print(f"{[self.env.now]} messages list given to wait_for_is_ready_to_update: ", messages)
        events = [self.is_ready_to_update_messages.get(lambda x: x == msg) for msg in messages]
        all_events = simpy.AllOf(self.env, events)
        
        # Attendre que tous les événements se produisent
        while not all_events.triggered:
            print(f"{[self.env.now]} wait_for boucle  : is_ready_to_update_messages : ", self.is_ready_to_update_messages.items)
            yield self.env.timeout(2)
           
        
        print("testB")


    # def wait_for_is_ready_to_update(self, messages: list):
    #     print("---- wait_for_is_ready_to_update called")
    #     while True:
    #         all_ready = all(msg in self.is_ready_to_update_messages.items for msg in messages)
    #         if all_ready:
    #             print("All items are available")
    #             return True
    #         else:
    #             yield self.env.timeout(1)

    def run(self):
        while True:
            if self.insertion_request_messages.items:
                print(f'{[ self.env.now ]} {self.id} has {len(self.insertion_request_messages.items)} remaning insertion request messages.')
                msg = self.insertion_request_messages.get().value
                yield from self.process_insertion_request(msg)
                print(f'{[ self.env.now ]} {self.id} has {len(self.insertion_request_messages.items)} remaning insertion request messages.')

            if self.update_request_messages.items:
                yield from self.process_update_request(self.update_request_messages.get().value)
            
            yield self.env.timeout(1)

# Créer l'environnement
env = simpy.Environment()

# Créer les nodes
node1 = Node(env, 1)
node10 = Node(env, 10)
node1.neighbour = node10


node3 = Node(env, 3)
node4 = Node(env, 4)

insert_msg = Message(env=env, 
                     _type='insertion_request',
                     _from = node3,
                     _to=node1)

node1.insertion_request_messages.put(insert_msg)



node1.insertion_request_messages.put(insert_msg)


def simulate():
    print("\n\n ----------------------------------------- \n\n")
    env.process(node1.run())
    env.process(node10.run())
    env.process(node3.run())


# Démarrer la simulation
simulate()
env.run(until=60)  # Exécuter la simulation pendant 20 unités de temps