from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

import winsound

df = pd.read_csv('top1m-2.csv')


def main():
    options = Options()
    options.accept_untrusted_certs = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    userdatadir = 'C:/Users/Admin/AppData/Local/Google/Chrome/User Data'
    options.add_argument(f"--user-data-dir={userdatadir}")
    driver = webdriver.Chrome(options=options)

    import time
    from selenium.common.exceptions import TimeoutException

    for value in df.values:
        try:
            url = "https://www." + str(value[1])
            driver.set_page_load_timeout(8)
            start_time = time.time()
            max_time_allowed = 17

            try:
                driver.get(url)
            except TimeoutException:
                driver.execute_script("window.stop();")

            time.sleep(0.8)

            current_url = driver.current_url
            while time.time() - start_time < max_time_allowed:
                time.sleep(0.7)

                if driver.current_url != current_url:
                    current_url = driver.current_url
                    start_time = time.time()

                page_state = driver.execute_script('return document.readyState;')
                if page_state == 'complete':
                    break

            if time.time() - start_time >= max_time_allowed:
                driver.execute_script("window.stop();")

            if int(value[0]) > 100:
                break

        except Exception as e:
            print(f"Error visiting {url}: {e}")
            try:
                driver.execute_script("window.stop();")
            except Exception as e:
                print(f"Error visiting {url}: {e}")
                pass
            continue

    freq = 2500
    dur = 500
    winsound.Beep(freq, dur)

    driver.quit()


if __name__ == "__main__":
    main()
