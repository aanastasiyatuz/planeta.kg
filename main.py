import requests
from bs4 import BeautifulSoup as BS
import csv
import time

MAIN_URL = 'http://planeta.kg'
INITIAL_CATEGORIES = '/catalog/kompyutery_noutbuki_planshety_i_org_tekhnika/'
headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}

def parse_html(url):
    time.sleep(1)
    html = requests.get(url, headers=headers).text
    return BS(html, 'lxml')

def parse_pages(url):
    print("parse_pages",url)
    doc = parse_html(url)
    pagination = doc.find("div", class_="pagintaion")
    if pagination:
        return pagination.find_all("a", class_="num")
    return None


def parse_initial_categories(url):
    doc = parse_html(url)
    menu = doc.find("div", class_="sub-menu").find_all("div", class_="block-4")
    initial_categories = []
    for categories in menu:
        [initial_categories.append(c.get("href")) for c in categories.find_all("a")]
    return initial_categories

def parse_categories_urls(url):
    doc = parse_html(url)
    categories = doc.find_all("div", class_="product")
    return [category.find('a').get("href") for category in categories]

def parse_subcategories(url):
    doc = parse_html(url)
    categories = doc.find_all("div", class_="product")
    return [category.find('a').get("href") for category in categories]

def to_csv(data):
    with open("data.csv", 'a') as file:
        writer = csv.writer(file)
        writer.writerow((data["title"], data["category"], data["description"], data["price"], data["image"]))

def parse_info(url):
    time.sleep(1)
    doc = parse_html(url)
    products = doc.find_all("div", class_="card-product")
    category = doc.find("div", class_="breadcrumbs").find_all("li")[-1].text

    for product in products:
        title = product.find('p', class_="name").find("a")
        price = product.find("div", class_="price").text
        img = product.find("div", class_="img-rating-stock").find("img").get("src")

        description = product.find("div", class_="section-property-option")

        # save data
        data = {}

        data["title"] = title.get("title")        
        data["category"] = category
        data["description"] = description if description else "no description"
        data["price"] = price.replace("\n", '').strip()
        data["image"] = MAIN_URL + img

        to_csv(data)

def main():
    with open("data.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["title", "category", "description", "price", "image"])

    initial_categories = parse_initial_categories(MAIN_URL)

    for init_cat in initial_categories:
        categories = parse_categories_urls(MAIN_URL + init_cat)
        for category in categories:
            subcategories = parse_subcategories(MAIN_URL + category)
            if subcategories:
                for subcategory in subcategories:
                    sub_subcategories = parse_subcategories(MAIN_URL + subcategory)
                    if sub_subcategories:
                        for s_s_category in sub_subcategories:
                            pages = parse_pages(MAIN_URL + s_s_category)
                            if pages:
                                if len(pages) > 1:
                                    for page in pages[1:]:
                                        page = page.get("href")
                                        parse_info(MAIN_URL + page)
                                else:
                                    parse_info(MAIN_URL + s_s_category)

                    else:
                        pages = parse_pages(MAIN_URL + subcategory)
                        if pages:
                            if len(pages) > 1:
                                for page in pages[1:]:
                                    page = page.get("href")
                                    parse_info(MAIN_URL + page)
                            else:
                                parse_info(MAIN_URL + subcategory)

            else:
                pages = parse_pages(MAIN_URL + category)
                if pages:
                    if len(pages) > 1:
                        for page in pages[1:]:
                            page = page.get("href")
                            parse_info(MAIN_URL + page)
                    else:
                        parse_info(MAIN_URL + category)


main()
