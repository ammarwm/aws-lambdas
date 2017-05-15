import logging
import json
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
        formatted_documents.extend([{"document_name":document_name,\
                             "document_age":document_age}] * no_documents)
    return formatted_documents

def handler(event, context=None):
    """To get the required documents for payslip"""
    try:
        conn = db.connect(**DATABASES['lendi_ai'])
    except db.Error:
        LOGGER.exception("Error in connecting to lendi_ai, %s", db.Error)
    data = event['body']
    lender_name = data['lender_name']
    applicants = data['applicants']
    cur = conn.cursor()
    for app in applicants:
        app.update({"req_documents":None})
        command = SQLQUERIES['select_payslip_requirements'].format(lender_name,\
                                  app['employment_type'])
        cur.execute(command)
        req_documents = cur.fetchall()
        if req_documents:
            req_documents = formatter(req_documents)
            app.update({"req_documents":req_documents})
    cur.close()
    conn.close()
    return data

if __name__ == "__main__":
    #For testing
    req = {"body":{"lender_name":"ANZ",
                   "applicants":[{"name":"John","employment_type":"PAYG"}]}
                   }
    print(handler(req))