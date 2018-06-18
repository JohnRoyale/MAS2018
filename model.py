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
        self.N_rooms = 8

        # keep track of the real world
        self.real_world = None

        # initialize print queue
        self.print_queue = []

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

        self.background = pygame.image.load("ship2.jpg")
        self.bg_width = self.background.get_width()
        self.bg_height = self.background.get_height()
        self.small_text = pygame.font.SysFont(None, 20)
        self.medium_text = pygame.font.SysFont(None, 30)
        self.text = pygame.font.SysFont(None, 40)
        self.game_height = 100
        self.zero_location = (self.bg_width/2 + 50, 300)
        self.roomlocations = [(self.zero_location[0], self.zero_location[1]),
                              (self.zero_location[0] - 100, self.zero_location[1] + 100),
                              (self.zero_location[0] + 100, self.zero_location[1] + 100),
                              (self.zero_location[0] - 100, self.zero_location[1] + 200),
                              (self.zero_location[0] + 100, self.zero_location[1] + 200),
                              (self.zero_location[0] - 250, self.zero_location[1] + 150),
                              (self.zero_location[0] + 250, self.zero_location[1] + 150),
                              (self.zero_location[0], self.zero_location[1] + 250)]


        info = pygame.display.Info()
        #window_dimensions = (self.screen_width, self.screen_height)
        window_dimensions = (self.bg_width, 1000)
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
        self.corridors[0] = [1, 2]
        self.corridors[1] = [0, 2, 3, 5]
        self.corridors[2] = [0, 1, 4, 6]
        self.corridors[3] = [1, 4, 7]
        self.corridors[4] = [2, 3, 6, 7]
        self.corridors[5] = [1, 3]
        self.corridors[6] = [2, 4]
        self.corridors[7] = [3, 4]

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

    # the real world has to have unique killer-target pairs
    def correct_real_world(self, world):
        counts = []
        for i in range(len(self.schedule.agents)):
            counts.append(0)
        for formula in world.assignment:
            counts[int(formula[1])] += 1
            # if agent appears as a target for more than 1 agent, the world is not suitable as the real world
            if (counts[int(formula[1])] > 1):
                return False
        return True

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
        self.actions_rect = Rect(0, 100+self.bg_height, self.screen_width/2, 400)
        self.info_rect = Rect(1+self.screen_width/2, 100+self.bg_height, self.screen_width/2, 400)

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
        self.draw_level(screen)
        self.draw_controls(screen)
        self.draw_agents(screen)
        self.draw_actions(screen)
        self.draw_knowledge(screen)

    def draw_controls(self, screen):
        screen.fill([220, 220, 220], self.control_rect)
        # screen.fill([220, 220, 220], self.start_rect)
        # screen.fill([220, 220, 220], self.pause_rect)
        # screen.fill([220, 220, 220], self.step_rect)
        pygame.draw.rect(screen, [200,200,200], self.start_rect, 5)
        pygame.draw.rect(screen, [200,200,200], self.pause_rect, 5)
        pygame.draw.rect(screen, [200,200,200], self.step_rect, 5)

        screen.blit(self.text.render("Play", True, [0, 0, 0]), (self.start_rect.x+(self.start_rect.w/2)-20, 40))
        screen.blit(self.text.render("Pause", True, [0, 0, 0]), (self.pause_rect.x+(self.pause_rect.w/2)-20, 40))
        screen.blit(self.text.render("Next", True, [0, 0, 0]), (self.step_rect.x+(self.step_rect.w/2)-20, 40))

    def draw_level(self, screen):
        screen.fill([220, 220, 220])
        screen.blit(self.background, (0, 100))

    def draw_agents(self, screen):
        for idx, corridor in enumerate(self.corridors):
            #print(self.corridors[idx])
            #print(idx)
            roomlocation = self.roomlocations[idx]
            temp_roomloc = (roomlocation[0]+50, roomlocation[1]+15)
            for connection in self.corridors[idx]:
                connector = self.roomlocations[connection]
                temp_connectorloc = (connector[0]+50, connector[1]+15)
                pygame.draw.line(screen, [0, 0, 0], temp_roomloc, temp_connectorloc, 3)

        #draw rooms and agents in rooms
        for idx, room in enumerate(self.rooms):
            location = self.roomlocations[idx]
            room_agents = []
            for agent in room:
                room_agents.append(agent.unique_id)

            rect = Rect(location[0], location[1], 100, 30)
            pygame.draw.rect(screen, [200, 200, 200], rect)
            screen.blit(self.small_text.render(str(idx) + "  " + str(room_agents), True, [0, 0, 0]), (rect.x+5, rect.y+5))




    def draw_actions(self, screen):
        pygame.draw.rect(screen, [200,200,200], self.actions_rect, 5)
        y = self.actions_rect.y+5
        for action in self.print_queue:
            screen.blit(self.medium_text.render(str(action), True, [0, 0, 0]), (self.actions_rect.x+5, y))
            y += 25

    def draw_knowledge(self, screen):
        pygame.draw.rect(screen, [200,200,200], self.info_rect, 5)



    ################## main loop function ######################

    def step(self):
        #print("Worlds left:", len(self.kripke_model.ks.worlds))
        self.print_queue = []

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

        # redraw game
        # self.draw_step(self.GAMEDISPLAY)
        # pygame.display.update()

        if len(self.smart_agents) > 0:
            self.running = False

    def run(self):
        quit = False
        self.pause = True
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

        pygame.quit()


############### run program #############

if __name__ == '__main__':
    try:
        n = int(sys.argv[1])
    except:
        print("Give the amount of agents as an integer")
    if (n > 3 and n < 7):
        game = ShipModel(n)
        game.run()
        sys.exit()
    else:
        print("Input between 4-6 agents")
