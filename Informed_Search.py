from copy import copy
import heapq
import random
import sys
import time
from typing import Optional

#/------------------------------------------------------------  
#   We use this class to create Node in the A* search tree
#   each node contain their current state of pancakes list,
#   flip_index: index for fliping, inorder to get to current pancake
#   state from it's parent node. They also contain backward and 
#   forward cost for itself. Also it's parent to keep track of the
#   history states.
#   Most of caculation is done in init method using some class method,
#   I think it's best we leave those node along after creating them, never change
#   a alive node's config.
#/-------------------------------------------------------------  
class Node:
    #/---------------------------------------------------------------------------------
    #   Init method, pancakes: list of pancakes before flip,
    #                  flip_index: index we want to flip pancakes, none for the first node,
    #                  parent: parent of this node, none for the first node,
    #                  id: current number of nodes we created, each node have different id,
    #                      used in compare when total cost is a tie.
    #/---------------------------------------------------------------------------------
    def __init__(self, pancakes: list[int], flip_index: Optional[int], parent, id: int) -> None:
        self.pancakes = pancakes
        self.flip_index = flip_index
        self.parent: Optional[Node] = parent
        if self.parent is not None: #if this is not the very first node
            self.flip(flip_index)
            self.backward_cost = self.parent.backward_cost + self.lens() - flip_index
        else:
            self.backward_cost = 0
        self.forward_cost = self.heuristic_func(self.pancakes)
        self.total_cost = self.backward_cost + self.forward_cost
        self.id = id
        

    #   convert this node to string, we only 
    #   care about the pancake list when printing
    def __str__(self) -> str:
        return str(self.pancakes)

    #/------------------------------------------------------
    #   Three method below is used for node compare in the 
    #   Priority queue, since we cannot compare object drictly,
    #   we want to override compare method. 
    #/------------------------------------------------------
    def __eq__(self, other) -> bool:    #equal
        if isinstance(other, Node):
            return self.total_cost == other.total_cost
        return False
    def __lt__(self, other) -> bool:    #less than
        if isinstance(other, Node):
            if self.total_cost == other.total_cost:
                #compare order of creation if total is tie
                return self.id < other.id
            return self.total_cost < other.total_cost
        return False   
    def __gt__(self, other) -> bool:    #greater than
        if isinstance(other, Node):
            if self.total_cost == other.total_cost:
                #compare order of creation if total is tie
                return self.id > other.id 
            return self.total_cost > other.total_cost
        return False
    

    #   Return length of the pancake list
    def lens(self) -> int:
        return len(self.pancakes)

    #   Heuristic function, return forward cost for input "node".
    def heuristic_func(self, pancakes: list[int]) -> int:
        result = 0
        for i in range(len(pancakes)-1):
            # if there is a gap between two adjacent pancake
            # increase forward cost by one
            if abs(pancakes[i]-pancakes[i+1]) > 1:
                result += 1
        return result

    #   We do the flip of pancakes by use this funciton.
    def flip(self, insert_index: int) -> None:
        length = self.lens()
        # Flip!
        self.pancakes[insert_index : length] = self.pancakes[insert_index : length][::-1]

#/------------------------------------------------------------------------
#   This class is a sub-class for Node, used for doing the uninform search,
#   the only difference between this class and it's supper class: Node is
#   the total cost for this funciton is only the backward cost, not backward and forward.
#/------------------------------------------------------------------------
class Uninform_Node(Node):
    def __init__(self, pancakes: list[int], flip_index: Optional[int], parent, id: int) -> None:
        super().__init__(pancakes, flip_index, parent, id)
        self.total_cost = self.backward_cost

#/------------------------------------------------------------------------
#   Class for Priority queue in searchs, used heapq to do the insert, delect min...
#   implementation does not have merge method, since I don't think we will be use 
#   in search problem.
#/------------------------------------------------------------------------
class My_Priority_queue():
    
    #   Create the heap, where we are 
    #   going to store all the nodes.
    #   Keep track of visited node.
    def __init__(self) -> None:
        self.heap: list[Node] = []
        self.visited = set()

    #   Let heapq to do the insert for us.
    def insert(self, child: Node) -> None:
        heapq.heappush(self.heap, child)

    #   Node with smallest total cost will 
    #   always in the first place(root of the heap).
    def find_min(self) -> Node:
        return self.heap[0]
    
    #   Let heapq to do the delete_min for us.
    #   Mark this node visited.
    def delete_min(self) -> Node:
        temp_node = heapq.heappop(self.heap)
        self.visited.add(str(temp_node.pancakes))
        return temp_node

    #   We want to go through the heap first to find if there
    #   is a node that share same pancakes list with the 
    #   new node we passed in.
    #   If we find such node, change it's total cost if the new node
    #   has smaller cost. Then we want to reheapify the heap, since 
    #   the key has just been decrease, that node might need to flow up.
    def decrease_key(self, new_node: Node) -> None:
        for old_node in self.heap:
            if old_node.pancakes == new_node.pancakes:
                if old_node > new_node:
                    Index = self.heap.index(old_node)
                    self.heap[Index] = new_node
                    heapq.heapify(self.heap)
                return None

    #   Go through the heap, find if there
    #   is a node that share same pancakes list with the 
    #   new node we passed in.
    def contain(self, node: Node) -> bool:
        for old_node in self.heap:
            if old_node.pancakes == node.pancakes:
                return True
        return False

    #   Return the length of the heap
    def lens(self) -> int:
        return len(self.heap)
    
#/------------------------------------------------------------------------
#   This class define the object we will use to run the A*.
#   Keep track of the frontier, where it is a My_Priority_queue,
#   I include all the work for A* in this class, instead of build it 
#   in a function, that would be way too hard to read.
#   Also there is a method called display, which will print out
#   the output.
#/------------------------------------------------------------------------
class A_star:
    #/--------------------------------
    #   We can create as many A_star object we want, but each object
    #   will only have it's own frontier.
    #/--------------------------------
    def __init__(self, pancakes: list[int]) -> None:
        #   First we need to check if this is a valid input
        self.pancake_check(pancakes)
        #   Initialize the frontier
        self.frontier = My_Priority_queue()
        #   Initialize the init state, 
        #   which have no parent and backward cost is 0
        init_state = Node(pancakes, None, None, 1)
        self.frontier.insert(init_state)
        #   Number of Node we totally created,
        #   use for compare between A* and uninform
        self.Node_num = 1
        #   This is the final result node, which we can trace back to 
        #   init node using it's parent.
        #   This result will stay None if there are no solution.
        self.result: Node = None
        #   Keep track the time
        self.time_used = None

    #   check if the given pancake list is vaild
    def pancake_check(self, pancakes: list[int]):
        for slice in pancakes:
            #   if the first in the list is not the plate
            if slice > pancakes[0]:
                print("ERROR: Can NOT have pancake lager than the plate!(input[0] should be largest)")
                exit(1)
        #   if there is only one pancake on the plate,
        #   there arre no point for flip
        if len(pancakes) < 3:
            print("ERROR: No point to search if there only 1 pancake!")
            exit(1)
        #   If some pair of adjaent pancake is not differ by 1
        if sum(pancakes) != (pancakes[0]*2 - len(pancakes)+1)*len(pancakes)/2:
            print("ERROR: After sort, each pair of adjaent pancake should only differ by 1!")
            exit(1)

    #   Create new nodes based on a given node, and put it in frontier
    def expand_childs(self, father: Node) -> None:
        for i in range(1,father.lens()-1):
            #   make a new list, so we won't pass old node's list to flip 
            dup_pancake = father.pancakes[:]
            #   assume this new node will be add to frontier
            self.Node_num += 1
            new_node = Node(dup_pancake, i, father, self.Node_num)
            #   if new node is not in fronter and not visited
            if (not self.frontier.contain(new_node)) and (str(new_node) not in self.frontier.visited):
                self.frontier.insert(new_node)
            #   if new node is in fronter, we invoke decrease key 
            #   to check if new node have a lower total cost
            elif self.frontier.contain(new_node):
                self.frontier.decrease_key(new_node)
                #   we are not adding new node to frontier,
                #   so we need to adjust node number
                self.Node_num -= 1
            else:
                self.Node_num -= 1
        return None

    #   This function will be call when the time we want to run A*
    def Run(self) -> None:
        #   start the timmer
        start = time.time()
        #   Never stop until we find the result
        while(True):
            #   if we have a empty frontier, then there is no solution
            if(self.frontier.lens() <= 0):
                print("Can not find a solution for input pancakes, please try other one!")
                return None
            curr_node = self.frontier.delete_min()
            #   if this node have forward cost of 0,
            #   then we sorted the list by fliping
            #   this is where we stop search.
            if curr_node.forward_cost == 0:
                #   update the result with actual result
                self.result = curr_node
                #   end the timer and update time_used
                self.time_used = time.time() - start
                return None
            self.expand_childs(curr_node)

    #   By invoke this method, result will be printed.
    def display(self, style: str) -> None:
        if(self.result is None):
            exit(1)

        solution_list: list[Node] = []
        current_node = self.result

        #   put the tree path for result in to a list for later use
        while(current_node.parent is not None):
            solution_list.append(current_node)
            current_node = current_node.parent
        #   since we stored the path 
        #   from result to root, we need to reverse it
        solution_list.reverse()
        print("Started from: ", current_node, "!")
        if (style == "long"):
            flip_num = 1
            #   for each node on the path
            for node in solution_list:
                print("Flip NO.", flip_num, ": ", node, "fliped from index ", node.flip_index)
                flip_num += 1
        print("Total number of Node created: ", self.Node_num)
        print("Finished searching, total time used: ", self.time_used)


#/------------------------------------------------------------------------
#   This class define the object we will use to run the Uninform search.
#   This is a sub-class for A_star, the only difference is this calss
#   is creating Uninform_Node instead of Node object
#/------------------------------------------------------------------------
class Uninform_search(A_star):
    def __init__(self, pancakes: list[int]) -> None:
        self.frontier = My_Priority_queue()
        #   creating Uninform_Node
        init_state = Uninform_Node(pancakes, None, None, 1)
        self.frontier.insert(init_state)
        self.Node_num = 1
        #   creating Uninform_Node
        self.result: Uninform_Node = None
        self.time_used = None

    def expand_childs(self, father: Node) -> None:
        for i in range(1,father.lens()-1):
            dup_pancake = father.pancakes[:]
            self.Node_num += 1
            #   creating Uninform_Node
            new_node = Uninform_Node(dup_pancake, i, father, self.Node_num)
            if (not self.frontier.contain(new_node)) and (str(new_node) not in self.frontier.visited):
                self.frontier.insert(new_node)
            elif self.frontier.contain(new_node):
                self.frontier.decrease_key(new_node)
                self.Node_num -= 1
            else:
                self.Node_num -= 1
        return None

def main():
    #   if numbers been pass in from STDIN
    if (len(sys.argv) > 1):
        Pancake = []
        for i in range(1,len(sys.argv)):
            Pancake.append(int(sys.argv[i]))
    #   random generate a pancake list with length of 8
    #   if no numbers been pass in from STDIN
    else:
        Pancake: list[int] = [8]
        Pancake[1:] = random.sample(range(1,8), 7)
    #   type long for full result, otherwise only the time and number of node will be display
    inp = input("How would you like your answer(long/short): ")
    #   create and invoke the A*
    Astar = A_star(Pancake)
    Astar.Run()
    Astar.display(inp)
    input("How would you like to see how Uniform search does(hit enter): ")
    #   create and invoke the Uninform search
    Uninform = Uninform_search(Pancake)
    Uninform.Run()
    Uninform.display(inp)
    
if __name__ == '__main__':
    main()