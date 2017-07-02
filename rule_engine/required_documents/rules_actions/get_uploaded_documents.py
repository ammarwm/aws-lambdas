import json
from connectors.database import Database
from sql_queries import SQLQUERIES
from base_action import BaseAction


class GetUploadedDocuments(BaseAction):
    def __init__(self):
        pass

    def do(self, opportunity_uuid):

        db = Database(self.db_info)
        db.connect()
        command = SQLQUERIES['select_uploaded_documents'].format(opportunity_uuid)
        db.execute(command)
        self.result = db.get_result('all')
        db.close()



