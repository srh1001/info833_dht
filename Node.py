## Node.py 
import random
import simpy
from typing_extensions import Self
from Message import Message

class Node(object):
    def __init__(self, env: simpy.Environment, node_id: int):
        self.env: simpy.Environment = env
        self.node_id: int = node_id
        self.is_inserted: bool = False # booléen pour savoir si le noeud est inséré
        self.is_leaving_dht = False # booléen pour savoir si le noeud cherche à quitter la dht
        self.process: simpy.Process = None # processus simpy associé au noeud dans la simulation

        self.right_neighbour: Node = None
        self.left_neighbour: Node = None

        self.insertion_request_messages = simpy.FilterStore(env) # messages de demandes d'insertion reçues
        self.is_processing_insertion_request: bool = False # booléen pour savoir si le noeud est en train d'en insérer un autre
        
        self.update_request_messages: simpy.Store = simpy.FilterStore(env) # messages reçus de demande pour se préparer à mettre à jour ses voisins
        self.is_processing_update_request: bool = False # booléen pour savoir si le noeud est en train de traiter une demande d'update de voisins

        self.is_ready_to_update_messages: simpy.Store = simpy.FilterStore(env) # messages reçus informant le noeud que ses voisins sont prêts à s'updater

        self.update_messages: simpy.Store = simpy.FilterStore(env) # message reçus contenant les données à mettre à jour

        self.other_messages: simpy.Store = simpy.Store(env) # autres messages reçus

        self.data: dict = {} # données du noeud

    def __str__(self):
        result = f"[ {self.env.now} ] I am node {self.node_id}, my neighbours are: "
        result += f"left={self.left_neighbour.node_id if self.left_neighbour != None else None} "
        result += f"right={self.right_neighbour.node_id if self.left_neighbour != None else None}.\n"
        return result

    def receive_message(self, message: Message):
        """
        Méthode pour traiter la réception d'un message, en l'envoyant dans la bonne liste (Store).
        """
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
        """
        Méthode pour envoyer un message.
        """
        message._to.receive_message(message)


    def process_insertion_request(self, insertion_message:Message):
        """
        Méthode pour traiter un message de demande d'insertion.
        """

        # Se mettre en mode insertion
        self.is_processing_insertion_request = True

        # Récupération du noeud émetteur de la demande d'insertion
        joining_node = insertion_message._from

        print(f"[ {self.env.now} ] Node {self.node_id} started processing insertion request from node {joining_node.node_id}.\n")
       
        
        if joining_node.node_id < self.node_id:

            # si le noeud joignant est inférieur à mon voisin gauche et que je ne suis pas le minimum
            if  not (self.left_neighbour.node_id >= self.node_id) and joining_node.node_id < self.left_neighbour.node_id:
                
                # envoyer le message de demande d'insertion qui venait de joining_node, à son voisin gauche
                insertion_message.update({'_to': self.left_neighbour})
                self.send_message(message = insertion_message)
                                

            else:
                
            # sinon créer deux messages de demande d'update et l'envoyer à son voisin gauche et au nouveau noeud
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

                # attendre de recevoir ces messages dans sa liste is_ready_to_update_messages
                neighbours_ready = yield from self.wait_for_is_ready_to_update_timeout([msg_left, msg_joining])

                if neighbours_ready:

                    # Si les noeuds sont prêts, modifier les messages pour qu'ils deviennent de type update et contiennent les données à mettre à jour.
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

                else:
                    # si on n'a pas reçu les messages is_ready_to_update à temps, modifier les messages pour qu'ils deviennent de type update mais ils seront vides (i.e. sans rien à updater)
                    _to = msg_left._from
                    msg_left.update(
                                    {
                                        '_type': 'update', 
                                        '_from': self, 
                                        '_to' : _to, 
                                        'content': {'updates': {}},
                                        'tag': 'canceled' 
                                        }
                                    )

                    self.send_message(message = msg_left)

                    _to = msg_joining._from
                    msg_joining.update(
                                        {
                                            '_type': 'update', 
                                            '_from': self, 
                                            '_to': _to, 
                                            'content': {'updates': {}},
                                            'tag': 'canceled'
                                        }
                                    )
                    self.send_message(message = msg_joining)

                    # remettre le message de demande d'insertion dans sa liste des demandes d'insertion, afin de réessayer plus tard
                    self.insertion_request_messages.put(insertion_message)

                    yield self.env.timeout(1)  

                
        elif joining_node.node_id > self.node_id:
                
                # exactement le même procédé que ci-dessus mais pour le voisin droit au lieu du voisin gauche
                
                if  joining_node.node_id > self.right_neighbour.node_id and not (self.right_neighbour.node_id <= self.node_id): # si le noeud joignant est supérieur à mon voisin droit et que je ne suis pas le max

                    # envoyer le message de demande d'insertion qui venait de joining_node, à son voisin droit
                    insertion_message.update({'_to': self.right_neighbour})
                    self.send_message(message = insertion_message)
                                                     
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
                    neighbours_ready = yield from self.wait_for_is_ready_to_update_timeout([msg_right, msg_joining])


                    if neighbours_ready:
                        # si retour dans les temps, modifier les messages pour qu'ils deviennent de type update
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

                    else:
                        # si pas de is_ready dans les temps, modifier les messages pour qu'ils deviennent de type update mais ils seront vides (i.e. sans rien à updater)
                        _to = msg_right._from
                        msg_right.update(
                                            {
                                                '_type': 'update', 
                                                '_from': self, 
                                                '_to': _to, 
                                                'content': {'updates': {}},
                                                'tag': 'canceled'
                                            }
                                        )
                        self.send_message(message = msg_right)

                        _to = msg_joining._from
                        msg_joining.update(
                                            {
                                                '_type': 'update', 
                                                '_from': self, 
                                                '_to': _to, 
                                                'content': {'updates': {}},
                                                'tag': 'canceled'
                                            }
                                        )
                        
                        self.send_message(message = msg_joining)

                        # remettre le message de demande d'insertion dans sa liste des demandes d'insertion afin de réessayer plus tard
                        self.insertion_request_messages.put(insertion_message)
                    
                        yield self.env.timeout(1)    
                    
        # Cesser d'être en mode insertion
        self.is_processing_insertion_request = False


    def process_update_request(self, message: Message):
        """
        Méthode pour traiter les messages de demande d'update des voisins.
        """

        # Se mettre en mode traitement d'une demande d'update
        self.is_processing_update_request = True
        print(f"[ {self.env.now} ] Node {self.node_id} started processing update request from node {message._from.node_id}.\n")
        
        # attendre qu'on ne soit plus en train de traiter l'insertion d'un noeud (bon là normalement c'est jamais censé arriver car à l'heure actuelle un noeud traite un message à la fois)
        while self.is_processing_insertion_request:
            yield self.env.timeout(1)

        # dès qu'on est prêt, changer le type du message reçu en 'is_ready_to_update' et l'envoyer
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
        
        # Attendre de recevoir le message contenant les données à mettre à jour
        yield self.update_messages.get(lambda x: x == message)
        
        # Mettre à jour ses données selon le contenu du message
        self.update(message.content.get('updates'))
    
        yield self.env.timeout(1)

        # Cesser d'être en mode traitement d'une demande d'insertion
        self.is_processing_update_request = False


    def leave_dht(self):
        """
        Méthode pour le départ d'un noeud de la DHT.
        """
        
        print(f"[ {self.env.now} ] Node {self.node_id} preparing to leave dht.\n")

        # Se mettre en mode départ de la DHT
        self.is_leaving_dht = True

        # Attendre qu'on ne soit plus en train de traiter l'insertion d'un noeud ou de traiter une demande d'update
        while self.is_processing_insertion_request or self.is_processing_update_request:
            yield self.env.timeout(1)
                
            
        # Créer deux messages de demande d'update et l'envoyer à son voisin gauche et droit pour informer du départ
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
        
        
        self.send_message(message=msg_left)
        self.send_message(message=msg_right)

        yield self.env.timeout(1)

        # Attendre de recevoir ces messages dans la liste is_ready_to_update_messages
        neighbours_ready = yield from self.wait_for_is_ready_to_update_timeout([msg_left, msg_right])

        if neighbours_ready:
            # Si les messages is_ready_to_update sont reçus dans les temps, alors modifier les messages pour qu'ils deviennent de type update avec les données à updater
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

            _to = msg_right._from
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

            # Transmettre ses demandes d'insertion à ses voisins étant donné qu'on ne pourra pas les traiter
            for insertion_message in self.insertion_request_messages.items:
                joining_node = insertion_message._from
                if joining_node.node_id < self.node_id:
                    # Renvoyer la demande d'insertion au voisin gauche
                    insertion_message.update({'_to': self.left_neighbour})
                    self.send_message(message=insertion_message)
                else:
                    # Renvoyer la demande d'insertion au voisin droit
                    insertion_message.update({'_to': self.right_neighbour})
                    self.send_message(message=insertion_message)        
            
            # Se mettre en mode non insérer
            self.is_inserted = False
            print(f"[ {self.env.now} ] Node {self.node_id} has finished warning its neighbours of its departure. It is now not inserted.\n")
            
            # Renvoie True pour indiquer que le noeud à pu quitter la DHT (pas de blocage)
            return True
        
        else:
            # Si les messages is_ready_to_update n'ont pas été reçus dans les temps, renvoyer False pour signaler qu'on n'a pas pu sortir de la DHT
            # La classe DHT va donc réessayer de faire quitter le noeud après un délai d'attente aléatoire (méthode DHT.leave_random())
            # Pour autant on ne quitte pas le mode départ de la DHT (leaving_dht) car on ne veut pas que le noeud continue de traiter les messages reçus
            yield self.env.timeout(1)
            return False

    def update(self, updates: dict):
        """
        Méthode pour mettre à jour ses données à partir d'un dictionnaire. Le dictionnaire doit avoir comme clés les attributs à updater dans le noeud.
        """
        for key, value in updates.items():
            if hasattr(self, key):
                print(f"{[ self.env.now ]} node {self.node_id} is updating {key}.\n")  
                setattr(self, key, value)
            else:
                print(f"{[ self.env.now ]} node {self.node_id} does not have attribute {key} to be updated.\n")  


    def wait_for_is_ready_to_update(self, messages: list):
        """
        Méthode pour attendre la reception d'une liste de messages is_ready_to_update, sans timeout. (Pas utilisé dans la DHT actuellement.)
        """
        for msg in messages:
        # Pour chaque objet Message de la liste donnée en paramètres, attendre sa réception dans le Store des is_ready_to_update_messages.
            yield self.is_ready_to_update_messages.get(lambda x: x == msg) 

        print(f"[ {self.env.now} ] All is_ready messages received for node {self.node_id}.\n")

    def wait_for_is_ready_to_update_timeout(self, messages: list):
        """
        Méthode pour attendre la reception d'une liste de messages is_ready_to_update, avec un timeout, i.e. une limite de temps d'attente.
        """
        ready_messages = [] # liste pour stocker les messages is_ready_to_update à recevoir
        timeout = random.randint(4,10) # temps limite d'attente aléatoire

        # Attendre que chaque message soit reçu ou que le timeout se produise
        start_time = self.env.now
        while self.env.now - start_time < timeout and len(ready_messages) < len(messages):
            msg = yield self.is_ready_to_update_messages.get(lambda x: x in messages)
            ready_messages.append(msg)

        # Checker si on a bien reçus tous les messages attendus
        if len(ready_messages) == len(messages):
            print(f"[ {self.env.now} ] All is_ready messages received for node {self.node_id}.\n")
            return True  # retourner True pour indiquer que les noeuds sont prêts à s'updater
        else:
            print(f"[ {self.env.now} ] Timeout while waiting is_ready messages for node {self.node_id}.\n")
            return False  # le timeout s'est produit avant de recevoir tous les messages is_ready_to_update, on renvoie False 


    def run(self):
        """
        Méthode définissant le comportement du noeud dans la simulation.
        """
        print(f"[ {self.env.now} ] Node {self.node_id} running.\n")

        # Tant que le noeud ne cherche pas à quitter la DHT, il va traiter les messages
        while self.is_leaving_dht == False:

            # Tant qu'il y a des demandes d'update, on traite ces messages en priorités pour qu'il y ait le moins de risque de blocage (bien qu'on évite ces blocages avec les temps d'attente limites)
            while self.update_request_messages.items:
                yield from self.process_update_request(self.update_request_messages.get().value)

            # Traiter une demande d'insertion
            if self.is_inserted:
                if self.insertion_request_messages.items:
                    yield from self.process_insertion_request(self.insertion_request_messages.get().value)
            
            # Traiter les messages d'update
            while self.update_messages.items:
                msg = self.update_messages.get().value
                updates = msg.get('updates')
                self.update(updates)

            yield self.env.timeout(1)

    