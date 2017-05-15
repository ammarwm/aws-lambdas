from durable.lang import *

with ruleset('payslip'):
    @when_all(m.req_document_age > 0)
    def init(c):
        c.s.req_document_age_ = c.m.req_document_age
        print("Required document age",c.s.req_document_age_)

    @when_all(m.doc_age < c.s.req_document_age_)
    def valid(c):
        print("Valid", c.m.doc_age)

    @when_all(m.doc_age > c.s.req_document_age_)
    def invalid(c):
        print("Invalid due to document age", c.m.doc_age)

    @when_start
    def start(host):
        host.assert_fact("payslip", {"sid":1, "req_document_age":30})
        host.post("payslip", {"sid": 1, "doc_age": 200})

run_all([{'host': 'lendi-redis.ny2tmo.0001.apse2.cache.amazonaws.com', 'port': 6379}])