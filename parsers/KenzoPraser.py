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

    def get_product_positions(self, path, num_of_pages):
        positions = []
        for i in range(num_of_pages):
            new_path = path + f"?page={i + 1}" if i > 0 else path
            response = self.get_request(new_path)
            tree = fromstring(response.text)
            positions.extend(tree.xpath('//div[@is="m-product-tile"]'))

        return positions

    def iterate_products(self, positions, page_num):
        counter = 0
        for pos in positions:
            counter += 1
            link = str()
            try:
                link = pos.xpath('.//a[@is="m-tile-images"]/@href')[0]
            except IndexError:
                print(pos.attrib)
                continue

            pos_page = fromstring(self.get_request(link).text)
            title = pos_page.xpath('//h1[@class="t-big-bold"]/text()')[0].strip().lower()
            title = title.replace("/", "-")

            pictures = pos_page.xpath('//picture[@class="swiper-slide"]')

            paths = []
            dir_name = f"id_{page_num}_{counter}"
            os.makedirs("dataset/Kenzo/" + dir_name, exist_ok=True)
            for i in range(len(pictures)):
                img_link = pictures[i].xpath('.//img/@srcset')[0]
                img_link = img_link[img_link.rfind('https://') : img_link.rfind(' ')]
                with open(f"dataset/Kenzo/{dir_name}/{i}.jpg", "wb") as img:
                    paths.append(f"Kenzo/{dir_name}/{i}.jpg")
                    img.write(requests.get(img_link).content)

            self.products.append(
                {
                    "brand": "Kenzo",
                    "title": title,
                    "pictures": paths,
                }
            )
            print(title, " - done")

    def paginate(self, path, page_num, num_of_pages):
        positions = self.get_product_positions(path, num_of_pages)
        self.iterate_products(positions, page_num)

    def pipeline(self):
        men_RFW_path = "/en-nl/c-men/see-all"
        women_RFW_path = "/en-nl/c-women/see-all"
        # self.paginate(men_RFW_path, 0, 12)
        self.paginate(women_RFW_path, 2, 11)
        export_to_csv(self.products)


def main():
    url = "https://www.kenzo.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()