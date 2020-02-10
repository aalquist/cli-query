
from bin.send_analytics import Analytics 

from bin.tests.unittest_utils import CommandTester, MockResponse

import unittest
from unittest.mock import patch

class Analytics_Test(unittest.TestCase):


    @patch('requests.Session')
    def testSendingAnalytics(self, mockSessionObj):

        session = mockSessionObj()
        response = MockResponse()

        response.appendResponse("test response")
        response.appendResponseCode(000)

        session.get.return_value = response
        
        self.assertEquals(0,session.get.call_count)
        self.assertEquals(0,session.get.call_count)

        obj = Analytics()
        obj.setSession(session)

        obj.disableAnalytics()
        t = obj.async_send_analytics(debug=False)
        t.join()
        self.assertEquals(0,session.get.call_count)

        obj.enableAnalytics()
        t = obj.async_send_analytics(debug=False)
        t.join()

        self.assertEquals(1,session.get.call_count)

        obj.enableAnalytics()
        t = obj.async_send_analytics(debug=True)
        t.join()

        self.assertEquals(2,session.get.call_count)