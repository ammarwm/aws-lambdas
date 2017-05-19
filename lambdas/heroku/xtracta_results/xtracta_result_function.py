import logging
import requests
import json
import xmltodict
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


def _update_salesforce_line_items(lendi_document_id, sfid, result, conn):

    #Update line items in salesforce
    field_set_id = result['field_data']['field_set']['field_set_id']
    cur = conn.cursor()
    #Delete existing line items first
    command = SQLQUERIES['delete_xtracta_result_line_items_in_sf'].format(lendi_document_id)
    cur.execute(command)
    #Insert new ones
    ###work around a bug in xtracta#####
    if isinstance(result['field_data']['field_set']['row'], dict):
        result['field_data']['field_set']['row'] = [result['field_data']['field_set']['row']]
    for i, row in enumerate(result['field_data']['field_set']['row']):
        for field in row['field']:
            command = SQLQUERIES['insert_xtracta_result_line_item_in_sf'].format(lendi_document_id,\
                                sfid, field['field_name'], field['field_value'], i+1, field_set_id)
            cur.execute(command)
    conn.commit()
    return

def handler(event, context=None):
    """Update salesforce with the results"""
    lendi_document_id = event.get('lendi_document_id')
    xtracta_result = event.get('xtracta_result')
    if not lendi_document_id or not xtracta_result:
        return {"message":"document id or result is none"}
    try:
        conn = db.connect(**DATABASES['salesforce'])
    except db.Error:
        LOGGER.exception("Error in update_salesforce(), %s", db.Error)
    cur = conn.cursor()
    command = SQLQUERIES['select_sfid_for_lendi_document_id'].format(lendi_document_id)
    cur.execute(command)
    sfid = cur.fetchone()
    if sfid:
        sfid = sfid[0]
        #Delete existing header items first
        command = SQLQUERIES['delete_xtracta_result_in_sf'].format(lendi_document_id)
        cur.execute(command)
        for field in xtracta_result['field_data']['field']:
            command = SQLQUERIES['insert_xtracta_result_in_sf'].format(lendi_document_id,\
                    sfid, field['field_name'], field['field_value'], field['field_id'],)
            cur.execute(command)
        conn.commit()
        _update_salesforce_line_items(lendi_document_id, sfid, xtracta_result, conn)
    else:
        LOGGER.error('Error in update_salesforce(), no sfid for %s', lendi_document_id)

    conn.close()
    return {"message":"Done"}

if __name__ == "__main__":
    #For testing
    xtracta = {u'xtracta_result': {u'number_of_pages': u'1', u'classification': u'full', u'document_status': u'indexing', u'free_form': None, u'api_download_status': u'active', u'workflow_id': u'50713', u'image_url': u'https://web1-akl.xtracta.com/datasource/1/0f/96/AxnmHCGRup-1-0800.jpg', u'@revision': u'2', u'field_data': {u'field': [{u'field_value_location': None, u'field_name': u'ABN', u'field_id': u'2191421', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Employer Name', u'field_id': u'2202699', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Payment Date', u'field_id': u'2213696', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Employment Status', u'field_id': u'2202713', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Employee Name', u'field_id': u'2213698', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Job Title', u'field_id': u'7349460', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Pament Period Begin Date', u'field_id': u'2202714', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Payment Period End Date', u'field_id': u'2202715', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Annual Income', u'field_id': u'8495671', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Gross Income', u'field_id': u'7340312', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Net Income', u'field_id': u'7340313', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Superannuation', u'field_id': u'7349845', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Paid Tax', u'field_id': u'8495672', u'field_value': None}, {u'field_value_location': None, u'field_name': u'Bank Amount', u'field_id': u'7350614', u'field_value': None}], u'field_set': {u'row': {u'field': [{u'field_name': u'Description', u'field_id': u'7340700', u'field_value': u'Normal'}, {u'field_name': u'Rate', u'field_id': u'7340701', u'field_value': None}, {u'field_name': u'Unit', u'field_id': u'7340702', u'field_value': u'22.00'}, {u'field_name': u'Amount', u'field_id': u'7340703', u'field_value': u'440.00'}, {u'field_name': u'YTD Amount', u'field_id': u'9961539', u'field_value': None}]}, u'field_set_id': u'1176480', u'field_set_name': u'Payments/Deductions'}}, u'document_id': u'23134394', u'document_url': u'https://web1-akl.xtracta.com/datasource/1/c7/cf/AxnmHCGRup.pdf'}, u'lendi_document_id': u'8aa22416-a330-494e-b8be-120a3a055afd'}
    #xtracta =
    handler(xtracta)