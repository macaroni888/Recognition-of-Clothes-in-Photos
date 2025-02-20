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
        positions = tree.xpath('//div[@class="product-body"]')

        return positions

    def iterate_products(self, positions, page_num):
        counter = 0
        for pos in positions:
            counter += 1
            link = str()
            try:
                link = pos.xpath('.//a[@class="tile-image  "]/@href')[0]
            except IndexError:
                print(pos.attrib)
                continue

            pos_page = fromstring(self.get_request(link).text)
            title = pos_page.xpath('//h1[@class="product-name"]/text()')[0].strip().lower()
            title = title.replace("/", "-")


            pictures = pos_page.xpath('//div[@class="swiper-slide"]')

            paths = []
            dir_name = f"id_{page_num}_{counter}"
            os.makedirs("dataset/Balmain/" + dir_name, exist_ok=True)
            for i in range(len(pictures)):
                img = pictures[i].xpath('.//img')[0]
                img_link = img.attrib.get("data-src") or img.attrib.get("src")
                with open(f"dataset/Balmain/{dir_name}/{i}.jpg", "wb") as img:
                    paths.append(f"Balmain/{dir_name}/{i}.jpg")
                    img.write(requests.get(img_link).content)

            self.products.append(
                {
                    "brand": "Balmain",
                    "title": title,
                    "pictures": paths,
                }
            )
            print(title, " - done")

    def paginate(self, path, page_num):
        positions = self.get_product_positions(path)
        self.iterate_products(positions, page_num)

    def pipeline(self):
        men_RFW_path = "/en/men/ready-to-wear/?sz=167"
        # men_shoes_path = "/en/men/shoes/?sz=48"
        # women_RFW_path = "/en/women/ready-to-wear/?sz=252"
        women_shoes_path = "/en/women/shoes/?sz=60"
        self.paginate(men_RFW_path, 0)
        # self.paginate(men_shoes_path, 1)
        # self.paginate(women_RFW_path, 2)
        self.paginate(women_shoes_path, 3)
        export_to_csv(self.products)


def main():
    url = "https://nl.balmain.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()