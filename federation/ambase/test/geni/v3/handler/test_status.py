from federation.ambase.src.geni.exceptions.manager import GENIExceptionManager
from federation.ambase.src.geni.v3.handler.handler import GeniV3Handler
from federation.ambase.test.utils import testcase
from federation.ambase.test.utils.mockcredentialmanager import MockCredentialManager
from federation.ambase.test.utils.mockdelegate import MockDelegate
from federation.ambase.test.utils.mockrspecmanager import MockRSpecManager


class TestStatus(testcase.TestCase):
    """ Testing very basic behaviour to see 
        whether the Handler is able to respond
        with error_results or success_results  
    """
    
    def setUp(self):
        self.handler = GeniV3Handler()
        self.handler.set_credential_manager(MockCredentialManager())
        self.handler.set_rspec_manager(MockRSpecManager())
        self.handler.set_delegate(MockDelegate())
        self.handler.set_geni_exception_manager(GENIExceptionManager()) #is too simple to mock it
        
    def tearDown(self):
        self.handler = None
        
    def test_should_fail_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        value = self.handler.Status([], [], {})
        self.assertEquals(GENIExceptionManager.FORBIDDEN, value.get('code').get('geni_code'))
    
    def test_should_fail_when_worng_status(self):
        self.handler.set_delegate(MockDelegate(False))
        value = self.handler.Status([], [], {})
        self.assertEquals(GENIExceptionManager.ERROR, value.get('code').get('geni_code'))
        
    def test_should_status(self):
        value = self.handler.Status([], [], {})
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
    
if __name__ == "__main__":
    # Allows to run in stand-alone mode
    testcase.main()