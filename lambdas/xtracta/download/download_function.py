import logging
import requests
import json
import xmltodict
try:
    #raise ImportError('I know Python!')
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


def handler(event, context=None):
    """Lambda function handler to be called by Xtracta"""
    #Connection to the database
    LOGGER.info(event)
    try:
        conn = db.connect(**DATABASES['lendi_ai'])
        cur = conn.cursor()
    except db.Error:
        LOGGER.exception("Error in handler() lendi_db error")

    try:
        body_ = event['body']
        if 'xml' in body_:
            event = event['body']
            event = xmltodict.parse(event)
        else:
            event = event['body']
        xtracta_document_id = event['events']['event']['document']['document_id']
        revision = event['events']['event']['document']['@revision']
        result = event['events']['event']['document']
        xtracta_status = event['events']['event']['document']['document_status']
    except TypeError:
        LOGGER.exception('Error in handler formatting xtracta response')

    try:
        command = SQLQUERIES['insert_xtracta_result'].format(xtracta_document_id,\
                                revision, json.dumps(result))
        command = command.replace("%", "%%")
        cur.execute(command)
    except db.Error:
        LOGGER.exception('Failed to insert xtracta result %s', command)
    ##########This part might not be necessary######################
    if int(revision) == 2:
        url = get_ui_from_xtracta(xtracta_document_id)
        if url:
            command = SQLQUERIES['update_document_url'].format(url,\
                                'xtracta_'+xtracta_status, xtracta_document_id)
            try:
                cur.execute(command)
            except db.Error:
                LOGGER.exception("Error in updating salesforce db %s", command)
            finally:
                conn.commit()

    ####The below part needs to be writtend as another service####
    try:
        if int(revision) > 1:
            command = SQLQUERIES['select_lendi_id_for_xtracta_id'].format(xtracta_document_id)
            cur.execute(command)
            lendi_document_id = cur.fetchone()
            if lendi_document_id:
                lendi_document_id = lendi_document_id[0]
                import pdb;pdb.set_trace()
                update_salesforce(lendi_document_id, result)
            else:
                LOGGER.error("No lendi_document_id for %s", xtracta_document_id)
    except db.Error:
        LOGGER.exception("Error in updating salesforce db %s", command)
    finally:
        conn.commit()
        conn.close()

    return {'Status':'Done'}


def get_ui_from_xtracta(document_id):
    """To get document UI from xtracta"""
    response = requests.post(XTRACTA['url']+"documents/"+"ui",\
        data={"submit":"Submit", "api_key":XTRACTA['key'],\
         "document_id":document_id, "expire":84600})
    response_content = xmltodict.parse(response.content)
    if response_content['documents_response']['status'] == '200':
        url = response_content['documents_response']['url']
    else:
        LOGGER.error("get_ui_from_xtracta() %s", response_content['documents_response']['status'])
        url = ''
    return url

def _update_salesforce_line_items(lendi_document_id, sfid, result, conn):
    #Update line items in salesforce
    field_set_id = result['field_data']['field_set']['field_set_id']
    cur = conn.cursor()
    #Delete existing line items first
    command = SQLQUERIES['delete_xtracta_result_line_items_in_sf'].format(lendi_document_id+'shit')
    cur.execute(command)
    #Insert new ones
    for i, row in enumerate(result['field_data']['field_set']['row']):
        for field in row['field']:
            command = SQLQUERIES['insert_xtracta_result_line_item_in_sf'].format(lendi_document_id,\
                                sfid, field['field_name'], field['field_value'], i+1, field_set_id)
            cur.execute(command)
    conn.commit()
    return

# def _update_salesforce_line_items(lendi_document_id, sfid, result, conn):
#     #Update line items in salesforce
#     field_set_id = result['field_data']['field_set']['field_set_id']
#     cur = conn.cursor()
#     command = SQLQUERIES['select_field_set_id_in_sf'].format(field_set_id)
#     cur.execute(command)
#     isexit = cur.fetchone()
#     if isexit:
#         #Delete existing line items first
#         command = SQLQUERIES['delete_xtracta_result_line_items_in_sf'].format(lendi_document_id+'shit')
#         cur.execute(command)
#     #Insert new ones
#     for i, row in enumerate(result['field_data']['field_set']['row']):
#         for field in row['field']:
#             command = SQLQUERIES['insert_xtracta_result_line_item_in_sf'].format(lendi_document_id,\
#                                 sfid, field['field_name'], field['field_value'], i+1, field_set_id)
#             cur.execute(command)
#     conn.commit()
#     return


def update_salesforce(lendi_document_id, result):
    """Update salesforce with the results"""
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
        for field in result['field_data']['field']:
            command = SQLQUERIES['update_xtracta_result_in_sf_new'].format(lendi_document_id,\
                    sfid, field['field_name'], field['field_value'], field['field_id'],\
                    field['field_value'])
            cur.execute(command)
        _update_salesforce_line_items(lendi_document_id, sfid, result, conn)
        conn.commit()
    else:
        LOGGER.error('Error in update_salesforce(), no sfid for %s', lendi_document_id)

    conn.close()
# def update_salesforce(lendi_document_id, result):
#     """Update salesforce with the results"""
#     try:
#         conn = db.connect(**DATABASES['salesforce'])
#     except db.Error:
#         LOGGER.exception("Error in update_salesforce(), %s", db.Error)
#     cur = conn.cursor()
#     command = SQLQUERIES['select_sfid_for_lendi_document_id'].format(lendi_document_id)
#     cur.execute(command)
#     sfid = cur.fetchone()
#     if sfid:
#         sfid = sfid[0]
#         for field in result['field_data']['field']:
#             command = SQLQUERIES['select_record_in_sf'].format(lendi_document_id,\
#                                   field['field_name'])
#             cur.execute(command)
#             isexist = cur.fetchone()
#             if isexist:
#                 command = SQLQUERIES['update_xtracta_result_in_sf'].format(field['field_value'],\
#                                 lendi_document_id, field['field_id'])
#                 cur.execute(command)
#             else:
#                 command = SQLQUERIES['insert_xtracta_result_in_sf'].format(lendi_document_id,\
#                                                     sfid, field['field_name'], field['field_value'], field['field_id'])
#                 cur.execute(command)

#         _update_salesforce_line_items(lendi_document_id, sfid, result, conn)
#         conn.commit()
#     else:
#         LOGGER.error('Error in update_salesforce(), no sfid for %s', lendi_document_id)

#     conn.close()

if __name__ == "__main__":

    event = {u'body': u'<?xml version="1.0" encoding="utf-8"?>\n<events><event sequence="3238"><generated>2017-05-03T05:36:27+00:00</generated><document revision="2"><workflow_id>50713</workflow_id><document_id>22478582</document_id><document_status>indexing</document_status><number_of_pages>1</number_of_pages><api_download_status>active</api_download_status><free_form/><classification>full</classification><document_url>https://web1-akl.xtracta.com/datasource/1/7d/17/dNQyiZCaB1NC.pdf</document_url><image_url>https://web1-akl.xtracta.com/datasource/1/21/be/dNQyiZCaB1NC-1-0800.jpg</image_url><field_data><field><field_id>2191421</field_id><field_name>ABN</field_name><field_value>53 880 104 872</field_value><field_value_location><word><page_number>1</page_number><left>75.85%</left><top>10.46%</top><width>1.49%</width><height>0.85%</height></word><word><page_number>1</page_number><left>77.98%</left><top>10.46%</top><width>2.38%</width><height>0.85%</height></word><word><page_number>1</page_number><left>81.01%</left><top>10.46%</top><width>2.3%</width><height>0.85%</height></word><word><page_number>1</page_number><left>83.87%</left><top>10.46%</top><width>2.38%</width><height>0.85%</height></word></field_value_location></field><field><field_id>2202699</field_id><field_name>Employer Name</field_name><field_value>Woonona Radiology Trust</field_value><field_value_location><word><page_number>1</page_number><left>71.81%</left><top>5.13%</top><width>6.53%</width><height>0.83%</height></word><word><page_number>1</page_number><left>78.75%</left><top>5.1%</top><width>7.02%</width><height>1.08%</height></word><word><page_number>1</page_number><left>86.25%</left><top>5.13%</top><width>3.51%</width><height>0.83%</height></word></field_value_location></field><field><field_id>2213696</field_id><field_name>Payment Date</field_name><field_value>18/10/2016</field_value><field_value_location><word><page_number>1</page_number><left>41.77%</left><top>28.98%</top><width>7.46%</width><height>0.85%</height></word></field_value_location></field><field><field_id>2202713</field_id><field_name>Employment Status</field_name><field_value/><field_value_location/></field><field><field_id>2213698</field_id><field_name>Employee Name</field_name><field_value>Michelle Turner</field_value><field_value_location><word><page_number>1</page_number><left>17.46%</left><top>19.83%</top><width>7.14%</width><height>1.03%</height></word><word><page_number>1</page_number><left>25.16%</left><top>19.86%</top><width>5.48%</width><height>1%</height></word></field_value_location></field><field><field_id>7349460</field_id><field_name>Job Title</field_name><field_value/><field_value_location/></field><field><field_id>2202714</field_id><field_name>Pament Period Begin Date</field_name><field_value>03/10/2016</field_value><field_value_location><word><page_number>1</page_number><left>12.14%</left><top>28.98%</top><width>7.58%</width><height>0.85%</height></word></field_value_location></field><field><field_id>2202715</field_id><field_name>Payment Period End Date</field_name><field_value>16/10/2016</field_value><field_value_location><word><page_number>1</page_number><left>21.33%</left><top>28.98%</top><width>7.46%</width><height>0.85%</height></word></field_value_location></field><field><field_id>8495671</field_id><field_name>Annual Income</field_name><field_value>$76,780.00</field_value><field_value_location><word><page_number>1</page_number><left>82.46%</left><top>19.81%</top><width>7.42%</width><height>1.05%</height></word></field_value_location></field><field><field_id>7340312</field_id><field_name>Gross Income</field_name><field_value>$2,945.00</field_value><field_value_location><word><page_number>1</page_number><left>68.91%</left><top>28.84%</top><width>7.94%</width><height>1.28%</height></word></field_value_location></field><field><field_id>7340313</field_id><field_name>Net Income</field_name><field_value>$1,813.00</field_value><field_value_location><word><page_number>1</page_number><left>87.26%</left><top>28.84%</top><width>7.94%</width><height>1.28%</height></word></field_value_location></field><field><field_id>7349845</field_id><field_name>Superannuation</field_name><field_value>$279.78</field_value><field_value_location><word><page_number>1</page_number><left>76.98%</left><top>61.58%</top><width>4.76%</width><height>0.85%</height></word></field_value_location></field><field><field_id>8495672</field_id><field_name>Paid Tax</field_name><field_value>$956.00</field_value><field_value_location><word><page_number>1</page_number><left>76.98%</left><top>50.95%</top><width>4.8%</width><height>0.85%</height></word></field_value_location></field><field><field_id>7350614</field_id><field_name>Bank Amount</field_name><field_value>$1,813.00</field_value><field_value_location><word><page_number>1</page_number><left>89.64%</left><top>77.2%</top><width>5.93%</width><height>0.97%</height></word></field_value_location></field><field_set><field_set_id>1176480</field_set_id><field_set_name>Payments/Deductions</field_set_name><row><field><field_id>7340700</field_id><field_name>Description</field_name><field_value>Ordinary Hours</field_value></field><field><field_id>7340701</field_id><field_name>Rate</field_name><field_value>$38.0000</field_value></field><field><field_id>7340702</field_id><field_name>Unit</field_name><field_value>70.0000</field_value></field><field><field_id>7340703</field_id><field_name>Amount</field_name><field_value>$2,660.00</field_value></field></row><row><field><field_id>7340700</field_id><field_name>Description</field_name><field_value>Public Holiday</field_value></field><field><field_id>7340701</field_id><field_name>Rate</field_name><field_value>$38.0000</field_value></field><field><field_id>7340702</field_id><field_name>Unit</field_name><field_value>7.5000</field_value></field><field><field_id>7340703</field_id><field_name>Amount</field_name><field_value>$285.00</field_value></field></row></field_set></field_data></document></event></events>'}
    print (handler(event))