import sys
import os
from StringIO import StringIO
from agent.utils.xml import vtRspecInterface

'''
    @author: msune, lber
    
    Parses the incoming XML to the data model
'''

'''
    Parsing Exception 
'''
class XMLParsingException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


'''
    XML Query Parser class 
'''
class XmlParser(object):

    @staticmethod
    def parse_xml(rawXML):
        print "Parsing XML..."
        try:
            object = vtRspecInterface.parseString(rawXML)
            print "Parsing of XML concluded without significant errors."
            return object
        except Exception as e:
            #TODO: add more info
            print >> sys.stderr, e
            raise XMLParsingException("Could not parse parse XML; traceback\n")


'''
    XML Query Crafter class 
'''
class XmlCrafter(object):
    @staticmethod
    def craft_xml(XMLclass):
        print "Crafting Model..."
        try:
            xml = StringIO()
            xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            XMLclass.export(xml, level=0)
            print "Crafting of the XML Class concluded without significant errors."
            xmlString = xml.getvalue()
            xml.close()
            return xmlString
        except Exception as e:
            #TODO: add more info
            print >> sys.stderr, e
            raise XMLParsingException("Could not craft Model; traceback\n")

def xml_file_to_string(file):
    try:        
        f = open(file, 'r')
        xml =  f.read()
        f.close()
        #print xml
        return xml
    except Exception:
        print "Oops!  File not found"

class XmlHelper(object):
    #TODO: improve this by creating a proper constructor    
    @staticmethod
    def get_simple_action_specific_query(type, server_uuid):
        with open(os.path.dirname(__file__)+'/xml/queryprovisioning.xml','r') as open_prov:
            simple_rspec =  XmlHelper.parse_xml_string(open_prov.read())
        if type == 'stop': type = 'hardStop'
        simple_rspec.query.provisioning.action[0].type_ = type
        simple_rspec.query.provisioning.action[0].server.uuid = server_uuid
        return simple_rspec
#        if type == 'start':
#            simple_rspec =  XmlHelper.parse_xml_string(open(os.path.dirname(__file__)+'/xml/queryStart.xml','r').read())
#        if type == 'delete':
#            simple_rspec =  XmlHelper.parse_xml_string(open(os.path.dirname(__file__)+'/xml/queryDelete.xml','r').read())            
#        if type == 'stop':
#            simple_rspec =  XmlHelper.parse_xml_string(open(os.path.dirname(__file__)+'/xml/queryStop.xml','r').read())
#        if type == 'reboot':
#            simple_rspec =  XmlHelper.parse_xml_string(open(os.path.dirname(__file__)+'/xml/queryReboot.xml','r').read())
#        return simple_rspec
    
    @staticmethod
    def get_processing_response(status, action,  description, ):
        with open(os.path.dirname(__file__)+'/xml/emptyresponse.xml','r') as open_resp:
            simple_rspec =  XmlHelper.parse_xml_string(open_resp.read())
        simple_rspec.response.provisioning.action[0].status = status
        simple_rspec.response.provisioning.action[0].description = description
        #XXX:This is because the ActionController sends a dummy, None, dummy request
        if action != None: 
            simple_rspec.response.provisioning.action[0].id = action.id
            simple_rspec.response.provisioning.action[0].server.uuid = action.server.uuid
        return simple_rspec
    
    @staticmethod
    def get_simple_action_query(action=None):
        with open(os.path.dirname(__file__)+'/xml/simpleactionquery.xml','r') as open_action:
            simple_rspec =  XmlHelper.parse_xml_string(open_action.read())
        if action:
            simple_rspec.query.provisioning.action[0] = action
        return simple_rspec
    
    @staticmethod
    def get_simple_information():
        with open(os.path.dirname(__file__)+'/xml/simplelistresources.xml','r') as open_resources:
            simple_rspec =  XmlHelper.parse_xml_string(open_resources.read())
        return simple_rspec
    
    @staticmethod
    def get_list_active_vms_query():
        with open(os.path.dirname(__file__)+'/xml/listactivevmsquery.xml','r') as open_vms:
            simple_rspec =  XmlHelper.parse_xml_string(open_vms.read())
        return simple_rspec
    
    @staticmethod
    def craft_simple_action_query(simple_rspec, status, description):
        simple_rspec.query.provisioning.action[0].status = status
        simple_rspec.query.provisioning.action[0].description = description
        return craft_xml_class(simple_rspec)
    
    @staticmethod
    def parse_xml_string(xml):
        return XmlParser.parse_xml(xml)
    
    #def parse_xml_stringResponse(xml):
    #    return XmlResponseParser.parse_xml(xml)
    
    @staticmethod
    def craft_xml_class(xml_class):
        return XmlCrafter.craft_xml(xml_class)