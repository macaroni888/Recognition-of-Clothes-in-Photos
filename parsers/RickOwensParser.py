import os

import requests
from lxml.html import fromstring
from time import sleep

from utils import export_to_csv


class Scraper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.products = []

    def get_request(self, path, params=None):
        if params is None:
            params = {}
        try:
            response = requests.get(self.url + path, headers=self.headers, params=params)
        except requests.exceptions.ConnectionError as e:
            sleep(10)
            response = requests.get(self.url + path, headers=self.headers, params=params)
        return response

    def get_product_positions(self, path):
        response = self.get_request(path)
        tree = fromstring(response.text)
        positions = tree.xpath('//article[@class="product"]')

        return positions

    def iterate_products(self, positions):
        for pos in positions:
            link = pos.xpath('.//a[@itemprop="url"]/@href')[0]
            pos_page = fromstring(self.get_request(link).text)
            print()
            title = pos_page.xpath('//div[@class="product-details"]//span//text()')[0].strip().lower()
            title = title.replace("/", "-")
            pictures = list(set(pos_page.xpath('//img[@itemprop="image"]/@src')))

            paths = []
            os.makedirs("dataset/rick_owens/" + title, exist_ok=True)
            for i in range(len(pictures)):
                with open(f"dataset/rick_owens/{title}/{i}.jpg", "wb") as img:
                    paths.append(f"rick_owens/{title}/{i}.jpg")
                    img.write(requests.get(pictures[i]).content)

            self.products.append(
                {
                    "brand": "Rick Owens",
                    "title": title,
                    "pictures": paths,
                }
            )

            print(title, " - done")

    def paginate(self, path):
        positions = self.get_product_positions(path)
        self.iterate_products(positions)

    def pipeline(self):
        men_path = "/en/BR/men/section/all?utf8=✓&view_all=true"
        women_path = "/en/BR/women/section/all?view_all=true"
        self.paginate(men_path)
        self.paginate(women_path)
        export_to_csv(self.products)


def main():
    url = "https://www.rickowens.eu"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()
