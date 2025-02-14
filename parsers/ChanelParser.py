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
        positions = tree.xpath('//li[@class="fs-products-grid__product-grid__item"]')
        return positions

    def iterate_products(self, positions):
        for pos in positions:
            link = pos.xpath('.//a[@class="fs-product-item__link"]/@href')[0]
            link = link.replace(self.url, '')
            title = link.split('/')[-2].replace('-', ' ').lower()
            title = title.replace("/", "-")
            pictures = pos.xpath('.//img[@class="fs-image__img"]/@src')

            paths = []
            os.makedirs("dataset/chanel/" + title, exist_ok=True)
            for i in range(len(pictures)):
                with open(f"dataset/chanel/{title}/{i}.jpg", "wb") as img:
                    paths.append(f"chanel/{title}/{i}.jpg")
                    img.write(requests.get(pictures[i]).content)

            self.products.append(
                {
                    "brand": "Chanel",
                    "title": title,
                    "pictures": paths,
                }
            )

            print(title, " - done")

    def paginate(self, path):
        tree = fromstring(self.get_request(path).text)
        n_pages = int(tree.xpath('//ul[@class="fs-product-grid__load-more__page-list__hidden"]//a/text()')[-1])
        print()
        for page in range(1, n_pages + 1):
            positions = self.get_product_positions(path + f"page-{page}/")
            self.iterate_products(positions)

    def pipeline(self):
        ready_to_wear = "/us/fashion/ready-to-wear/"
        tree = fromstring(self.get_request(ready_to_wear).text)
        categories = tree.xpath('//a[@id="button-fs-button-fs-qca-modal__btn-link"]/@href')[2:]
        for url in categories:
            path = url.replace(self.url, "")
            self.paginate(path)
        print()


def main():
    url = "https://www.chanel.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()
