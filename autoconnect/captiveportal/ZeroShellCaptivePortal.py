from requests import *
from captiveportal.CaptivePortalHandler import CaptivePortalHandler


class ZeroShellCaptivePortal(CaptivePortalHandler):

    def __init__(self):
        CaptivePortalHandler.__init__(self, "text", "Authenticator")
        self.domain_name = None
        self.domains = []

    def try_to_connect(self):
        resp = request(method='GET', url="http://clients3.google.com/generate_204")
        html = resp.text
        input_exist = self.find_input_fields(html)
        if input_exist:
            url = resp.url.split("?", 1)[0]
            f = open("resources/credentials")

            for domain in self.domains:
                for line in f:
                    credentials = line.strip().split(",")
                    username = credentials[0]
                    password = credentials[1]
                    realm = domain
                    zscp_redirect = "_:::_"
                    print(username, password, realm)

                    params = {self.username_field_name: username, self.password_field_name: password, self.domain_name: realm,
                              'Section': 'CPAuth', 'Action': 'Authenticate', 'ZSCPRedirect': zscp_redirect}
                    resp = get(url, params=params)
                    html = resp.text

                    if 'Access Denied' in html:
                        print("Wrong username or password")

                    else:
                        authkey = self.find_token(html)
                        if authkey is not None:
                            params = {self.username_field_name: username, self.password_field_name: password, self.domain_name: realm,
                                      'Authenticator': authkey, 'Section': 'CPGW', 'Action': 'Connect', 'ZSCPRedirect': zscp_redirect}
                            resp = get(url, params=params)

                            params = {self.username_field_name: username, self.password_field_name: password, self.domain_name: realm,
                                      'Authenticator': authkey, 'Section': 'ClientCTRL', 'Action': 'Connect',
                                      'ZSCPRedirect': zscp_redirect}
                            resp = get(url, params=params)

                            resp = request(method='GET', url="http://clients3.google.com/generate_204", allow_redirects=False)
                            if resp.status_code == 204:
                                print("Successfully connected!")
                                return True
                            else:
                                print("Unable to connect!")
                                return False
                        else:
                            print("No authentication key")
        else:
            print("Unable to connect!")
            return False

    def find_input_fields(self, html_content):
        found = CaptivePortalHandler.find_input_fields(self, html_content)
        form = self.parser.getElementsByTagName("form")
        tag_collection = form.getElementsByTagName("select")
        if len(tag_collection) > 0:
            select = tag_collection[0]
            self.domain_name = select.name
            for option in select:
                self.domains.append(option.value)
        return found and self.domain_name is not None
