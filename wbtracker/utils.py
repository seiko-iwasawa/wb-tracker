import datetime
import threading
import webbrowser
from collections.abc import Generator
from pathlib import Path
from tkinter.filedialog import askopenfile

import database
import opener
import pandas as pd
import requests


def read_products() -> Generator[tuple[str, str, int]]:
    if not (file := askopenfile()):
        return
    for product in pd.read_excel(file.name).values:
        yield str(product[0]), str(product[1]), int(product[2])


def read_wb_sales() -> Generator[tuple[str, str, int, str]]:
    if not (file := askopenfile()):
        return
    for product in pd.read_excel(file.name).values:
        yield str(product[2]), str(product[4]), int(product[10]), str(product[12])


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
            host = f"basket-{i//10}{i%10}.wbbasket.ru"
            url = f"https://{host}/vol{vol}/part{part}/{art}/info/ru/card.json"
            if requests.get(url).status_code // 100 == 2:
                return url
    b = 1
    while b < 100:
        host = f"basket-{b//10}{b%10}.wbbasket.ru"
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


def add_products() -> Generator[str]:

    def add_product(store: str, id: str, cost: int):
        product = build_product(store, id, cost)
        with lock:
            db.add_product(product)

    db = database.Database()
    products = list(read_products())
    lock = threading.Lock()
    for s in range(0, len(products), 10):
        yield f"{int(100 * s // len(products))}%"
        threads: list[threading.Thread] = []
        for store, id, cost in products[s : s + 10]:
            thread = threading.Thread(target=add_product, args=(store, id, cost))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()


def add_wb_sales() -> Generator[str]:
    db = database.Database()
    for sticker, date, price, id in read_wb_sales():
        yield f"({date}) {id}"
        db.add_sale(
            database.Database.Sale(
                {
                    "store": "wb",
                    "sticker": sticker,
                    "id": id,
                    "date": date,
                    "price": price,
                }
            )
        )


def update_price() -> Generator[tuple[database.Database.Product, int, str]]:

    def f(product: database.Database.Product):
        nonlocal cnt
        new_price = get_price(product._store, product._id)
        with lock:
            cnt += 1
            res.append((product, new_price, f"{int(100 * cnt // len(db._products))}%"))

    db = database.Database()
    cnt = 0
    for s in range(0, len(db._products), 10):
        threads: list[threading.Thread] = []
        res: list[tuple[database.Database.Product, int, str]] = []
        lock = threading.Lock()
        for product in db._products[s : s + 10]:
            thread = threading.Thread(target=f, args=(product,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        yield from res


def apply_price(product: database.Database.Product, new_price: int) -> None:
    db = database.Database()
    product._price = new_price
    db.add_product(product)


def webopen(article: str) -> None:
    webbrowser.open(f"https://www.wildberries.ru/catalog/{article}/detail.aspx")


def appopen(filename: str) -> None:
    opener.subprocess_opener(f"'{filename}'")


def download_folder() -> Path:
    return Path.home() / "Downloads"


def download_products() -> str:
    db = database.Database()
    df = pd.DataFrame(columns=["store", "id", "vendor_code", "name", "price", "cost"])
    for i, product in enumerate(db._products):
        df.loc[i + 1] = [
            product._store,
            product._id,
            product._vendor_code,
            product._name,
            product._price,
            product._cost,
        ]
    filename = "products.xlsx"
    n = 1
    while (download_folder() / filename).exists():
        n += 1
        filename = f"products ({n}).xlsx"
    df.to_excel((download_folder() / filename))
    return str(download_folder() / filename)


def download_sales() -> str:
    db = database.Database()
    df = pd.DataFrame(columns=["store", "id", "vendor_code", "name", "all", "month"])
    for i, product in enumerate(db._products):
        all_time = 0
        month = 0
        for sale in db._sales:
            print(sale._store, sale._id, product._store, product._id)
            if (sale._store, sale._id) != (product._store, product._id):
                continue
            all_time += sale._price
            delta = (
                datetime.datetime.strptime(sale._date, "%H:%M:%S %d.%m.%Y")
                - datetime.datetime.now()
            )
            if delta < datetime.timedelta(days=31):
                month += sale._price
        df.loc[i + 1] = [
            product._store,
            product._id,
            product._vendor_code,
            product._name,
            all_time,
            month,
        ]
    filename = "sales.xlsx"
    n = 1
    while (download_folder() / filename).exists():
        n += 1
        filename = f"sales ({n}).xlsx"
    df.to_excel((download_folder() / filename))
    return str(download_folder() / filename)
