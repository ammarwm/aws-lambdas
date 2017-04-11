"""List of all the database inquires"""
sql_queries = {"get_sfid_for_lendi_document_id": """SELECT sfid from salesforce.click_uploaded_documents__c\
                                                    WHERE lendi_uploaded_file_uuid__c = '{}';""",

               "get_lendi_id_for_xtracta_id": """SELECT lendi_document_id FROM xtracta.document_id_mapping WHERE\
                                                 xtracta_document_id = '{}';""",

               "insert_xtracta_result_in_sf": """INSERT INTO salesforce.document_schema__c (upload_document_uuid__c, uploaded_document__c, field_display_name__c, field_value__c)
                                                 VALUES ('{}','{}','{}','{}');""",\

               "update_xtracta_result_in_sf": """UPDATE salesforce.document_schema__c SET field_value__c = '{}' 
                                                 WHERE upload_document_uuid__c = '{}' and field_display_name__c = '{}'""",\

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

                "update_document_url":"""UPDATE xtracta.document_id_mapping SET ui_url = '{}' WHERE xtracta_document_id = '{}';"""}
