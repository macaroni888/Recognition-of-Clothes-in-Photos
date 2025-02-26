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
        positions = tree.xpath('//li[@class="w-full h-auto lg:h-full"]')

        return positions

    def iterate_products(self, positions):
        for pos in positions:
            link = pos.xpath('.//a[@class="h-full product-card__link"]/@href')[0]
            link = link.replace(self.url, "")
            pos_page = fromstring(self.get_request(link).text)
            title = pos_page.xpath('//h1[@class="text-title-big lg:text-title-big-lg text-black mb-sp-11 lg:mb-2 '
                                   'relative sm:text-[14px] sm:leading-[18px] lg:text-[20px] lg:leading-[24px] '
                                   'font-bold tracking-wide"]/text()')[0].strip().lower()
            title = title.replace("/", "-")
            pictures = list(set(pos_page.xpath('//div[@class="block gallery-images__item"]//img/@data-srcset')))

            paths = []
            os.makedirs("dataset/prada/" + title, exist_ok=True)
            for i in range(len(pictures)):
                l = pictures[i].split(", ")
                for j in range(len(l)):
                    with open(f"dataset/prada/{title}/{j}.jpg", "wb") as img:
                        paths.append(f"prada/{title}/{j}.jpg")
                        img.write(requests.get(l[j].split()[0]).content)

            self.products.append(
                {
                    "brand": "Prada",
                    "title": title,
                    "pictures": paths,
                }
            )

            print(title, " - done")

    def paginate(self, path, pages):
        for i in range(1, pages + 1):
            positions = self.get_product_positions(path + f"/{i}")
            self.iterate_products(positions)

    def pipeline(self):
        men_path = "/nl/en/mens/ready-to-wear/c/10130EU/page"
        women_path = "/nl/en/womens/ready-to-wear/c/10048EU/page"
        self.paginate(men_path, 24)
        # self.paginate(women_path)
        export_to_csv(self.products)


def main():
    url = "https://www.prada.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()
