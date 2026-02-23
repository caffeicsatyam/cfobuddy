from langchain_community.document_loaders.csv_loader import CSVLoader
loader = CSVLoader(file_path="data\FinancialStatements.csv")

documents = loader.load()

# For large datasets, lazily load documents
for document in loader.lazy_load():
    print(document)