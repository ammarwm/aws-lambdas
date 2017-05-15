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
            print(command)
        conn.commit()
        _update_salesforce_line_items(lendi_document_id, sfid, xtracta_result, conn)
    else:
        LOGGER.error('Error in update_salesforce(), no sfid for %s', lendi_document_id)

    conn.close()
    return {"message":"Done"}

if __name__ == "__main__":
    #For testing
    xtracta = {u'xtracta_result': {u'number_of_pages': u'1', u'classification': u'full', u'document_status': u'indexing', u'free_form': None, u'api_download_status': u'active', u'workflow_id': u'50713', u'image_url': u'https://web1-akl.xtracta.com/datasource/1/b6/47/03KAZiMb2JEs-1-0800.jpg', u'@revision': u'2', u'field_data': {u'field': [{u'field_value_location': {u'word': [{u'width': u'1.41%', u'top': u'10.89%', u'height': u'0.71%', u'page_number': u'1', u'left': u'37.06%'}, {u'width': u'1.9%', u'top': u'10.89%', u'height': u'0.71%', u'page_number': u'1', u'left': u'39.03%'}, {u'width': u'2.18%', u'top': u'10.89%', u'height': u'0.71%', u'page_number': u'1', u'left': u'41.53%'}, {u'width': u'2.14%', u'top': u'10.89%', u'height': u'0.71%', u'page_number': u'1', u'left': u'44.19%'}]}, u'field_name': u'ABN', u'field_id': u'2191421', u'field_value': u'43 101 490 000'}, {u'field_value_location': {u'word': [{u'width': u'5.93%', u'top': u'5.36%', u'height': u'1.4%', u'page_number': u'1', u'left': u'3.95%'}, {u'width': u'5.36%', u'top': u'5.33%', u'height': u'1.42%', u'page_number': u'1', u'left': u'10.93%'}, {u'width': u'1.85%', u'top': u'5.33%', u'height': u'1.45%', u'page_number': u'1', u'left': u'17.3%'}, {u'width': u'4.6%', u'top': u'5.36%', u'height': u'1.4%', u'page_number': u'1', u'left': u'20.08%'}, {u'width': u'10.85%', u'top': u'5.33%', u'height': u'1.42%', u'page_number': u'1', u'left': u'25.69%'}, {u'width': u'3.95%', u'top': u'5.36%', u'height': u'1.77%', u'page_number': u'1', u'left': u'37.58%'}, {u'width': u'3.83%', u'top': u'5.36%', u'height': u'1.4%', u'page_number': u'1', u'left': u'42.54%'}]}, u'field_name': u'Employer Name', u'field_id': u'2202699', u'field_value': u'Multi Civil & Rail Services Pty Ltd'}, {u'field_value_location': {u'word': {u'width': u'10.36%', u'top': u'13.25%', u'height': u'0.83%', u'page_number': u'1', u'left': u'73.95%'}}, u'field_name': u'Payment Date', u'field_id': u'2213696', u'field_value': u'8/02/2017'}, {u'field_value_location': None, u'field_name': u'Employment Status', u'field_id': u'2202713', u'field_value': None}, {u'field_value_location': {u'word': [{u'width': u'3.35%', u'top': u'18.12%', u'height': u'0.8%', u'page_number': u'1', u'left': u'14.96%'}, {u'width': u'4.23%', u'top': u'18.1%', u'height': u'0.83%', u'page_number': u'1', u'left': u'18.87%'}]}, u'field_name': u'Employee Name', u'field_id': u'2213698', u'field_value': u'Brian CARR'}, {u'field_value_location': {u'word': [{u'width': u'3.06%', u'top': u'21.09%', u'height': u'0.83%', u'page_number': u'1', u'left': u'14.64%'}, {u'width': u'5.48%', u'top': u'21.12%', u'height': u'1%', u'page_number': u'1', u'left': u'18.15%'}, {u'width': u'4.44%', u'top': u'21.09%', u'height': u'0.83%', u'page_number': u'1', u'left': u'24.15%'}]}, u'field_name': u'Job Title', u'field_id': u'7349460', u'field_value': u'Safe Working Officer'}, {u'field_value_location': {u'word': [{u'width': u'7.5%', u'top': u'23.85%', u'height': u'0.83%', u'page_number': u'1', u'left': u'17.54%'}, {u'width': u'2.1%', u'top': u'23.88%', u'height': u'0.8%', u'page_number': u'1', u'left': u'36.98%'}, {u'width': u'6.65%', u'top': u'23.77%', u'height': u'0.83%', u'page_number': u'1', u'left': u'40.6%'}, {u'width': u'5.32%', u'top': u'24.05%', u'height': u'0.83%', u'page_number': u'1', u'left': u'69.4%'}, {u'width': u'3.27%', u'top': u'24.08%', u'height': u'0.77%', u'page_number': u'1', u'left': u'75.28%'}, {u'width': u'6.65%', u'top': u'24%', u'height': u'1.03%', u'page_number': u'1', u'left': u'79.44%'}]}, u'field_name': u'Pament Period Begin Date', u'field_id': u'2202714', u'field_value': u'30/01/2017 To: 5/02/2017 GROSS PAY: $3,675.60'}, {u'field_value_location': {u'word': {u'width': u'6.65%', u'top': u'23.77%', u'height': u'0.83%', u'page_number': u'1', u'left': u'40.6%'}}, u'field_name': u'Payment Period End Date', u'field_id': u'2202715', u'field_value': u'5/02/2017'}, {u'field_value_location': None, u'field_name': u'Annual Income', u'field_id': u'8495671', u'field_value': None}, {u'field_value_location': {u'word': {u'width': u'6.65%', u'top': u'24%', u'height': u'1.03%', u'page_number': u'1', u'left': u'79.44%'}}, u'field_name': u'Gross Income', u'field_id': u'7340312', u'field_value': u'$3,675.60'}, {u'field_value_location': {u'word': {u'width': u'6.65%', u'top': u'26.67%', u'height': u'1.03%', u'page_number': u'1', u'left': u'79.44%'}}, u'field_name': u'Net Income', u'field_id': u'7340313', u'field_value': u'$2,457.00'}, {u'field_value_location': {u'word': [{u'width': u'5.4%', u'top': u'38.3%', u'height': u'0.97%', u'page_number': u'1', u'left': u'54.23%'}, {u'width': u'6.65%', u'top': u'38.3%', u'height': u'1.03%', u'page_number': u'1', u'left': u'68.31%'}, {u'width': u'10.56%', u'top': u'38.36%', u'height': u'1.03%', u'page_number': u'1', u'left': u'77.06%'}, {u'width': u'6.53%', u'top': u'38.39%', u'height': u'1%', u'page_number': u'1', u'left': u'88.19%'}]}, u'field_name': u'Superannuation', u'field_id': u'7349845', u'field_value': u'$169.67 $1,393.09 Superannuation Expenses'}, {u'field_value_location': {u'word': {u'width': u'7.14%', u'top': u'37.08%', u'height': u'1.03%', u'page_number': u'1', u'left': u'52.5%'}}, u'field_name': u'Paid Tax', u'field_id': u'8495672', u'field_value': u'-$1,218.60'}, {u'field_value_location': None, u'field_name': u'Bank Amount', u'field_id': u'7350614', u'field_value': None}], u'field_set': {u'row': [{u'field': [{u'field_name': u'Description', u'field_id': u'7340700', u'field_value': u'CSS (A)'}, {u'field_name': u'Rate', u'field_id': u'7340701', u'field_value': u'$47.00'}, {u'field_name': u'Unit', u'field_id': u'7340702', u'field_value': u'18'}, {u'field_name': u'Amount', u'field_id': u'7340703', u'field_value': u'$846.00'}]}, {u'field': [{u'field_name': u'Description', u'field_id': u'7340700', u'field_value': u'CSS (B)'}, {u'field_name': u'Rate', u'field_id': u'7340701', u'field_value': u'$78.60'}, {u'field_name': u'Unit', u'field_id': u'7340702', u'field_value': u'36'}, {u'field_name': u'Amount', u'field_id': u'7340703', u'field_value': u'$2,829.60'}]}], u'field_set_id': u'1176480', u'field_set_name': u'Payments/Deductions'}}, u'document_id': u'22554202', u'document_url': u'https://web1-akl.xtracta.com/datasource/1/b0/f5/03KAZiMb2JEs.pdf'}, u'lendi_document_id': u'94d1100a-25ae-49fb-97c5-347a62826347'}
    handler(xtracta)