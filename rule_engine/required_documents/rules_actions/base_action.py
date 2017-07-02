import abc
from config import DATABASES

class BaseAction(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, action_type):
        self.db_info = DATABASES['lendi_ai']
        self.action_type = action_type
        self.result = None

    @abc.abstractmethod
    def do(self):
        raise NotImplementedError
