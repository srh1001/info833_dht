## Node.py 
import random
import simpy
from Message import Message
from typing_extensions import Self

class Node(object):
    def __init__(self, env: simpy.Environment, node_id: int):
        self.env: simpy.Environment = env
        self.node_id: int = node_id
        self.right_neighbour: Node = None
        self.left_neighbour: Node = None
        self.insertion_requests: list[Node] = []
        self.is_processing_insertion_request: bool = False
        self.is_inserted: bool = False
        
        self.update_requests: list[Message] = []
        self.is_processing_update_request: bool = False
        self.is_ready_to_update_messages: list[Message] = []
        self.update_neighbours_messages: list[Message] = []
        self.other_messages: list[Message] = []


    def __str__(self):
        return f"[ {self.env.now} ] I am node {self.node_id} and my neighbours are : left={self.left_neighbour.node_id} & right={self.right_neighbour.node_id}.\n"    

    def process_insertion_request(self, joining_node: Self):

        self.is_processing_insertion_request = True


        print(f"[ {self.env.now} ] Node {self.node_id} started processing insertion request from node {joining_node.node_id}.\n")

        if joining_node.node_id < self.node_id:

            if  not (self.left_neighbour.node_id >= self.node_id) and joining_node.node_id < self.left_neighbour.node_id: # si le noeud joignant est inférieur à mon voisin gauche et que je ne suis pas le min
                                                
                self.left_neighbour.add_insertion_request(joining_node)



            else:

                joining_node.right_neighbour = self
                joining_node.left_neighbour = self.left_neighbour
                self.left_neighbour.right_neighbour = joining_node
                self.left_neighbour = joining_node
                joining_node.is_inserted = True
                print(f"[ {self.env.now} ] Node {joining_node.node_id} is inserted : " +
                    f"left_neighbour={joining_node.left_neighbour.node_id if joining_node.left_neighbour != None else None} & " + 
                    f"right_neighbour={joining_node.right_neighbour.node_id if joining_node.right_neighbour != None else None}.\n")

                
        elif joining_node.node_id > self.node_id:
                                
                if  not (self.right_neighbour.node_id <= self.node_id) and joining_node.node_id > self.right_neighbour.node_id: # si le noeud joignant est supérieur à mon voisin droit et que je ne suis pas le max
                    self.right_neighbour.add_insertion_request(joining_node)
            
                else:

                    joining_node.left_neighbour = self
                    joining_node.right_neighbour = self.right_neighbour
                    self.right_neighbour.left_neighbour = joining_node
                    self.right_neighbour = joining_node
                    joining_node.is_inserted = True
                    print(f"[ {self.env.now} ] Node {joining_node.node_id} is inserted : " +
                        f"left_neighbour={joining_node.left_neighbour.node_id if joining_node.left_neighbour != None else None} & " + 
                        f"right_neighbour={joining_node.right_neighbour.node_id if joining_node.right_neighbour != None else None}.\n")
                
        self.is_processing_insertion_request = False


    def add_insertion_request(self, joining_node: Self): 
        self.insertion_requests.append(joining_node)
        print(f"[ {self.env.now} ] Node {joining_node.node_id} requested insertion to node {self.node_id}.\n")

        
    def process_insertion_requests(self):
        for joining_node in self.insertion_requests:
            self.process_insertion_request(joining_node)
            self.insertion_requests.remove(joining_node)
            

    def run(self):
            while True:
                if len(self.insertion_requests) > 0 and self.is_inserted==True and self.is_processing_insertion_request==False:
                    joining_node = self.insertion_requests.pop(0)
                    self.process_insertion_request(joining_node)

                # Attendre un certain temps avant de continuer
                yield self.env.timeout(random.randint(10, 100))