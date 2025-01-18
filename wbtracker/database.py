import json

import appdata


class Database:

    class Product:

        Key = tuple[str, str]

        def __init__(self, args: dict) -> None:
            self._store: str = args["store"]
            self._id: str = args["id"]
            self.vendor_code: str = args["vendor_code"]
            self.name: str = args["name"]
            self.price: int = args["price"]
            self.cost: int = args["cost"]
            self.brand: str = args["brand"]

        def __eq__(self, value: object) -> bool:
            return isinstance(value, Database.Product) and self.key == value.key

        @property
        def args(self) -> dict:
            return {
                "store": self._store,
                "id": self._id,
                "vendor_code": self.vendor_code,
                "name": self.name,
                "price": self.price,
                "cost": self.cost,
                "brand": self.brand,
            }

        @property
        def key(self) -> Key:
            return self._store, self._id

    class Sale:

        Key = tuple[str, str, str, str]

        def __init__(self, args: dict) -> None:
            self._store: str = args["store"]
            self._sticker: str = args["sticker"]
            self._id: str = args["id"]
            self._date: str = args["date"]
            self.price: int = args["price"]

        def __eq__(self, value: object) -> bool:
            return isinstance(value, Database.Sale) and self.key == value.key

        @property
        def args(self) -> dict:
            return {
                "store": self._store,
                "sticker": self._sticker,
                "id": self._id,
                "date": self._date,
                "price": self.price,
            }

        @property
        def key(self) -> Key:
            return self._store, self._sticker, self._id, self._date

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
        if product not in self._products:
            self._products.append(product)

    def add_sale(self, sale: Sale) -> None:
        if sale not in self._sales:
            self._sales.append(sale)

    def find_product(self, key: Product.Key) -> Product | None:
        for product in self._products:
            if key == product.key:
                return product
        return None

    def find_sale(self, key: Sale.Key) -> Sale | None:
        for sale in self._sales:
            if key == sale.key:
                return sale
        return None
