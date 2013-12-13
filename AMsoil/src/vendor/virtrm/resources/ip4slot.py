from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import validates, relationship, backref

import inspect

from utils.commonbase import Base, db_session
from utils.ip4utils import IP4Utils


'''@author: SergioVidiella'''

class Ip4Slot(Base):
    """Ip4Slot Class."""

    __tablename__ = 'vt_manager_ip4slot'

    id = Column(Integer, autoincrement=True, primary_key=True)
    ip = Column(String(15), nullable=False)
    ipRange_id = Column(Integer, ForeignKey('vt_manager_ip4range.id'))
    ipRange = relationship('Ip4Range')
    isExcluded = Column(TINYINT(1))
    comment = Column(String(1024))

    @staticmethod
    def constructor(ipRange, ip, excluded, comment=""):
    	self = Ip4Slot()
	try:
	    #check IP
	    IP4Utils.checkValidIp(ip)
            self.ip = ip
            self.isExcluded = excluded
            self.ipRange = ipRange
            self.comment = comment
	    db_session.add(self)
	    db_session.commit()
	except Exception as e:
	    raise e
        return self

    '''Getters'''
    def isExcludedIp(self):
    	return self.isExcluded

    def getLockIdentifier(self):
    	#Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def getIp(self):
	return self.ip
    
    def getNetmask(self):
   	return self.ipRange.getNetmask()
        
    def getGatewayIp(self):
 	return self.ipRange.getGatewayIp()
    
    def getDNS1(self):
        return self.ipRange.getDNS1()
        
    def getDNS2(self):
        return self.ipRange.getDNS2()

    '''Validators'''
    @validates('ip')
    def validate_ip(self, key, ip):
        try:
            IP4Utils.checkValidIp(ip)
            return ip
        except Exception as e:
            raise e

    ''' Factories '''
    @staticmethod
    def ipFactory(ipRange, ip):
        return Ip4Slot.constructor(ipRange, ip, False, "")

    @staticmethod
    def excludedIpFactory(ipRange, ip, comment):
        return MacSlot.constructor(ipRange, ip, True, comment)
