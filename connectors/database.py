import logging
try:
    import psycopg2 as db
except ImportError:
    import pg8000 as db
from sql_queries import sql_queries
from config import DATABASES

#Get the LOGGER
LOGGER = logging.getLogger("root")
LOG_HANDLER = logging.StreamHandler()
LOGGER.addHandler(LOG_HANDLER)
LOGGER.setLevel(logging.INFO)

class Database:
    def __init__(self):
        pass

    def connect(self):
        try:
            self.conn = db.connect(**DATABASES['lendi_ai'])
        except db.Error:
            LOGGER.exception("Error in handler() lendi_db error")
        return {}
        self.cur = self.conn.cursor()

    def execute(self, command):
        try:
            self.cur.execute(command)
        except db.Error:
            LOGGER.exception("Data base error to Lendi db")
        result = self.cur.fetchone()

    def close(self):
        if self.conn:
            self.cur.close()
            self.conn.close()
            