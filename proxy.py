import re
import string
import random

import mitmproxy.http
import numpy as np

# low = range_low[4]
# high = range_high[1]
# epsilon = range_epsilon[2]

low = 0
high = 1
epsilon = 0.01
i = 1


class ModifyResponseAddOn:

    def change_cookies(self, cookie):
        newcookie = ''
        for char in cookie:
            if char.isalpha():
                new_char = random.choice(string.ascii_lowercase if char.islower() else string.ascii_uppercase)
            elif char.isdigit():
                new_char = random.choice(string.digits)
            else:
                new_char = char
            newcookie += new_char

        cookie = newcookie
        with open("newvalues.txt", 'a') as f:
            f.write(str(newcookie) + "\n")
        return cookie

    def replace_cookie_values(self, original_cookies, anonymized_cookies):
        anonymized_values_map = {name: value for name, value in anonymized_cookies}

        updated_cookies = []
        for cookie_str in original_cookies:
            parts = cookie_str.split(';', 1)
            name_value = parts[0]
            attributes = parts[1] if len(parts) > 1 else ""

            cookie_name = name_value.split('=')[0]

            if cookie_name in anonymized_values_map:
                new_cookie = f"{cookie_name}={anonymized_values_map[cookie_name]}"

                if attributes:
                    new_cookie += ';' + attributes

                updated_cookies.append(new_cookie)
            else:
                updated_cookies.append(cookie_str)

        return updated_cookies

    def exponential_calculations(self, epsilon, cookies):
        pattern = (r"[a-zA-Z0-9\-%/.]+")
        utility_change_values = []
        utility_keep_values = []

        for cookie in cookies:
            if isinstance(cookie, tuple):
                cookie = cookie[0]
            if bool(re.match(pattern, cookie[1])) or "id" in cookie[1].lower() or "id" in cookie[0].lower():
                utility_change = low
                utility_keep = high
            else:
                utility_change = high
                utility_keep = low

            utility_change_values.append(utility_change)
            utility_keep_values.append(utility_keep)

        utility_change_avg = sum(utility_change_values)
        utility_keep_avg = sum(utility_keep_values)

        sensitivity = len(cookies)

        score_change = np.exp((utility_change_avg * epsilon) / (2 * sensitivity))
        score_keep = np.exp((utility_keep_avg * epsilon) / (2 * sensitivity))

        pchange = score_change / (score_change + score_keep)
        pkeep = score_keep / (score_change + score_keep)

        return pchange, pkeep

    def process_cookies(self, cookies):
        try:
            pchange, pkeep = self.exponential_calculations(epsilon, cookies)
            probs = [pchange, pkeep]
            choices = ["change", "keep"]
            choice = np.random.choice(choices, 1, p=probs)
            if choice == "change":
                for i in range(len(cookies)):
                    cookies[i][1] = self.change_cookies(cookies[i][1])
            return cookies
        except Exception as e:
            print(f'The error is {e}')
            return cookies

    def request(self, flow: mitmproxy.http.HTTPFlow):

        cookies = flow.request.cookies.fields

        host = flow.request.host

        referer = dict(flow.request.headers.fields).get(b'referer')

        if referer is not None and host not in str(referer):
            with open(f"results/experiments/{str(low)}_{str(high)}_{str(epsilon)}_{str(i)}"
                      f"_paths.txt", 'a') as f:
                f.write("*** " + str(host) + " ***" + "\n" + "\n")
                f.write(str(referer) + ": " + str(flow.request.path) + " with " + str(referer) + "\n")

            if cookies and cookies is not None:
                new_cookies = self.process_cookies(flow.request.cookies.fields)
                try:
                    flow.request.cookies.fields = new_cookies
                except Exception as e:
                    print(f"The error is '{e}'")

    def response(self, flow: mitmproxy.http.HTTPFlow):

        set_cookies = flow.response.headers.get_all("Set-Cookie")

        host = flow.request.host
        referer = dict(flow.request.headers.fields).get(b'referer')
        if referer is None or host in str(referer):
            pass
        else:
            if flow.request.cookies.fields and flow.request.cookies.fields is not None:
                with open(f"results/experiments/{str(low)}_{str(high)}_{str(epsilon)}_{str(i)}"
                          f"_cookietest.txt", 'a') as f:
                    f.write("*** " + str(host) + " ***" + "\n" + "\n")
                    for cookie in flow.request.cookies.fields:
                        f.write(str(referer) + ": " + str(cookie) + "\n")
            if set_cookies and set_cookies is not None:
                with open(f"results/experiments/{str(low)}_{str(high)}_{str(epsilon)}_{str(i)}"
                          f"_cookietest.txt", 'a') as f:
                    f.write("*** " + str(host) + " ***" + "\n" + "\n")
                    for cookie in set_cookies:
                        f.write(str(referer) + ": " + str(cookie) + "\n")
                cookies = []
                for set_cookie in set_cookies:
                    parts = set_cookie.split(';', 1)
                    cookie = parts[0].split('=', 1)
                    cookies.append(cookie)
                cookies = tuple(cookies)

                new_cookies = self.process_cookies(cookies)
                replced_cookies = self.replace_cookie_values(set_cookies, new_cookies)
                flow.response.headers.pop("Set-Cookie")

                for cookie in replced_cookies:
                    tuple_cookie = ("set-cookie".encode(), cookie.encode())
                    flow.response.headers.fields += (tuple_cookie,)


addons = [ModifyResponseAddOn()]

if __name__ == '__main__':
    from mitmproxy.tools.main import mitmdump

    mitmdump(['-s', __file__])
