import json
import uuid
from connectors.database import Database
from sql_queries import SQLQUERIES
from base_action import BaseAction


class InsertDocRules(BaseAction):
    def __init__(self):
        pass

    def do(self, kwarg):

        db = Database(self.db_info)
        db.connect()
        command = SQLQUERIES['delete_application_rules'].format(
                                  kwarg['application_uuid'], kwarg['applicant_uuid'])
        db.execute(command, 'w')

        db.close()

if __name__ == "__main__":

    insert = InsertDocRules()
    insert.do({"lender_name":"AMP",
               "employment_type":"PAYG",
               "loan_type":"Refinance",
               "application_uuid":"xxxx",
               "applicant_uuid":"xxx",
               "type":"required_documents"})
    #print(insert.result)