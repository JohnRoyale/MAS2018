from mesa import Model


class ShipModel(Model):
	"""The ship with a number of logical agents"""
	def __init__(self, N):
		self.num_agents = N
		self.kripke model = []
		self.rooms = []
		self.corridors = () # dictionary

		for i in range(self.num_agents):
			a = Person(i, self)
			self.schedule.add(a)

		construct_kripke()

	# functions
	def construct_kripke(self):


	def step(self):
		