from mesa import Agent
import random

class Person(Agent):
    def __init__(self, i, model):
        super().__init__(i, model)
        self.alive = True
        self.position = 0
        self.targets = []
        self.murderers = []
        self.kb = []


    # actions
    def evaluateKB(self):
        pass


    def updateKB(self):
        pass

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
            # if the agent is in the same room with any of its murderers, the agent flees
            if(any(murderer in room for murderer in self.murderers)):
                self.flee()
            #if the agent is in the same room with any of its targets, the agent will select
            # one of them randomly to kill
            elif(any(target in room for target in self.targets)):
                selected = random.randint(0, len(self.targets) - 1)
                self.kill(self.targets[selected], room)
            else:
                self.stay()

            self.evaluateKB()
            self.updateKB()



    def __repr__(self):
        return "Agent " + str(self.unique_id + 1)

