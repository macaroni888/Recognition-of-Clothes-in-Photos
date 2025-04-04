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
            positions.extend(tree.xpath('//li[@class="c-tiles col-6 col-lg-3 d-flex flex-column"]'))

        return positions

    def iterate_products(self, positions, page_num):
        counter = 0
        for pos in positions:
            counter += 1
            link = str()
            try:
                link = pos.xpath('.//a[@class="link-background"]/@href')[0]
            except IndexError:
                print(pos.attrib)
                continue

            pos_page = fromstring(requests.get(link, headers=self.headers).text)
            title = pos_page.xpath('//p[@class="product-short-description font-small"]/text()')[0].strip().lower()
            title = title.replace("/", "-")

            section = pos_page.xpath('//section[@id="hero-product-carousel"]')[0]
            pictures = section.xpath('.//a/@data-src')

            paths = []
            dir_name = f"id_{page_num}_{counter}"
            os.makedirs("dataset/Fendi/" + dir_name, exist_ok=True)
            for i in range(len(pictures)):
                img_link = pictures[i]
                with open(f"dataset/Fendi/{dir_name}/{i}.jpg", "wb") as img:
                    paths.append(f"Fendi/{dir_name}/{i}.jpg")
                    img.write(requests.get(img_link).content)

            self.products.append(
                {
                    "brand": "Fendi",
                    "title": title,
                    "pictures": paths,
                }
            )
            print(title, " - done")

    def paginate(self, path, page_num, num_of_pages):
        positions = self.get_product_positions(path, num_of_pages)
        self.iterate_products(positions, page_num)

    def pipeline(self):
        men_RFW_path = "/nl/en/men/clothing/?start=0&sz=240"
        women_RFW_path = "/nl-en/woman/ready-to-wear?start=0&sz=204"
        self.paginate(men_RFW_path, 0, 1)
        self.paginate(women_RFW_path, 2, 1)
        export_to_csv(self.products)


def main():
    url = "https://www.versace.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'sec - ch - ua': '"Not(A:Brand";v = "99", "Google Chrome"; v = "133", "Chromium";v= "133"',
        'sec-fetch-user': '?1'
    }
    parser = Scraper(url, headers)
    parser.pipeline()


if __name__ == '__main__':
    main()