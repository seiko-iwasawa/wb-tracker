import datetime
import webbrowser
from collections.abc import Generator
from pathlib import Path
from tkinter.filedialog import askopenfile

import database
import opener
import pandas as pd


def read_products() -> Generator[tuple[str, str, int]]:
    if not (file := askopenfile()):
        return
    for product in pd.read_excel(file.name).values:
        yield str(product[0]), str(product[1]), int(product[2])


def read_wb_sales() -> Generator[tuple[str, str, int, str, str, str, str]]:
    if not (file := askopenfile()):
        return
    for product in pd.read_excel(file.name).values:
        yield str(product[2]), str(product[4]), int(product[10]), str(product[12]), str(
            product[16]
        ), str(product[6]), str(product[13])


def read_ozon_sales() -> Generator[tuple[str, str, int, str, str, str, str]]:
    if not (file := askopenfile()):
        return
    for product in pd.read_csv(file.name, sep=";").values:
        yield str(product[0]), str(product[5]), int(product[7]), str(product[10]), str(
            product[4]
        ), str(product[9]), str(product[11])


def build_product(store: str, id: str, cost: int) -> database.Database.Product:
    return database.Database.Product(
        {
            "store": store,
            "id": id,
            "vendor_code": "",
            "name": "",
            "price": -1,
            "cost": cost,
            "brand": "",
        }
    )


def add_products() -> Generator[str]:
    db = database.Database()
    products = list(read_products())
    for s in range(0, len(products)):
        yield f"{int(100 * s // len(products))}%"
        store, id, cost = products[s]
        product = build_product(store, id, cost)
        db.add_product(product)


def add_sales(store: str) -> Generator[str]:
    db = database.Database()
    for sticker, date, price, id, status, name, vendor_code in (
        read_wb_sales() if store == "wb" else read_ozon_sales()
    ):
        yield f"({date}) {id}"
        if status == "Продано":
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
            for product in db._products:
                if (product._store, product._id) == ("wb", id):
                    product._name = name
                    product._vendor_code = vendor_code
                    db.save()


def webopen(store: str, article: str) -> None:
    if store == "wb":
        webbrowser.open(f"https://www.wildberries.ru/catalog/{article}/detail.aspx")
    elif store == "ozon":
        webbrowser.open(f"https://www.ozon.ru/product/{article}/")
    else:
        raise NotImplemented(f"cannot open webpage for '{store}' store")


def appopen(filename: str) -> None:
    opener.subprocess_opener(f"'{filename}'")


def download_folder() -> Path:
    return Path.home() / "Downloads"


def download_products() -> str:
    db = database.Database()
    df = pd.DataFrame(
        columns=["store", "id", "vendor_code", "brand", "name", "price", "cost"]
    )
    for i, product in enumerate(db._products):
        df.loc[i + 1] = [
            product._store,
            product._id,
            product._vendor_code,
            product._brand,
            product._name,
            product._price,
            product._cost,
        ]
    df.sort_values(by="price", ascending=False, inplace=True)
    filename = "products.xlsx"
    n = 1
    while (download_folder() / filename).exists():
        n += 1
        filename = f"products ({n}).xlsx"
    with pd.ExcelWriter(download_folder() / filename, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="summary", index=False)
        writer.sheets["summary"].autofit()
    return str(download_folder() / filename)


def download_sales(start: datetime.datetime, end: datetime.datetime) -> str:
    db = database.Database()
    df = pd.DataFrame(
        columns=["store", "id", "vendor_code", "brand", "name", "n", "sum", "profit"]
    )
    for i, product in enumerate(db._products):
        n = 0
        sp = 0
        pr = 0
        for sale in db._sales:
            if (sale._store, sale._id) != (product._store, product._id):
                continue
            date_format = (
                "%H:%M:%S %d.%m.%Y" if sale._store == "wb" else "%Y-%m-%d %H:%M:%S"
            )
            delta = (
                datetime.datetime.strptime(sale._date, date_format)
                - datetime.datetime.now()
            )
            if start <= datetime.datetime.strptime(sale._date, date_format) <= end:
                n += 1
                sp += sale._price
                pr += sale._price - product._cost
        df.loc[i + 1] = [
            product._store,
            product._id,
            product._vendor_code,
            product._brand,
            product._name,
            n,
            sp,
            pr,
        ]
    df = df[df["n"] > 0]
    df.sort_values("n", ascending=False, inplace=True)
    filename = "sales.xlsx"
    n = 1
    while (download_folder() / filename).exists():
        n += 1
        filename = f"sales ({n}).xlsx"
    with pd.ExcelWriter(download_folder() / filename, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="summary", index=False)
        writer.sheets["summary"].autofit()
    return str(download_folder() / filename)
