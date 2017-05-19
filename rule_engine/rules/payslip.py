import logging
from durable.lang import *
from rules_actions.actions import Actions

#Get the LOGGER
LOGGER = logging.getLogger("root")

def do(uuid='', rule_type='document_age', rule_result='Invalid', msge=''):
    result = {
        'uuid': uuid,
        'type': rule_type,
        'result': rule_result,
        'message': msge
    }
    Actions.write_results(uuid, result)

with statechart('payslip'):
    with state('input'):
        @to('valid')
        @when_all(c.fact1 << (m.required_document_age != None) & (m.sid != None),
                  c.fact2 << m.document_age <= c.fact1.required_document_age)
        def valid(c):
            do(uuid=c.fact1.sid, rule_result='valid')
            c.delete()

        @to('invalid')
        @when_all(c.fact1 << (m.required_document_age != None) & (m.sid != None),
                  c.fact2 << m.document_age > c.fact1.required_document_age)
        def invalid(c):
            message = 'Invalid payslip due to payslip age {} larger than {}'.\
                             format(c.fact2.document_age, c.fact1.required_document_age)
            do(uuid=c.fact1.sid, rule_result='invalid', msge=message)
            c.delete()

    state('valid')
    state('invalid')


