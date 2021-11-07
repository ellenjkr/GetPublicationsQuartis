import pandas as pd

from Classes.PyscopusModified import ScopusModified
from Classes.researcher import Researcher


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