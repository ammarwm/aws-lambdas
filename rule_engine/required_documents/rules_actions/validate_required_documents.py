import json
from connectors.database import Database
from sql_queries import SQLQUERIES
from base_action import BaseAction


class ValidateReqDocuments(BaseAction):
    def __init__(self):
        pass

    def do(self, kwarg):
        db = Database('lendi_ai')
        db.connect()
        command = SQLQUERIES['application_rules'].format(kwarg['application_uuid'], kwarg['applicant_uuid'])
        db.execute(command)
        rule = db.get_result('all')
        command = SQLQUERIES['select_uploaded_documents'].format(kwarg['application_uuid'], kwarg['applicant_uuid'])
        db.execute(command)
        result = db.get_result('all')
        evaluation_result = self.evaluate_rule(result, rule)
        db.close()

    def evaluate_rule(self, docs, rule):
        rule = rule[0]['rule']
        rule_ = rule.replace('or', '').\
                    replace('and', '').\
                    replace('(', '').\
                    replace(')', '').split()
        for re in rule_:
            exec(re + "= 0")

        for re in docs:
            exec(re['name'] + "= 1")
        result = eval(rule)
        
        return result

if __name__ == "__main__":

    validator = ValidateReqDocuments()
    validator.do({
               "application_uuid":"fa731f80-e882-430d-9e2e-fb1c5b485aeb",
               "applicant_uuid":"9ac41a7e-045b-4ca0-9bed-408009cc63f5"})
