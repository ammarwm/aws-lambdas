import json
import uuid
from connectors.database import Database
from sql_queries import SQLQUERIES
from base_action import BaseAction


class InsertDocRules(BaseAction):
    def __init__(self):
        super(InsertDocRules, self).__init__(object.__class__.__name__)

    def do(self, kwarg):

        db = Database(self.db_info)
        db.connect()
        command = SQLQUERIES['select_lender_rule'].format(kwarg['lender_name'],
                            kwarg['loan_type'], kwarg['employment_type'], kwarg['type'])
        db.execute(command)
        self.result = db.get_result('all')

        for row in self.result:
            command = SQLQUERIES['insert_application_reqdoc_rule'].format(
                                  kwarg['application_uuid'], kwarg['applicant_uuid'], row['rule'])
            db.execute(command, 'w')

        db.close()

if __name__ == "__main__":

    insert = InsertDocRules()
    insert.do({"lender_name":"default",
               "employment_type":"PAYG",
               "loan_type":"refinance",
               "application_uuid":"xxxx",
               "applicant_uuid":"xxx",
               "type":"loan_document"})
    #print(insert.result)
