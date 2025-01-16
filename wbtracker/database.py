import json

import appdata


class Database:

    class Product:

        def __init__(self, args: dict) -> None:
            self._store: str = args["store"]
            self._id: str = args["id"]
            self._vendor_code: str = args["vendor_code"]
            self._name: str = args["name"]
            self._price: int = args["price"]
            self._cost: int = args["cost"]

        def __eq__(self, value: object) -> bool:
            return isinstance(value, Database.Product) and (self._store, self._id) == (
                value._store,
                value._id,
            )

        @property
        def args(self) -> dict:
            return {
                "store": self._store,
                "id": self._id,
                "vendor_code": self._vendor_code,
                "name": self._name,
                "price": self._price,
                "cost": self._cost,
            }

    class Sale:

        def __init__(self, args: dict) -> None:
            self._store: str = args["store"]
            self._sticker: str = args["sticker"]
            self._id: str = args["id"]
            self._date: str = args["date"]
            self._price: int = args["price"]

        def __eq__(self, value: object) -> bool:
            return isinstance(value, Database.Sale) and (
                self._store,
                self._sticker,
                self._id,
                self._date,
            ) == (value._store, value._sticker, value._id, value._date)

        @property
        def args(self) -> dict:
            return {
                "store": self._store,
                "sticker": self._sticker,
                "id": self._id,
                "date": self._date,
                "price": self._price,
            }

    def __init__(self) -> None:
        self._products = self._load_products()
        self._sales = self._load_sales()

    def _load_products(self) -> list[Product]:
        with open(appdata.root / "data" / "database" / "products.json", "r") as fp:
            return [Database.Product(args) for args in json.load(fp)["products"]]

    def _save_products(self) -> None:
        with open(appdata.root / "data" / "database" / "products.json", "w") as fp:
            json.dump({"products": [product.args for product in self._products]}, fp)

    def _load_sales(self) -> list[Sale]:
        with open(appdata.root / "data" / "database" / "sales.json", "r") as fp:
            return [Database.Sale(args) for args in json.load(fp)["sales"]]

    def _save_sales(self) -> None:
        with open(appdata.root / "data" / "database" / "sales.json", "w") as fp:
            json.dump({"sales": [sale.args for sale in self._sales]}, fp)

    def save(self) -> None:
        self._save_products()
        self._save_sales()

    def add_product(self, product: Product) -> None:
        if product in self._products:
            ind = self._products.index(product)
            self._products[ind] = product
        else:
            self._products.append(product)
        self.save()

    def add_sale(self, sale: Sale) -> None:
        if sale in self._sales:
            ind = self._sales.index(sale)
            self._sales[ind] = sale
        else:
            self._sales.append(sale)
        self.save()

if __name__ == "__main__":
    db = Database()
    print(db._products[0]._name)
    db.save()