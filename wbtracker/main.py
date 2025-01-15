import datetime
import json
from tkinter.filedialog import askopenfile
from typing import Any

import appdata
import requests
import win
from pandas import read_excel


def read_product_list() -> dict:
    with open(appdata.root / "data" / "product-list.json", "r") as pl:
        return json.load(pl)


def write_product_list(product_list: Any) -> None:
    with open(appdata.root / "data" / "product-list.json", "w") as pl:
        json.dump(product_list, pl)


def get_wb_price(article: str) -> int:
    wb = requests.get(f"https://card.wb.ru/cards/v2/detail?dest=-1257786&nm={article}")
    return wb.json()["data"]["products"][0]["sizes"][0]["price"]["total"] // 100


class MainWindow(win.Window):
    def __init__(self) -> None:
        super().__init__(1080, 720, "WB Tracker")
        self.reg_obj(win.Background(self, (200, 200, 200)))
        self.reg_obj(
            win.TextButton(
                "add-products",
                self,
                100,
                600,
                250,
                50,
                10,
                "Добавить виды товаров",
                14,
                self._add_products,
            )
        )
        self.reg_obj(
            win.TextButton(
                "record",
                self,
                400,
                600,
                250,
                50,
                10,
                "Сделать запись",
                14,
                self._record,
            )
        )
        self.reg_obj(
            win.TextButton(
                "show-deltas",
                self,
                700,
                600,
                250,
                50,
                10,
                "Проверить цены",
                14,
                self._show_deltas,
            )
        )

    def _add_products(self) -> None:
        if not (file := askopenfile()):
            return
        for product in read_excel(file.name).values:
            self._add_product(product[0], product[1])

    def _add_product(self, inner_article: str, wb_article: str) -> None:
        product_list = read_product_list()
        if wb_article not in product_list:
            product_list[wb_article] = {"inner-article": inner_article, "history": {}}
            write_product_list(product_list)

    def _record(self) -> None:
        if "body" in self:
            self.remove_obj("body")
            self.on_draw()
        cnt = 0
        loading = win.Text("loading", self, "0/?", 100, 100, 14)
        self.reg_obj(loading)
        self.on_draw()
        product_list = read_product_list()
        loading.text.text = f"0/{len(product_list)}"
        self.on_draw()
        for wb_article, data in product_list.items():
            try:
                print(wb_article)
                data["history"][str(datetime.date.today())] = get_wb_price(wb_article)
            except Exception:
                ...
            cnt += 1
            loading.text.text = f"{cnt}/{len(product_list)}"
            self.on_draw()
        write_product_list(product_list)
        self.remove_obj("loading")

    def _show_deltas(self):

        def draw_top():
            if "top" in body:
                body.remove_obj("top")
            top_obj = win.WinBlock("top", self)
            body.reg_obj(top_obj)
            for i in range(10):
                if i + start[0] >= len(top):
                    break
                wb_article = top[i + start[0]][0]
                cur_price = top[i + start[0]][1][1]
                old_price = top[i + start[0]][2][1]
                top_obj.reg_obj(
                    win.Text(
                        f"top-wb-{i}", self, f"{wb_article}", 100, 500 - 20 * i, 14
                    )
                )
                top_obj.reg_obj(
                    win.Text(
                        f"top-cur-{i}", self, f"{cur_price}", 220, 500 - 20 * i, 14
                    )
                )
                top_obj.reg_obj(
                    win.Text(
                        f"top-old-{i}", self, f"{old_price}", 300, 500 - 20 * i, 14
                    )
                )

        def up():
            if start[0] >= 0:
                start[0] -= 1
                draw_top()

        def down():
            if start[0] + 1 < len(top):
                start[0] += 1
                draw_top()

        if "body" in self:
            self.remove_obj("body")
        body = win.WinBlock("body", self)
        self.reg_obj(body)
        body.reg_obj(
            win.TextButton("scroll-up", self, 1000, 400, 50, 50, 5, "up", 14, up)
        )
        body.reg_obj(
            win.TextButton("scroll-down", self, 1000, 300, 50, 50, 5, "down", 14, down)
        )
        product_list = read_product_list()
        top = []
        for wb_article, data in product_list.items():
            history = list(data["history"].items())
            history.sort(
                key=lambda x: datetime.datetime.strptime(x[0], "%Y-%m-%d"), reverse=True
            )
            if len(history) >= 2:
                top.append([wb_article, history[0], history[1]])
        top.sort(key=lambda x: abs(x[1][1] - x[2][1]))
        start = [0]
        print(len(top))
        draw_top()


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
