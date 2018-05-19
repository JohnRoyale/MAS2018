from mesa import Agent
import random

class Person(Agent):
    def __init__(self, i, model):
        super().__init__(i, model, position, target)
        self.alive = True
        self.position = position
        self.targets = targets
        self.murderers = []
        self.kb = kb
        self.step()

    # actions
    def evaluateKB(self):
        pass


    def updateKB(self):
        pass

    # move the agent to a random other room
    def move(self):
        corridors = model.corridors[position]
        selected = random.randint(0, len(corridors) - 1)
        self.position = selected

    # optional action (kill, flee, stay)
    def flee(self):
        self.move()
    
    def kill(self, target):
        # victim agent is now no longer alive; remove him from murderer's target list
        target.alive = False
        self.targets.remove(target)
        # add observers to new targets; add agent as murderer to observers;
        #don't add self as murderer
        for agent in room:
            targets.add(agent)
            if(agent != self):
                agent.murderer.add(self)

    # don't take any action
    def stay(self):
        pass

    def step(self):
        if(self.alive):
            # get the room that the agent is in
            room = model.rooms[position]
            # if the agent is in the same room with any of its murderers, the agent flees
            if(any(murderer in room for murderer in murderers)):
                self.flee()
            #if the agent is in the same room with any of its targets, the agent will select
            # one of them randomly to kill
            elif(any(target in room for target in targets)):
                selected = random.randint(0, len(targets) - 1)
                self.kill(self.targets[selected])
            else:
                self.stay()

            self.evaluateKB()
            self.updateKB()
            
