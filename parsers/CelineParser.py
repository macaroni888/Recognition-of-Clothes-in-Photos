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
        positions = tree.xpath('//li[contains(@class, "o-listing-grid__item o-listing-grid__item--to-animate")]')

        return positions

    def iterate_products(self, positions):
        for pos in positions:
            title = pos.xpath('.//h3/text()')[0].strip().lower()
            title = title.replace("/", "-")
            pictures = (
                pos.xpath('.//div[@class="m-product-listing__img-img m-product-listing__img-img--swipeable"]/img/@src')
            )

            paths = []
            os.makedirs("dataset/celine/" + title, exist_ok=True)
            for i in range(len(pictures)):
                with open(f"dataset/celine/{title}/{i}.jpg", "wb") as img:
                    paths.append(f"celine/{title}/{i}.jpg")
                    img.write(requests.get(pictures[i]).content)

            self.products.append(
                {
                    "brand": "Celine",
                    "title": title,
                    "pictures": paths,
                }
            )

            print(title, " - done")

    def paginate(self, path, tag):
        for page in range(0, 100, 20):
            suffix = f"?cgid={tag}&prefn1=celShowInPLP&prefv1=true&start={page}&sz=20&isviewall=true"
            positions = self.get_product_positions(path + suffix)
            self.iterate_products(positions)
            print("new_page")

    def pipeline(self):
        main_path = "on/demandware.store/Sites-CELINE_WW-Site/en/Search-UpdateGrid"
        tags = {
            "men_view_all": "E0017",
            "men_view_all_shoes": "E0025",
            "women_view_all": "A0018",
            "women_view_all_shoes": "A0025"
        }
        self.paginate(main_path, tags["men_view_all"])
        self.paginate(main_path, tags["men_view_all_shoes"])
        self.paginate(main_path, tags["women_view_all"])
        self.paginate(main_path, tags["women_view_all_shoes"])

        export_to_csv(self.products)


def main():
    url = "https://www.celine.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        "priority": "u=0, i",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()
