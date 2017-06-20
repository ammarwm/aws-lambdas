import logging
from durable.lang import *
from rule_engine.required_documents.rules_actions import *

#Get the LOGGER
LOGGER = logging.getLogger("root")

with ruleset('validate_required_documents'):

    @when_all(+m.application_uuid &
              +m.applicant_uuid)
    def validate_required_documents(c):
        validator = ValidateReqDocuments()
        validator.do({'application_uuid': c.m.application_uuid,
                      'applicant_uuid': c.m.applicant_uuid})

