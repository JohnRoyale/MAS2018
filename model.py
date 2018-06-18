from mesa import Model
from mesa.time import RandomActivation, BaseScheduler
from agent import Person
from mlsolver.kripke_model import TheShipNAgents
import random


class ShipModel(Model):
    """The ship with a number of logical agents"""
    def __init__(self, N):
        self.schedule = BaseScheduler(self)
        self.num_agents = N
        self.kripke_model = []
        # the rooms store which agents are currently in which rooms
        self.rooms = []
        # the corridors determine the connections between the rooms
        self.corridors = {}
        # amount of rooms
        self.N_rooms = 13

        # keep track of the real world
        self.real_world = None

        for i in range(self.num_agents):
            a = Person(i, self)
            self.schedule.add(a)

        self.dead_agents = []
        self.living_agents = list(self.schedule.agents)
        self.smart_agents = []

        self.construct_kripke(N)
        self.construct_graph()
        self.init_game()

        print("Initial amount of worlds:", len(self.kripke_model.ks.worlds))







    # kripke model functions
    def construct_kripke(self, N):
        self.kripke_model = TheShipNAgents(N)


    # construct the graph, containing the rooms and their connections
    def construct_graph(self):
        # create N amount of rooms
        for i in range(self.N_rooms):
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

    def update_knowledge(self):
        """
        # take the real world
        world = self.kripke_model.ks.worlds[0]
        for p in self.kripke_model.propositions:
            # if an agent knows a propositions, add it to its knowledge base
            for agent in self.schedule.agents:
                self.kripke_model.add_knowledge(agent, world, p)

        # update the kripke structure, using the new knowledge among agents
        self.kripke_model.update_structure(self.schedule.agents)
        """

        self.kripke_model.update_structure(self.schedule.agents)
        #self.kripke_model.ks.print()

    # the real world has to have unique killer-target pairs
    def correct_real_world(self, world):
        counts = []
        for i in range(len(self.schedule.agents)):
            counts.append(0)
        for formula in world.assignment:
            counts[int(formula[1])] += 1
            # if agent appears as a target for more than 1 agent, the world is not suitable as the real world
            if(counts[int(formula[1])] > 1):
                return False
        return True





    # initialize rooms, targets and knowledge
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
        print("------------------------------------------------------")
        # take a random world where each agent targets a different agent
        worlds = self.kripke_model.ks.worlds
        self.real_world = random.choice(worlds)

        while(not(self.correct_real_world(  self.real_world))):
            self.real_world = random.choice(worlds)

        print("***** Real world: ******", self.real_world)

        for i in range(self.num_agents):
            for formula in self.real_world.assignment:
                if( int(formula[0]) == i ):
                    self.schedule.agents[i].targets.append(self.schedule.agents[int(formula[1])])
                    self.schedule.agents[i].kb[formula] = [True, False]
                    break
        print("Targets:")
        for i in range(self.num_agents):
            print(self.schedule.agents[i], ":", self.schedule.agents[i].targets)

        print("------------------------------------------------------")


        # add initial knowledge to agent's knowledge base
        self.update_knowledge()

        print("------------------------------------------------------")
        print("Initial Agent knowledge:")
        for agent in self.schedule.agents:
            print(agent, ":", agent.kb)

        

    # all agents take a move step
    def move_agents(self):
        for agent in self.schedule.agents:
            if (agent.alive):
                agent.updateKB()
                agent.move()


    # update the position of agents in the rooms
    def update_rooms(self):
        #reset rooms
        self.rooms = []
        for i in range(self.N_rooms):
            self.rooms.append([])
        for i in range(self.num_agents):
            position = self.schedule.agents[i].position
            self.rooms[position].append(self.schedule.agents[i])





    def step(self):
        #print("Worlds left:", len(self.kripke_model.ks.worlds))

        print("Living:", self.living_agents)
        print("Dead:", self.dead_agents)
        print("Smart:", self.smart_agents)
        print("Filled rooms:")
        print(self.rooms)
        # agents perform action step
        print("------")
        print("ACTING:")

        # re-add agents to schedule
        # check if agent is in room with target
        """agents_copy = list(self.schedule.agents)[:]
        self.schedule = BaseScheduler(self)

        for i in range(self.num_agents):
            agent = agents_copy[i]
            room = self.rooms[agent.position]
            if(any(target in room for target in agent.targets)):
                self.schedule.add(agent)
                agents_copy.remove(agent)

        # add any remaining agents to the schedule
        for agent in agents_copy:
            self.schedule.add(agent)"""


        self.schedule.step()
        # agents perform move step
        print("------")
        print("MOVING:")
        self.move_agents()

        # store which agents are dead and alive, for clarity
        for agent in self.schedule.agents:
            if(agent.alive == False and agent not in self.dead_agents):
                self.dead_agents.append(agent)
                self.living_agents.remove(agent)

            if(agent.alive and len(agent.murderers) != 0 and agent not in self.smart_agents):
                self.smart_agents.append(agent)


