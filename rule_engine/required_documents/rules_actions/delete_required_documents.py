import json
import uuid
from connectors.database import Database
from sql_queries import SQLQUERIES
from base_action import BaseAction


class DelReqDocuments(BaseAction):
    def __init__(self):
        pass

    def do(self, kwarg):

        db = Database('lendi_ai')
        db.connect()
        command = SQLQUERIES['delete_application_required_documents'].format(kwarg['application_uuid'],
                             kwarg['applicant_uuid'])
        db.execute(command)
        db.close()


if __name__ == "__main__":

    insert = DelReqDocuments()
    insert.do({"application_uuid":"xxxx", "applicant_uuid":"xxx"})
    print(insert.result)