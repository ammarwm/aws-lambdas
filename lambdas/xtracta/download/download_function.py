import logging
import requests
import json
import xmltodict
try:
    import psycopg2 as db
except ImportError:
    import pg8000 as db
from sql_queries import sql_queries
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
    except TypeError:
        LOGGER.exception('Error in handler formatting xtracta response')

    try:
        command = sql_queries['insert_xtracta_result'].format(xtracta_document_id,\
                                revision, json.dumps(result))
        command = command.replace("%", "%%")
        cur.execute(command)
    except db.Error:
        LOGGER.exception('Failed to insert xtracta result %s', command)

    if int(revision) == 2:
        url = get_ui_from_xtracta(xtracta_document_id)
        if url:
            command = sql_queries['update_document_url'].format(url, xtracta_document_id)
            try:
                cur.execute(command)
            except db.Error:
                LOGGER.exception("Error in updating salesforce db %s", command)
            finally:
                conn.commit()
                conn.close()

    """
    try:
        if int(revision) > 1:
            command = sql_queries['get_lendi_id_for_xtracta_id'].format(xtracta_document_id)
            cur.execute(command)
            lendi_document_id = cur.fetchone()
            if lendi_document_id:
                lendi_document_id = lendi_document_id[0]
                #update_salesforce(lendi_document_id, result)
    except Exception:
        LOGGER.exception("Error in updating salesforce db %s", command)
    finally:
        conn.commit()
        conn.close()
    """
    return {'Status':'Done'}


def get_ui_from_xtracta(document_id):
    """To get document UI from xtracta"""
    response = requests.post(XTRACTA['url']+"documents/"+"ui",\
        data={"submit":"Submit", "api_key":XTRACTA['key'], "document_id":document_id})
    response_content = xmltodict.parse(response.content)
    if response_content['documents_response']['status'] == '200':
        url = response_content['documents_response']['url']
    else:
        LOGGER.error("get_ui_from_xtracta() %s", response_content['documents_response']['status'])
        url = ''
    return url


def update_salesforce(lendi_document_id, result):
    """Update salesforce with the results"""
    try:
        conn = db.connect(**DATABASES['salesforce'])
    except db.Error:
        LOGGER.exception("Error in update_salesforce(), salesforce_db error")
    cur = conn.cursor()
    command = sql_queries['get_sfid_for_lendi_document_id'].format(lendi_document_id)
    cur.execute(command)
    sfid = cur.fetchone()

    if sfid:
        sfid = sfid[0]
        for field in result['field_data']['field']:
            command = sql_queries['select_record_in_sf'].format(lendi_document_id,
                                                                field['field_name'])
            cur.execute(command)
            isexist = cur.fetchone()
            if isexist:
                command = sql_queries['update_xtracta_result_in_sf'].format(field['field_value'],\
                                lendi_document_id, field['field_name'])
                cur.execute(command)
            else:
                command = sql_queries['insert_xtracta_result_in_sf'].format(lendi_document_id,\
                                                    sfid, field['field_name'], field['field_value'])
                cur.execute(command)
    else:
        LOGGER.error('Error in update_salesforce(), no sfid for %s', lendi_document_id)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    
    event = {u'body': u'<?xml version="1.0" encoding="utf-8"?>\n<events><event sequence="759"><generated>2017-03-17T03:51:31+00:00</generated><document revision="2"><workflow_id>50713</workflow_id><document_id>20533496</document_id><document_status>indexing</document_status><number_of_pages>1</number_of_pages><api_download_status>active</api_download_status><free_form/><classification/><document_url>https://web1-akl.xtracta.com/datasource/1/8a/f1/juNwiyeL7.pdf</document_url><image_url>https://web1-akl.xtracta.com/datasource/1/c8/b5/juNwiyeL7-1-0800.jpg</image_url><field_data><field><field_id>2191421</field_id><field_name>ABN</field_name><field_value>48 076 700 000</field_value><field_value_location><word><page_number>1</page_number><left>69.87%</left><top>10.73%</top><width>1.33%</width><height>0.68%</height></word><word><page_number>1</page_number><left>71.63%</left><top>10.73%</top><width>2%</width><height>0.68%</height></word><word><page_number>1</page_number><left>74.05%</left><top>10.69%</top><width>2%</width><height>0.73%</height></word><word><page_number>1</page_number><left>76.47%</left><top>10.73%</top><width>2.06%</width><height>0.68%</height></word></field_value_location></field><field><field_id>2202699</field_id><field_name>Employer Name</field_name><field_value>Hayes Pest Control Pty Ltd</field_value><field_value_location><word><page_number>1</page_number><left>10.47%</left><top>10.99%</top><width>9.56%</width><height>2.27%</height></word><word><page_number>1</page_number><left>21.36%</left><top>10.99%</top><width>6.78%</width><height>1.75%</height></word><word><page_number>1</page_number><left>29.16%</left><top>10.99%</top><width>11.62%</width><height>1.84%</height></word><word><page_number>1</page_number><left>42.17%</left><top>11.03%</top><width>4.9%</width><height>2.31%</height></word><word><page_number>1</page_number><left>48.28%</left><top>11.07%</top><width>4.84%</width><height>1.8%</height></word></field_value_location></field><field><field_id>2213696</field_id><field_name>Payment Date</field_name><field_value>18/10/2016</field_value><field_value_location><word><page_number>1</page_number><left>69.93%</left><top>17.49%</top><width>6.05%</width><height>0.73%</height></word></field_value_location></field><field><field_id>2202713</field_id><field_name>Employment Status</field_name><field_value/><field_value_location/></field><field><field_id>2213698</field_id><field_name>Employee Name</field_name><field_value>BRENDAN McCUMBER</field_value><field_value_location><word><page_number>1</page_number><left>19.84%</left><top>15.18%</top><width>5.93%</width><height>0.73%</height></word><word><page_number>1</page_number><left>26.26%</left><top>15.18%</top><width>6.9%</width><height>0.73%</height></word></field_value_location></field><field><field_id>7349460</field_id><field_name>Job Title</field_name><field_value/><field_value_location/></field><field><field_id>2202714</field_id><field_name>Pament Period Begin Date</field_name><field_value>12/10/2016</field_value><field_value_location><word><page_number>1</page_number><left>29.16%</left><top>26.51%</top><width>6.11%</width><height>0.73%</height></word></field_value_location></field><field><field_id>2202715</field_id><field_name>Payment Period End Date</field_name><field_value>18/10/2016</field_value><field_value_location><word><page_number>1</page_number><left>44.95%</left><top>26.55%</top><width>6.11%</width><height>0.73%</height></word></field_value_location></field><field><field_id>2202716</field_id><field_name>Payment Period </field_name><field_value/><field_value_location/></field><field><field_id>7340312</field_id><field_name>Gross Income</field_name><field_value>$961.54</field_value><field_value_location><word><page_number>1</page_number><left>72.84%</left><top>26.55%</top><width>4.48%</width><height>0.77%</height></word></field_value_location></field><field><field_id>7340313</field_id><field_name>Net Income</field_name><field_value>$792.00</field_value><field_value_location><word><page_number>1</page_number><left>72.84%</left><top>28.82%</top><width>4.48%</width><height>0.81%</height></word></field_value_location></field><field><field_id>7340410</field_id><field_name>Deduction</field_name><field_value/><field_value_location/></field><field><field_id>7349845</field_id><field_name>Superannuation</field_name><field_value>$91.35</field_value><field_value_location><word><page_number>1</page_number><left>52.69%</left><top>40.74%</top><width>3.75%</width><height>0.81%</height></word></field_value_location></field><field><field_id>7350614</field_id><field_name>Bank Amount</field_name><field_value/><field_value_location/></field><field_set><field_set_id>1176480</field_set_id><field_set_name>Payments</field_set_name><row><field><field_id>7340700</field_id><field_name>Description</field_name><field_value>Base Salary</field_value></field><field><field_id>7340701</field_id><field_name>Rate</field_name><field_value/></field><field><field_id>7340702</field_id><field_name>Unit</field_name><field_value/></field><field><field_id>7340703</field_id><field_name>Amount</field_name><field_value>$961.54</field_value></field><field><field_id>7340704</field_id><field_name>YTD Amount</field_name><field_value>$13,765.20</field_value></field></row><row><field><field_id>7340700</field_id><field_name>Description</field_name><field_value>Holiday Pay</field_value></field><field><field_id>7340701</field_id><field_name>Rate</field_name><field_value/></field><field><field_id>7340702</field_id><field_name>Unit</field_name><field_value/></field><field><field_id>7340703</field_id><field_name>Amount</field_name><field_value/></field><field><field_id>7340704</field_id><field_name>YTD Amount</field_name><field_value>$1,619.44</field_value></field></row><row><field><field_id>7340700</field_id><field_name>Description</field_name><field_value>Holiday Leave Loading</field_value></field><field><field_id>7340701</field_id><field_name>Rate</field_name><field_value/></field><field><field_id>7340702</field_id><field_name>Unit</field_name><field_value/></field><field><field_id>7340703</field_id><field_name>Amount</field_name><field_value/></field><field><field_id>7340704</field_id><field_name>YTD Amount</field_name><field_value>$283.40</field_value></field></row></field_set></field_data></document></event></events>'}
    print (handler(event))