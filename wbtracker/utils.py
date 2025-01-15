import json

import appdata
import requests


def read_product_list() -> dict:
    with open(appdata.root / "data" / "product-list.json", "r") as pl:
        return json.load(pl)


def write_product_list(product_list: dict) -> None:
    with open(appdata.root / "data" / "product-list.json", "w") as pl:
        json.dump(product_list, pl)


def get_wb_price(article: str) -> int:
    wb = requests.get(f"https://card.wb.ru/cards/v2/detail?dest=-1257786&nm={article}")
    return wb.json()["data"]["products"][0]["sizes"][0]["price"]["total"] // 100
