## DHT.py
import random 
import simpy
from Node import Node
from Message import Message

class DHT(object):
    def __init__(self, name: str, env: simpy.Environment):
        self.name: str = name
        self.env: simpy.Environment = env
        self.nodes: dict = {}
        self.processes = []

    def __str__(self):
        """
        Affiche l'état de la DHT.
        """
        result = f"[ {self.env.now} ] State of DHT {self.name}:\n"
        sorted_nodes = sorted(self.nodes.values(), key=lambda node: node.node_id)
        for n in sorted_nodes:
            left_neighbour_id = n.left_neighbour.node_id if n.left_neighbour is not None else None
            right_neighbour_id = n.right_neighbour.node_id if n.right_neighbour is not None else None
            result += f"{n.node_id} : left_neighbour={left_neighbour_id} & right_neighbour={right_neighbour_id}\n"
        return result + "\n"

    def initialize(self):
        """
        Initialise la DHT avec 5 noeuds.
        """

        # Création des noeuds
        node1 = Node(self.env, 1)
        node2 = Node(self.env, 2)
        node3 = Node(self.env, 3)
        node4 = Node(self.env, 4)
        node5 = Node(self.env, 5)

        # Ajout des noeuds dans la DHT et dans l'environnement de simulation.
        self.nodes[1] = node1
        p = self.env.process(node1.run())
        node1.process = p

        self.nodes[2] = node2
        p = self.env.process(node2.run())
        node2.process = p

        self.nodes[3] = node3
        p = self.env.process(node3.run())
        node3.process = p
        
        self.nodes[4] = node4
        p = self.env.process(node4.run())
        node4.process = p
        
        self.nodes[5] = node5
        p = self.env.process(node5.run())
        node5.process = p

        # Création des liens entre les noeuds
        node1.left_neighbour = node5
        node1.right_neighbour = node2
        node1.is_inserted = True

        node2.left_neighbour = node1
        node2.right_neighbour = node3
        node2.is_inserted = True

        node3.left_neighbour = node2
        node3.right_neighbour = node4
        node3.is_inserted = True

        node4.left_neighbour = node3
        node4.right_neighbour = node5
        node4.is_inserted = True

        node5.left_neighbour = node4
        node5.right_neighbour = node1
        node5.is_inserted = True


    def join_random(self):
        """
        Méthode pour ajouté un noeud aléatoire à la DHT.
        """
        # Choix d'un ID de noeud qui ne soit pas déjà dans la DHT
        new_node_id = random.randint(6, 1000)  
        while new_node_id in self.nodes.keys():
            new_node_id = random.randint(1, 1000)

        # Création du noeud
        joining_node = Node(self.env, new_node_id)

        # Ajout du noeud dans la DHT
        if self.nodes:
            # sélection d'un noeud cible
            target_node = random.choice(list(self.nodes.values()))

            # création du message de demande d'insertion
            msg = Message(env = self.env,
                            _type='insertion_request', 
                            _from=joining_node,
                            _to=target_node
            )

            # ajout du noeud joignant à la liste des noeuds de la DHT
            self.nodes[new_node_id] = joining_node
            print(f"[ {self.env.now} ] Node {joining_node.node_id} joined DHT {self.name}.\n")

            # ajout du noeud joignant dans l'environnement de simulation
            p = self.env.process(joining_node.run())
            joining_node.process = p

            # noeud joignant envoi le message de demande d'insertion au noeud cible
            joining_node.send_message(msg)

        else:
            print("Cannot join DHT, no existing nodes.")


    def join_node(self, joining_node: Node, target_node: Node):
        """
        Méthode pour ajouté un noeud à la DHT à partir d'un objet Node existant.
        """

        # Check si le noeud joignant n'a pas un ID déjà utilisé dans la DHT
        if joining_node.node_id in self.nodes.keys():
            print(f"[ {self.env.now} ] Node {joining_node.node_id} could not join DHT {self.name} as ID is already used.\n")

        # Check si le noeud cible donné en paramètres n'existe pas dans la DHT
        elif target_node.node_id not in self.nodes.keys():
            print(f"[ {self.env.now} ] Node {joining_node.node_id} could not join DHT {self.name} as target node {target_node.node_id} does not exist.\n")

        else:
            # Préparation d'un message de demande d'insertion
            msg = Message(env = self.env,
                            _type='insertion_request', 
                            _from=joining_node,
                            _to=target_node
            )

            # Ajout du noeud joignant à la DHT
            self.nodes[joining_node.node_id] = joining_node
            print(f"[ {self.env.now} ] Node {joining_node.node_id} joined DHT {self.name}.\n")

            # Ajout du noeud joignant à l'environnement de simulation
            p = self.env.process(joining_node.run())
            joining_node.process = p

            # Envoi du message de demande d'insertion
            joining_node.send_message(msg)    


    def join_id(self, joining_node_id: int, target_node_id: int):
        """
        Méthode pour ajouter un noeud à la DHT à partir d'IDs donnés.
        """

        # Check si l'ID choisi pour le noeud joignant n'est pas déjà dans la DHT
        if joining_node_id in self.nodes.keys():
            print(f"[ {self.env.now} ] Node {joining_node_id} could not join DHT {self.name} as ID is already used.\n")

        # Check si l'ID du noeud cible donné n'existe pas dans la DHT
        elif target_node_id not in self.nodes.keys():
            print(f"[ {self.env.now} ] Node {joining_node_id} could not join DHT {self.name} as target node {target_node_id} does not exist.\n")

        else:
            # Création du noeud joignant
            joining_node = Node(self.env, joining_node_id)

            # Récupération du noeud cible
            target_node = self.nodes.get(target_node_id)

            # Préparation d'un message de demande d'insertion
            msg = Message(env = self.env,
                            _type='insertion_request', 
                            _from=joining_node,
                            _to=target_node
            )

            # Ajout du noeud joignant à la DHT
            self.nodes[joining_node.node_id] = joining_node
            print(f"[ {self.env.now} ] Node {joining_node.node_id} joined DHT {self.name}.\n")

            # Ajout du noeud joignant à l'environnement de simulation
            p = self.env.process(joining_node.run())
            joining_node.process = p

            # Envoi du message de demande d'insertion.
            joining_node.send_message(msg)


    def leave_random(self):
            """
            Méthode générant le départ d'un noeud de la DHT.
            """
            if len(self.nodes) > 0:
                # S'il y a des noeuds dans la DHT, sélection aléatoire d'un noeud inséré (i.e. a ses voisins) pour le faire quitter
                target_node = random.choice(list(self.nodes.values()))
                while target_node.is_inserted is False:
                    target_node = random.choice(list(self.nodes.values()))

                # On essaie de faire quitter le noeud
                could_left = yield from target_node.leave_dht()
                
                # Si le noeud n'a pas pu quitter (car blocage comme expliqué dans le rapport), on attend un temps aléatoire et on réessaie
                while could_left == False:
                    self.env.timeout(random.randint(2,6))
                    could_left = yield from target_node.leave_dht()

                # Une fois que le noeud à quitter la DHT on le supprime de la liste des noeuds
                del self.nodes[target_node.node_id]
                print(f"[ {self.env.now} ] Node {target_node.node_id} removed from DHT.\n")
            else:
                print(f"[ {self.env.now} ] No node to make leave DHT currently.\n")


    def schedule_join_random(self, start_time: int = 10, end_time: int = 180, delay: list[int] = [5, 10], nb_nodes: int = 2):
        """
        Méthode permettant de générer des ajouts de noeuds au cours de la simulation à des moments aléatoires.
        """
        while True:
            # Ajout d'un noeud aléatoire si on se trouve dans l'intervalle de temps de simulation choisi en paramètres de la méthode.
            if start_time <= self.env.now <= end_time:
                for _ in range(nb_nodes): # Nombre de noeud joignant en même temps
                    self.join_random() # appel de la méthode permettant d'ajouter un noeud aléatoire
                yield self.env.timeout(delay[0], delay[1]) # attente d'un délai aléatoire avant le prochain ajout
            else:
                yield self.env.timeout(1)

    def schedule_leave_random(self, start_time: int = 20, end_time: int = 170, delay: list[int] = [10, 20], nb_nodes: int = 1):
        """
        Méthode permettant de générer le départ de noeuds de la DHT au cours de la simulation et à des moments aléatoires.
        """
        while True:
            # Départ d'un noeud aléatoire si on se trouve dans l'intervalle de temps de simulation choisi en paramètres de la méthode.
            if start_time <= self.env.now <= end_time:
                for _ in range(nb_nodes): # Nombre de départs à faire simultanément
                    yield from self.leave_random() # attendre la fin de la méthode permettant de faire quitter un noeud aléatoire
                yield self.env.timeout(delay[0], delay[1]) # attente d'un délai aléatoire avant le prochain départ
            else:
                yield self.env.timeout(1)

    def schedule_print_dht(self, interval: int = 5):
        """
        Méthode pour afficher l'état de la DHT à des temps réguliers au fur et à mesure de la simulation.
        """
        while True:
            yield self.env.timeout(interval)
            print(self)
        

    def run_simulation(self, until_time):
        """
        Méthode définissant la simulation jusqu'à un temps limite.
        """

        # On commence par initialiser la DHT
        self.initialize()

        # Ajout de deux noeuds à partir d'IDs
        self.join_id(6, 5)
        self.join_id(7, 4)

        # Ajout de deux noeuds aléatoires
        for _ in range(0,2):
            self.join_random()

        # Ajout à la simulation de la méthode programmant l'insertion aléatoire de noeuds
        self.env.process(self.schedule_join_random())

        # Ajout à la simulation de la méthode programmant le départ aléatoire de noeuds
        self.env.process(self.schedule_leave_random())

        # Ajout à la simulation de l'affichage régulier de l'état de la DHT
        self.env.process(self.schedule_print_dht())

        # Run simulation jusqu'au temps limite
        self.env.run(until=until_time)






