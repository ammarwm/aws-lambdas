import pprint
import json
def pretty_json(json_, file_name= './pjson.txt'):
    json_ = json.loads(json_)
    with open('./pjson.txt','w') as f:
        f.write(json.dumps(json_, indent=2))
    

if __name__ == "__main__":
    
    _json = '{"@revision": "2", "workflow_id": "50713", "document_id": "20742383", "document_status": "indexing", "number_of_pages": "1", "api_download_status": "active", "free_form": null, "classification": null, "document_url": "https://web1-akl.xtracta.com/datasource/1/1a/00/PfsPvqTmENGX.pdf", "image_url": "https://web1-akl.xtracta.com/datasource/1/82/d2/PfsPvqTmENGX-1-0800.jpg", "field_data": {"field": [{"field_id": "2191421", "field_name": "ABN", "field_value": null, "field_value_location": null}, {"field_id": "2202699", "field_name": "Employer Name", "field_value": null, "field_value_location": null}, {"field_id": "2213696", "field_name": "Payment Date", "field_value": "19/12/2016", "field_value_location": null}, {"field_id": "2202713", "field_name": "Employment Status", "field_value": null, "field_value_location": null}, {"field_id": "2213698", "field_name": "Employee Name", "field_value": null, "field_value_location": null}, {"field_id": "7349460", "field_name": "Job Title", "field_value": null, "field_value_location": null}, {"field_id": "2202714", "field_name": "Pament Period Begin Date", "field_value": null, "field_value_location": null}, {"field_id": "2202715", "field_name": "Payment Period End Date", "field_value": null, "field_value_location": null}, {"field_id": "8495671", "field_name": "Annual Income", "field_value": null, "field_value_location": null}, {"field_id": "7340312", "field_name": "Gross Income", "field_value": null, "field_value_location": null}, {"field_id": "7340313", "field_name": "Net Income", "field_value": null, "field_value_location": null}, {"field_id": "7349845", "field_name": "Superannuation", "field_value": null, "field_value_location": null}, {"field_id": "8495672", "field_name": "Paid Tax", "field_value": null, "field_value_location": null}, {"field_id": "7350614", "field_name": "Bank Amount", "field_value": null, "field_value_location": null}], "field_set": {"field_set_id": "1176480", "field_set_name": "Payments/Deductions", "row": {"field": [{"field_id": "7340700", "field_name": "Description", "field_value": null}, {"field_id": "7340701", "field_name": "Rate", "field_value": null}, {"field_id": "7340702", "field_name": "Unit", "field_value": null}, {"field_id": "7340703", "field_name": "Amount", "field_value": null}]}}}}'
    
    pretty_json(_json)


