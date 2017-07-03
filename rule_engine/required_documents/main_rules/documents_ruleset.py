import logging
from durable.lang import *
from rule_engine.required_documents.rules_actions import *

#Get the LOGGER
LOGGER = logging.getLogger("root")

with ruleset('required_documents'):

    @when_all(+m.lender_name &
              +m.employment_type &
              +m.loan_type &
              +m.application_uuid &
              +m.applicant_uuid)
    def insert_required_documents(c):
        inserter = InsertReqDocuments()
        inserter.do({'employment_type': c.m.employment_type,
                    'lender_name': c.m.lender_name,
                    'loan_type': c.m.loan_type,
                    'application_uuid': c.m.application_uuid,
                    'applicant_uuid': c.m.applicant_uuid})

        ruleinserter = InsertDocRules()
        ruleinserter.do({'employment_type': c.m.employment_type,
                    'lender_name': c.m.lender_name,
                    'loan_type': c.m.loan_type,
                    'application_uuid': c.m.application_uuid,
                    'applicant_uuid': c.m.applicant_uuid,
                    'type': "loan_document"})











