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

	#move action
	def move(self):


	#optional action (kill, flee, stay)
	def flee(self):


	def kill(self):


	def stay(self):
		pass


	def step(self):
		if(self.alive):
			if(murderer in room):
				flee(random connect room)
			elif(target in room):
				kill([target])
			else:
				stay()

			evaluateKB()
			updateKB()
			move()