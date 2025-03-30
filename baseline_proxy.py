import mitmproxy
from mitmproxy import http

i = 1


class ModifyResponseAddOn:

    def __init__(self):
        self.cache = {}

    def request(self, flow: mitmproxy.http.HTTPFlow):

        host = flow.request.host
        referer = dict(flow.request.headers.fields).get(b'referer')

        if referer is not None and host not in str(referer):
            with open(f"results/blocked/paths_{str(i)}.txt", 'a') as f:
                f.write("*** " + str(host) + " ***" + "\n" + "\n")
                f.write(str(referer) + ": " + str(flow.request.path) + " with " + str(referer) + "\n")

    def response(self, flow: mitmproxy.http.HTTPFlow):

        host = flow.request.host
        set_cookies = flow.response.headers.get_all("Set-Cookie")
        referer = dict(flow.request.headers.fields).get(b'referer')
        if referer is None or host in str(referer):
            pass
        else:
            if flow.request.cookies.fields and flow.request.cookies.fields is not None:
                with open(f"results/blocked/"
                          f"cookietest_{str(i)}.txt", 'a') as f:
                    f.write("*** " + str(host) + " ***" + "\n" + "\n")
                    for cookie in flow.request.cookies.fields:
                        f.write(str(referer) + ": " + str(cookie) + "\n")
            if set_cookies and set_cookies is not None:
                if flow.request.cookies.fields and flow.request.cookies.fields is not None:
                    with open(f"results/blocked/"
                              f"cookietest_{str(i)}.txt", 'a') as f:
                        f.write("*** " + str(host) + " ***" + "\n" + "\n")
                        for cookie in set_cookies:
                            f.write(str(referer) + ": " + str(cookie) + "\n")


addons = [ModifyResponseAddOn()]

if __name__ == '__main__':
    from mitmproxy.tools.main import mitmdump

    mitmdump(['-s', __file__])
