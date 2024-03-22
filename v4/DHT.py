## DHT.py
import random 
import simpy
from Node import Node
from Message import Message
import MessageLogger

class DHT(object):
    def __init__(self, name: str, env: simpy.Environment):
        self.name: str = name
        self.env: simpy.Environment = env
        self.nodes: dict = {}
        self.processes = []

    def __str__(self):
        result = f"[ {self.env.now} ] State of DHT {self.name}:\n"
        for n in self.nodes.values():
            left_neighbour_id = n.left_neighbour.node_id if n.left_neighbour is not None else None
            right_neighbour_id = n.right_neighbour.node_id if n.right_neighbour is not None else None
            result += f"{n.node_id} : left_neighbour={left_neighbour_id} & right_neighbour={right_neighbour_id}\n"
        return result + "\n"

    def initialize(self):
        node1 = Node(self.env, 1)
        node2 = Node(self.env, 2)
        node3 = Node(self.env, 3)
        node4 = Node(self.env, 4)
        node5 = Node(self.env, 5)

        self.nodes[1] = node1
        self.nodes[2] = node2
        self.nodes[3] = node3
        self.nodes[4] = node4
        self.nodes[5] = node5

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


    def join(self):
        new_node_id = random.randint(6, 20)  # Choisir une plage d'IDs
        while new_node_id in [n.node_id for n in self.nodes]:
            new_node_id = random.randint(1, 20)

        joining_node = Node(self.env, new_node_id)
        target_node = random.choice(self.nodes)
        msg = Message(env = self.env,
                        _type='insertion_request', 
                        _from=joining_node,
                        _to=target_node
        )

        self.nodes[new_node_id] = joining_node
        print(f"[ {self.env.now} ] Node {joining_node.node_id} joined DHT {self.name}.\n")
        joining_node.send_message(msg)


    def join(self, joining_node: Node, target_node: Node):
        if joining_node.node_id in self.nodes.keys():
            print(f"[ {self.env.now} ] Node {joining_node.node_id} could not join DHT {self.name} as ID is already used.\n")

        elif target_node.node_id not in self.nodes.keys():
            print(f"[ {self.env.now} ] Node {joining_node.node_id} could not join DHT {self.name} as target node {target_node.node_id} does not exist.\n")

        else:
            msg = Message(env = self.env,
                            _type='insertion_request', 
                            _from=joining_node,
                            _to=target_node
            )

            self.nodes[joining_node.node_id] = joining_node
            print(f"[ {self.env.now} ] Node {joining_node.node_id} joined DHT {self.name}.\n")
            joining_node.send_message(msg)    


    def join(self, joining_node_id: int, target_node_id: int):
        if joining_node_id in self.nodes.keys():
            print(f"[ {self.env.now} ] Node {joining_node_id} could not join DHT {self.name} as ID is already used.\n")

        elif target_node_id not in self.nodes.keys():
            print(f"[ {self.env.now} ] Node {joining_node_id} could not join DHT {self.name} as target node {target_node_id} does not exist.\n")

        else:
            joining_node = Node(self.env, joining_node_id)
            target_node = self.nodes.get(target_node_id)

            msg = Message(env = self.env,
                            _type='insertion_request', 
                            _from=joining_node,
                            _to=target_node
            )

            self.nodes[joining_node.node_id] = joining_node
            print(f"[ {self.env.now} ] Node {joining_node.node_id} joined DHT {self.name}.\n")
            joining_node.send_message(msg)    


    def run_simulation(self, until_time):

        self.initialize()

        #for _ in range(0,2):
        #    self.join()

        self.join(6, 5)
        self.join(7, 4)

        for node in self.nodes.values():
            self.env.process(node.run())

        self.env.run(until=until_time)

