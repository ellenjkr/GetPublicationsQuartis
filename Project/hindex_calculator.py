from PyscopusModified import ScopusModified
import pandas as pd


class Researcher():  # Researcher class that holds its data
	def __init__(self, name, researcher_id, search=None, quartis=None, period=None):
		super(Researcher, self).__init__()
		self.name = name
		self.id = researcher_id

		self.search = search
		self.quartis = quartis
		self.period = period


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

	def save_quartis(self):
		for researcher in self.researchers:
			researcher.quartis.to_csv(f"Quartis/{researcher.name}.csv", sep=';', index=False, encoding='utf-8')


class ScopusRetriever():
	def __init__(self, data, key):  # Parameters are the data and the scopus api key
		super(ScopusRetriever, self).__init__()
		self.data = data
		self.key = key
		self.scopusModified = ScopusModified(self.key)  # Instance of a modified Scopus class

		self.researchers = []  # List of researchers

	def retrieve_data(self):
		for researcher in self.data.researchers: 
			if researcher.id != '-':
				search = self.scopusModified.search(f"AU-ID ({researcher.id})")  # Searches for an author by its ID

				quartis = self.get_quartis_documents(search, researcher)  # Get the documents info that its needed to calculate the quartis
				self.researchers.append(Researcher(researcher.name, researcher.id, search, quartis))  # Add a new researcher to the list of researchers

		return self.researchers

	def get_quartis_documents(self, search, researcher):
		info = search.to_dict()
		data = {'year': [], 'title': [], 'publication_name': [], 'issn': []}
		for pos, title in enumerate(info["title"]):
			date = info["cover_date"][pos].split('-')
			date = date[0]

			if date == "2020" or date == "2019" or date == "2018" or date == "2017":
				if date == "2017" and researcher.period["17"] is False:
					continue
				elif date == "2018" and researcher.period["18"] is False:
					continue
				elif date == "2019" and researcher.period["19"] is False:
					continue
				elif date == "2020" and researcher.period["20"] is False:
					continue
				else:
					if info["aggregation_type"][pos] == "Journal" or info["aggregation_type"][pos] == "Conference Proceeding":
						data['title'].append(info["title"][pos])
						data['publication_name'].append(info["publication_name"][pos])
						if info["issn"][pos] == None:
							data['issn'].append('-')
						else:
							data['issn'].append(info["issn"][pos])
						data['year'].append(date)

		return pd.DataFrame(data)


if __name__ == '__main__':
	data = Data('entrada.csv')  # Reads the data from the file
	scopus_retriever = ScopusRetriever(data, '2f8a856ea2c32c265b4c5a9895e6900d')  # Responsible for retrieving information from scopus using the data
	data.add_data(scopus_retriever.retrieve_data())  # Add the new info retrieved from scopus to the previous data
	data.save_quartis()
