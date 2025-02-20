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
        positions = response.json()["products"]

        return positions

    def iterate_products(self, positions):
        for pos in positions:
            title = pos["name"].lower()
            pictures = []
            for img in pos["images"]:
                pictures.append(img["src"])
            os.makedirs("dataset/YSL/" + title, exist_ok=True)
            paths = []
            if len(pictures) == 0:
                print()
            for i in range(len(pictures)):
                with open(f"dataset/YSL/{title}/{i}.jpg", "wb") as img:
                    paths.append(f"YSL/{title}/{i}.jpg")
                    img.write(requests.get(pictures[i], headers=self.headers).content)

            self.products.append(
                {
                    "brand": "YSL",
                    "title": title,
                    "pictures": paths,
                }
            )

            print(title, " - done")

    def paginate(self, path, page_n, gender):
        for page in range(0, page_n + 1):
            # Ready to wear
            suffix = f",ready-to-wear?locale=en-en&page={page}&categoryContext={gender}_clothing&categoryIds=view-all-rtw-{gender}&isEmployeeOnly=false&isEmployee=false&clickAnalytics=true&hitsPerPage=15"
            positions = self.get_product_positions(path + suffix)
            self.iterate_products(positions)

            # Shoes
            suffix = f",shoes?locale=en-en&page={page}&categoryContext={gender}_shoes&categoryIds=view-all-shoes-{gender}&isEmployeeOnly=false&isEmployee=false&clickAnalytics=true&hitsPerPage=15"
            positions = self.get_product_positions(path + suffix)
            self.iterate_products(positions)

    def pipeline(self):
        men = "/api/v1/category/shop-men"
        men_n_of_pages = 11
        women = "/api/v1/category/shop-women"
        women_n_of_pages = 14
        self.paginate(men, men_n_of_pages, "men")
        print("Men page is parsed")
        self.paginate(women, women_n_of_pages, "women")
        print("Women page is parsed")

        'https://www.ysl.com/api/v1/category/shop-men,shoes?locale=en-en&page=0&categoryContext=men_shoes&categoryIds=view-all-shoes-men&isEmployeeOnly=false&isEmployee=false&clickAnalytics=true&hitsPerPage=15'

        export_to_csv(self.products)


def main():
    url = "https://www.ysl.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()
