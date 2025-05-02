import enum
from enum import Enum

class UserType(Enum):
    USER='USER'
    SIGNAL_PROVIDER='SIGNAL_PROVIDER'
   
    @classmethod
    def choices(cls):
        return tuple((i.name,i.value) for i in cls)


class GENDERCHOICE(Enum):
    Male='Male'
    Female='Female'
    Others='Others'
   
    @classmethod
    def choices(cls):
        return tuple((i.name,i.value) for i in cls)
