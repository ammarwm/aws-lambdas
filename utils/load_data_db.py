import pandas as pd
from connectors.database import Database

def copy(columns, table1, table2):

    db = Database('lendi_ai')
    command = "SELECT {} FROM {}".format({columns},{table1})
    db.execute(command)
    results = db.get_result('all')

def copy_from_csv_to_table(columns, path, table):

    data = pd.read_csv(path, delimiter=',')
    db = Database('lendi_ai')

    for i,d in data.iterrows():
        import pdb;pdb.set_trace()
        command = """INSERT INTO {} ({}) VALUES ({});""".format(table, columns, d)

if __name__ == "__main__":


    copy_from_csv_to_table("[sfid,name]", "/Users/localuser/document_master__c.txt", 'required_documents.document_master')


