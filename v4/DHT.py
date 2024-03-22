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
        self.env.process(node1.run())

        self.nodes[2] = node2
        self.env.process(node2.run())
        
        self.nodes[3] = node3
        self.env.process(node3.run())

        self.nodes[4] = node4
        self.env.process(node4.run())

        self.nodes[5] = node5
        self.env.process(node5.run())


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
        new_node_id = random.randint(6, 20)  # Choisir une plage d'IDs
        while new_node_id in self.nodes.keys():
            new_node_id = random.randint(1, 20)

        joining_node = Node(self.env, new_node_id)
        if self.nodes:

            target_node = random.choice(list(self.nodes.values()))
            msg = Message(env = self.env,
                            _type='insertion_request', 
                            _from=joining_node,
                            _to=target_node
            )

            self.nodes[new_node_id] = joining_node
            print(f"[ {self.env.now} ] Node {joining_node.node_id} joined DHT {self.name}.\n")
            self.env.process(joining_node.run())
            joining_node.send_message(msg)
        else:
            print("Cannot join DHT, no existing nodes.")


    def join_node(self, joining_node: Node, target_node: Node):
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

            self.env.process(joining_node.run())
            joining_node.send_message(msg)    


    def join_id(self, joining_node_id: int, target_node_id: int):
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
            self.env.process(joining_node.run())
            joining_node.send_message(msg)

    def leave_random(self):
            if len(self.nodes) > 0:
                target_node = random.choice(list(self.nodes.values()))

                while target_node.is_inserted is False:
                    target_node = random.choice(list(self.nodes.values()))

                self.env.process(target_node.leave_dht())
                del self.nodes[target_node.node_id]
                print(f"[{self.env.now}] Node {target_node.node_id} removed from DHT.\n")
            else:
                print(f"[{self.env.now}] No node to make leave DHT currently.\n")



    def schedule_join_random(self, n: int = 2):
        while True:
            delay = random.uniform(5, 15)
            delay = 5
            yield self.env.timeout(delay)
            
            for _ in range(0,n):
                self.join_random()

    def schedule_leave_random(self, n: int = 2):

        while True:
            delay = random.uniform(10, 12)
            delay = 10
            yield self.env.timeout(delay)

            for _ in range(0,n):
                self.leave_random()

            

    def run_simulation(self, until_time):

        self.initialize()

        self.join_id(6, 5)
        self.join_id(7, 4)

        for _ in range(0,2):
            self.join_random()

        self.env.process(self.schedule_join_random())

        self.env.process(self.schedule_leave_random())

        self.env.run(until=until_time)






