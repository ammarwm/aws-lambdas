import logging
import json
try:
    import psycopg2 as db
except ImportError:
    import pg8000 as db
from sql_queries import sql_queries
from config import DATABASES


#Get the LOGGER
LOGGER = logging.getLogger("root")
LOG_HANDLER = logging.StreamHandler()
LOGGER.addHandler(LOG_HANDLER)
LOGGER.setLevel(logging.INFO)


def handler(event, context=None):
    """Lambda function handler to be called by Xtracta"""
    #Connection to the database
    LOGGER.info(event)
    data = {}
    try:
        conn = db.connect(**DATABASES['lendi_ai'])
    except db.Error:
        LOGGER.exception("Error in handler() lendi_db error")
        return {}
    cur = conn.cursor()

    lendi_document_id = event['body']['lendi_document_uuid']

    command = sql_queries['select_document_data'].format(lendi_document_id)
    cur.execute(command)
    result = cur.fetchone()

    if result:
        url, data = result[0], result[1]
    conn.close()
    data = json.dumps(data)
    return data

if __name__ == "__main__":
    event = {"body":{"lendi_document_uuid":"8e7162ff-450c-4073-9dfe-1b2e373a606f"}}
    print(handler(event))
