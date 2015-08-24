import re
import urllib
import urllib2

from cookielib import CookieJar, DefaultCookiePolicy

class NetflixConnection(object):
    login_url = 'https://www.netflix.com/Login'
    viewing_activity_url = 'https://account.netflix.com/WiViewingActivity'
    search_url ="http://www.netflix.com/api/shakti/305c8638/pathEvaluator?withSize=true&materialize=true&model=harris&fallbackEsn=NFCDCH-MC-"
    cookie_policy = \
        DefaultCookiePolicy(rfc2965=True,
                            strict_ns_domain=DefaultCookiePolicy.DomainStrict)

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cj = CookieJar(self.cookie_policy)
        self.opener = urllib2.build_opener(urllib2.HTTPSHandler,
                                      urllib2.HTTPCookieProcessor(self.cj))

    def login(self):
        res = self.opener.open(self.login_url)
        data = res.read()
        results = re.search('name="authURL".*?value="(?P<authURL>.*?)"', data)
        print "Login results %s" % (results.group())
        if results is None:
            print "Login failed.  No authURL token found in Login page"
            return False

        self.authURL = results.group('authURL')
        form_data = {'email': self.email,
                     'password': self.password,
                     'authURL': self.authURL}
        post_data = urllib.urlencode(form_data)

        req = urllib2.Request(res.url, post_data)

        res = self.opener.open(req)
        if 'signup' in res.url:
            print "Login failed.  Not sure why"
            return False

        return True

    def search_film(self, film):
        form_data = {'all': 'true'}
        post_data = """{"paths":[["search","titanic","person",{"from":0,"to":20},"person","summary"],["search","titanic","person",{"from":0,"to":20},"referenceId"],["search","titanic","person",["summary","reference","trackId"]]],"authURL":"%s"}""" % (self.authURL)

        print "post data", post_data

        req = urllib2.Request(self.search_url, post_data)

        res = self.opener.open(req)

        return res.read()

    def search_dvd(self, film):
        req = urllib2.Request("http://dvd.netflix.com/Search?oq=&ac_posn=&search_submit=&v1=charade")

        res = self.opener.open(req)

        return res.read()

    # TODO: refactor into common dispatch method
    def get_viewing_activity(self):
        form_data = {'all': 'true'}
        post_data = urllib.urlencode(form_data)

        req = urllib2.Request(self.viewing_activity_url, post_data)

        res = self.opener.open(req)

        return res
