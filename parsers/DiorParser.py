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
        positions = tree.xpath('//li[@class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-6 MuiGrid-grid-md-4 mui-jkozsk"]')

        return positions

    def iterate_products(self, positions):
        for pos in positions:
            link = str()
            try:
                link = pos.xpath('.//a[@class="product-card__link MuiBox-root mui-1692cqp"]/@href')[0]
            except IndexError:
                print("Zalupa")
                print(pos.attrib)
                link = "/en_ch/fashion/products/" + pos.attrib['data-object-id'][4:-4] + "_" + pos.attrib['data-object-id'][-4:]

            pos_page = fromstring(self.get_request(link).text)
            title = pos_page.xpath('//h1[@class="MuiTypography-root MuiTypography-headline-s DS-Typography mui-1mpckll"]/text()')[0].strip().lower()
            title = title.replace("/", "-")
            pictures = list(set(pos_page.xpath('//img[@class="MuiBox-root mui-ot5e1e"]/@src')))

            paths = []
            dir_name = "id_" + pos.attrib['data-object-id'][4:-4] + "_" + pos.attrib['data-object-id'][-4:]
            os.makedirs("dataset/Dior/" + dir_name, exist_ok=True)
            for i in range(len(pictures)):
                with open(f"dataset/Dior/{dir_name}/{i}.jpg", "wb") as img:
                    paths.append(f"Dior/{dir_name}/{i}.jpg")
                    img.write(requests.get(pictures[i]).content)

            self.products.append(
                {
                    "brand": "Dior",
                    "title": title,
                    "pictures": paths,
                }
            )

            print(title, " - done")

    def paginate(self, path):
        positions = self.get_product_positions(path)
        self.iterate_products(positions)

    def pipeline(self):
        men_RFW_path = "/en_ch/fashion/mens-fashion/ready-to-wear/all-ready-to-wear"
        men_shoes_path = "/en_ch/fashion/mens-fashion/shoes/all-shoes"
        women_RFW_path = "/en_ch/fashion/womens-fashion/ready-to-wear/all-ready-to-wear"
        women_shoes_path = "/en_ch/fashion/womens-fashion/shoes/all-shoes"
        self.paginate(men_RFW_path)
        self.paginate(men_shoes_path)
        self.paginate(women_RFW_path)
        self.paginate(women_shoes_path)
        export_to_csv(self.products)


def main():
    url = "https://www.dior.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'if-none-match': '"u4fdpw8w989an5"',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-platform': '"macOS"'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()