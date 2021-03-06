import os
from dotenv import Dotenv
try:
    dotenv_ = Dotenv('/Users/localuser/.env')
    os.environ.update(dotenv_)
except IOError:
    pass

DATABASES = {
    "lendi_ai" : {"host":os.getenv("LENDIAI_DBHOST"),
                  "database":os.getenv("LENDIAI_DATABASE"),
                  "user":os.getenv("LENDIAI_DBUSER"),
                  "password":os.getenv("LENDIAI_DBPASSWORD")},
    "salesforce" : {"host":os.getenv("SF_DBHOST"),
                    "database":os.getenv("SF_DATABASE"),
                    "user":os.getenv("SF_DBUSER"),
                    "password":os.getenv("SF_DBPASSWORD"),
                    "ssl":True}}

XTRACTA = {"url":os.getenv("XTRACTA_URL"), "key":os.getenv("XTRACTA_KEY")}

WORKFLOW_MAPPING = {"a1u6F000003HtqHQAS":"50713"}
