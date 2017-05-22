import sys
import config
import logging
from durable.lang import *
import payslip

#Get the LOGGER
LOGGER = logging.getLogger("root")

with select('payslip'):
    @when_start
    def on_start(host):
        LOGGER.info('staring payslip rules')

#run_all([config.AWS_REDIS],host_name = config.AWS_EC2_RULE_ENGINE )
run_all(host_name='192.168.25.214')