#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import sys

range_low = [0]
range_high = [1]
range_epsilon = [0.01]

#MITMPROXY_SCRIPT = "proxy.py"
MITMPROXY_SCRIPT = "baseline_proxy.py"
WEBDRIVER_SCRIPT = "webdriver.py"


def modify_proxy_script(low, high, epsilon, original_script_path, i):
    temp_script_path = original_script_path + ".temp"

    with open(original_script_path, 'r') as f:
        content = f.read()

    content = content.replace("low = 0", f"low = [{low}]")
    content = content.replace("high = 1", f"high = [{high}]")
    content = content.replace("epsilon = 0.01", f"epsilon = [{epsilon}]")
    content = content.replace("i = 1", f"i = {i}")

    with open(temp_script_path, 'w') as f:
        f.write(content)

    return temp_script_path


def run_experiment(low, high, epsilon, i):
    temp_script_path = modify_proxy_script(low, high, epsilon, MITMPROXY_SCRIPT, i)
    proxy_process = subprocess.Popen([sys.executable, temp_script_path])

    time.sleep(5)

    try:
        subprocess.run([sys.executable, WEBDRIVER_SCRIPT],
                       check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error {e.returncode}")
    finally:
        proxy_process.send_signal(signal.SIGTERM)
        proxy_process.wait()

        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)


def main():
    current_experiment = 0

    for i in range(1, 10):
        for low in range_low:
            for high in range_high:
                for epsilon in range_epsilon:
                    current_experiment += 1
                    run_experiment(low, high, epsilon, i)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
