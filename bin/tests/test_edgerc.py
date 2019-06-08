# Copyright 2017 Akamai Technologies, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import os
import sys
from bin.credentialfactory import CredentialFactory



class EdgeRCTest(unittest.TestCase):


    def test_load(self):
        factory = CredentialFactory()
        #update to support current filename

        
        basedir = os.path.abspath(os.path.dirname(__file__))
        edgeRc = "{}/other/.dummy_edgerc".format(basedir)
        duplicateEdgeRc = "{}/other/.duplicate.dummy_edgerc".format(basedir)

        context = factory.load(edgeRc, "other", None)
        self.assertEqual("akab-MjIzMTE5ODM5NTQ1MGRkNTczNmIyZjk0.luna.akamaiapis.net", context.base_url )
        self.assertEqual("", context.account_key )
        self.assertIsNotNone(context.session)

        context = factory.load(edgeRc, None, None)
        self.assertEqual("akab-DjIzMTE5ODM5NTQ1MGRkNTczNmIyZjk0.luna.akamaiapis.net", context.base_url )
        self.assertEqual("", context.account_key )
        self.assertIsNotNone(context.session)

        context = factory.load(edgeRc, "default", None)
        self.assertEqual("akab-DjIzMTE5ODM5NTQ1MGRkNTczNmIyZjk0.luna.akamaiapis.net", context.base_url )
        self.assertEqual("", context.account_key )
        self.assertIsNotNone(context.session)

        context = factory.load(edgeRc, "other", "someKey")
        self.assertEqual("akab-MjIzMTE5ODM5NTQ1MGRkNTczNmIyZjk0.luna.akamaiapis.net", context.base_url )
        self.assertEqual("accountSwitchKey=someKey", context.account_key )
        self.assertIsNotNone(context.session)

        error = False
        try:
            context = factory.load(edgeRc, "missingSection", None)
            
        except ValueError:
            error = True
        
        self.assertTrue(error)

        os.environ['AKAMAI_EDGERC'] = duplicateEdgeRc
        context = factory.load(None, "duplicatesection", None)
        self.assertEqual("akab-DjIzMTE5ODM5NTQ1MGRkNTczNmIyZjk0.luna.akamaiapis.net", context.base_url )

        os.environ['AKAMAI_EDGERC'] = duplicateEdgeRc
        os.environ['AKAMAI_EDGERC_SECTION'] = "duplicatesection"
        
        context = factory.load(None, None, None)
        self.assertEqual("akab-DjIzMTE5ODM5NTQ1MGRkNTczNmIyZjk0.luna.akamaiapis.net", context.base_url )

        del os.environ['AKAMAI_EDGERC']
        del os.environ['AKAMAI_EDGERC_SECTION']
        
        


if __name__ == '__main__':
    unittest.main()