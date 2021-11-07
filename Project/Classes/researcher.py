class Researcher():  # Researcher class that holds their data
	def __init__(self, name, researcher_id, search=None, quartis=None, period=None):
		super(Researcher, self).__init__()
		self.name = name
		self.id = researcher_id

		self.search = search
		self.quartis = quartis
		self.period = period