import logging
import json
import uuid

try:
    import psycopg2 as db
except ImportError:
    import pg8000 as db
from sql_queries import SQLQUERIES
from config import DATABASES, XTRACTA


#Get the LOGGER
LOGGER = logging.getLogger("root")
LOG_HANDLER = logging.StreamHandler()
LOGGER.addHandler(LOG_HANDLER)
LOGGER.setLevel(logging.INFO)

def formatter(documents):
    formatted_documents = []
    for doc in documents:
        _, document_name, document_age, no_documents = doc[0], doc[1], doc[2], int(doc[3])
        for i in range(no_documents):
            formatted_documents.extend([{"uuid":str(uuid.uuid4()), "document_name":document_name,\
                             "document_age":document_age}])
    return formatted_documents

def handler(event, context=None):
    """To get the required documents for payslip"""
    try:
        conn = db.connect(**DATABASES['lendi_ai'])
    except db.Error:
        LOGGER.exception("Error in connecting to lendi_ai, %s", db.Error)
    documents = []
    data = event['body']
    lender_name = data['lender_name']
    applicants = data['applicants']
    cur = conn.cursor()
    for app in applicants:
        command = SQLQUERIES['select_payslip_requirements'].format(lender_name,\
                                  app['employment_type'])
        cur.execute(command)
        req_documents = cur.fetchall()
        if req_documents:
            app_req_documents = formatter(req_documents)
            for doc in app_req_documents:
                doc.update(app)
            documents.extend(app_req_documents)
    cur.close()
    conn.close()
    return documents

if __name__ == "__main__":
    #For testing
    req = {"body":{"lender_name":"AMP","lender_id":"xxxxxx","opportunity_id":"4289ee41-f39c-4acf-9e48-52c29c66838a","applicants":[{"employment_type":"Full Time - PAYG","application_uuid":"4289ee41-f39c-4acf-9e48-52c29c66838a","applicant_uuid":"fc964eac-2e8e-419e-90e5-2677aa1dc2ea"},{"employment_type":"Full Time - PAYG","application_uuid":"4289ee41-f39c-4acf-9e48-52c29c66838a","applicant_uuid":"17b6c521-11b7-493a-9bfb-37d0ad9e425a"}],"uuid":"e69fc567-4d9b-4e05-8157-770add60898c"}}
    print(handler(req))