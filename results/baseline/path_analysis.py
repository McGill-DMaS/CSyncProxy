import re
import os
import glob
from collections import defaultdict


def extract_alphanumeric_from_path(path):
    all_strings = re.findall(r'[a-zA-Z0-9.%\-]{11,}', path)
    long_strings = [s for s in all_strings if len(s) > 9]
    return long_strings


def get_domain_root(domain):
    parts = domain.split('.')

    if len(parts) <= 1:
        return domain
    tlds = {'com', 'org', 'net', 'io', 'co', 'gov', 'edu', 'ca', 'uk', 'au', 'de', 'fr', 'jp', 'cn', 'in', 'br', 'ru'}
    if len(parts) >= 3 and parts[-2] in {'co', 'com', 'org', 'net', 'ac', 'gov', 'edu'}:
        if parts[-1] in {'uk', 'jp', 'au', 'nz', 'in'}:
            return parts[-3]

    if parts[-1] in tlds:
        return parts[-2]
    for i in range(len(parts) - 1, 0, -1):
        if parts[i] in tlds and i > 0:
            return parts[i - 1]
    if len(parts) >= 2:
        return parts[-2]

    return domain


def are_domains_truly_unique(domains):
    domain_roots = [get_domain_root(domain) for domain in domains]
    seen_roots = set()
    unique_roots = []
    truly_unique_roots = []
    for root in domain_roots:
        if root not in seen_roots:
            seen_roots.add(root)
            unique_roots.append(root)
    for root in unique_roots:
        if not any(root in r for r in truly_unique_roots):
            truly_unique_roots.append(root)
    return len(truly_unique_roots) > 1, unique_roots


def process_file(file_path):
    domain_strings = defaultdict(set)
    string_counter = defaultdict(int)
    string_domains = defaultdict(set)
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return domain_strings, string_counter, string_domains
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            lines = file.readlines()
            current_path = None
            for line in lines:
                line = line.strip()
                if line.startswith("b'") and ": /" in line:
                    parts = line.split(": /", 1)
                    if len(parts) >= 2:
                        path_part = "/" + parts[1].split(" with", 1)[0]
                        current_path = path_part
                elif line.startswith("***") and line.endswith("***"):
                    current_domain = line.strip("* ")
                    if current_path and current_domain:
                        alphanumeric_strings = extract_alphanumeric_from_path(current_path)
                        for string in alphanumeric_strings:
                            domain_strings[current_domain].add(string)
                            string_counter[string] += 1
                            string_domains[string].add(current_domain)
                        current_path = None
    except Exception as e:
        print(f"The error is: {e}")
    return domain_strings, string_counter, string_domains


def process_and_save_results(input_file):
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    domain_strings, string_counter, string_domains = process_file(input_file)
    cross_domain_strings = {s: domains for s, domains in string_domains.items() if len(domains) > 1}
    truly_unique_domain_strings = {}
    for string, domains in cross_domain_strings.items():
        is_truly_unique, unique_roots = are_domains_truly_unique(domains)
        if is_truly_unique and len(domains) > 1:
            truly_unique_domain_strings[string] = domains

    if not os.path.exists('test_crossdomains'):
        os.makedirs('test_crossdomains')

    truly_unique_file = os.path.join('test_crossdomains', f"{base_filename}_recurring_ids2.txt")
    with open(truly_unique_file, "w", encoding='utf-8') as unique_file:
        sorted_truly_unique = sorted(truly_unique_domain_strings.items(), key=lambda x: (-len(x[1]), x[0]))
        for string, _ in sorted_truly_unique:
            unique_file.write(f"ID: {string}\n")

    if truly_unique_domain_strings and len(sorted_truly_unique) > 0:
        top_count = min(3, len(sorted_truly_unique))
        for i, (string, domains) in enumerate(sorted_truly_unique[:top_count], 1):
            _, unique_roots = are_domains_truly_unique(domains)
    return len(cross_domain_strings), len(truly_unique_domain_strings)


def main():
    txt_files = glob.glob("*paths.txt")

    if not txt_files:
        return

    if not os.path.exists('test_crossdomains'):
        os.makedirs('test_crossdomains')

    total_processed = 0
    total_cross_domain = 0
    total_truly_unique = 0

    for txt_file in txt_files:
        cross_domain_count, truly_unique_count = process_and_save_results(txt_file)
        total_processed += 1
        total_cross_domain += cross_domain_count
        total_truly_unique += truly_unique_count
        print("-" * 50)

    print(f"Completed processing {total_processed} files.")


if __name__ == "__main__":
    main()
