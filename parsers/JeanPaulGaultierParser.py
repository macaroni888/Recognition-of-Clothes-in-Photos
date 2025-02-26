import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from lxml.html import fromstring
import requests

from utils import export_to_csv

URL = "https://fashion.jeanpaulgaultier.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

products = []

# Инициализация WebDriver (необходимы драйвера для Chrome или Firefox)
service = webdriver.ChromeService('../webdrivers/chromedriver')
driver = webdriver.Chrome(service=service)

# Открываем страницу
driver.get("https://fashion.jeanpaulgaultier.com/en-fr/categories/new-in")

# Прокручиваем страницу до конца, чтобы подгрузить все товары
body = driver.find_element(By.TAG_NAME, 'body')
for i in range(28): # 28
    body.send_keys(Keys.END)
    time.sleep(3)  # Подождать, чтобы данные успели подгрузиться

# Получаем HTML код страницы
tree = fromstring(driver.page_source)
driver.quit()

products_paths = tree.xpath('//a[@class="styles_productCard__fAEnz styles_ProductCard__8klnm"]/@href')

for path in products_paths:
    page = fromstring(requests.get(URL + path, headers=HEADERS).text)

    title = page.xpath(
        '//p[@class="styles_name__I01KZ styles_text-display-20__Gdmoj colors_black__ZedF6"]/text()')[0].strip().lower()
    title = title.replace("/", "-")

    pictures = page.xpath('//div[@class="styles_imageWrapper__vwIcI"]//img/@src')[::2]
    paths = []
    os.makedirs("dataset/jean_paul_gaultier/" + title, exist_ok=True)
    for i in range(len(pictures)):
        with open(f"dataset/jean_paul_gaultier/{title}/{i}.jpg", "wb") as img:
            paths.append(f"jean_paul_gaultier/{title}/{i}.jpg")
            img.write(requests.get(pictures[i]).content)

    products.append(
        {
            "brand": "Jean Paul Gaultier",
            "title": title,
            "pictures": paths,
        }
    )

    print(title, " - done")

export_to_csv(products)
