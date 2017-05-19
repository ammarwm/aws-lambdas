"""List of all the database inquires"""
SQLQUERIES = {"select_sfid_for_lendi_document_id": """SELECT sfid from salesforce.click_uploaded_documents__c\
                                                    WHERE lendi_uploaded_file_uuid__c = '{}';""",

               "select_lendi_id_for_xtracta_id": """SELECT lendi_document_id FROM xtracta.document_id_mapping WHERE\
                                                 xtracta_document_id = '{}';""",\

               "insert_xtracta_result_in_sf": """INSERT INTO salesforce.document_schema__c (upload_document_uuid__c, uploaded_document__c, field_display_name__c, field_value__c, field_id__c)
                                                 VALUES ('{}','{}','{}','{}','{}');""",\

               "delete_xtracta_result_line_items_in_sf": """DELETE FROM salesforce.document_schema_extension__c WHERE upload_document_uuid__c = '{}'""",\

               "delete_xtracta_result_in_sf": """DELETE FROM salesforce.document_schema__c WHERE upload_document_uuid__c = '{}'""",\

               "insert_xtracta_result_line_item_in_sf": """INSERT INTO salesforce.document_schema_extension__c (upload_document_uuid__c, uploaded_document__c,field_name__c,\
                                                                field_value__c, row_index__c, field_set_id__c) VALUES ('{}','{}','{}','{}','{}','{}');""",\

               "update_xtracta_result_in_sf": """INSERT INTO salesforce.document_schema__c
                                                (upload_document_uuid__c, uploaded_document__c, field_display_name__c, field_value__c, field_id__c)
                                                 VALUES ('{}','{}','{}','{}','{}') ON CONFLICT (field_id__c)
                                                 DO UPDATE SET  field_value__c = '{}'""",\

               "select_record_in_sf":"""SELECT 1 FROM salesforce.document_schema__c
                                        WHERE upload_document_uuid__c = '{}' and field_display_name__c = '{}'""",

               "insert_xtracta_result": """INSERT INTO xtracta.result (xtracta_document_id, revision, result)
                                              VALUES ({}, {}, '{}');""",\

               "insert_new_document": """INSERT INTO xtracta.document_id_mapping (xtracta_document_id, lendi_document_id, status)
                                                VALUES ('{}','{}','{}');""",

               "update_document_status": """UPDATE xtracta.document_id_mapping SET status='{}' WHERE xtracta_document_id='{}'""",

               "update_lendi_document_id":"""UPDATE xtracta.document_id_mapping SET lendi_document_id='{}' WHERE xtracta_document_id='{}'""",

               "select_xtracta_document_id":"""SELECT * FROM xtracta.document_id_mapping WHERE xtracta_document_id='{}'""", 

               "select_master_document_for_uploaded_document":"""SELECT doc_master.sfid FROM salesforce.document_master__c AS doc_master
                                                                 JOIN salesforce.required_document__c AS req_doc 
                                                                      ON doc_master.sfid = req_doc.acfdocument_master__c 
                                                                 JOIN salesforce.click_uploaded_documents__c AS up_doc 
                                                                      ON up_doc.click_loans_required_document__c = req_doc.sfid 
                                                                 WHERE up_doc.lendi_uploaded_file_uuid__c = '{}';""",

               "select_document_data":"""SELECT result from xtracta.result JOIN xtracta.document_id_mapping
                                           ON result.xtracta_document_id = document_id_mapping.xtracta_document_id 
                                           WHERE document_id_mapping.lendi_document_id = '{}' ORDER BY revision DESC LIMIT 1;""",

               "update_document_url":"""UPDATE xtracta.document_id_mapping SET ui_url = '{}' WHERE xtracta_document_id = '{}';""",

               "select_xtracta_document":"""SELECT xtracta_document_id, ui_url, timestamp FROM xtracta.document_id_mapping WHERE lendi_document_id = '{}'""",

               "select_field_set_id_in_sf":"""SELECT 1 FROM salesforce.document_schema_extension__c WHERE field_set_id__c = '{}'""",
               
               "select_payslip_requirements":"""SELECT lender_name, document_name, document_age, no_of_documents FROM required_documents.payslip_master\
                                                WHERE lender_name = '{}' AND employment_type = '{}';""",
              
              "update_validation_result":"""UPDATE validator.validation_request SET result = '{0}' WHERE uuid = '{1}';"""}
