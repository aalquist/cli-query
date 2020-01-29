import requests
import time
import sys

from threading import Thread

class Analytics():

    disable = False

    @staticmethod
    def disableAnalytics():
        Analytics.disable = True

    @staticmethod
    def enableAnalytics():
        Analytics.disable = False

    def __init__(self):
        pass

    def send_analytics(self, path, debug):

        try:
            url = "https://github-aalquist-cli-query-analytics.akamaized.net/{}".format(path)
            response = requests.get(url, timeout=.200, allow_redirects=False)

            if debug == True:
                code = response.status_code
                print("analytics sent {} and got HTTP code {}".format( url, code ), file=sys.stderr )

        except Exception:
            pass

    def no_send(self, path, debug):
        pass

    def async_send_analytics(self, path="empty.json", debug=False ):

        if Analytics.disable == True:
            t = Thread(target=self.no_send, args=(path,debug), daemon=True)
            t.start()
            return t

        else:    
            t = Thread(target=self.send_analytics, args=(path,debug), daemon=True)
            t.start()
            return t

    
    


