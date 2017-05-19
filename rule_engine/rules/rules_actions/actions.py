import json
from connectors.database import Database
from sql_queries import SQLQUERIES


class Actions:
    def __init__(self):
        pass

    @staticmethod
    def write_results(uuid, result={}):
        lendiai_db = Database('lendi_ai')
        lendiai_db.connect()
        lendiai_db.execute(SQLQUERIES["update_validation_result"].format(json.dumps(result), uuid))
        lendiai_db.close()

if __name__ == '__main__':
    db = Database()
    db.connect()
    db.execute('select "document_master_id" from required_documents.payslip_master limit 10')
    results = db.get_result('all')
    print results
    db.close()