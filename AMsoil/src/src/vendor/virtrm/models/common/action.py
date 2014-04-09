from sqlalchemy.orm import validates
from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import uuid
import logging 

logging=amsoil.core.log.getLogger('Action')

'''@author: SergioVidiella'''

class Action(db.Model):
    """Class to store actions"""
    
    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'action'
    __table_args__ = {'extend_existing':True}
    
    '''Action status Types'''
    QUEUED_STATUS = "QUEUED"
    ONGOING_STATUS= "ONGOING"
    SUCCESS_STATUS  = "SUCCESS"
    FAILED_STATUS   = "FAILED"
    
    __possible_status = (QUEUED_STATUS, ONGOING_STATUS, SUCCESS_STATUS, FAILED_STATUS)
    
    '''Action type Types'''
    ## Monitoring
    # Servers
    MONITORING_SERVER_VMS_TYPE="listActiveVMs"

    __monitoring_types = (
        # Server
        MONITORING_SERVER_VMS_TYPE,
    )

    # VMs
    ## Provisioning 
    # VM provisioning actions        
    PROVISIONING_VM_CREATE_TYPE = "create"
    PROVISIONING_VM_START_TYPE = "start"
    PROVISIONING_VM_DELETE_TYPE = "delete"
    PROVISIONING_VM_STOP_TYPE = "hardStop"
    PROVISIONING_VM_REBOOT_TYPE = "reboot"

    __provisioning_types = (
        # VM
        PROVISIONING_VM_CREATE_TYPE,
        PROVISIONING_VM_START_TYPE,
        PROVISIONING_VM_DELETE_TYPE,
        PROVISIONING_VM_STOP_TYPE,
        PROVISIONING_VM_REBOOT_TYPE,
    )
    
    '''All possible types '''
    __possible_types = (
        # Monitoring
        # Server
        MONITORING_SERVER_VMS_TYPE,

        ## Provisioning
        # VM
        PROVISIONING_VM_CREATE_TYPE,
        PROVISIONING_VM_START_TYPE,
        PROVISIONING_VM_DELETE_TYPE,
        PROVISIONING_VM_STOP_TYPE,
        PROVISIONING_VM_REBOOT_TYPE,
    )
    
    '''General parameters'''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    type = db.Column(db.String(16), nullable=False, default="")
    uuid = db.Column(db.String(512), nullable=False, default="")
    callback_url = db.Column("callBackUrl", db.String(200), nullable=False, default="")
    status = db.Column(db.String(16), nullable=False, default="")
    description = db.Column(db.String(2048), default="")
    object_uuid = db.Column("objectUUID", db.String(512), default="")
    
    '''Public methods'''
    @staticmethod
    def constructor(a_type,status,object_uuid=None,description=""):
        self = Action()
        self.set_type(a_type)
        self.set_status(status)
        self.set_uuid(uuid.uuid4())
        if not object_uuid == None:
            self.set_object_uuid(object_uuid)
        if not description == "":
            self.setDescription(description)
        return self
    
    def destroy(self):
        db.session.delete(self)
        db.session.commit()
    
    def check_action_is_present_and_unique(self):
        if len(Action.query.filter_by(uuid = self.uuid).all()) != 0:
            logging.error("Action with the same uuid already exists")
            raise Exception("Action with the same uuid already exists")
    
    '''Validators'''
    @validates('type')
    def validate_type(self, key, type):
        if type not in self.__possible_types:
            raise Exception("Action type not valid")
        return type


    @validates('status')
    def validate_status(self, key, status):
        if status not in self.__possible_status:
            raise Exception("Status not valid")
        return status

    '''Getters and setters'''
    @staticmethod
    def get_and_check_action_by_uuid(uuid):
        actions = Action.query.filter_by(uuid = uuid).all()
        if len(actions) ==  1:
            return actions[0]
        elif len(actions) == 0:
            logging.error("Action with uuid %s does not exist" % uuid)
            raise Exception("Action with uuid %s does not exist" % uuid)
        elif len(actions) > 1:
            logging.error("Action with uuid %s does not exist" % uuid)
            raise Exception("More than one Action with uuid %s" % uuid)
    
    def set_status(self, status):
        if status not in self.__possible_status:
            raise Exception("Status not valid")
        self.status = status
        db.session.add(self)
        db.session.commit()
    
    def get_status(self):
        return self.status

    def set_type(self, type):
        if type not in self.__possibleTypes:
            raise Exception("Action type not valid")
        self.type = type
        db.session.add(self)
        db.session.commit()
    
    def get_type(self):
        return self.type
    
    def is_provisioning_type(self):
        return self.type in self.__provisioning_types
    
    def is_monitoring_type(self):
        return self.type in self.__monitoring_types
    
    def set_description(self, description):
        self.description = description
        db.session.add(self)
        db.session.commit()
    
    def get_description(self):
        return self.descripion
    
    def set_uuid(self, uuid):
        self.uuid = uuid
        db.session.add(self)
        db.session.commit()
    
    def get_uuid(self):
        return self.uuid
    
    def set_callback_url(self, url):
        self.url = url
        db.session.add(self)
        db.session.commit()
    
    def get_callback_url(self):
        return self.url
    
    def set_object_uuid(self, obj_uuid):
        self.object_uuid = obj_uuid
        db.session.add(self)
        db.session.commit()
        
    def get_object_uuid(self):
        return self.object_uuid
