import pandas as pd

from Classes.data import Data
from Classes.excel import ExcelFile
from Classes.quartis import Quartis
from Classes.scopus_retriever import ScopusRetriever


if __name__ == '__main__':
	data = Data('entrada2.csv')  # Reads the csv entry file
	scopus_retriever = ScopusRetriever(data, '2f8a856ea2c32c265b4c5a9895e6900d')  # Responsible for retrieving information from scopus using the data
	data.add_data(scopus_retriever.retrieve_data())  # Add the new info retrieved from scopus to the previous data

	relatorios = {'Autor': [], 'Relatorio': []}

	for researcher in data.researchers:
		quartis = Quartis(researcher.quartis, '2f8a856ea2c32c265b4c5a9895e6900d')
		relatorio = quartis.get_quartis()
		relatorios['Relatorio'].append(pd.DataFrame(relatorio))
		relatorios['Autor'].append(researcher.name)

	excel = ExcelFile(relatorios)
	excel.salva_arquivo()
