from abc import ABC, abstractmethod
from collections.abc import Generator

import database


class Store(ABC):
    name: str

    @classmethod
    @abstractmethod
    def build_sale(
        cls, row: list[str]
    ) -> tuple[database.Database.Sale, str, str, str]: ...

    @classmethod
    @abstractmethod
    def link(cls, id: str) -> str: ...


class WB(Store):
    name = "wb"

    @classmethod
    def build_sale(cls, row: list[str]) -> tuple[database.Database.Sale, str, str, str]:
        return (
            database.Database.Sale(
                {
                    "store": cls.name,
                    "sticker": row[2],
                    "id": row[12],
                    "date": row[4],
                    "price": int(float(row[10])),
                }
            ),
            row[16],
            row[6],
            row[13],
        )

    @classmethod
    def link(cls, id: str) -> str:
        return f"https://www.wildberries.ru/catalog/{id}/detail.aspx"


class Ozon(Store):
    name = "ozon"

    @classmethod
    def build_sale(cls, row: list[str]) -> tuple[database.Database.Sale, str, str, str]:
        return (
            database.Database.Sale(
                {
                    "store": cls.name,
                    "sticker": row[0],
                    "id": row[10],
                    "date": row[5],
                    "price": int(float(row[7])),
                }
            ),
            row[4],
            row[9],
            row[11],
        )

    @classmethod
    def link(cls, id: str) -> str:
        return f"https://www.ozon.ru/product/{id}/"


class UnknownStore(Store):
    name = "unknown"


def get_store(name: str) -> tuple[type[Store], str]:
    if name.startswith("wb") or name.startswith("вб"):
        return WB, name[2:]
    elif name.startswith("oz") or name.startswith("оз"):
        return Ozon, name[2:]
    elif name.startswith("ozon") or name.startswith("озон"):
        return Ozon, name[4:]
    else:
        return UnknownStore, name


def build_product(name: str, id: str, cost: int) -> database.Database.Product:
    store, brand = get_store(name)
    return database.Database.Product(
        {
            "store": store.name,
            "id": id,
            "vendor_code": "",
            "name": "",
            "price": -1,
            "cost": cost,
            "brand": brand,
        }
    )
