from mesa import Model
from mesa.time import RandomActivation
from agent import Person
from mlsolver.kripke_model import TheShipNAgents
import random
import pygame
import time
import sys
from pygame.locals import *


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
        # amount of rooms
        self.N_rooms = 13

        for i in range(self.num_agents):
            a = Person(i, self)
            self.schedule.add(a)

        self.dead_agents = []
        self.living_agents = list(self.schedule.agents)
        self.smart_agents = []

        self.construct_kripke(N)
        self.construct_graph()
        self.init_game()

        # set visual parameters
        pygame.init()
        self.MAX_FPS = 50
        pygame.mouse.set_visible
        self.mouse = {'l_down': -1, 'l_up': -1, 'pos': (0,0)}

        self.background = pygame.image.load("titanic.png")
        self.game_height = 100
        self.roomlocations = [(200,self.game_height+250), (250,self.game_height+250), (300,self.game_height+250), (350,self.game_height+250), 
                              (400,self.game_height+250), (450,self.game_height+250), (500,self.game_height+250), (550,self.game_height+250), 
                              (600,self.game_height+250), (650,self.game_height+250), (700,self.game_height+250), (750,self.game_height+250), 
                              (800,self.game_height+250)]


        info = pygame.display.Info()
        #window_dimensions = (self.screen_width, self.screen_height)
        window_dimensions = (1600,1000)
        self.screen_width = int(window_dimensions[0])
        self.screen_height = int(window_dimensions[1])
        #self.screen_width = int(self.UI_PORTION * self.screen_width)
        self.GAMEDISPLAY = pygame.display.set_mode(window_dimensions)
        pygame.display.set_caption('The Ship')

        self.draw_init(self.GAMEDISPLAY)
        self.draw_step(self.GAMEDISPLAY)


        self.play = False
        self.running = True


    ################### init functions ######################
    
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
        # take the first world to be the real world
        print("------------------------------------------------------")
        world = self.kripke_model.ks.worlds[0]
        for i in range(self.num_agents):
            for formula in world.assignment:
                if( int(formula[0]) == i ):
                    self.schedule.agents[i].targets.append(self.schedule.agents[int(formula[1])])
                    self.schedule.agents[i].kb[formula] = False
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


    ################# update functions ################

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
        self.kripke_model.ks.print()        

    # all agents take a move step
    def move_agents(self):

        for agent in self.schedule.agents:
            if (agent.alive):
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


    ################ event handlers ###############
    
    def reset_mouse(self):
        self.mouse['l_down'] = -1 
        self.mouse['l_up'] = -1

    def button_active(self, button, check_click=True):
        if check_click and not self.mouse['l_down'] == 1:
            # No mouse click
            return False
            
        if self.mouse['pos'][0] >= button.x + button.w or \
           self.mouse['pos'][0] < button.x:
            return False
        if self.mouse['pos'][1] >= button.y + button.h or \
           self.mouse['pos'][1] < button.y:
            return False
        return True

    def check_buttons(self):
        if self.button_active(self.start_rect):
            self.pause = False
        if self.button_active(self.pause_rect):
            self.pause = True    
        if self.button_active(self.step_rect):
            self.step()


    def parse_events(self, event_handle):
        # Handle input events
        for event in event_handle:
            if event.type == QUIT:
                quit = True
                pygame.quit()
                sys.exit()
            else:
                try:
                    self.mouse['pos'] = event.dict['pos']
                except:
                    self.mouse['pos'] = (0,0)
                if event.type == MOUSEBUTTONDOWN:
                    if event.dict['button'] == 1:
                        self.mouse['l_down'] = 1
                elif event.type == MOUSEBUTTONUP:
                    if event.dict['button'] == 1:
                        self.mouse['l_up'] = 1


    ################ visualization functions ###################
    
    def draw_init(self, screen):
        self.control_rect = Rect(0, 0, self.screen_width, 100)
        self.game_rect = Rect(0, 100, self.screen_width, 500)
        self.actions_rect = Rect(0, 600, self.screen_width/2, 400)
        self.info_rect = Rect(1+self.screen_width/2, 100, self.screen_width, 400)

        # control boxes
        self.button_amount = 3
        self.start_rect = Rect(0, 0, self.screen_width/self.button_amount, 100)
        self.pause_rect = Rect(1*self.screen_width/self.button_amount, 0, self.screen_width/self.button_amount, 100)
        self.step_rect = Rect(2*self.screen_width/self.button_amount, 0, self.screen_width/self.button_amount, 100)
        # self.pause_rect = Rect(3*self.screen_width/self.button_amount, 0, self.screen_width/self.button_amount, 100)


        # self.GAMEDISPLAY.fill([255, 255, 255], self.game_rect)
        # self.GAMEDISPLAY.fill([0, 0, 0], self.control_rect)
        # self.GAMEDISPLAY.fill([255, 255, 255], self.actions_rect)
        # self.GAMEDISPLAY.blit(self.background, (0, 100))
    
    def draw_step(self, screen):
        self.draw_controls(screen)
        self.draw_level(screen)
        self.draw_agents(screen)
        self.draw_actions(screen)
        self.draw_knowledge(screen)

    def draw_controls(self, screen):
        screen.fill([0, 0, 0], self.control_rect)
        screen.fill([0, 255, 0], self.start_rect)
        screen.fill([255, 0, 0], self.pause_rect)
        screen.fill([0, 0, 255], self.step_rect)

    def draw_level(self, screen):
        screen.fill([255, 255, 255], self.game_rect)
        screen.blit(self.background, (0, 100))

    def draw_agents(self, screen):
        #draw rooms and agents in rooms
        for idx, room in enumerate(self.rooms):
            location = self.roomlocations[idx]
            # draw room

            agents = len(room)
            for agent in room:
                # draw agentnumbers under room
                pass

        for idx, corridor in enumerate(self.corridors):
            roomlocation = self.roomlocations[idx]
            # for connection in corridor:
            #     connector = self.roomlocations[connection]
            #     # draw arrow from roomloc to connectorloc
            #     pass        

            
    def draw_actions(self, screen):
        screen.fill([255, 255, 255], self.actions_rect)

    def draw_knowledge(self, screen):
        pass



    ################## main loop function ######################
    
    def step(self):
        # print("ROOMS:", self.rooms)
        # print()
        print("Living:", self.living_agents)
        print("Dead:", self.dead_agents)
        print("Smart:", self.smart_agents)
        # agents perform action step
        print("------")
        print("ACTING:")
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

        # redraw game 
        # self.draw_step(self.GAMEDISPLAY)
        # pygame.display.update()

        if len(self.smart_agents) > 0:
            self.running = False

    def run(self): 
        quit = False
        self.pause = False
        TICK = USEREVENT + 1
        pygame.time.set_timer(TICK, 1000)
        # Simulation loop
        while not quit:
            frame_time = pygame.time.get_ticks()
            
            # Clear inputs each frame
            self.reset_mouse()
            self.key = None
            
            if(pygame.event.peek(TICK) and not self.pause):
                self.step()
            self.parse_events(pygame.event.get())

            self.check_buttons()

            self.draw_step(self.GAMEDISPLAY)
                        
            pygame.display.update()
            
            duration = pygame.time.get_ticks() - frame_time
            if duration < 1000/self.MAX_FPS:
                x = 1000/self.MAX_FPS - duration
                pygame.time.delay(int(x))
                
            self.last_frame_time = pygame.time.get_ticks() - frame_time
                
        pygame.quit()


############### run program #############

if __name__ == '__main__':
    try:
        n = int(sys.argv[1])
        if (n > 3 and n < 6):
            game = ShipModel(n)
            game.run()
            sys.exit()
        else:
            print("Input 4 or 5 agents")
    except:
        print("Give the amount of agents as an integer")
    