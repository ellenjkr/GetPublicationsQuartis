import pandas as pd

from Classes.researcher import Researcher


class Data():
	def __init__(self, file_name):
		super(Data, self).__init__()
		self.file_name = file_name
		self.parse_data()

	def parse_data(self):
		data = pd.read_csv(self.file_name, sep=';', encoding='iso-8859-1')  # Reads the csv file

		self.researchers = []  # A list of researchers

		for pos, researcher_id in enumerate(data["SCOPUS ID"]):  # Goes through the data and gets the id's from the researchers
			name = data['Nome'][pos]  # Gets the name
			if str(name) == 'nan':
				name = '-'

			if str(researcher_id) == 'nan' or str(researcher_id) == 'NaN':  # If the id is null
				researcher_id = '-'
			
			if name != '-' and researcher_id != '-':
				period = {}
				if str(data["17"][pos]) != "nan" and str(data["17"][pos]) != "NaN":
					period["17"] = True
				else:
					period["17"] = False
				if str(data["18"][pos]) != "nan" and str(data["18"][pos]) != "NaN":
					period["18"] = True
				else:
					period["18"] = False
				if str(data["19"][pos]) != "nan" and str(data["19"][pos]) != "NaN":
					period["19"] = True
				else:
					period["19"] = False
				if str(data["20"][pos]) != "nan" and str(data["20"][pos]) != "NaN":
					period["20"] = True
				else:
					period["20"] = False
	
				self.researchers.append(Researcher(name=name, researcher_id=int(researcher_id), period=period))  # Adds a new researcher with its name and id
	
	def add_data(self, researchers_updated):  # Adds new data (documents, citations and hindex) to each researcher. The parameter is a list of researchers
		for researcher_updated in researchers_updated:
			for researcher in self.researchers:
				if researcher.id == researcher_updated.id and researcher.id != "-":  # The compatible researcher
					researcher.search = researcher_updated.search
					researcher.quartis = researcher_updated.quartis
