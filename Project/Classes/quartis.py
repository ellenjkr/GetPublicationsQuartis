import json
import os
import requests

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError


class Quartis():
	def __init__(self, researcher_quartis, api_key):
		super(Quartis, self).__init__()
		self.researcher_quartis = researcher_quartis
		self.api_key = api_key
		
	def search_percentil(self, issn):
		if issn != None:
			issn = issn.replace("-", "")
			issn = issn.replace(".0", "")
		percentil = None
		log = ''
		link_scopus = ''
		try:
			insttoken = os.environ.get('INSTTOKEN')  # The insttoken is being hold as an environment variable
			headers = {'X-ELS-Insttoken': insttoken, 'X-ELS-APIKey': self.api_key}
			uri = "https://api.elsevier.com/content/serial/title?issn=" + issn + "&view=citescore"
			response = requests.get(uri, headers=headers)
			json_data = json.loads(response.text)

			link_scopus = json_data['serial-metadata-response']['entry'][0]['link'][0]['@href']
			try:
				percentil = json_data['serial-metadata-response']['entry'][0]['citeScoreYearInfoList']['citeScoreYearInfo'][1]['citeScoreInformationList'][0]['citeScoreInfo'][0]['citeScoreSubjectRank'][0]['percentile']
			except Exception as err:
				log = f'sem valor de percentil {err}'
				print(log)

		except HTTPError as http_err:
			log += 'HTTP error occurred: ' + str(http_err) + ' - Status_code: ' + str(response.status_code)
			print(log)
		except Exception as err:
			log += 'Other error occurred: ' + str(err) + ' - Status_code: ' + str(response.status_code)
			print(log)

		if percentil == '':
			percentil = None

		return percentil, link_scopus, str(log)

	def get_journal_str(self, main_journal):
		journal_array = main_journal.split(" ")

		journal_string = ""
		for i in range(len(journal_array) - 1):
			journal_string += journal_array[i] + "+"
		journal_string += journal_array[-1]

		return journal_string

	def get_publication_page(self, journal_str, main_journal):
		r1 = requests.get(f"https://www.scimagojr.com/journalsearch.php?q={journal_str}")

		soup = BeautifulSoup(r1.text, 'lxml')
		soup = soup.find('div', class_='search_results')

		uri = None
		for link in soup.find_all('a'):
			journal_name = link.find_all(class_="jrnlname")
			for journal in journal_name:
				if journal.contents[0].lower() == main_journal.lower():
					uri = link.get('href')
		return uri

	def search_issn(self, uri):
		issn = "-"
		if uri != None:
			r2 = requests.get(f"https://www.scimagojr.com/{uri}")

			soup = BeautifulSoup(r2.text, 'lxml')
			soup = soup.find("div", class_="journaldescription colblock")

			table_items = soup.find_all("tr")
			
			for i in table_items:
				if str(i.contents[0]) == "<td>ISSN</td>":
					i.find_all("td")
					issn = i.contents[1].contents[0]

		return issn

	def get_issn(self, journal_name):
		journal_str = self.get_journal_str(journal_name)
		uri = self.get_publication_page(journal_str, journal_name)
		return self.search_issn(uri)

	def set_per_quarti(self, relatorio, value):
		per, link, log = self.search_percentil(issn=str(value))
		
		if per == None:
			print(value, " não foi possível")
			relatorio["Percentile"].append("-")
			relatorio["Quartile"].append("-")
		else:
			relatorio["Percentile"].append(per)
			if int(per) >= 75:
				quarti = "Q1"
			elif int(per) >= 50:
				quarti = "Q2"
			elif int(per) >= 25:
				quarti = "Q3"
			else:
				quarti = "Q4"

			relatorio["Quartile"].append(quarti)

		return relatorio

	def get_quartis(self):
		relatorio = {'Ano': [], 'Titulo': [], 'Nome de Publicação': [], 'ISSN': [], 'Percentile': [], 'Quartile': []}

		for pos, value in enumerate(self.researcher_quartis["issn"]):
			if value == "-":
				relatorio["Titulo"].append(self.researcher_quartis["title"][pos])
				relatorio["Nome de Publicação"].append(self.researcher_quartis["publication_name"][pos])

				issn = self.get_issn(self.researcher_quartis["publication_name"][pos])
				relatorio["ISSN"].append(issn)

				if issn != "-":
					relatorio = self.set_per_quarti(relatorio, issn)
					relatorio["Ano"].append(self.researcher_quartis["year"][pos])
				else:
					relatorio["Percentile"].append("-")
					relatorio["Quartile"].append("-")
					relatorio["Ano"].append(self.researcher_quartis["year"][pos])
			else:
				relatorio["Titulo"].append(self.researcher_quartis["title"][pos])
				relatorio["Nome de Publicação"].append(self.researcher_quartis["publication_name"][pos])
				relatorio["ISSN"].append(value)

				relatorio = self.set_per_quarti(relatorio, value)

				relatorio["Ano"].append(self.researcher_quartis["year"][pos])

		for pos, issn in enumerate(relatorio["ISSN"]):
			for pos2, issn2 in enumerate(relatorio["ISSN"]):
				if relatorio["Nome de Publicação"][pos] == relatorio["Nome de Publicação"][pos2]:
					if issn == '-' and issn2 != '-':
						relatorio["ISSN"][pos] = issn2
						relatorio["Percentile"][pos] = relatorio["Percentile"][pos2]
						relatorio["Quartile"][pos] = relatorio["Quartile"][pos2]

		return relatorio