import webbrowser
from collections.abc import Generator
from tkinter.filedialog import askopenfile

import database
import requests
from pandas import read_excel


def read_products() -> Generator[tuple[str, str, int]]:
    if not (file := askopenfile()):
        return
    for product in read_excel(file.name).values:
        yield str(product[0]), str(product[1]), int(product[2])


def get_wb_card_url(art: int):
    vol = art // 10**5
    part = art // 10**3
    edges = [
        -1,
        143,
        287,
        431,
        719,
        1007,
        1061,
        1115,
        1169,
        1313,
        1601,
        1655,
        1919,
        2045,
        10**9,
    ]
    for i in range(1, len(edges)):
        if edges[i - 1] <= vol and vol <= edges[i]:
            host = f"basket-{i//10}{i%10}.wb.ru"
            url = f"https://{host}/vol{vol}/part{part}/{art}/info/ru/card.json"
            if requests.get(url).status_code // 100 == 2:
                return url
    b = 1
    while b < 100:
        host = f"basket-{b//10}{b%10}.wb.ru"
        url = f"https://{host}/vol{vol}/part{part}/{art}/info/ru/card.json"
        if requests.get(url).status_code // 100 == 2:
            return url
        b += 1
    raise ValueError("basket not found: article {art}")


def get_vendor_code(store: str, id: str) -> str:
    if store == "wb":
        wb = requests.get(get_wb_card_url(int(id)))
        return str(wb.json()["vendor_code"])
    else:
        raise NotImplemented(f"cannot get vendor code for '{store}' store")


def get_name(store: str, id: str) -> str:
    if store == "wb":
        wb = requests.get(get_wb_card_url(int(id)))
        return str(wb.json()["imt_name"])
    else:
        raise NotImplemented(f"cannot get name for '{store}' store")


def get_price(store: str, id: str) -> int:
    if store == "wb":
        try:
            wb = requests.get(
                f"https://card.wb.ru/cards/v2/detail?dest=-1257786&nm={id}"
            )
            return (
                int(wb.json()["data"]["products"][0]["sizes"][0]["price"]["total"])
                // 100
            )
        except Exception:
            return -1
    else:
        raise NotImplemented(f"cannot get price for '{store}' store")


def build_product(store: str, id: str, cost: int) -> database.Database.Product:
    return database.Database.Product(
        {
            "store": store,
            "id": id,
            "vendor_code": get_vendor_code(store, id),
            "name": get_name(store, id),
            "price": get_price(store, id),
            "cost": cost,
        }
    )


def add_products() -> None:
    db = database.Database()
    for store, id, cost in read_products():
        print(id)
        db.add_product(build_product(store, id, cost))


def webopen(article: str) -> None:
    webbrowser.open(f"https://www.wildberries.ru/catalog/{article}/detail.aspx")
