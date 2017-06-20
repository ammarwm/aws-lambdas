import abc

class BaseAction(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, action_type):
        self.action_type = action_type
        self.result = None

    @abc.abstractmethod
    def do(self):
        raise NotImplementedError
