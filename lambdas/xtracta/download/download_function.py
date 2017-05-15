import logging
import requests
import json
import xmltodict
import boto3

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

lambda_client = boto3.client('lambda', region_name='ap-southeast-2')

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

    try:
        if int(revision) > 1:
            command = SQLQUERIES['select_lendi_id_for_xtracta_id'].format(xtracta_document_id)
            cur.execute(command)
            lendi_document_id = cur.fetchone()
            if lendi_document_id:
                lendi_document_id = lendi_document_id[0]
                payload = {"lendi_document_id":lendi_document_id, "xtracta_result":result}
                write_to_heroku_response = lambda_client.invoke(
                    FunctionName='HerokuXtractResult:Production',
                    InvocationType='Event',
                    LogType='None',
                    Payload=json.dumps(payload))
            else:
                LOGGER.error("No lendi_document_id for %s", xtracta_document_id)
    except db.Error:
        LOGGER.exception("Error in updating salesforce db %s", command)
    finally:
        conn.commit()
        conn.close()

    return {'Status':'Done'}


if __name__ == "__main__":

    event = {u'body': u'<?xml version="1.0" encoding="utf-8"?>\n<events><event sequence="3242"><generated>2017-05-04T05:13:45+00:00</generated><document revision="2"><workflow_id>50713</workflow_id><document_id>22553527</document_id><document_status>indexing</document_status><number_of_pages>1</number_of_pages><api_download_status>active</api_download_status><free_form/><classification>full</classification><document_url>https://web1-akl.xtracta.com/datasource/1/e5/c7/YHpbJ2gQBL.pdf</document_url><image_url>https://web1-akl.xtracta.com/datasource/1/d3/72/YHpbJ2gQBL-1-0800.jpg</image_url><field_data><field><field_id>2191421</field_id><field_name>ABN</field_name><field_value>43 101 490 000</field_value><field_value_location><word><page_number>1</page_number><left>37.06%</left><top>10.89%</top><width>1.41%</width><height>0.71%</height></word><word><page_number>1</page_number><left>39.03%</left><top>10.89%</top><width>1.9%</width><height>0.71%</height></word><word><page_number>1</page_number><left>41.53%</left><top>10.89%</top><width>2.18%</width><height>0.71%</height></word><word><page_number>1</page_number><left>44.19%</left><top>10.89%</top><width>2.14%</width><height>0.71%</height></word></field_value_location></field><field><field_id>2202699</field_id><field_name>Employer Name</field_name><field_value>Multi Civil &amp; Rail Services Pty Ltd</field_value><field_value_location><word><page_number>1</page_number><left>3.95%</left><top>5.36%</top><width>5.93%</width><height>1.4%</height></word><word><page_number>1</page_number><left>10.93%</left><top>5.33%</top><width>5.36%</width><height>1.42%</height></word><word><page_number>1</page_number><left>17.3%</left><top>5.33%</top><width>1.85%</width><height>1.45%</height></word><word><page_number>1</page_number><left>20.08%</left><top>5.36%</top><width>4.6%</width><height>1.4%</height></word><word><page_number>1</page_number><left>25.69%</left><top>5.33%</top><width>10.85%</width><height>1.42%</height></word><word><page_number>1</page_number><left>37.58%</left><top>5.36%</top><width>3.95%</width><height>1.77%</height></word><word><page_number>1</page_number><left>42.54%</left><top>5.36%</top><width>3.83%</width><height>1.4%</height></word></field_value_location></field><field><field_id>2213696</field_id><field_name>Payment Date</field_name><field_value>8/02/2017</field_value><field_value_location><word><page_number>1</page_number><left>73.95%</left><top>13.25%</top><width>10.36%</width><height>0.83%</height></word></field_value_location></field><field><field_id>2202713</field_id><field_name>Employment Status</field_name><field_value/><field_value_location/></field><field><field_id>2213698</field_id><field_name>Employee Name</field_name><field_value>Brian CARR</field_value><field_value_location><word><page_number>1</page_number><left>14.96%</left><top>18.12%</top><width>3.35%</width><height>0.8%</height></word><word><page_number>1</page_number><left>18.87%</left><top>18.1%</top><width>4.23%</width><height>0.83%</height></word></field_value_location></field><field><field_id>7349460</field_id><field_name>Job Title</field_name><field_value>Safe Working Officer</field_value><field_value_location><word><page_number>1</page_number><left>14.64%</left><top>21.09%</top><width>3.06%</width><height>0.83%</height></word><word><page_number>1</page_number><left>18.15%</left><top>21.12%</top><width>5.48%</width><height>1%</height></word><word><page_number>1</page_number><left>24.15%</left><top>21.09%</top><width>4.44%</width><height>0.83%</height></word></field_value_location></field><field><field_id>2202714</field_id><field_name>Pament Period Begin Date</field_name><field_value>30/01/2017 To: 5/02/2017 GROSS PAY: $3,675.60</field_value><field_value_location><word><page_number>1</page_number><left>17.54%</left><top>23.85%</top><width>7.5%</width><height>0.83%</height></word><word><page_number>1</page_number><left>36.98%</left><top>23.88%</top><width>2.1%</width><height>0.8%</height></word><word><page_number>1</page_number><left>40.6%</left><top>23.77%</top><width>6.65%</width><height>0.83%</height></word><word><page_number>1</page_number><left>69.4%</left><top>24.05%</top><width>5.32%</width><height>0.83%</height></word><word><page_number>1</page_number><left>75.28%</left><top>24.08%</top><width>3.27%</width><height>0.77%</height></word><word><page_number>1</page_number><left>79.44%</left><top>24%</top><width>6.65%</width><height>1.03%</height></word></field_value_location></field><field><field_id>2202715</field_id><field_name>Payment Period End Date</field_name><field_value>5/02/2017</field_value><field_value_location><word><page_number>1</page_number><left>40.6%</left><top>23.77%</top><width>6.65%</width><height>0.83%</height></word></field_value_location></field><field><field_id>8495671</field_id><field_name>Annual Income</field_name><field_value/><field_value_location/></field><field><field_id>7340312</field_id><field_name>Gross Income</field_name><field_value>$3,675.60</field_value><field_value_location><word><page_number>1</page_number><left>79.44%</left><top>24%</top><width>6.65%</width><height>1.03%</height></word></field_value_location></field><field><field_id>7340313</field_id><field_name>Net Income</field_name><field_value>$2,457.00</field_value><field_value_location><word><page_number>1</page_number><left>79.44%</left><top>26.67%</top><width>6.65%</width><height>1.03%</height></word></field_value_location></field><field><field_id>7349845</field_id><field_name>Superannuation</field_name><field_value>$169.67 $1,393.09 Superannuation Expenses</field_value><field_value_location><word><page_number>1</page_number><left>54.23%</left><top>38.3%</top><width>5.4%</width><height>0.97%</height></word><word><page_number>1</page_number><left>68.31%</left><top>38.3%</top><width>6.65%</width><height>1.03%</height></word><word><page_number>1</page_number><left>77.06%</left><top>38.36%</top><width>10.56%</width><height>1.03%</height></word><word><page_number>1</page_number><left>88.19%</left><top>38.39%</top><width>6.53%</width><height>1%</height></word></field_value_location></field><field><field_id>8495672</field_id><field_name>Paid Tax</field_name><field_value>-$1,218.60</field_value><field_value_location><word><page_number>1</page_number><left>52.5%</left><top>37.08%</top><width>7.14%</width><height>1.03%</height></word></field_value_location></field><field><field_id>7350614</field_id><field_name>Bank Amount</field_name><field_value/><field_value_location/></field><field_set><field_set_id>1176480</field_set_id><field_set_name>Payments/Deductions</field_set_name><row><field><field_id>7340700</field_id><field_name>Description</field_name><field_value>CSS (A)</field_value></field><field><field_id>7340701</field_id><field_name>Rate</field_name><field_value>$47.00</field_value></field><field><field_id>7340702</field_id><field_name>Unit</field_name><field_value>18</field_value></field><field><field_id>7340703</field_id><field_name>Amount</field_name><field_value>$846.00</field_value></field></row><row><field><field_id>7340700</field_id><field_name>Description</field_name><field_value>CSS (B)</field_value></field><field><field_id>7340701</field_id><field_name>Rate</field_name><field_value>$78.60</field_value></field><field><field_id>7340702</field_id><field_name>Unit</field_name><field_value>36</field_value></field><field><field_id>7340703</field_id><field_name>Amount</field_name><field_value>$2,829.60</field_value></field></row></field_set></field_data></document></event></events>'}
    print (handler(event))