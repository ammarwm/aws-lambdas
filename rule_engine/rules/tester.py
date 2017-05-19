import unittest
import requests
import uuid
import sys
class Test(unittest.TestCase):

    def setup(self):
        pass

    def test_payslip_1(self):
        sid = str(uuid.uuid4())
        sid = 'c8274353-8753-440a-af82-4efb21335001'
        url = 'http://localhost:5000/payslip/'
        requests.post(url+'facts', json={'sid':sid,'required_document_age':14})
        requests.post(url+'events', json={"sid":sid,"document_age":89})

if __name__ == '__main__':
    unittest.main()



