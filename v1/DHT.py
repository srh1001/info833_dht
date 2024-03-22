## DHT.py
import random 
import simpy
from Node import Node

class DHT(object):
    def __init__(self, name: str, env: simpy.Environment):
        self.name: str = name
        self.env: simpy.Environment = env
        self.nodes: list[Node] = []
        self.processes = []

    def __str__(self):
        result = f"[ {self.env.now} ] State of DHT {self.name}:\n"
        for n in self.nodes:
            left_neighbour_id = n.left_neighbour.node_id if n.left_neighbour is not None else None
            right_neighbour_id = n.right_neighbour.node_id if n.right_neighbour is not None else None
            result += f"{n.node_id} : left_neighbour={left_neighbour_id} & right_neighbour={right_neighbour_id}\n"
        return result + "\n"

    
    def add_node(self):
        new_node_id = random.randint(1, 20)  # Choisir une plage d'IDs
        while new_node_id in [n.node_id for n in self.nodes]:
            new_node_id = random.randint(1, 20)

        joining_node = Node(self.env, new_node_id)

        if self.nodes == []:
            self.nodes.append(joining_node)
            print(f"[ {self.env.now} ] First node {joining_node.node_id} joined DHT {self.name}.")

            joining_node.left_neighbour = joining_node
            joining_node.right_neighbour = joining_node
            joining_node.is_inserted = True

            print(f"[ {self.env.now} ] Node {joining_node.node_id} is inserted : " +
                f"left_neighbour={joining_node.left_neighbour.node_id if joining_node.left_neighbour != None else None} & " + 
                f"right_neighbour={joining_node.right_neighbour.node_id if joining_node.right_neighbour != None else None}.\n")


        elif joining_node.node_id in [n.node_id for n in self.nodes] :
            print(f"[ {self.env.now} ] Node id {joining_node.node_id} already used in DHT {self.name}. Node couldn't be inserted.\n")

        else:
            target_node = random.choice(self.nodes)
            self.nodes.append(joining_node)
            print(f"[ {self.env.now} ] Node {joining_node.node_id} joined DHT {self.name}.")
            target_node.add_insertion_request(joining_node)

    def run_simulation(self, until_time):
        for node in self.nodes:
            self.env.process(node.run())

        self.env.run(until=until_time)



    # def add_node(self, joining_node: Node):
    #     if self.nodes == []:
    #         self.nodes.append(joining_node)
        
    #         print(f"First node {joining_node.node_id} added to DHT {self.name}.\n")

    #     elif joining_node.node in [n.node_id for n in self.nodes] :
    #         print(f"Node id {joining_node.node_id} already used in DHT {self.name}. Node couldn't be inserted.\n")

    #     else:
    #         target_node = random.choice(self.nodes)
    #         target_node.add_insertion_request(joining_node)
    #         self.nodes.append(joining_node)
    #         print(f"Node {joining_node.node_id} added to DHT {self.name} by requesting for insertion.\n")