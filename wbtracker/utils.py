import datetime
import webbrowser
from collections.abc import Generator
from pathlib import Path
from tkinter.filedialog import askopenfile

import database
import opener
import pandas as pd


def read_products() -> Generator[database.Database.Product]:
    if not (file := askopenfile()):
        return
    for product in pd.read_excel(file.name).values:
        yield database.Database.Product(
            {
                "store": str(product[0]),
                "id": str(product[1]),
                "vendor_code": "",
                "name": "",
                "price": -1,
                "cost": int(product[2]),
                "brand": "",
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
    db = database.Database()
    for product in read_products():
        yield f"{product.key}"
        add_product(db, product)
    db.save()


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
    df_to_xlsx(get_df_products(), file := gen_download_file("products", "xlsx"))
    return str(file)


def get_df_sales(start: datetime.datetime, end: datetime.datetime) -> pd.DataFrame:

    def check_date(row: pd.Series):
        date_format = (
            "%H:%M:%S %d.%m.%Y" if row["store"] == "wb" else "%Y-%m-%d %H:%M:%S"
        )
        return start <= datetime.datetime.strptime(row["date"], date_format) <= end

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
        .rename(
            {
                "store": "Магазин",
                "id": "Артикул",
                "vendor_code": "Код продавца",
                "name": "Название",
                "sum": "Сумма",
                "n": "Кол-во",
                "profit": "Прибыль",
            }
        )
        .sort_values("n", ascending=False)
    )
    return df


def download_sales(start: datetime.datetime, end: datetime.datetime) -> str:
    df_to_xlsx(get_df_sales(start, end), file := gen_download_file("sales", "xlsx"))
    return str(file)


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
