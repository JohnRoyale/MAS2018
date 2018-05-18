from mesa import Agent

class Person(Agent):
	def __init__(self, i, model):
		super().__init__(i, model, position, target)
		self.alive = True
		self.position = position
		self.target = target
		self.murderer = []
		self.kb = kb


	# actions
	def evaluateKB(self):


	def updateKB(self):



	# move action
	def move(self):
		corridors = model.corridors[position]
		selected = random.int(len(corridors))
		self.position = selected


	# optional action (kill, flee, stay)
	def flee(self):
		self.move()

	def kill(self, target):
		victim = target[0];
		victim.alive = False
		for agent in room:
			target.add(agent)
			agent.murderer.add(self)

	def stay(self):
		pass



	def step(self):
		if(self.alive):
			if(murderer in room):
				self.flee(random connect room)
			elif(target in room):
				self.kill(self.target)
			else:
				self.stay()

			self.evaluateKB()
			self.updateKB()
			