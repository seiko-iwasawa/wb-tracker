import json
from collections.abc import Generator
from tkinter.filedialog import askopenfile

import appdata
import requests
from pandas import read_excel


def read_product_list() -> dict:
    with open(appdata.root / "data" / "product-list.json", "r") as pl:
        return json.load(pl)


def write_product_list(product_list: dict) -> None:
    with open(appdata.root / "data" / "product-list.json", "w") as pl:
        json.dump(product_list, pl)


def read_products() -> Generator[tuple[str, str]]:
    if not (file := askopenfile()):
        return
    for product in read_excel(file.name).values:
        yield str(product[0]), str(product[1])


def add_product(inner_article: str, wb_article: str) -> None:
    product_list = read_product_list()
    if wb_article not in product_list:
        product_list[wb_article] = {"inner-article": inner_article, "history": {}}
        write_product_list(product_list)


def add_products() -> None:
    for inner_article, wb_article in read_products():
        add_product(inner_article, wb_article)


def get_wb_price(article: str) -> int:
    wb = requests.get(f"https://card.wb.ru/cards/v2/detail?dest=-1257786&nm={article}")
    return wb.json()["data"]["products"][0]["sizes"][0]["price"]["total"] // 100
