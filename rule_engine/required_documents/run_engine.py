#!/Users/localuser/anaconda/bin python
import sys
if 'linux' in sys.platform():
    sys.path.append("/Users/localuser/Workspace/lendi-ai")
import config
import logging
from durable.lang import *
from main_rules import documents_ruleset
from main_rules import validation_ruleset

#Get the LOGGER
LOGGER = logging.getLogger("root")

with select('validate_required_documents'):

    @when_start
    def on_start(host):
        LOGGER.info('staring validate documents rules')


with select('required_documents'):

    @when_start
    def on_start(host):
            LOGGER.info('staring required documents rules')

#run_all([config.AWS_REDIS],host_name = config.AWS_EC2_RULE_ENGINE )
run_all()