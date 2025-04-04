import requests
from lxml.html import fromstring
from time import sleep

import json
from utils import scroll_with_selenium


def get_request(url, path, headers, params=None):
    if params is None:
        params = {}
    try:
        response = requests.get(url + path, headers=headers, params=params)
        if response.status_code == 429:
            response = requests.get(url + path, headers=headers, params=params)
    except requests.exceptions.ConnectionError as e:
        sleep(90)
        response = requests.get(url + path, headers=headers, params=params)
    return response


def parse_brands(url, path):
    tree = fromstring(scroll_with_selenium(url + path, 10, 3))
    brand_names = tree.xpath('//a[@data-testid="designer-link"]/text()')
    brand_links = tree.xpath('//a[@data-testid="designer-link"]/@href')
    brands = dict(zip(brand_names, brand_links))
    return brands


def main():
    url = "https://www.farfetch.com"
    headers = {
        "Cache-Control": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-arch": '"arm"',
        "sec-ch-ua-full-version-list": '"Chromium";v="134.0.6998.89", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.89"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"macOS"',
        "sec-ch-ua-platform-version": '"15.3.0"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    data = {}

    men_path = "/nl/designers/men"
    brands_men = parse_brands(url, men_path)
    data["men"] = brands_men
    women_path = "/nl/designers/women"
    brands_women = parse_brands(url, women_path)
    data["women"] = brands_women

    with open("farfetch_brands.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    main()
