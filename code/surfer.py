"""
READS CONFIG.json's root directory and scrapes assets as per protocol.
"""

import os
import csv
import requests
from bs4 import BeautifulSoup


def fetch_html(url):
    """Fetches the html content from the given url."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_links(root_url, selector):
    """Extracts links from the given URL."""
    html_content = fetch_html(root_url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.select(selector)

    extracted_data = []

    for link in links:
        href = link.get('href')
        if href.endswith('.html'):

            subfolder_url = os.path.join(os.path.dirname(root_url), href)
            extracted_data += extract_links(subfolder_url, selector)
        elif href.endswith('.nc'):

            url_path_parts = href.split('/')
            name = url_path_parts[-1]

            path_components = url_path_parts[:-1]
            path_data = {f'p{i+1}': part for i,
                         part in enumerate(reversed(path_components))}

            row_data = {
                'name': name,
                'url': os.path.join(os.path.dirname(root_url), href)
            }
            row_data.update(path_data)

            extracted_data.append(row_data)

    return extracted_data


def write_to_csv(extracted_data, filename='output.csv'):
    """Creates the CSV with dynamic path component columns."""
    if not extracted_data:
        return

    all_keys = set()
    for row in extracted_data:
        all_keys.update(row.keys())

    sorted_keys = sorted(all_keys, key=lambda k: (k != 'name', k != 'url', k))

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=sorted_keys)
        writer.writeheader()
        writer.writerows(extracted_data)
