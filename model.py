from mesa import Model
from mesa.time import RandomActivation
from agent import Person
from mlsolver.kripke_model import TheShipNAgents
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

        self.dead_agents = []
        self.living_agents = list(self.schedule.agents)

        self.construct_kripke(N)
        self.construct_graph()
        self.init_game()



    # kripke model functions
    def construct_kripke(self, N):
        self.kripke_model = TheShipNAgents(N)


    # construct the graph, containing the rooms and their connections
    def construct_graph(self):
        N_rooms = 13
        
        # create N amount of rooms
        for i in range(N_rooms):
            self.rooms.append([])
        
        # establish the room connections
        self.corridors[0] = [2]
        self.corridors[1] = [2, 4]
        self.corridors[2] = [0, 1, 3, 5]
        self.corridors[3] = [2, 6]
        self.corridors[4] = [1, 5, 7, 11]
        self.corridors[5] = [2, 4, 6, 8]
        self.corridors[6] = [3, 5, 9, 12]
        self.corridors[7] = [4, 8]
        self.corridors[8] = [5, 7, 9, 10]
        self.corridors[9] = [6, 8]
        self.corridors[10] = [8]
        self.corridors[11] = [4]
        self.corridors[12] = [6]
       
    # initialize rooms and targets
    def init_game(self):
        # randomly distribute the agents over the rooms; don't make agent spawn in the same room
        available_rooms = [i for i in range(len(self.rooms))]
        for i in range(self.num_agents):
            selected = random.choice(available_rooms)
            self.rooms[selected].append(self.schedule.agents[i])
            self.schedule.agents[i].position = selected
            available_rooms.remove(selected)
        print("------------------------------------------------------")
        print("Filled rooms:")
        print(self.rooms)
        
        # randomly distribute killing targets among the agents
        """available_targets = [agent for agent in self.schedule.agents]
        for i in range(self.num_agents):
            selected_agent = random.choice(available_targets)
            # an agent can't have himself as a target
            while(selected_agent == self.schedule.agents[i]):
                selected_agent = random.choice(available_targets)
            self.schedule.agents[i].targets.append(selected_agent)
            available_targets.remove(selected_agent)

        print("------------------------------------------------------")
        print("Targets:")
        for i in range(self.num_agents):
            print(self.schedule.agents[i], ":", self.schedule.agents[i].targets)
        print("------------------------------------------------------")
        """

        # assign targets based on agent knowledge
        # take the first world to be the real world
        print("------------------------------------------------------")
        world = self.kripke_model.ks.worlds[0]
        print("Real world:",world)
        for i in range(self.num_agents):
            for formula in world.assignment:
                if( int(formula[0]) == i+1 ):
                    self.schedule.agents[i].targets.append(self.schedule.agents[int(formula[1]) - 1])
                    break
        print("Targets:")
        for i in range(self.num_agents):
            print(self.schedule.agents[i], ":", self.schedule.agents[i].targets)

        print("------------------------------------------------------")


        

    # all agents take a move step
    def move_agents(self):
        for agent in self.schedule.agents:
            agent.move()


    def step(self):
        print("Living:", self.living_agents)
        print("Dead:", self.dead_agents)
        # agents perform action step
        self.schedule.step()
        # agents perform move step
        self.move_agents()

        # store which agents are dead and alive, for clarity
        for agent in self.schedule.agents:
            if(not(agent.alive) and not(agent in self.dead_agents)):
                self.dead_agents.append(agent)
                self.living_agents.remove(agent)
