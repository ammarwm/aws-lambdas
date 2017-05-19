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

run_all()
