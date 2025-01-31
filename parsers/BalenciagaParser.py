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
        positions = tree.xpath('//div[@class="c-product__item"]')

        return positions

    def iterate_products(self, positions):
        for pos in positions:
            link = pos.xpath('.//a[@class="c-product__focus"]/@href')[0]
            pos_page = fromstring(self.get_request(link).text)
            title = pos_page.xpath('//h1[@class="c-product__name"]/text()')[0].strip()
            title = title.replace("/", "-")
            pictures = pos_page.xpath('//button[@class="c-productcarousel__button"]/img/@data-src')

            paths = []
            os.makedirs("dataset/balenciaga/" + title, exist_ok=True)
            for i in range(len(pictures)):
                with open(f"dataset/balenciaga/{title}/{i}.jpg", "wb") as img:
                    paths.append(f"balenciaga/{title}/{i}.jpg")
                    img.write(requests.get(pictures[i]).content)

            self.products.append(
                {
                    "brand": "Balenciaga",
                    "title": title,
                    "pictures": paths,
                }
            )

            print(title, " - done")

    def paginate(self, gender, department):
        path = f"/en-nl/{gender}/{department}"
        r = self.get_request(path)
        if r.status_code != 200:
            path = f"/en-nl/{department}"
            r = self.get_request(path)
            if r.status_code != 200:
                return False
        tree = fromstring(r.text)
        res = tree.xpath('//span[@class="c-filters__count"]/text()')[0].strip()
        number_of_results = 100
        try:
            number_of_results = int(res.split()[0])
        except ValueError:
            print(res)
        start = 0
        sz = 24
        while start < number_of_results:
            next_path = path + f"?start={start}&sz={sz}"
            positions = self.get_product_positions(next_path)
            self.iterate_products(positions)
            start += sz
        return True

    def pipeline(self):
        with open("parsers/balenciaga", "r") as f:
            for line in f:
                department = line.strip()
                if self.paginate("men", department):
                    self.paginate("women", department)
        export_to_csv(self.products)


def main():
    url = "https://www.balenciaga.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()
