import requests
from bs4 import BeautifulSoup as BS
import csv

MAIN_URL = 'http://planeta.kg'
INITIAL_CATEGORIES = '/catalog/kompyutery_noutbuki_planshety_i_org_tekhnika/'
headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}

def parse_categories_urls(main_url):
    html = requests.get(main_url, headers=headers).text
    doc = BS(html, 'lxml')
    categories = doc.find_all("div", class_="product")
    return [category.find('a').get("href") for category in categories]

def parse_subcategories(url):
    html = requests.get(url, headers=headers).text
    doc = BS(html, 'lxml')
    categories = doc.find_all("div", class_="product")
    return [category.find('a').get("href") for category in categories]

def to_csv(data):
    with open("data.csv", 'a') as file:
        writer = csv.writer(file)
        writer.writerow((data["title"], data["category"], data["price"], data["image"]))

def parse_info(url):
    html = requests.get(url, headers=headers).text
    doc = BS(html, 'lxml')
    products = doc.find_all("div", class_="card-product")
    category = doc.find("div", class_="breadcrumbs").find_all("li")[-1].text

    for product in products:
        data = {}

        title = product.find('p', class_="name").find("a").get("title")
        data["title"] = title
        
        data["category"] = category

        price = product.find("div", class_="price").text
        data["price"] = price.replace("\n", '').strip()

        img = product.find("div", class_="img-rating-stock").find("img").get("src")
        data["image"] = MAIN_URL + img

        to_csv(data)

def main():
    with open("data.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["title", "category", "price", "image"])
    categories = parse_categories_urls(MAIN_URL + INITIAL_CATEGORIES)
    for category in categories:
        subcategories = parse_subcategories(MAIN_URL + category)
        if subcategories:
            for subcategory in subcategories:
                parse_info(MAIN_URL + subcategory)
        else:
            parse_info(MAIN_URL + category)



main()
