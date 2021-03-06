from mesa import Agent
from mlsolver.formula import Atom
import random

class Person(Agent):
    def __init__(self, i, model):
        super().__init__(i, model)
        self.alive = True
        self.position = 0
        self.targets = []
        self.murderers = []
        self.kb = {}
        # remember an agent's last move
        self.last_move = ""
        #remember an agent's last roommates
        self.roommates = []


    # actions
    def evaluateKB(self):
        pass

    # update an agent's knowledge base based on recent events; then update the kripke model
    def updateKB(self):
        # for each roommate, if the agent did not flee from them, the roomate knows that the other agents
        #  are not his killer
        if(self.last_move != "flee"):
            for agent in self.roommates:
                if(agent.alive and agent != self):
                    id = agent.unique_id
                    formula = str(id) + str(self.unique_id)
                    #self.kb[formula] = [False, False]
                    for otheragent in self.roommates:
                        otheragent.kb[formula] = [False, False]


        if (self.last_move == "flee"):
            for agent in self.roommates:
                if(agent.alive):
                    if(len(self.roommates) == 3):
                        if(agent != self and agent not in self.murderers):
                            formula = str(self.murderers[0].unique_id) + str(self.unique_id)
                            agent.kb[formula] = [True, False]
                    if (len(self.roommates) > 3):
                        if (agent != self and agent not in self.murderers):
                            possible_murderers = self.roommates[:]
                            possible_murderers.remove(self)
                            possible_murderers.remove(agent)
                            formula = ""
                            for m in possible_murderers:
                                formula = formula + str(m.unique_id) + str(self.unique_id) + "v"
                                formula = formula[:-1]
                            agent.kb[formula] = [True, False]






        # check if, according to transition relations, an agent knows its murderer(s)
        # look at the transition relations for this agent
        relations = list(self.model.kripke_model.ks.relations[str(self.unique_id)])

        world1 = relations[0][0]
        potential_murderer = world1.index(str(self.unique_id))
        murderer_found = True
        # check all worlds to see if potential murderer is in all of them
        for worlds in relations:
            w = worlds[0]
            murderer = w.index(str(self.unique_id))
            if(murderer != potential_murderer):
                murderer_found = False
                break

        # if murderer was the same in all worlds considered possible by the agent, it has to be his murderer
        if(murderer_found):
            self.murderers.append(self.model.schedule.agents[potential_murderer])
            formula = str(potential_murderer) + str(self.unique_id)
            self.kb[formula] = [True, False]

        self.model.update_knowledge()



    # move the agent to a random other room
    def move(self, flee=False):
        corridors = self.model.corridors[self.position]
        selected = random.randint(0, len(corridors) - 1)
        self.position = corridors[selected]

        if(flee):
            output = str(self) + " fled to room " + str(self.position)
            print(output)
            self.model.print_queue.append(output)
        else:
            output = str(self) + " moved to room " + str(self.position)
            print(output)
            self.model.print_queue.append(output)

        # update the rooms
        self.model.update_rooms()


    # optional action (kill, flee, stay)
    def flee(self):
        self.move(flee=True)
    
    def kill(self, target, room):
        output = str(self) + " kills " + str(target) + " in room " + str(self.position) + "!"
        print(output)
        self.model.print_queue.append(output)
        # victim agent is now no longer alive; remove him from murderer's target list
        target.alive = False

        self.targets.remove(target)

        # update knowledge of target
        f = (str(self.unique_id) + str(target.unique_id))
        target.kb[f] = [True, True]
        f = Atom(f)
        self.model.kripke_model.ks = self.model.kripke_model.ks.solve_a(str(target.unique_id), f)

        # update knowledge of any observers present
        for agent in room:
            if (agent != self and agent != target):
                # add new knowledge to kb of witness
                agent.kb[(str(self.unique_id) + str(target.unique_id))] = [True, False]

    # don't take any action
    def stay(self):
        output = str(self) + " stayed in room " + str(self.position)
        print(output)
        self.model.print_queue.append(output)

    def step(self):
        if(self.alive):
            #print("Agent", self.unique_id + 1, "is now acting.")
            #print("Room:", self.position)

            # get the room that the agent is in
            room = self.model.rooms[self.position]
            # remember the roommates
            self.roommates = room[:]
            print("Roommates: ", self.roommates)
            # remove self from roommates
            #print(room, self.position)
            self.roommates.remove(self)

            # if the agent is in the same room with any of its murderers, the agent flees
            if(any(murderer and murderer.alive in room for murderer in self.murderers)):
                self.flee()
                self.last_move = "flee"
            #if the agent is in the same room with any of its targets, the agent will select
            # one of them randomly to kill
            elif(any(target in room for target in self.targets)):
                selected = random.randint(0, len(self.targets) - 1)
                self.kill(self.targets[selected], room)

                self.last_move = "kill"
            else:
                self.stay()
                self.last_move = "stay"



    def __repr__(self):
        return "Agent " + str(self.unique_id)

