from mesa import Model
from mesa.time import RandomActivation
from agent import Person
import random


class ShipModel(Model):
    """The ship with a number of logical agents"""
    def __init__(self, N):
        self.schedule = RandomActivation(self)
        self.num_agents = N
        self.kripke_model = []
        # the rooms store which agents are currently in which rooms
        self.rooms = []
        # the corridors determine the connections between the rooms
        self.corridors = {}

        for i in range(self.num_agents):
            a = Person(i, self)
            self.schedule.add(a)

        construct_graph()
        init_game()
        construct_kripke()
        

    # kripke model functions
    def construct_kripke(self):
        pass


    # construct the graph, containing the rooms and their connections
    def construct_graph(self):
        N_rooms = 13
        
        # create N amount of rooms
        for i in range(N_rooms):
            self.rooms.append([])
        
        # establish the room connections
        self.corridors[1] = [3]
        self.corridors[2] = [3, 5]
        self.corridors[3] = [1, 2, 4, 6]
        self.corridors[4] = [3, 7]
        self.corridors[5] = [2, 6, 8, 12]
        self.corridors[6] = [3, 5, 7, 9]
        self.corridors[7] = [4, 6, 10, 13] 
        self.corridors[8] = [5, 9]
        self.corridors[9] = [6, 8, 10, 11]
        self.corridors[10] = [7, 9]
        self.corridors[11] = [9]
        self.corridors[12] = [5]
        self.corridors[13] = [7]          
       
    # initialize rooms and targets
    def init_game(self):
        # randomly distribute the agents over the rooms; don't make agent spawn in the same room
        available_rooms = [i+1 for i in range(len(self.rooms))]
        for i in range(self.num_agents):
            selected = random.choice(available_rooms)
            self.rooms[selected].append(self.schedule.agent[selected])
            available_rooms.remove(selected)
        
        # randomly distribute killing targets among the agents
        available_targets = [agent for agent in self.schedule.agent]
        for i in range(self.num_agents):
            selected = random.choice(available_targets)
            # an agent can't have himself as a target
            while(self.schedule.agent[selected] != self.schedule.agent[i]):
                selected = random.choice(available_targets)
            self.schedule.agent[i].targets.append(self.schedule.agent[selected])
            available_targets.remove(self.schedule.agent[selected])
   
            
            
        

    # all agents take a move step
    def move_agents(self):
        for agent in self.schedule.agent:
            agent.move()


    def step(self):
        # agents perform action step
        self.schedule.step()
        # agents perform move step
        self.move_agents()
