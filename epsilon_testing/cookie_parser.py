import re
import string
import random
import sys

import pandas as pd
import numpy as np

sum_c = 0
total = 0


def parse_cookies(file_path):
    cookies_by_request = []
    current_domain = None
    current_cookies = []

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('***'):
                if current_domain and current_cookies:
                    cookies_by_request.append((current_domain, current_cookies))
                    current_cookies = []

                current_domain = line.strip('* \n')
                continue

            if current_domain and "b'" in line:
                try:
                    match = re.search(r"b'([^']+)':\s+\['([^']+)',\s+'([^']+)']", line)
                    if match:
                        domain, name, value = match.groups()
                        current_cookies.append({
                            'domain': domain,
                            'name': name,
                            'value': value
                        })
                    else:
                        parts = line.strip().split("': ['")
                        if len(parts) >= 2:
                            domain = parts[0].strip("b'")
                            cookie_parts = parts[1].strip("']").split("', '")
                            if len(cookie_parts) >= 2:
                                name, value = cookie_parts[0], cookie_parts[1]
                                current_cookies.append({
                                    'domain': domain,
                                    'name': name,
                                    'value': value
                                })
                except Exception:
                    pass

    if current_domain and current_cookies:
        cookies_by_request.append((current_domain, current_cookies))

    return cookies_by_request


def create_cookies_dataframe(cookies_list):
    rows = []

    for http_request, cookies in cookies_list:
        for cookie in cookies:
            rows.append({
                'http_request': http_request,
                'cookie_domain': cookie['domain'],
                'name': cookie['name'],
                'value': cookie['value']
            })

    df = pd.DataFrame(rows)
    return df


def exponential_calculations(high, low, epsilon, cookies):

    utility_change_values = []
    utility_keep_values = []

    for cookie in cookies:
        name = cookie['name']
        value = cookie['value']

        if bool(re.match(r'[a-zA-Z0-9\-%/.]+', value)) or "id" in value.lower() or "id" in name.lower():
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


def change_cookies(cookie):
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
    return cookie


def process_cookies(low, high, epsilon, cookies):
    try:
        anon = 0
        total = 0
        pchange, pkeep = exponential_calculations(high, low, epsilon, cookies)
        probs = [pchange, pkeep]
        choices = ["change", "keep"]
        choice = np.random.choice(choices, 1, p=probs)
        if choice == "change" and pkeep > pchange:
            anon += 1
            total += 1
        elif choice == "keep" and pkeep > pchange:
            total += 1
        return cookies, anon, total
    except Exception as e:
        return cookies


def process_cookies_by_request(cookies_list, high, low, epsilon):
    http_total = 0
    anonymized = 0
    for http_request, cookies in cookies_list:
        cookies, anon, total = process_cookies(low, high, epsilon, cookies)
        http_total += total
        anonymized += anon

    return anonymized / http_total


def main(file_path="responses.txt", high=100, low=2, epsilon=1):
    cookies_list = parse_cookies(file_path)
    cookies_df = create_cookies_dataframe(cookies_list)
    results = process_cookies_by_request(cookies_list, high, low, epsilon)

    return cookies_df, results


if __name__ == "__main__":
    open('averages.txt', 'w').close()

    high = [1]
    low = [0]
    epsilon = [0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1]
    paths = ["cookietest.txt"]

    total_iterations = 100 * 9
    completed = 0
    bar_length = 50

    for l in range(1):
        for k in range(1):
            for i in range(9):
                open('averages.txt', 'w').close()
                for j in range(100):
                    cookies_df, results = main(file_path=paths[l], high=high[0], low=low[0], epsilon=epsilon[i])
                    with open(f"averages.txt", 'a') as f:
                        f.write(str(results) + "\n")
                    completed += 1
                    percent = completed / total_iterations
                    filled_length = int(bar_length * percent)
                    bar = '█' * filled_length + '-' * (bar_length - filled_length)

                    # Print progress bar
                    sys.stdout.write(f'\rProgress: |{bar}| {percent:.1%} Complete ({completed}/{total_iterations})')
                    sys.stdout.flush()
                with open(f"analyze_averages.py") as script:
                    exec(script.read())
