import logging

import pg8000 as db

from config import DATABASES

#Get the LOGGER
LOGGER = logging.getLogger("root")


class Database:
    def __init__(self, db_name='lendi_ai'):
        self.db_name = db_name
        self.conn = None
        self.cur = None


    def connect(self):
        try:
            self.conn = db.connect(**DATABASES[self.db_name])
            self.cur = self.conn.cursor()
        except db.Error:
            LOGGER.exception("Error in establishing connection to lendi_db error" )

    def execute(self, command, type='r'):
        try:
            self.cur.execute(command)
            if type == 'w':
                self.conn.commit()
        except db.Error as error:
            LOGGER.exception("Data base error to Lendi db")
            self.conn.rollback()

    def executemany(self, command, data):
        try:
            self.cur.executemany(command, data)
            self.conn.commit()
        except db.Error as error:
            LOGGER.exception("Data base error to Lendi db")
            self.conn.rollback()

    def get_result(self, type='one'):
        rows = []
        result = []
        try:
            if type == 'one':
                rows = self.cur.fetchone()
            elif type == 'all':
                rows = self.cur.fetchall()
        except db.Error as error:
            LOGGER.exception('No result returned')
            return result
        cols = [a[0].decode("utf-8") for a in self.cur.description]

        for row in rows:
            result.append({a: b for a, b in zip(cols, row)})
        #import pdb;pdb.set_trace()
        return result

    def close(self):
        if self.conn:
            self.cur.close()
            self.conn.close()

if __name__ == '__main__':
    db_ = Database()
    db_.connect()
    db_.execute('select * from required_documents.payslip_master limit 10')
    print(db_.get_result('all'))