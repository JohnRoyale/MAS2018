from mesa import Agent
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
        # for each roommate, if the agent did not flee from them, the agent knows that they are not one of its killers
        if(self.last_move != "flee"):
            for agent in self.roommates:
                id = agent.unique_id
                formula = str(id) + str(self.unique_id)
                self.kb[formula] = [False, False]
            self.model.update_knowledge()

        # check if, according to transition relations, an agent knows its murderer(s)
        # look at the transition relations for this agent
        relations = list(self.model.kripke_model.ks.relations[str(self.unique_id)])

        world1 = relations[0][0]
        potential_murderer = world1.index(str(self.unique_id))
        murderer_found = True
        # check all worlds to see if potential murderer is in all of them
        for worlds in relations:
            w = worlds[0]
            #print(w)
            murderer = w.index(str(self.unique_id))
            if(murderer != potential_murderer):
                murderer_found = False
                break

        # if murderer was the same in all worlds considered possible by the agent, it has to be his murderer
        if(murderer_found):
            self.murderers.append(self.model.schedule.agents[potential_murderer])
            formula = str(potential_murderer) + str(self.unique_id)
            self.kb[formula] = [True, False]





    # move the agent to a random other room
    def move(self):
        corridors = self.model.corridors[self.position]
        selected = random.randint(0, len(corridors) - 1)
        self.position = corridors[selected]
        print(self, "moved to room", self.position)

        # update the rooms
        self.model.update_rooms()


    # optional action (kill, flee, stay)
    def flee(self):
        self.move()
    
    def kill(self, target, room):
        print(self, "stabs", target, "to death in room", str(self.position) + "!")
        # victim agent is now no longer alive; remove him from murderer's target list
        target.alive = False

        self.targets.remove(target)

        # add observers to new targets; add agent as murderer to observers;
        #don't add self as murderer
        for agent in room:
            if (agent != self and agent != target):
                self.targets.append(agent)
                agent.murderers.append(self)

    # don't take any action
    def stay(self):
        print(self, "stayed in room", self.position)

    def step(self):
        if(self.alive):
            #print("Agent", self.unique_id + 1, "is now acting.")
            #print("Room:", self.position)

            # get the room that the agent is in
            room = self.model.rooms[self.position]
            # remember the roommates
            self.roommates = room[:]
            # remove self from roommates
            #print(room, self.position)
            self.roommates.remove(self)

            # if the agent is in the same room with any of its murderers, the agent flees
            if(any(murderer in room for murderer in self.murderers)):
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

            self.updateKB()


    def __repr__(self):
        return "Agent " + str(self.unique_id)

