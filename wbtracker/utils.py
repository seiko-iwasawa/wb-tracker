import datetime
import webbrowser
from collections.abc import Generator
from pathlib import Path
from tkinter.filedialog import askopenfile

import database
import matplotlib.pyplot as plt
import numpy as np
import opener
import pandas as pd


def read_products() -> Generator[database.Database.Product]:

    def process_store(store: str) -> tuple[str, str]:
        if store.startswith("wb") or store.startswith("вб"):
            return "wb", store[2:]
        elif store.startswith("oz") or store.startswith("оз"):
            return "ozon", store[2:]
        elif store.startswith("ozon") or store.startswith("озон"):
            return "ozon", store[4:]
        else:
            return "unknown", store

    if not (file := askopenfile()):
        return
    for product in pd.read_excel(file.name).values:
        store, brand = process_store(product[0])
        yield database.Database.Product(
            {
                "store": store,
                "id": str(product[1]),
                "vendor_code": "",
                "name": "",
                "price": -1,
                "cost": int(product[2]),
                "brand": brand,
            }
        )


def read_wb_sales() -> Generator[tuple[database.Database.Sale, str, str, str]]:
    if not (file := askopenfile()):
        return
    for product in pd.read_excel(file.name).values:
        yield database.Database.Sale(
            {
                "store": "wb",
                "sticker": str(product[2]),
                "id": str(product[12]),
                "date": str(product[4]),
                "price": int(product[10]),
            }
        ), str(product[16]), str(product[6]), str(product[13])


def read_ozon_sales() -> Generator[tuple[database.Database.Sale, str, str, str]]:
    if not (file := askopenfile()):
        return
    for product in pd.read_csv(file.name, sep=";").values:
        yield database.Database.Sale(
            {
                "store": "ozon",
                "sticker": str(product[0]),
                "id": str(product[10]),
                "date": str(product[5]),
                "price": int(product[7]),
            }
        ), str(product[4]), str(product[9]), str(product[11])


def add_product(db: database.Database, product: database.Database.Product) -> None:
    if db_product := db.find_product(product.key):
        db_product.cost = product.cost
    else:
        db.add_product(product)


def add_products() -> Generator[str]:
    try:
        db = database.Database()
        for product in read_products():
            yield f"{product.key}"
            if product._store == "unknown":
                yield f"warning: неверно указан магазин для {product._id}"
            elif product.cost < 0:
                yield f"warning: себестоимость не может быть отрицательной (id: {product._id})"
            else:
                add_product(db, product)
        db.save()
    except Exception:
        yield "warning: неправильный формат таблицы. данные не были введены"


def add_sale(
    db: database.Database, sale: database.Database.Sale, name: str, vendor_code: str
) -> None:
    db.add_sale(sale)
    if product := db.find_product(sale.product_key):
        product.name = name
        product.vendor_code = vendor_code
        product.price = sale.price


def add_sales(store: str) -> Generator[str]:
    db = database.Database()
    sales = read_wb_sales() if store == "wb" else read_ozon_sales()
    ok_status = "Продано" if store == "wb" else "Доставлен"
    for sale, status, name, vendor_code in sales:
        yield f"{sale.key}"
        if status == ok_status:
            add_sale(db, sale, name, vendor_code)
            if not db.find_product(sale.product_key):
                yield f"warning: {vendor_code} not found"
    db.save()


def webopen(store: str, article: str) -> None:
    if store == "wb":
        webbrowser.open(f"https://www.wildberries.ru/catalog/{article}/detail.aspx")
    elif store == "ozon":
        webbrowser.open(f"https://www.ozon.ru/product/{article}/")
    else:
        raise NotImplemented(f"cannot open webpage for '{store}' store")


def appopen(filename: str) -> None:
    opener.subprocess_opener(f"{filename}")


def download_folder() -> Path:
    return Path.home() / "Downloads"


def gen_download_file(name: str, ext: str) -> Path:
    filename = f"{name}.{ext}"
    n = 1
    while (download_folder() / filename).exists():
        n += 1
        filename = f"{name} ({n}).{ext}"
    return download_folder() / filename


def df_to_xlsx(df: pd.DataFrame, file: Path):
    with pd.ExcelWriter(file, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="summary", index=False)
        writer.sheets["summary"].autofit()


def get_df_products() -> pd.DataFrame:
    db = database.Database()
    return (
        db.df_products.drop("brand", axis=1)
        .sort_values(by="price", ascending=False)
        .rename(
            columns={
                "store": "Магазин",
                "id": "Артикул",
                "vendor_code": "Код продавца",
                "name": "Название",
                "price": "Цена",
                "cost": "Себестоимость",
            }
        )
    )


def download_products() -> str:
    df_to_xlsx(get_df_products(), file := gen_download_file("Данные о товарах", "xlsx"))
    return str(file)


def get_df_sales(start: datetime.datetime, end: datetime.datetime) -> pd.DataFrame:

    def check_date(row: pd.Series):
        try:
            date_format = (
                "%H:%M:%S %d.%m.%Y" if row["store"] == "wb" else "%Y-%m-%d %H:%M:%S"
            )
            return start <= datetime.datetime.strptime(row["date"], date_format) <= end
        except Exception:
            return False

    db = database.Database()
    products = db.df_products
    sales = db.df_sales
    sales = (
        sales[sales.apply(check_date, axis=1)]
        .groupby(["store", "id"])
        .agg({"price": "sum", "date": "count"})
        .rename(columns={"price": "sum", "date": "n"})
    )
    df = products.join(sales, on=["store", "id"], how="right")
    df = df[df["n"] > 0]
    df["profit"] = df["sum"] - df["cost"] * df["n"]
    df = (
        df.drop(["brand", "price", "cost"], axis=1)
        .sort_values("n", ascending=False)
        .rename(
            columns={
                "store": "Магазин",
                "id": "Артикул",
                "vendor_code": "Код продавца",
                "name": "Название",
                "sum": "Сумма",
                "n": "Кол-во",
                "profit": "Прибыль",
            }
        )
    )
    return df


def download_sales(
    start: datetime.datetime, end: datetime.datetime, filename: str
) -> str:
    df_to_xlsx(get_df_sales(start, end), file := gen_download_file(filename, "xlsx"))
    return str(file)


def build_plot(art: str) -> None:

    def short_date(date: str):
        try:
            date_format = "%H:%M:%S %d.%m.%Y"
            return datetime.datetime.strptime(date, date_format).strftime("%m.%y")
        except Exception:
            try:
                date_format = "%Y-%m-%d %H:%M:%S"
                return datetime.datetime.strptime(date, date_format).strftime("%m.%y")
            except Exception:
                return "01.01"

    db = database.Database()
    sales = db.df_sales
    products = db.df_products
    sales["short_date"] = sales["date"].apply(short_date)
    sales = sales.merge(products, on=["store", "id"])

    month, year = map(int, datetime.date.today().strftime("%m %y").split())
    months = []
    for i in range(25):
        months.append(f"{month // 10}{month % 10}.{year % 100}")
        month -= 1
        if not month:
            year -= 1
            month = 12
    months = months[::-1]
    wb = [
        sum(
            (sales["short_date"] == months[i])
            & (sales["vendor_code"].str.contains(art))
            & (sales["store"] == "wb")
        )
        for i in range(25)
    ]
    ozon = [
        sum(
            (sales["short_date"] == months[i])
            & (sales["vendor_code"].str.contains(art))
            & (sales["store"] == "ozon")
        )
        for i in range(25)
    ]

    plt.figure(figsize=(15, 6))

    x = np.arange(25)

    plt.bar(x - 0.2, wb, 0.4, color="violet")
    plt.bar(x + 0.2, ozon, 0.4, color="blue")

    plt.xticks(x, months, rotation=45)

    plt.xlabel("месяц")
    plt.ylabel("кол-во продаж")
    plt.legend(["wb", "ozon"])

    plt.show()


month_names = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]


def get_dynamic() -> float:

    def get_period(date: str):
        try:
            date_format = "%H:%M:%S %d.%m.%Y"
            return (
                datetime.datetime.now() - datetime.datetime.strptime(date, date_format)
            ).days // 90
        except Exception:
            try:
                date_format = "%Y-%m-%d %H:%M:%S"
                return (
                    datetime.datetime.now()
                    - datetime.datetime.strptime(date, date_format)
                ).days // 90
            except:
                return 9999

    db = database.Database()
    sales = db.df_sales
    products = db.df_products
    sales = sales.merge(products, on="id")
    sales_now = sales[sales["date"].apply(get_period) == 0]
    sales_last = sales[sales["date"].apply(get_period) == 1]
    now = sum(sales_now["price_x"] - sales_now["cost"])
    last = sum(sales_last["price_x"] - sales_last["cost"])
    return now / last if last != 0 else 1


def get_ABC() -> tuple[int, int, int]:

    def get_period(date: str):
        try:
            date_format = "%H:%M:%S %d.%m.%Y"
            return (
                datetime.datetime.now() - datetime.datetime.strptime(date, date_format)
            ).days // 90
        except Exception:
            try:
                date_format = "%Y-%m-%d %H:%M:%S"
                return (
                    datetime.datetime.now()
                    - datetime.datetime.strptime(date, date_format)
                ).days // 90
            except:
                return 9999

    db = database.Database()
    sales = db.df_sales
    sales = sales[sales["date"].apply(get_period) == 0]
    products = db.df_products
    sales = sales.merge(products, on="id")
    sales["profit"] = sales["price_x"] - sales["cost"]
    sales = list(
        (sales.groupby("vendor_code").agg({"profit": "sum"}))["profit"].sort_values(
            ascending=False
        )
    )
    if not sales:
        return 0, 0, 0
    s = sum(sales)
    a = 0
    while sum(sales[:a]) < 0.8 * sum(sales):
        a += 1
    b = a
    while sum(sales[:b]) < 0.95 * sum(sales):
        b += 1
    c = len(sales)
    return (
        (a + 1) * 100 // len(sales),
        (b - a + 1) * 100 // len(sales),
        (c - b + 1) * 100 // len(sales),
    )


def download_full(filename: str) -> str:

    def short_date(date: str):
        try:
            date_format = "%H:%M:%S %d.%m.%Y"
            return datetime.datetime.strptime(date, date_format).strftime("%m.%y")
        except Exception:
            try:
                date_format = "%Y-%m-%d %H:%M:%S"
                return datetime.datetime.strptime(date, date_format).strftime("%m.%y")
            except Exception:
                return "01.01"

    db = database.Database()
    sales = db.df_sales
    products = db.df_products
    sales["short_date"] = sales["date"].apply(short_date)
    sales = sales.merge(products, on=["store", "id"])
    sales = (
        sales.groupby(["short_date", "store", "id"])
        .agg({"date": "count", "vendor_code": "max", "name": "max", "brand": "max"})
        .rename(columns={"date": "n"})
        .reset_index()
    )
    print(sales)
    dates = list(set(sales["short_date"]))
    stores = list(set(sales["store"]))
    brands = list(set(sales["brand"]))
    df = []
    for x in sales.values:
        print(x)
    file = gen_download_file(filename, "xlsx")
    df_to_xlsx(sales, file)
    return str(file)
