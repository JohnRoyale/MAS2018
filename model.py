from mesa import Model
from mesa.time import RandomActivation
from agent import Person


class ShipModel(Model):
	"""The ship with a number of logical agents"""
	def __init__(self, N):
		self.schedule = RandomActivation(self)
		self.num_agents = N
		self.kripke model = []
		self.rooms = []
		self.corridors = () # dictionary

		for i in range(self.num_agents):
			a = Person(i, self)
			self.schedule.add(a)

		construct_kripke()

	# kripke model functions
	def construct_kripke(self):



	# all agents take a move step
	def move_agents(self):
		for agent in self.schedule.agent:
			agent.move()


	def step(self):
		# agents perform action step
		self.schedule.step()

		# agents perform move step
		self.move_agents()