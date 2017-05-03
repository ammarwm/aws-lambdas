import logging
import json
from datetime import datetime
import xmltodict
from urllib import unquote_plus
import requests
try:
    import psycopg2 as db
except ImportError:
    import pg8000 as db
from sql_queries import SQLQUERIES
from config import DATABASES, XTRACTA, XTRACTA_URL_TIMEOUT


#Get the LOGGER
LOGGER = logging.getLogger("root")
LOG_HANDLER = logging.StreamHandler()
LOGGER.addHandler(LOG_HANDLER)
LOGGER.setLevel(logging.INFO)


def handler(event, context=None):
    """Lambda function to return xtracta document url from database or direct from xtracta"""
    #Connection to the database
    LOGGER.info(event)
    data = {'status':'400', 'message':'No such document', 'xtracta_ui':''}
    try:
        conn = db.connect(**DATABASES['lendi_ai'])
    except db.Error:
        LOGGER.exception("Error in handler() lendi_db error")
        return data.update({'message':'Could not establish connection to lendi-ai db'})
    cur = conn.cursor()

    lendi_document_id = event['body']['lendi_document_uuid']

    command = SQLQUERIES['select_xtracta_document'].format(lendi_document_id)
    cur.execute(command)
    result = cur.fetchone()
    if result:
        xtracta_document_id, ui_url, timestamp = result[0], result[1], result[2]
        if ui_url and (datetime.now() - timestamp).total_seconds() < XTRACTA_URL_TIMEOUT:
            data.update({'status':200, 'message':'URL from database', 'xtracta_ui':ui_url})
        else:
            ui_url = get_ui_from_xtracta(xtracta_document_id)
            if ui_url['status'] == '200':
                command = SQLQUERIES['update_document_url'].format(ui_url['url'],\
                                     xtracta_document_id)
                try:
                    cur.execute(command)
                    conn.commit()
                except db.Error:
                    LOGGER.exception("Error in db %s", command)
                data.update({'status':ui_url['status'], 'message':ui_url['message'],\
                         'xtracta_ui':ui_url['url']})
            else:
                data.update({'status':ui_url['status'], 'message':ui_url['message'],\
                         'xtracta_ui':""})

    conn.close()
    data = json.dumps(data)
    return data


def get_ui_from_xtracta(document_id):
    """To get document UI from xtracta"""
    response = requests.post(XTRACTA['url']+"documents/"+"ui",\
        data={"submit":"Submit", "api_key":XTRACTA['key'],\
         "document_id":document_id, "expire":XTRACTA_URL_TIMEOUT})
    response_content = xmltodict.parse(response.content)

    return response_content['documents_response']

if __name__ == "__main__":
    event = {"body":{"lendi_document_uuid":"ac2a448e-dcc4-422e-a430-bbf22a58e6e5"}}
    print(handler(event))
