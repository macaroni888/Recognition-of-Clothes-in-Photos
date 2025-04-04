import os

import requests
from lxml.html import fromstring
from time import sleep
import json

from utils import export_to_csv
from utils import scroll_with_selenium


PROXY_PATH = "ProxyList.txt"
BRANDS_PATH = "farfetch_brands.json"


class Scraper:
    def __init__(self, url, headers, initial_proxy=0):
        self.url = url
        self.headers = headers
        self.products = []
        self.counter = 0

        with open(BRANDS_PATH, "r") as file:
            self.brands = json.load(file)

        with open(PROXY_PATH, "r") as file:
            self.proxy_list = [line.strip() for line in file]
        self.current_proxy = initial_proxy
        self.proxy = {"https": "http://" + self.proxy_list[self.current_proxy]}

    def rotate_proxy(self):
        self.current_proxy = (self.current_proxy + 1) % len(self.proxy_list)
        self.proxy = {"https": "http://" + self.proxy_list[self.current_proxy]}

    def get_request(self, path, params=None):
        if params is None:
            params = {}
        try:
            response = requests.get(self.url + path, headers=self.headers, params=params, proxies=self.proxy)
            if response.status_code == 429:
                self.rotate_proxy()
                response = requests.get(self.url + path, headers=self.headers, params=params, proxies=self.proxy)
        except requests.exceptions.ConnectionError as e:
            sleep(90)
            response = requests.get(self.url + path, headers=self.headers, params=params, proxies=self.proxy)
        return response

    def get_product_positions(self, tree):
        positions = tree.xpath('//script[@type="application/ld+json"]')
        if len(positions) == 2:
            positions = json.loads(positions[0].text)["itemListElement"]
        else:
            positions = []

        return positions

    def iterate_products(self, positions, brand_name, gender):
        for pos in positions:
            title = pos['name']
            title = title.replace("/", "-")

            picture = pos['image'][0]
            os.makedirs(f"dataset/{gender}/{brand_name}/" + title + str(self.counter), exist_ok=True)
            paths = []
            with open(f"dataset/{gender}/{brand_name}/{title + str(self.counter)}/0.jpg", "wb") as img:
                try:
                    r = requests.get(picture, headers=self.headers, proxies=self.proxy)
                    if r.status_code == 429:
                        self.rotate_proxy()
                        r = requests.get(picture, headers=self.headers, proxies=self.proxy)
                except requests.exceptions.ConnectionError as e:
                    sleep(30)
                    self.rotate_proxy()
                    r = requests.get(picture, headers=self.headers, proxies=self.proxy)
                img.write(r.content)
                paths.append(f"{gender}/{brand_name}/{title + str(self.counter)}/0.jpg")
            self.counter += 1

            self.products.append(
                {
                    "brand": brand_name,
                    "title": title,
                    "pictures": paths,
                }
            )

            print(title, " - done")

    def paginate(self, path, brand_name, gender):
        items = ['?page=1']
        while items != list():
            suffix = items[0]
            response = self.get_request(path + suffix)
            tree = fromstring(response.text)
            positions = self.get_product_positions(tree)
            if positions:
                self.iterate_products(positions, brand_name, gender)
            items = tree.xpath('//a[@data-component="PaginationNextActionButton"]/@href')

    def iterate_brands(self, brand_links, clothing_filter, gender):
        for name in brand_links:
            parts = brand_links[name].split("/")
            parts.insert(-2, clothing_filter)
            path = "/".join(parts)
            self.paginate(path, name, gender)
            export_to_csv(self.products)
            self.products = []
            print(f"{name} - done")

    def parse_brands(self, path):
        # TODO: 429 response (too many requests)
        tree = fromstring(scroll_with_selenium(self.url + path, 10, 3))
        brand_names = tree.xpath('//a[@data-testid="designer-link"]/text()')
        brand_links = tree.xpath('//a[@data-testid="designer-link"]/@href')
        brands = dict(zip(brand_names, brand_links))
        return brands

    def pipeline(self):
        brands_men = self.brands["men"]
        men_filter = "clothing-2"
        brands_women = self.brands["women"]
        women_filter = "clothing-1"
        self.iterate_brands(brands_men, men_filter, "men")
        self.iterate_brands(brands_women, women_filter, "women")


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
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()
