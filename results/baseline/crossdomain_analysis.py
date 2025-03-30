#!/usr/bin/env python3

import re


def id_extraction(filepath):
    ids = set()
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if line.strip().startswith("ID:"):
                id_value = line.split(":", 1)[1].strip()
                ids.add(id_value)
    return ids


def search_through_cookies(cookiefile, idset):
    matches = []
    domain = None
    matched_ids = set()

    with open(cookiefile, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            if line.startswith('***') and line.endswith('***'):
                domain = line.strip('* ')
                continue
            if not line:
                continue

            try:
                parts = line.split(":", 1)
                if len(parts) < 2:
                    continue

                url = parts[0].strip()
                value = parts[1].strip()

                pattern = r"'[^']*'[,\s]*'([^']*)'"
                match = re.search(pattern, value)
                if match:
                    cookievalue = match.group(1)
                else:
                    continue

                for idvalue in idset:
                    if idvalue not in matched_ids and idvalue in cookievalue:
                        matches.append({
                            'domain': domain,
                            'url': url,
                            'cookie_value': cookievalue,
                            'matched_id': idvalue,
                            'full_line': line
                        })
                        matched_ids.add(idvalue)
            except Exception as e:
                print("The error is: " + str(e))

    return matches


def main():
    crossdomainsfile = "test_crossdomains/9_paths_recurring_ids2.txt"
    cookiefile = "cookietest_9.txt"
    total_ids = id_extraction(crossdomainsfile)
    matches = search_through_cookies(cookiefile, total_ids)

    with open("../baseline_counts.txt", 'a', encoding='utf-8') as counts:
        counts.write(f"Files: {crossdomainsfile} and {cookiefile}\n")
        counts.write(f"Total unique IDs in crossdomains file {cookiefile}: {len(total_ids)}\n")
        counts.write(f"Total unique IDs found in cookies: {len(matches)}\n")

    print(f"Process COmpleted")


if __name__ == "__main__":
    main()
