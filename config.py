import os
import sys
import logging
from dotenv import Dotenv
try:
    dotenv_ = Dotenv('/Users/localuser/.env')
    os.environ.update(dotenv_)
except IOError:
    pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

LOGGER = logging.getLogger("root")
LOG_HANDLER = logging.StreamHandler()
#LOG_HANDLER = logging.FileHandler('/var/log/rule-engine/rules.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG_HANDLER.setFormatter(formatter)
LOGGER.addHandler(LOG_HANDLER)
LOGGER.setLevel(logging.INFO)

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

XTRACTA_URL_TIMEOUT = 3600
XTRACTA = {"url":os.getenv("XTRACTA_URL"), "key":os.getenv("XTRACTA_KEY")}

WORKFLOW_MAPPING = {"a1u6F000003HtqHQAS":"50713"}

AWS_REDIS = {'host': 'lendi-redis.ny2tmo.0001.apse2.cache.amazonaws.com', 'port': 6379}
AWS_EC2_RULE_ENGINE = '10.0.1.230'


