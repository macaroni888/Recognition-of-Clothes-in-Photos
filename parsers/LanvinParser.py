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
        positions = tree.xpath('//div[@class="collection__grid-item animate animate-up"]')

        return positions

    def iterate_products(self, positions, page_num):
        counter = 0
        for pos in positions:
            counter += 1
            link = str()
            try:
                link = pos.xpath('.//a[@class="product-item__image-link borders product-item__mobile-slider"]/@href')[0]
            except IndexError:
                print(pos.attrib)

            pos_page = fromstring(self.get_request(link).text)
            title = pos_page.xpath('//h1[@class="product-single__title title__show-desktop"]/text()')[0].strip().lower()
            title = title.replace("/", "-")


            pictures = pos_page.xpath('//a[@class="media__image"]/@href')

            paths = []
            dir_name = f"id_{page_num}_{counter}"
            os.makedirs("dataset/Lanvin/" + dir_name, exist_ok=True)
            for i in range(len(pictures)):
                trash_index = pictures[i].rfind('?')
                img_link = f"https:{pictures[i][:trash_index]}"
                with open(f"dataset/Lanvin/{dir_name}/{i}.jpg", "wb") as img:
                    paths.append(f"Lanvin/{dir_name}/{i}.jpg")
                    img.write(requests.get(img_link).content)

            self.products.append(
                {
                    "brand": "Lanvin",
                    "title": title,
                    "pictures": paths,
                }
            )
            print(title, " - done")

    def paginate(self, path, page_num):
        positions = self.get_product_positions(path)
        self.iterate_products(positions, page_num)

    def pipeline(self):
        men_RFW_path1 = "/collections/men-ready-to-wear?page=1"
        men_RFW_path2 = "/collections/men-ready-to-wear?page=2"
        men_RFW_path3 = "/collections/men-ready-to-wear?page=3"

        men_shoes_path1 = "/collections/men-shoes?page=1"
        men_shoes_path2 = "/collections/men-shoes?page=2"

        women_RFW_path1 = "/collections/women-ready-to-wear?page=1"
        women_RFW_path2 = "/collections/women-ready-to-wear?page=2"
        women_RFW_path3 = "/collections/women-ready-to-wear?page=3"
        women_RFW_path4 = "/collections/women-ready-to-wear?page=4"

        women_shoes_path1 = "/collections/women-shoes?page=1"
        women_shoes_path2 = "/collections/women-shoes?page=2"
        women_shoes_path3 = "/collections/women-shoes?page=3"

        self.paginate(men_RFW_path1, 0)
        self.paginate(men_RFW_path2, 1)
        self.paginate(men_RFW_path3, 2)

        self.paginate(men_shoes_path1, 3)
        self.paginate(men_shoes_path2, 4)

        self.paginate(women_RFW_path1, 5)
        self.paginate(women_RFW_path2, 6)
        self.paginate(women_RFW_path3, 7)
        self.paginate(women_RFW_path4, 8)

        self.paginate(women_shoes_path1, 9)
        self.paginate(women_shoes_path2, 10)
        self.paginate(women_shoes_path3, 11)
        # export_to_csv(self.products)


def main():
    url = "https://us.lanvin.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()