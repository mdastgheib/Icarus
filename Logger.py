# This class will be used to log data from the other classes
import datetime
import os
import logging
import sys

logger = logging.getLogger('Icarus Logger')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='log.properties', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s [%(asctime)s]'))
logger.addHandler(handler)

