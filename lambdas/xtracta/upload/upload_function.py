import logging
from urllib import unquote_plus
from io import BytesIO
import boto3
import xmltodict
import requests
try:
    import psycopg2 as dbconnector
except ImportError:
    import pg8000 as dbconnector
from sql_queries import sql_queries
from config import DATABASES, XTRACTA, WORKFLOW_MAPPING


#Get the LOGGER
LOGGER = logging.getLogger("root")
LOG_HANDLER = logging.StreamHandler()
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(LOG_HANDLER)
LOGGER.setLevel(logging.INFO)


XTRACTA_OPERATIONS = {
    "get_document":"get_document(data)",\
    "upload_document":"upload_document(data)"\
    }

S3 = boto3.client("s3")

def handler(event, context=None):
    """Lambda function handler for XTRACTA integration"""
    LOGGER.info(event)
    done = "Failed"
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"].encode("utf8"))
    obj = S3.get_object(Bucket=bucket, Key=key)
    document_file = (key, BytesIO(obj["Body"].read()))
    lendi_document_id = obj["Metadata"]["lendi_document_id"]
    master_document_id = obj["Metadata"]["master_document_id"]
    workflow_id = get_workflow_id(master_document_id)
    if workflow_id:
        xtracta_document_id = upload_document_to_xtracta(workflow_id, document_file)
    else:
        logging.error("No workflow_id for master_document_id: %s", master_document_id)
        return done
    if xtracta_document_id:
        insert_document(xtracta_document_id, lendi_document_id, workflow_id, 'uploaded')
    else:
        logging.error("No xtracta_document_id for %s", lendi_document_id)
        return done
    done = "Success"
    return done

def get_workflow_id(master_document_id):
    """Mapping master_document_id to xtracta workflow id"""
    workflow_id = WORKFLOW_MAPPING.get(master_document_id)
    return workflow_id


def insert_document(xtracta_document_id, lendi_document_id, workflow_id, status):
    """Update the status of the document in the smart_document table"""
    #Connection to the database
    done = False
    try:
        conn = dbconnector.connect(**DATABASES['lendi_ai'])
    except Exception:
        LOGGER.exception("Error update_document_status(), db connection error")
        return done
    cur = conn.cursor()
    command = sql_queries['select_xtracta_document_id'].format(xtracta_document_id)
    try:
        cur.execute(command)
        result = cur.fetchone()
        if result:
            lendi_document_id_ = result[1]
            if not lendi_document_id_:
                command = sql_queries['update_lendi_document_id'].format(lendi_document_id)
                cur.execute(command)
        else:
            command = sql_queries['insert_new_document'].format(xtracta_document_id,\
                        lendi_document_id, 'uploaded')
            cur.execute(command)
    except db.Error:
        LOGGER.exception("Error update_document_status command: %s", command)
    finally:
        conn.commit()
        conn.close()
    return done


def get_document_from_xtracta(document_id):
    """Get document from XTRACTA based on document_id"""
    response = None
    response = requests.post(XTRACTA['url']+"documents",
                             data={"submit":"Submit",\
                                   "api_key":XTRACTA['key'],\
                                   "document_id":document_id})
    return response


def upload_document_to_xtracta(workflow, document_file):
    """Upload document to XTRACTA based on document_id"""
    response = None
    file = {"userfile":document_file}
    response = requests.post(XTRACTA['url']+"documents"+"/"+"upload",\
                    files=file, data={"submit":"Submit", "api_key":XTRACTA['key'],\
                                     "workflow_id":workflow})
    response_content = xmltodict.parse(response.content)
    if response_content['xml']['status'] == '200':
        document_id = response_content['xml']['document_id']
    else:
        LOGGER.exception("Error upload_document_to_xtracta() %s", response_content['xml']['status'])
        document_id = ''
    return document_id


if __name__ == "__main__":
    Event = {u'Records': [{u'eventVersion': u'2.0', u'eventTime': u'2017-02-27T04:02:25.387Z', u'requestParameters': {u'sourceIPAddress': u'49.255.235.138'}, u's3': {u'configurationId': u'e82a657f-a272-4889-b1d8-f342cab8a720', u'object': {u'eTag': u'57841068390e2040d330f9c3af24e73d', u'sequencer': u'0058B3A4D15C34C972', u'key': u'test_613d84cd-410f-4e9d-97e9-385d3e5d76b5.pdf', u'size': 3796}, u'bucket': {u'arn': u'arn:aws:s3:::lendi-ai', u'name': u'lendi-ai', u'ownerIdentity': {u'principalId': u'A3NK8U3O9U5EZ2'}}, u's3SchemaVersion': u'1.0'}, u'responseElements': {u'x-amz-id-2': u'RB+q4LXINmgl/oP+OcSlo0cXRy7as0eXfdNLGmYtmKTZoR0+XJNsnI+VWpudNU3x', u'x-amz-request-id': u'797DD50585776ECA'}, u'awsRegion': u'ap-southeast-2', u'eventName': u'ObjectCreated:Put', u'userIdentity': {u'principalId': u'AWS:AIDAI6HACS6BALQXXKQOI'}, u'eventSource': u'aws:s3'}]}
    
    Event = {u'Records': [{u'eventVersion': u'2.0', u'eventTime': u'2017-03-09T05:33:04.046Z', u'requestParameters': {u'sourceIPAddress': u'54.224.67.1'}, u's3': {u'configurationId': u'UploadedDocumentS3', u'object': {u'eTag': u'75431eddcf7888c3740c44c67189f6ef', u'sequencer': u'0058C0E90FF31C8B53', u'key': u'files-uat/59504d7b-f3d4-41b0-beca-50f7fe998902_97I5G3pJxz.pdf', u'size': 164690}, u'bucket': {u'arn': u'arn:aws:s3:::lendi-documents', u'name': u'lendi-documents', u'ownerIdentity': {u'principalId': u'A3NK8U3O9U5EZ2'}}, u's3SchemaVersion': u'1.0'}, u'responseElements': {u'x-amz-id-2': u'JxHpLoMqmiqbYtOQEoukFX8kB0TAPa0RRCB6ZgrfmFFI1GOVE45P4QqZE8lrVxYc5+7iNem9E4g=', u'x-amz-request-id': u'215DC826312D7A9A'}, u'awsRegion': u'ap-southeast-2', u'eventName': u'ObjectCreated:Put', u'userIdentity': {u'principalId': u'AWS:AIDAJLFKZ7566PBBVH7SC'}, u'eventSource': u'aws:s3'}]}
    handler(Event)