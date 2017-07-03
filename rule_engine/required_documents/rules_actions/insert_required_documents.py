import json
import uuid
from connectors.database import Database
from sql_queries import SQLQUERIES
from base_action import BaseAction


class InsertReqDocuments(BaseAction):
    def __init__(self):
        super(InsertReqDocuments, self).__init__(object.__class__.__name__)

    def do(self, kwarg):

        db = Database(self.db_info)
        db.connect()
        command = SQLQUERIES['select_required_documents'].format(kwarg['lender_name'],
                            kwarg['employment_type'], kwarg['loan_type'])
        db.execute(command)
        self.result = db.get_result('all')

        data = [(kwarg['application_uuid'],
                 kwarg['applicant_uuid'], r['uuid'],
                 json.dumps(r['conditions']),
                 json.dumps(r['constraints'])) for r in self.result]
        command = SQLQUERIES['insert_required_documents']
        db.executemany(command, data)

        db.close()


if __name__ == "__main__":

    insert = InsertReqDocuments()
    insert.do({"lender_name":"AMP",
               "employment_type":"PAYG",
               "loan_type":"Refinance",
               "application_uuid":"xxxx",
               "applicant_uuid":"xxx",
               "document_master_uuid":"zzzz",
               "uuid":"fffff"})
    print(insert.result)
